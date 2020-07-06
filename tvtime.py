import pandas as pd

from apis.tvtime_scraper import get_show_names_from_episode_id
from helper import get_tv_shows

seen_episode_df = pd.read_csv("data/seen_episode.csv")

# Look up names of the shows on the tvtime.com website.
try:
    tv_shows_df = pd.read_csv("data/tv_shows.csv")
except FileNotFoundError:
    # Read the source file for TV shows seen from TvTime app.
    user_tv_show_data_df = pd.read_csv("data/user_tv_show_data.csv")

    # Keep only followed shows.
    is_followed = user_tv_show_data_df["is_followed"] == 1
    followed_tv_shows_df = user_tv_show_data_df.loc[is_followed]

    # Collect info about followed TV shows.
    tv_shows_df = get_tv_shows(followed_tv_shows_df)
    tv_shows_df.to_csv("data/tv_shows.csv")

# Link id_episode to id_tv_show.
try:
    tv_episodes_df = pd.read_csv("data/tv_episodes.csv")
except FileNotFoundError:
    tv_episodes_df = get_show_names_from_episode_id(seen_episode_df)
    tv_episodes_df = tv_episodes_df[["show_name", "episode_id", "created_at", "episode_name"]]
    tv_episodes_df.to_csv("data/tv_episodes.csv")
