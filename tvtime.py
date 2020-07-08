import pandas as pd

from helper import get_tv_shows, get_episodes


# Create csv file containing tv shows.
try:
    tv_shows_df = pd.read_csv("data/tv_shows.csv")
except FileNotFoundError:
    # Read the source file for TV series seen from TvTime app.
    user_tv_show_data_df = pd.read_csv("data/user_tv_show_data.csv")

    # Keep only followed shows.
    is_followed = user_tv_show_data_df["is_followed"] == 1
    followed_tv_shows_df = user_tv_show_data_df.loc[is_followed]

    # Collect info about followed TV shows.
    tv_shows_df = get_tv_shows(followed_tv_shows_df)
    tv_shows_df.to_csv("data/tv_shows.csv")

# Create csv file containing episodes.
try:
    tv_episodes_df = pd.read_csv("data/tv_episodes.csv")
except FileNotFoundError:
    # Read the source file for episodes seen from TvTime app.
    seen_episode_df = pd.read_csv("data/seen_episode.csv")

    # Collect info about seen TV shows.
    tv_episodes_df = get_episodes(seen_episode_df)
    tv_episodes_df.to_csv("data/tv_episodes.csv")
