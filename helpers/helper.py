import pandas as pd

from apis import tvdb_api
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
