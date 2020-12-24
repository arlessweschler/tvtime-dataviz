from io import StringIO

import pandas as pd
import requests

from apis import tvdb_api
from apis.tvdb_api import get_series_by_tvdb_id
from crawler.models import db_connect
from helpers.printer import green


def get_tv_shows(imdb_series_df):
    tv_shows = []
    tot = len(imdb_series_df)
    con = 0
    for i, row in imdb_series_df.iterrows():
        # Get data from TVDB api.
        try:
            tvdb_id = tvdb_api.get_series_by_imdb_id(imdb_id=i)["tvdb_id"]
        except TypeError:
            continue
        tv_show = tvdb_api.get_series_by_tvdb_id(tvdb_id=tvdb_id)
        tv_shows.append(tv_show)
        # Display info about progress.
        perc = green(f"[{(con / tot * 100):.1f} %]")
        print(f"{perc} Show {i}: {tv_show['series_name']} retrieved.")
        con += 1
    tv_shows_df = pd.DataFrame(tv_shows)
    return tv_shows_df


def get_episodes(seen_episodes_df):
    episodes = []
    l = len(seen_episodes_df)
    i = 0
    for _, row in seen_episodes_df.iterrows():
        print(f"{i} / {l} -> {(i/l*100):.1f} %")
        # Get data from TVDB api.
        episode_id = row["episode_id"]
        try:
            episode = tvdb_api.get_episode_by_id(episode_id)
            episode["first_seen"] = row["created_at"]
            episodes.append(episode)
        except TypeError:
            pass
        i += 1
    episodes_df = pd.DataFrame(episodes)
    return episodes_df


def refine_db():
    # Get data from IMDb database.
    engine = db_connect()
    print("Refining database...")
    imdb_series_df = pd.read_sql_query('SELECT * FROM imdb', con=engine, index_col="id")

    # Get a list of all the possible genres.
    genres = set("|".join(imdb_series_df["genres"].dropna().tolist()).split("|"))
    genres = list(filter(lambda x: len(x) > 0, genres))

    # Create and fill genre columns in the dataframe.
    for genre in genres:
        imdb_series_df[f"genre_{genre.lower()}"] = imdb_series_df['genres'].map(
            lambda x: int(genre in x), na_action='ignore')

    imdb_series_df = imdb_series_df.drop(columns=["genres"])

    # Export the dataframe to the database.
    print("Saving database to imdb table.")
    imdb_series_df.to_sql('imdb', engine, if_exists='replace')


def update_my_ratings():
    # Get data from tv_series database.
    engine = db_connect()
    my_ratings_df = pd.read_sql_query('SELECT * FROM my_ratings', con=engine, index_col="tvdb_id")
    my_ratings_df = pd.DataFrame()
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
        series = get_series_by_tvdb_id(tvdb_id=index)
        if series is not None:
            rating = pd.DataFrame({
                    "imdb_id": series['imdb_id'],
                    "series_name": series['series_name'],
                    "my_rating": None}, index=[index])
            print(f"Adding {series['series_name']}")
        else:
            rating = pd.DataFrame({
                "imdb_id": None,
                "series_name": None,
                "my_rating": None}, index=[index])
            print(f'Adding {index}')
        my_ratings_df = my_ratings_df.append(rating)

    # Export the dataframe to the database.
    engine = db_connect()
    print("Saving database to my_ratings table.")
    my_ratings_df.to_sql('my_ratings', engine, if_exists='replace')


def update_seen_tv_episodes():
    # Read seen_episode.csv from Google Drive.
    dwn_url = 'https://drive.google.com/uc?export=download&id='
    id_seen_episode = '14rdbDyQzawc_Xh49M5Nvgenm2njk8Rx4'
    seen_episode_df = pd.read_csv(StringIO(requests.get(dwn_url + id_seen_episode).text))

    # Create csv file containing episodes.
    try:
        # Get data from tv_series database.
        engine = db_connect()
        tv_episodes_df = pd.read_sql_query('SELECT * FROM tv_episodes', con=engine)

        # Collect info about new episodes.
        need_info = seen_episode_df["episode_id"].map(lambda x: x not in list(tv_episodes_df["tvdb_id"]))
        new_tv_episodes_df = get_episodes(seen_episode_df.loc[need_info])
        tv_episodes_df = tv_episodes_df.append(new_tv_episodes_df)
    except Exception:
        # Collect info all episodes.
        tv_episodes_df = get_episodes(seen_episode_df)

    # Export the dataframe to the database.
    engine = db_connect()
    print("Saving database to tv_episodes table.")
    tv_episodes_df.to_sql('tv_episodes', engine, if_exists='replace')


def show_predictions(local):
    # Get data from imdb database.
    engine = db_connect(local)
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
