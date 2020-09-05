import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder, StandardScaler, MinMaxScaler
from xgboost import XGBRegressor

from crawlers.imdb_crawler.models import db_connect


def train_model(local):
    # Import datasets.
    engine = db_connect(local)
    imdb_df = pd.read_sql_query('SELECT * FROM imdb', con=engine, index_col="id")
    tvdb_df = pd.read_sql_query('SELECT * FROM tvdb', con=engine, index_col="imdb_id")
    my_ratings_df = pd.read_sql_query('SELECT * FROM my_ratings', con=engine, index_col="imdb_id")

    # Drop tvdb genres columns because already present in imdb.
    genres_columns = [col for col in tvdb_df.columns if col.startswith("genre_")]
    tvdb_df.drop(columns=genres_columns, axis=1, inplace=True)

    # Drop num_seasons and runtime because already present in imdb.
    tvdb_df.drop(columns=['num_seasons', 'runtime'], axis=1, inplace=True)

    # Merge datasets together.
    cols_to_use = tvdb_df.columns.difference(imdb_df.columns)
    df1 = pd.merge(imdb_df, tvdb_df[cols_to_use], how="outer", left_index=True, right_index=True)

    cols_to_use = my_ratings_df.columns.difference(df1.columns)
    tv_df = pd.merge(df1, my_ratings_df[cols_to_use], how="outer", left_index=True, right_index=True)

    # Drop prediction feature if present.
    try:
        tv_df.drop('prediction', axis=1, inplace=True)
    except KeyError:
        pass

    # Save a copy to display results after prediction.
    main_df = tv_df.copy()

    # Remove useless columns.
    cols_to_remove = ["name", "series_name", "banner",
                      "fanart", "overview", "poster", "first_aired", "tvdb_id"]
    tv_df.drop(cols_to_remove, axis=1, inplace=True)

    # Identify popular networks.
    popular_networks = tv_df.groupby(by="network").count().sort_values(by="my_rating", ascending=False)[
                       :20].index.to_list()
    # Change network value of unpopular networks as "unpopular".
    tv_df["network"] = tv_df["network"].map(lambda x: x if x in popular_networks else "unpopular")

    # Split training set and test set.
    train_df = tv_df.dropna(axis=0, subset=["my_rating"])

    test_df = tv_df[tv_df["my_rating"].isna()].drop("my_rating", axis=1)
    test_df = test_df[test_df["type"].notna()]

    X = train_df.drop(["my_rating"], axis=1)
    y = train_df["my_rating"]

    # Break off validation set from training data.
    X_train, X_valid, y_train, y_valid = train_test_split(X, y, train_size=0.8, test_size=0.2, random_state=0)

    transformer = create_transformer(tv_df)

    tr_X_train = transformer.fit_transform(X_train)
    tr_X_valid = transformer.transform(X_valid)

    # Fit model.
    model = XGBRegressor(n_estimators=500, random_state=17)
    model.fit(tr_X_train, y_train, early_stopping_rounds=5, eval_set=[(tr_X_valid, y_valid)], verbose=False)
    n_estimators = model.get_booster().best_iteration

    # Predict results for validation set.
    valid_predictions = model.predict(tr_X_valid)

    # Display results comparing them to real personal ratings.
    valid_results = pd.DataFrame(data=dict(prediction=valid_predictions, real=y_valid.to_list(),
                                           difference=valid_predictions - y_valid.to_list()),
                                 index=main_df.loc[y_valid.index, "name"])
    print(valid_results.sort_values(by="difference", ascending=False).round(decimals=2))

    print(f"MRSE: {np.sqrt(mean_squared_error(y_valid, valid_predictions)):.2f}")
    print(f"R2 score: {r2_score(y_valid, valid_predictions):.2f}")

    # Fit model on the whole training data.
    tr_X = transformer.fit_transform(X)
    model = XGBRegressor(n_estimators=n_estimators)
    model.fit(tr_X, y)

    # Predict unseen ratings of unseen tv series.
    tr_X_test = transformer.transform(test_df)
    test_predictions = model.predict(tr_X_test)

    # Display best tv series to watch, removing documentary because I do not care about them.
    predictions_df = main_df.copy().dropna(how='all')
    predictions_df["prediction"] = pd.Series(data=test_predictions, index=test_df.index)
    # Remove documentaries.
    predictions_df = predictions_df[predictions_df["genre_documentary"] == 0]

    # Sort and round numbers.
    predictions_df = predictions_df.sort_values(by="prediction", ascending=False)[
        ["name", "prediction", "overview"]].round(decimals=2)

    # Save predictions to tvdb table.
    tvdb_df['prediction'] = predictions_df["prediction"]
    # Export the dataframe to the database.
    engine = db_connect(local)
    print("Saving database to tvdb table.")
    tvdb_df.to_sql('tvdb', engine, if_exists='replace')


def create_transformer(tv_df):
    year_pipe = make_pipeline(
        SimpleImputer(strategy="constant", fill_value=tv_df["start_year"].dropna().max()),
        StandardScaler())

    genre_pipe = make_pipeline(
        SimpleImputer(strategy="constant", fill_value=0))

    string_pipe = make_pipeline(
        SimpleImputer(strategy="most_frequent"),
        OrdinalEncoder())

    cat_pipe = make_pipeline(
        SimpleImputer(strategy="constant", fill_value="unknown"),
        OneHotEncoder(categories=[np.append(tv_df["rating"].unique(), "unknown")]))

    rating_pipe = make_pipeline(
        SimpleImputer(strategy="median", add_indicator=True),
        StandardScaler())

    popularity_pipe = make_pipeline(
        SimpleImputer(strategy="constant", fill_value=tv_df["popularity_rank"].max(), add_indicator=True),
        StandardScaler())

    network_pipe = make_pipeline(
        OneHotEncoder(categories=[tv_df["network"].unique()]))

    year_cat = ["start_year", "end_year"]
    genre_cat = [name for name in tv_df.columns if name.startswith("genre")]
    rating_cat = [name for name in tv_df.columns if name.startswith("rating_")]
    popularity_cat = ["popularity_rank"]
    ordinal_cat = ["type", "status"]

    transformers = [
        ("start_year", year_pipe, year_cat),
        ("genre", genre_pipe, genre_cat),
        ("ratings", rating_pipe, rating_cat),
        ("popularity", popularity_pipe, popularity_cat),
        ("ordinal", string_pipe, ordinal_cat),
        ("cat", cat_pipe, ["rating"]),
        ("network", network_pipe, ["network"])
    ]

    transformer = ColumnTransformer(
        transformers,
        remainder=SimpleImputer(add_indicator=True))

    return transformer
