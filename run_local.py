from io import StringIO

import pandas as pd
import requests

from crawlers.imdb_crawler.models import db_connect
from helpers.helper import get_tv_shows, get_episodes
from helpers.utility import transform_length


def refine_db(local):
    # Get data from IMDb database.
    engine = db_connect(local)
    print("Refining database...")
    imdb_series_df = pd.read_sql_query('SELECT * FROM imdb', con=engine, index_col="id")

    # Get a list of all the possible genres.
    genres = set(" ".join(imdb_series_df["genres"].dropna().tolist()).split(" "))
    genres = list(filter(lambda x: len(x) > 0, genres))

    # Create and fill columns in the dataframe.
    for i, row in imdb_series_df.iterrows():
        for genre in genres:
            if row["genres"] is not None:
                imdb_series_df.loc[i, f"genre_{genre.lower()}"] = int(genre in row["genres"])

        # Change ep_length format.
        if row["ep_length"] is not None:
            imdb_series_df.loc[i, "ep_length"] = transform_length(row["ep_length"])
    imdb_series_df = imdb_series_df.drop(columns=["genres"])

    # Export the dataframe to the database.
    print("Saving database in imdb table.")
    imdb_series_df.to_sql('imdb', engine, if_exists='replace')


def improve_db(local):
    # Get data from IMDb database.
    engine = db_connect(local)
    print("Improving database...")
    imdb_series_df = pd.read_sql_query('SELECT * FROM imdb', con=engine, index_col="id")

    # Use TVDb APIs to enrich IMDb results.
    tv_series_df = get_tv_shows(imdb_series_df)

    # Encoding of genres.
    # Get a list of all the possible genres.
    genres = set(" ".join(tv_series_df["genres"].tolist()).split(" "))

    # Create and fill columns in the dataframe.
    for i, row in tv_series_df.iterrows():
        for genre in genres:
            tv_series_df.loc[i, f"genre_{genre.lower()}"] = int(genre in row["genres"])
    tv_series_df = tv_series_df.drop(columns=["genres"])

    # Export the dataframe to the database.
    print("Saving database to tvdb table.")
    tv_series_df.to_sql('tvdb', engine, if_exists='replace')


def update_my_ratings(local):
    # Read the source file for TV series found in TV Time.
    engine = db_connect(local)
    tvdb_series_df = pd.read_sql_query('SELECT * FROM tvdb', con=engine, index_col="tvdb_id")

    dwn_url = 'https://drive.google.com/uc?export=download&id='
    id_user_show = '1EfCJWOkRlAagAAkVLBucqeuXlohCQLt0'
    id_my_ratings = '1JQjgo091UeSe-QiAo1turIniipyJqVzb'

    user_tv_show_data_df = pd.read_csv(StringIO(requests.get(dwn_url + id_user_show).text), index_col="tv_show_id")
    my_ratings_df = pd.read_csv(StringIO(requests.get(dwn_url + id_my_ratings).text), index_col="tvdb_id")

    # Keep only followed shows.
    is_followed = user_tv_show_data_df["is_followed"] == 1
    followed_tv_shows_df = user_tv_show_data_df.loc[is_followed]

    # Add ratings for TV series not yet rated.
    for i, tv_show in followed_tv_shows_df.iterrows():
        if i not in list(my_ratings_df.index):
            try:
                rating = pd.DataFrame({
                    "imdb_id": tvdb_series_df.loc[i, "imdb_id"],
                    "series_name": tvdb_series_df.loc[i, "series_name"],
                    "my_rating": None}, index=[i])
                print(f"Adding {tvdb_series_df.loc[i, 'series_name']}")
            except KeyError:
                print(f"Error: {i}")
                rating = pd.DataFrame({
                    "imdb_id": "",
                    "series_name": "",
                    "my_rating": None}, index=[i])
            my_ratings_df = my_ratings_df.append(rating)

    # Export the dataframe to the database.
    engine = db_connect(local)
    print("Saving database to my_ratings table.")
    my_ratings_df.to_sql('my_ratings', engine, if_exists='replace')


def update_seen_tv_episodes():
    # Read the source file for episodes seen from TvTime app.
    seen_episode_df = pd.read_csv("data/input/seen_episode.csv")

    # Create csv file containing episodes.
    try:
        tv_episodes_df = pd.read_csv("data/output/seen_tv_episodes.csv")
        # Collect info about new episodes.
        need_info = seen_episode_df["episode_id"].map(lambda x: x not in list(tv_episodes_df["tvdb_id"]))
        new_tv_episodes_df = get_episodes(seen_episode_df.loc[need_info])
        tv_episodes_df = tv_episodes_df.append(new_tv_episodes_df)
    except FileNotFoundError:
        # Collect info all episodes.
        tv_episodes_df = get_episodes(seen_episode_df)

    tv_episodes_df.to_csv("data/output/seen_tv_episodes.csv")
