import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder, StandardScaler, MinMaxScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score

try:
    from xgboost import XGBRegressor
except:
    pass

from crawlers.imdb_crawler.models import db_connect


def train_model(local):
    tv_df = create_dataset(local)
    main_df = tv_df.copy()
    tv_df = remove_useless_features(tv_df)

    X, y, X_train, X_valid, y_train, y_valid, test_df = split_data(tv_df)

    transformer = create_transformer(tv_df=tv_df)

    tr_X_train = transformer.fit_transform(X_train)
    tr_X_valid = transformer.transform(X_valid)

    num1 = np.sum(np.isnan(tr_X_train))
    num2 = X_train.isna().sum()

    # Fit model.
    try:
        model = XGBRegressor(n_estimators=500, random_state=17)
        model.fit(tr_X_train, y_train, early_stopping_rounds=5, eval_set=[(tr_X_valid, y_valid)], verbose=False)
    except NameError:
        model = RandomForestRegressor(random_state=17)
        model.fit(tr_X_train, y_train)

    # Predict results for validation set.
    valid_predictions = model.predict(tr_X_valid)

    # Display results comparing them to real personal ratings.
    valid_results = pd.DataFrame(data=dict(prediction=valid_predictions, real=y_valid.to_list(),
                                           difference=valid_predictions - y_valid.to_list()),
                                 index=main_df.loc[y_valid.index, "name"])
    print(valid_results.sort_values(by="difference", ascending=False))

    print(f"MRSE: {np.sqrt(mean_squared_error(y_valid, valid_predictions)):.2f}")
    print(f"R2 score: {r2_score(y_valid, valid_predictions):.2f}")

    # Fit model on the whole training data.
    tr_X = transformer.fit_transform(X)
    try:
        model = XGBRegressor(n_estimators=75)
    except NameError:
        pass
    model.fit(tr_X, y)

    # Predict unseen ratings of unseen tv series.
    tr_X_test = transformer.transform(test_df)
    test_predictions = model.predict(tr_X_test)

    # Display best tv series to watch, removing documentary because I do not care about them.
    predictions_df = main_df.copy()
    predictions_df["prediction"] = pd.Series(data=test_predictions, index=test_df.index)
    # Remove documentaries.
    predictions_df = predictions_df[predictions_df["genre_documentary"] == 0]

    predictions_df = predictions_df.sort_values(by="prediction", ascending=False)[["name", "prediction", "overview"]]

    export_predictions(local, predictions_df)


def create_dataset(local):
    # Import datasets.
    engine = db_connect(local)
    tvdb_series_df = pd.read_sql_query('SELECT * FROM tvdb', con=engine, index_col="imdb_id")
    my_ratings_df = pd.read_sql_query('SELECT * FROM my_ratings', con=engine, index_col="imdb_id")
    imdb_series_df = pd.read_sql_query('SELECT * FROM imdb', con=engine, index_col="id")

    # Merge datasets together.
    cols_to_use = tvdb_series_df.columns.difference(imdb_series_df.columns)
    df1 = pd.merge(imdb_series_df, tvdb_series_df[cols_to_use], how="outer", left_index=True, right_index=True)

    cols_to_use = my_ratings_df.columns.difference(df1.columns)
    tv_df = pd.merge(df1, my_ratings_df[cols_to_use], how="outer", left_index=True, right_index=True)

    print("Dataset created.")
    return tv_df


def remove_useless_features(tv_df):
    # Get features correlation.
    corr_matrix = tv_df.corr()

    # Select upper triangle of correlation matrix.
    upper = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(np.bool))

    # Find features with correlation greater than 0.95.
    suspicious_features = upper[upper > 0.95]
    suspicious_features = suspicious_features.dropna(axis=0, how="all").dropna(axis=1, how="all")

    # Rename some columns.
    tv_df.rename(columns={
        "genre_arts": "genre_martial_arts",
        "genre_fiction": "genre_science_fiction",
        "genre_interest": "genre_special_interest"
    })

    # Remove useless columns.
    cols_to_remove = ["name", "genre_martial", "genre_science", "genre_special", "genre_", "series_name", "banner",
                      "fanart", "overview", "poster", "first_aired", "tvdb_id"]
    tv_df.drop(cols_to_remove, axis=1, inplace=True)

    # Identify popular networks.
    popular_networks = tv_df.groupby(by="network").count().sort_values(by="my_rating", ascending=False)[:20].index.to_list()
    # Change network value of unpopular networks as "unpopular".
    tv_df["network"] = tv_df["network"].map(lambda x: x if x in popular_networks else "unpopular")

    return tv_df


def split_data(tv_df):
    # Split training set and test set.
    train_df = tv_df.dropna(axis=0, subset=["my_rating"])

    test_df = tv_df[tv_df["my_rating"].isna()].drop("my_rating", axis=1)
    test_df = test_df[test_df["type"].notna()]

    X = train_df.drop(["my_rating"], axis=1)
    y = train_df["my_rating"]

    # Break off validation set from training data.
    X_train, X_valid, y_train, y_valid = train_test_split(X, y, train_size=0.8, test_size=0.2, random_state=0)

    return X, y, X_train, X_valid, y_train, y_valid, test_df


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

    remainder_pipe = make_pipeline(
        SimpleImputer(add_indicator=True),
        MinMaxScaler()
    )

    year_cat = ["start_year", "end_year"]
    genre_cat = [name for name in tv_df.columns if name.startswith("genre")]
    rating_cat = [name for name in tv_df.columns if name.startswith("rating_")]
    popularity_cat = ["popularity_rank"]
    ordinal_cat = ["type", "status"]

    remainder_cat = [col for col in tv_df.columns if
                     col not in year_cat + genre_cat + rating_cat + popularity_cat + ordinal_cat + ["rating", "network",
                                                                                                    "my_rating"]]

    transformers = [
        ("start_year", year_pipe, year_cat),
        ("genre", genre_pipe, genre_cat),
        ("ratings", rating_pipe, rating_cat),
        ("popularity", popularity_pipe, popularity_cat),
        ("ordinal", string_pipe, ordinal_cat),
        ("cat", cat_pipe, ["rating"]),
        ("network", network_pipe, ["network"]),
        ("remaining", remainder_pipe, remainder_cat)
    ]

    transformer = ColumnTransformer(
        transformers,
        remainder=SimpleImputer(add_indicator=True))

    return transformer


def export_predictions(local, predictions_df):
    # Export the dataframe to the database.
    engine = db_connect(local)
    print("Saving database to tv_episodes table.")
    predictions_df.to_sql('predictions', engine, if_exists='replace')
