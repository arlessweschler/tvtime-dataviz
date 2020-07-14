import pandas as pd

from apis import tvtime_scraper, tvdb_api


def get_tv_shows(followed_tv_shows_df):
    tv_shows = []
    for i, row in followed_tv_shows_df.iterrows():
        # Get data from TVDB api.
        series_id = row["tv_show_id"]
        try:
            tv_shows.append(tvdb_api.get_series_by_id(series_id))
        except TypeError:
            series_name = tvtime_scraper.get_series_name_from_series_id(series_id=series_id)
            tv_shows.append(tvdb_api.get_series_by_name(series_name=series_name))

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
