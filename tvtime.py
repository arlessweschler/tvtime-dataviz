import pandas as pd

from apis.tvdb_api import attach_show_name_to_episodes
from apis.tvtime_api import get_tv_shows, get_show_names_from_episode_id, assign_names_to_episodes

# Read the source files.
user_tv_show_data_df = pd.read_csv("data/user_tv_show_data.csv")
seen_episode_df = pd.read_csv("data/seen_episode.csv")

# Look up names of the shows on the tvtime.com website.
try:
    tv_shows_df = pd.read_csv("data/tv_shows.csv")
except FileNotFoundError:
    tv_shows_df = get_tv_shows(user_tv_show_data_df)
    tv_shows_df = tv_shows_df[["tv_show_id", "show_name"]]
    tv_shows_df.to_csv("data/tv_shows.csv")

# Link id_episode to id_tv_show.
try:
    tv_episodes_df = pd.read_csv("data/tv_episodes.csv")
except FileNotFoundError:
    tv_episodes_df = get_show_names_from_episode_id(seen_episode_df)
    tv_episodes_df = tv_episodes_df[["show_name", "episode_id", "created_at", "episode_name"]]
    tv_episodes_df.to_csv("data/tv_episodes.csv")
