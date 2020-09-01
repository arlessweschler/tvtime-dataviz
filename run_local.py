import pandas as pd

from crawlers.run_crawler import run_crawler
from helpers.helper import get_tv_shows, get_episodes
from helpers.utility import transform_length


def update_imdb_tv_series():
    run_crawler()


def create_imdb_csv():
    # Get data from IMDb crawler database.
    imdb_series_df = pd.read_sql_table("tv_series", "sqlite:///data/input/imdb.db")

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

    imdb_series_df.to_csv("data/output/imdb_series.csv", index=False)


def update_tv_series():
    # Read the source file for TV series found in IMDb.
    imdb_series_df = pd.read_csv("data/output/imdb_series.csv", index_col="id")

    tv_series_df = get_tv_shows(imdb_series_df)

    # Encoding of genres.
    # Get a list of all the possible genres.
    genres = set(" ".join(tv_series_df["genres"].tolist()).split(" "))

    # Create and fill columns in the dataframe.
    for i, row in tv_series_df.iterrows():
        for genre in genres:
            tv_series_df.loc[i, f"genre_{genre.lower()}"] = int(genre in row["genres"])
    tv_series_df = tv_series_df.drop(columns=["genres"])

    tv_series_df.to_csv("data/output/tvdb_series.csv", index=False)


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
    # Read the source file for TV series found in TV Time.
    user_tv_show_data_df = pd.read_csv("data/input/user_tv_show_data.csv", index_col="tv_show_id")

    # Keep only followed shows.
    is_followed = user_tv_show_data_df["is_followed"] == 1
    followed_tv_shows_df = user_tv_show_data_df.loc[is_followed]

    tvdb_series_df = pd.read_csv("data/output/tvdb_series.csv", index_col="tvdb_id")

    # Create my_ratings csv file.
    try:
        my_ratings_df = pd.read_csv("data/input/my_ratings.csv", index_col="tvdb_id")
    except FileNotFoundError:
        my_ratings_df = pd.DataFrame(columns=["tvdb_id", "imdb_id", "series_name", "my_rating"])
        my_ratings_df.set_index("tvdb_id")

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
    my_ratings_df.to_csv("data/input/my_ratings.csv")


update_imdb_tv_series()
# create_imdb_csv()
# update_tv_series()
# update_seen_tv_episodes()
# update_my_ratings()
