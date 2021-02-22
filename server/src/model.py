import pandas as pd
import xgboost as xgb
import numpy as np
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer, KNNImputer
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OrdinalEncoder, StandardScaler, MinMaxScaler

from pprint import pprint

from crawler.models import db_connect

from google.cloud import bigquery

bq_client = bigquery.Client()

import logging

logging.basicConfig(format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S', level=logging.INFO)

PREPROCESSOR_COLS = []


def train_model():
    # Import datasets.
    logging.info('Importing datasets.')
    engine = db_connect()
    imdb_df = pd.read_sql_query('SELECT * FROM imdb', con=engine)
    my_ratings_df = pd.read_sql_query('SELECT * FROM my_ratings', con=engine)
    tmdb_df = bq_client.query('SELECT * FROM `rosy-algebra-304808.tv_dataset.imdb_series_aug`').to_dataframe()

    # Merge datasets together.
    logging.info('Merging datasets.')
    tv_df = pd.merge(imdb_df, my_ratings_df, how="left", left_on='id', right_on='imdb_id')
    tv_df = pd.merge(tv_df, tmdb_df, how="left", left_on='id', right_on='index')
    imdb_df.set_index('id', inplace=True)
    tv_df.set_index('id', inplace=True)

    # Drop prediction feature.
    tv_df.drop('prediction', axis=1, inplace=True)

    # Save a copy to display results after prediction.
    main_df = tv_df.copy()

    # Create new feature: episodes per season.
    tv_df['ep_per_season'] = tv_df['n_episodes'] / tv_df['n_seasons']

    # Fill None values with nan.
    tv_df = tv_df.fillna(value=np.nan)

    # Divide rated tv shows from unrated ones.
    rated_df = tv_df.dropna(axis=0, subset=["my_rating"])
    unrated_df = tv_df[tv_df["my_rating"].isna()].drop(columns=["my_rating"])

    # Split rated tv shows into training set and test set.
    X = rated_df.drop(columns=["my_rating"])
    y = rated_df["my_rating"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, train_size=0.8, random_state=17)

    preprocessor = create_preprocessor(tv_df)

    model = make_pipeline(
        preprocessor,
        xgb.XGBRegressor(random_state=17))

    # Tune parameters.
    param_grid = {
        'xgbregressor__n_estimators': [500],
        'xgbregressor__max_depth': [4],
        'xgbregressor__min_child_weight': [9],
        'xgbregressor__eta': [.01],
        'xgbregressor__eval_metric': ['mae']
    }

    grid_clf = GridSearchCV(model, param_grid, cv=10, n_jobs=4, verbose=1)
    grid_clf.fit(X_train, y_train)

    logging.warning(f'BEST PARAMETERS: {grid_clf.best_params_}\n')

    model = grid_clf.best_estimator_

    # Calculate Mean Absolute Error over training set.
    scores = cross_val_score(model, X_train, y_train, scoring="neg_mean_absolute_error", cv=10)
    logging.info(f"MAE on training set: {-scores.mean():.2f} (+/- {(scores.std() * 2):.2f})\n")

    # Print out most important features.
    logging.info(pprint([f"{a}: {b:.2f}" for (a, b) in sorted(zip(PREPROCESSOR_COLS, model[1].feature_importances_),
                                                              key=lambda x: x[1], reverse=True)]))

    # Predict results for test set.
    predictions = model.predict(X_test)

    # Display results comparing them to real personal ratings.
    valid_results = pd.DataFrame(data=dict(prediction=predictions, real=y_test.to_list(),
                                           difference=predictions - y_test.to_list()),
                                 index=main_df.loc[y_test.index, "name"])
    logging.info(valid_results.sort_values(by="difference", ascending=False).round(decimals=2))

    logging.info(f"MAE on test set: {mean_absolute_error(y_test, predictions):.2f}\n")

    predictions = model.predict(unrated_df)

    # Display best tv series to watch.
    predictions_df = main_df.copy().dropna(how='all')
    predictions_df["prediction"] = pd.Series(data=predictions, index=unrated_df.index)

    # Sort and round numbers.
    predictions_df = predictions_df.sort_values(by="prediction", ascending=False)[
        ["name", "prediction"]].round(decimals=2)

    # Save predictions to tvdb table.
    imdb_df['prediction'] = predictions_df["prediction"]
    # Keep overview from tmdb table.
    imdb_df['overview'] = tmdb_df['overview']
    # Export the dataframe to the database.
    engine = db_connect()
    logging.info("Saving database to imdb table.")
    imdb_df.to_sql('imdb', engine, if_exists='replace')
    logging.info("Database updated with prediction.")


def create_preprocessor(tv_df):
    year_pipe = make_pipeline(
        SimpleImputer(strategy="constant", fill_value=tv_df["start_year"].max()),
        MinMaxScaler())

    genre_pipe = make_pipeline(
        SimpleImputer(strategy="constant", fill_value=0))

    avg_ratings_pipe = make_pipeline(
        KNNImputer(n_neighbors=5, weights="uniform"),
        StandardScaler())

    creators_avg_rating_pipe = make_pipeline(
        SimpleImputer(strategy="constant", fill_value='Unknown'),
        AvgRatingForCategoryTransformer(),
        MinMaxScaler())

    popularity_pipe = make_pipeline(
        SimpleImputer(strategy="constant", fill_value=tv_df["popularity_rank"].max(), add_indicator=True),
        MinMaxScaler())

    ordinal_pipe = make_pipeline(
        SimpleImputer(strategy="most_frequent"),
        OrdinalEncoder())

    knn_pipe = make_pipeline(
        KNNImputer(n_neighbors=3, weights="distance"),
        MinMaxScaler()
    )

    year_cat = ["start_year", "end_year"]
    genre_cat = [name for name in tv_df.columns if name.startswith("genre")]
    avg_ratings_cat = [name for name in tv_df.columns if name.startswith("rating_")]
    creators_avg_rating_cat = ['creators', 'networks', 'production_companies']
    popularity_cat = ["popularity_rank"]
    ordinal_cat = ["type"]
    knn_cat = ['n_episodes', 'n_ratings', 'n_seasons', 'ep_length', 'ep_per_season']

    transformers = [
        ('year', year_pipe, year_cat),
        ('genres', genre_pipe, genre_cat),
        ('avg_ratings', avg_ratings_pipe, avg_ratings_cat),
        ('creators_avg_rating', creators_avg_rating_pipe, creators_avg_rating_cat),
        ('popularity', popularity_pipe, popularity_cat),
        ('ordinal', ordinal_pipe, ordinal_cat),
        ('knn', knn_pipe, knn_cat)
    ]

    # Save columns used for column transformer. They will be used for feature importance in XGBoost.
    global PREPROCESSOR_COLS
    PREPROCESSOR_COLS = year_cat + genre_cat + avg_ratings_cat + creators_avg_rating_cat + popularity_cat + ordinal_cat + knn_cat

    preprocessor = ColumnTransformer(transformers, remainder='drop')

    return preprocessor


class AvgRatingForCategoryTransformer:
    def __init__(self):
        self.categories = []

    def fit(self, X, y=None, **fit_params):
        # Drop target feature (Series) index.
        y_series = y.reset_index(drop=True)

        # Save average ratings for each feature (3 at the moment).
        for col in range(X.shape[1]):
            ratings = {}
            # For each TV show, extrapolate avg rating for value of feature.
            for row in range(X.shape[0]):
                names_str = X[row, col]
                creators_list = names_str.split('|')
                # For each creator that made the TV show, find other TV shows made by him.
                for creator in creators_list:
                    # Drop rating being considered to avoid leakage.
                    y_list = y_series.drop(labels=[row]).tolist()

                    # Keep only tv shows related to the one being analyzed.
                    col_list = list(X[:, col])
                    # Remove row being considered.
                    del col_list[row]
                    # Filter all elements in 'creators' column containing name of creator.
                    mask = [creator in row for row in col_list]
                    mod_y_list = (np.array(y_list)[mask]).tolist()
                    # Save avg rating.
                    if len(mod_y_list) == 0:
                        ratings[creator] = 6
                    else:
                        value = y_series.iloc[row]
                        a = mod_y_list + [value]
                        ratings[creator] = np.mean(a)
            self.categories.append(ratings)
        return self

    def transform(self, X, **transform_params):
        for i in range(len(self.categories)):
            j = 0
            # For each column, substitute the name with its avg rating.
            for names in X[:, i]:
                names_list = names.split('|')
                # Assign the max avg_rating out of all the names present.
                # The thinking behind this is that a respectable name demands more from the others.
                X[j, i] = np.max([self.categories[i].get(name, 6) for name in names_list])
                j += 1
        return X
