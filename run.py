import pandas as pd

from crawlers.run_crawler import run_crawler
from helpers.helper import get_tv_shows, get_episodes
from helpers.utility import transform_length


def update_seen_tv_series():
    # Read the source file for TV series seen from TvTime app.
    user_tv_show_data_df = pd.read_csv("data/input/user_tv_show_data.csv")

    # Keep only followed shows.
    is_followed = user_tv_show_data_df["is_followed"] == 1
    followed_tv_shows_df = user_tv_show_data_df.loc[is_followed]

    # Avoid looking for info already present in tv_series.csv file.
    try:
        tv_shows_df = pd.read_csv("data/output/seen_tv_series.csv")
        # Collect only info about new shows.
        need_info = followed_tv_shows_df["tv_show_id"].map(lambda x: x not in list(tv_shows_df["tvdb_id"]))
        new_tv_shows_df = get_tv_shows(followed_tv_shows_df.loc[need_info])
        tv_shows_df = tv_shows_df.append(new_tv_shows_df)
    except FileNotFoundError:
        # Collect all info.
        tv_shows_df = get_tv_shows(followed_tv_shows_df)

    tv_shows_df.to_csv("data/output/seen_tv_series.csv")


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


def update_my_ratings():
    tv_shows_df = pd.read_csv("data/output/seen_tv_series.csv")
    # Create my_ratings csv file.
    try:
        my_ratings_df = pd.read_csv("data/input/my_ratings.csv")
    except FileNotFoundError:
        my_ratings_df = pd.DataFrame(columns=["tvdb_id", "imdb_id", "series_name", "my_rating"])
    # Add ratings for TV series not yet rated.
    new_series = []
    for i, tv_show in tv_shows_df.iterrows():
        if tv_show["tvdb_id"] not in list(my_ratings_df["tvdb_id"]):
            new_series.append({"tvdb_id": tv_show["tvdb_id"],
                               "imdb_id": tv_show["imdb_id"],
                               "series_name": tv_show["series_name"],
                               "my_rating": ""})
    new_series_df = pd.DataFrame(new_series)
    my_ratings_df = my_ratings_df.append(new_series_df, ignore_index=True)
    my_ratings_df.to_csv("data/input/my_ratings.csv")


def update_popular_tv_series():
    run_crawler()


def create_imdb_csv():
    # Get data from IMDb crawler database.
    imdb_series_df = pd.read_sql_table("tv_series", "sqlite:///data/input/imdb.db")

    # Get a list of all the possible genres.
    genres = set(" ".join(imdb_series_df["genres"].tolist()).split(" "))
    genres = list(filter(lambda x: len(x) > 0, genres))

    # Create and fill columns in the dataframe.
    for i, row in imdb_series_df.iterrows():
        for genre in genres:
            imdb_series_df.loc[i, f"genre_{genre.lower()}"] = int(genre in row["genres"])

        # Change ep_length format.
        imdb_series_df.loc[i, "ep_length"] = transform_length(row["ep_length"])
    imdb_series_df = imdb_series_df.drop(columns=["genres"])

    imdb_series_df.to_csv("data/output/imdb_series.csv")


"""update_seen_tv_series()
update_seen_tv_episodes()
update_my_ratings()
update_popular_tv_series()"""
create_imdb_csv()
