from io import StringIO
from time import time

import pandas as pd
import requests

from google.cloud import bigquery

from apis.tmdb_api import get_tv_id_by_tvdb, get_tv_show
from apis.tvtime_scraper import get_series_name_from_series_id
from crawler.models import db_connect
from helpers.printer import green, blue

import logging

# def get_episodes(seen_episodes_df):
#     episodes = []
#     l = len(seen_episodes_df)
#     i = 0
#     for _, row in seen_episodes_df.iterrows():
#         print(f"{i} / {l} -> {(i / l * 100):.1f} %")
#         # Get data from TVDB api.
#         episode_id = row["episode_id"]
#         try:
#             episode = tvdb_api.get_episode_by_id(episode_id)
#             episode["first_seen"] = row["created_at"]
#             episodes.append(episode)
#         except TypeError:
#             pass
#         i += 1
#     episodes_df = pd.DataFrame(episodes)
#     return episodes_df


def refine_db():
    # Get data from IMDb database.
    engine = db_connect()
    logging.info("Refining database...")
    imdb_series_df = pd.read_sql_query('SELECT * FROM imdb', con=engine, index_col="id")

    # Get a list of all the possible genres.
    genres = set("|".join(imdb_series_df["genres"].dropna().tolist()).split("|"))
    genres = list(filter(lambda x: len(x) > 0, genres))

    # Create and fill genre columns in the dataframe.
    for genre in genres:
        imdb_series_df[f"genre_{genre.lower()}"] = imdb_series_df['genres'].map(
            lambda x: int(genre in x), na_action='ignore')

    imdb_series_df = imdb_series_df.drop(columns=["genres"])

    logging.info("Handling of genres completed.")

    # Export the dataframe to the database.
    print("Saving database to imdb table.")
    imdb_series_df.to_sql('imdb', engine, if_exists='replace')


def update_tmdb_bq():
    # Get data from IMDb database.
    engine = db_connect()
    imdb_series_df = pd.read_sql_query('SELECT * FROM imdb', con=engine, index_col='id')

    # Get data from TMBd APIs.
    n = len(imdb_series_df)
    c = 0
    t = time()
    tmdb_dict = {}
    for i, row in imdb_series_df.iterrows():
        try:
            tmdb_id = get_tv_id_by_tvdb(i, 'imdb_id')
            tmdb_dict[i] = get_tv_show(tmdb_id)
        except IndexError:
            logging.warning(f"IMDb id {i} not found - {row['name']}")
        # Log progress.
        c += 1
        per = c / n * 100
        per_string = green(f"[{per:.1f}%]")
        logging.info(f"{per_string} {c} {row['name']}")
        # Print speed every 50 items.
        if c % 50 == 0:
            speed = 50 / (time() - t)
            logging.info(blue(f"[SPEED] {speed:.2f} e/s"))
            t = time()

    tmdb_df = pd.DataFrame.from_dict(tmdb_dict, orient='index')
    tmdb_df.reset_index(inplace=True)

    # Construct a BigQuery client object.
    client = bigquery.Client()

    # Set table_id to the ID of the table to create.
    table_id = "rosy-algebra-304808.tv_dataset.imdb_series_aug"

    job_config = bigquery.LoadJobConfig(
        schema=[
            bigquery.SchemaField("creators", bigquery.enums.SqlTypeNames.STRING),
            bigquery.SchemaField("networks", bigquery.enums.SqlTypeNames.STRING),
            bigquery.SchemaField("language", bigquery.enums.SqlTypeNames.STRING),
            bigquery.SchemaField("overview", bigquery.enums.SqlTypeNames.STRING),
            bigquery.SchemaField("production_companies", bigquery.enums.SqlTypeNames.STRING),
            # Indexes are written if included in the schema by name.
            bigquery.SchemaField("index", bigquery.enums.SqlTypeNames.STRING),
        ],
        # Optionally, set the write disposition. BigQuery appends loaded rows
        # to an existing table by default, but with WRITE_TRUNCATE write
        # disposition it replaces the table with the loaded data.
        write_disposition="WRITE_TRUNCATE",
    )

    job = client.load_table_from_dataframe(
        tmdb_df, table_id, job_config=job_config
    )  # Make an API request.
    job.result()  # Wait for the job to complete.

    table = client.get_table(table_id)  # Make an API request.
    print(
        "Loaded {} rows and {} columns to {}".format(
            table.num_rows, len(table.schema), table_id
        )
    )


