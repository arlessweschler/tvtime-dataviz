import pandas as pd

from helper import get_tv_shows, get_episodes


# TVTIME TV SERIES WATCHED

# Read the source file for TV series seen from TvTime app.
user_tv_show_data_df = pd.read_csv("data/input/user_tv_show_data.csv")

# Keep only followed shows.
is_followed = user_tv_show_data_df["is_followed"] == 1
followed_tv_shows_df = user_tv_show_data_df.loc[is_followed]

# Avoid looking for info already present in tv_series.csv file.
try:
    tv_shows_df = pd.read_csv("data/output/tv_series.csv")
    # Collect only info about new shows.
    need_info = followed_tv_shows_df["tv_show_id"].map(lambda x: x not in list(tv_shows_df["tvdb_id"]))
    new_tv_shows_df = get_tv_shows(followed_tv_shows_df.loc[need_info])
    tv_shows_df = tv_shows_df.append(new_tv_shows_df)
except FileNotFoundError:
    # Collect all info.
    tv_shows_df = get_tv_shows(followed_tv_shows_df)

tv_shows_df.to_csv("data/output/tv_series.csv")


# TVTIME EPISODES WATCHED

# Create csv file containing episodes.
try:
    tv_episodes_df = pd.read_csv("data/output/tv_episodes.csv")
except FileNotFoundError:
    # Read the source file for episodes seen from TvTime app.
    seen_episode_df = pd.read_csv("data/input/seen_episode.csv")

    # Collect info about seen TV shows.
    tv_episodes_df = get_episodes(seen_episode_df)
    tv_episodes_df.to_csv("data/output/tv_episodes.csv")

# Create my_ratings csv file.
try:
    my_ratings_df = pd.read_csv("data/input/my_ratings.csv")
except FileNotFoundError:
    my_ratings_df = pd.DataFrame(columns=["tvdb_id", "imdb_id", "series_name", "my_rating"])
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
