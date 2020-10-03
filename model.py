import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer, KNNImputer
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder, StandardScaler, MinMaxScaler
import xgboost as xgb

from crawlers.imdb_crawler.models import db_connect


def train_model(local):
    # Import datasets.
    engine = db_connect(local)
    imdb_df = pd.read_sql_query('SELECT * FROM imdb', con=engine, index_col="id")
    tvdb_df = pd.read_sql_query('SELECT * FROM tvdb', con=engine, index_col="imdb_id")
    my_ratings_df = pd.read_sql_query('SELECT * FROM my_ratings', con=engine, index_col="imdb_id")

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

    # Create new feature: episodes per season.
    tv_df['ep_per_season'] = tv_df['n_episodes'] / tv_df['n_seasons']

    # Fill NaN values in network.
    tv_df['network'] = tv_df['network'].fillna('Unknown')
    # Calculate my avg rating for each network.
    networks_rat = tv_df.groupby(by="network").mean()["my_rating"].sort_values(ascending=False)
    # Replace network name with my avg rating for its shows.
    tv_df['network'] = tv_df["network"].map(lambda x: networks_rat[x])

    # Split training set and test set.
    rated_df = tv_df.dropna(axis=0, subset=["my_rating"])

    unrated_df = tv_df[tv_df["my_rating"].isna()].drop("my_rating", axis=1)
    unrated_df = unrated_df[unrated_df["type"].notna()]

    X = rated_df.drop(["my_rating"], axis=1)
    y = rated_df["my_rating"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, train_size=0.8, random_state=17)

    preprocessor = create_preprocessor(tv_df)

    model = make_pipeline(
        preprocessor,
        xgb.XGBRegressor(random_state=17))

    # Tune parameters.
    param_grid = {
        'xgbregressor__n_estimators': [40],
        'xgbregressor__max_depth': [7],
        'xgbregressor__min_child_weight': [8],
        'xgbregressor__eta': [.1],
        'xgbregressor__eval_metric': ['mae']
    }

    grid_clf = GridSearchCV(model, param_grid, cv=10, n_jobs=4, verbose=1)
    grid_clf.fit(X_train, y_train)

    print(grid_clf.best_params_)

    model = grid_clf.best_estimator_

    # Calculate Mean Absolute Error over training set.
    scores = cross_val_score(model, X_train, y_train, scoring="neg_mean_absolute_error", cv=10)
    print(f"MAE on training set: {-scores.mean():.2f} (+/- {(scores.std() * 2):.2f})")

    # Predict results for test set.
    predictions = model.predict(X_test)

    # Display results comparing them to real personal ratings.
    valid_results = pd.DataFrame(data=dict(prediction=predictions, real=y_test.to_list(),
                                           difference=predictions - y_test.to_list()),
                                 index=main_df.loc[y_test.index, "name"])
    print(valid_results.sort_values(by="difference", ascending=False).round(decimals=2))

    print(f"MAE on test set: {mean_absolute_error(y_test, predictions):.2f}")

    predictions = model.predict(unrated_df)

    # Display best tv series to watch, removing documentary because I do not care about them.
    predictions_df = main_df.copy().dropna(how='all')
    predictions_df["prediction"] = pd.Series(data=predictions, index=unrated_df.index)

    # Sort and round numbers.
    predictions_df = predictions_df.sort_values(by="prediction", ascending=False)[
        ["name", "prediction", "overview"]].round(decimals=2)

    # Save predictions to tvdb table.
    tvdb_df['prediction'] = predictions_df["prediction"]
    # Export the dataframe to the database.
    engine = db_connect(local)
    print("Saving database to tvdb table.")
    tvdb_df.to_sql('tvdb', engine, if_exists='replace')


def create_preprocessor(tv_df):
    year_pipe = make_pipeline(
        SimpleImputer(strategy="constant", fill_value=tv_df["start_year"].max()),
        MinMaxScaler())

    genre_pipe = make_pipeline(
        SimpleImputer(strategy="constant", fill_value=0))

    avg_ratings_pipe = make_pipeline(
        KNNImputer(n_neighbors=5, weights="uniform"),
        StandardScaler())

    popularity_pipe = make_pipeline(
        SimpleImputer(strategy="constant", fill_value=tv_df["popularity_rank"].max(), add_indicator=True),
        MinMaxScaler())

    ordinal_pipe = make_pipeline(
        SimpleImputer(strategy="most_frequent"),
        OrdinalEncoder())

    rating_pipe = make_pipeline(
        SimpleImputer(strategy="constant", fill_value="unknown"),
        OneHotEncoder(categories=[np.append(tv_df["rating"].unique(), "unknown")]))

    network_pipe = make_pipeline(
        SimpleImputer(strategy='mean'),
        StandardScaler())

    knn_pipe = make_pipeline(
        KNNImputer(n_neighbors=3, weights="distance"),
        MinMaxScaler()
    )

    year_cat = ["start_year", "end_year"]
    genre_cat = [name for name in tv_df.columns if name.startswith("genre")]
    avg_ratings_cat = [name for name in tv_df.columns if name.startswith("rating_")]
    popularity_cat = ["popularity_rank"]
    ordinal_cat = ["type", "status"]
    rating_cat = ["rating"]
    network_cat = ["network"]
    knn_cat = ['n_episodes', 'n_ratings', 'tvdb_ratings', 'num_seasons', 'ep_length', 'tvdb_avg_rating',
               'ep_per_season']

    transformers = [
        ('year', year_pipe, year_cat),
        ('genres', genre_pipe, genre_cat),
        ('avg_ratings', avg_ratings_pipe, avg_ratings_cat),
        ('popularity', popularity_pipe, popularity_cat),
        ('ordinal', ordinal_pipe, ordinal_cat),
        ('rating', rating_pipe, rating_cat),
        ('network', network_pipe, network_cat),
        ('knn', knn_pipe, knn_cat)
    ]

    preprocessor = ColumnTransformer(transformers, remainder='drop')

    return preprocessor
