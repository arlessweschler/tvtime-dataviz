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
            series_name = tvtime_scraper.get_series_name_by_id(series_id=series_id)
            tv_shows.append(tvdb_api.get_series_by_name(series_name=series_name))

    tv_shows_df = pd.DataFrame(tv_shows)
    return tv_shows_df