def update_my_ratings():
    # Get data from tv_series database.
    engine = db_connect()
    my_ratings_df = pd.read_sql_query('SELECT * FROM my_ratings', con=engine, index_col="tvdb_id")

    # Read user_tv_show_data.csv from Google Drive.
    dwn_url = 'https://drive.google.com/uc?export=download&id='
    id_user_show = '1EfCJWOkRlAagAAkVLBucqeuXlohCQLt0'
    user_tv_show_data_df = pd.read_csv(StringIO(requests.get(dwn_url + id_user_show).text), index_col="tv_show_id")

    # Keep only followed shows.
    is_followed = user_tv_show_data_df["is_followed"] == 1
    followed_tv_shows_df = user_tv_show_data_df.loc[is_followed]

    # Add ratings for TV series not yet rated.
    new_indexes = [i for i in followed_tv_shows_df.index if i not in my_ratings_df.index]
    for index in new_indexes:
        rating = pd.DataFrame({
            'imdb_id': None,
            "series_name": get_series_name_from_series_id(series_id=index),
            "my_rating": None}, index=[index])
        print(f"Adding {rating['series_name']}")
        my_ratings_df = my_ratings_df.append(rating)

    # Export the dataframe to the database.
    engine = db_connect()
    print("Saving database to my_ratings table.")
    my_ratings_df.to_sql('my_ratings', engine, if_exists='replace')


#
# def update_seen_tv_episodes():
#     # Read seen_episode.csv from Google Drive.
#     dwn_url = 'https://drive.google.com/uc?export=download&id='
#     id_seen_episode = '14rdbDyQzawc_Xh49M5Nvgenm2njk8Rx4'
#     episodes_df = pd.read_csv(StringIO(requests.get(dwn_url + id_seen_episode).text))
#
#     # Create csv file containing episodes.
#     try:
#         # Get data from tv_series database.
#         engine = db_connect()
#         tv_episodes_df = pd.read_sql_query('SELECT * FROM tv_episodes', con=engine)
#
#         # Collect info about new episodes.
#         need_info = episodes_df["episode_id"].map(lambda x: x not in list(tv_episodes_df["tvdb_id"]))
#         new_tv_episodes_df = get_episodes(episodes_df.loc[need_info])
#
#         tv_episodes_df = tv_episodes_df.append(new_tv_episodes_df)
#     except Exception:
#         # Collect info all episodes.
#         tv_episodes_df = get_episodes(episodes_df)
#
#     # Export the dataframe to the database.
#     engine = db_connect()
#     print("Saving database to tv_episodes table.")
#     tv_episodes_df.to_sql('tv_episodes', engine, if_exists='replace')


def show_predictions():
    # Get data from imdb database.
    engine = db_connect()
    imdb_series_df = pd.read_sql_query('SELECT * FROM imdb', con=engine, index_col="id")

    # Sort predictions.
    imdb_series_df.sort_values(by='prediction', ascending=False, inplace=True)

    # Create table to display in the page.
    stringa = '<table>' \
              '<tr><th>prediction</th><th>title</th></tr>'
    for i, row in imdb_series_df.iloc[0:10, :].iterrows():
        link = f'https://www.imdb.com/title/{i}/'
        stringa += f'<tr>' \
                   f'<td width=5%><b>{row["prediction"]:.2f}</b></td>' \
                   f'<td width=20%><b><a href="{link}" target="_blank">{row["name"]}</a></b></td>' \
                   f'</tr>'
    stringa += '</table>'

    return stringa
