import pandas as pd
import requests
from bs4 import BeautifulSoup

from decouple import config

api_key = config('tvdb')

url = "https://api.thetvdb.com/login"
data = {"apikey": api_key, "username": "shakk17"}
token = requests.post(url, data=data)


def attach_names_to_tvshows(df):
    df["show_name"] = 0

    for i, show_id in enumerate(df["tv_show_id"]):
        name = get_tv_show_name(show_id)
        df["show_name"][i] = name
        print(f"Show {show_id}: {name} retrieved.")

    return df


def get_tv_show_name(tvtime_id):
    headers = {
        "ACCEPT": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "ACCEPT-ENCODING": "gzip, deflate, br",
        "ACCEPT-LANGUAGE": "en-US,en;q=0.9,it-IT;q=0.8,it;q=0.7,es;q=0.6,fr;q=0.5,nl;q=0.4,sv;q=0.3",
        "DNT": "1",
        "HOST": "www.tvtime.com",
        "REFERER": "https://www.google.com/",
        "SEC-FETCH-DEST": "document",
        "SEC-FETCH-MODE": "navigate",
        "SEC-FETCH-SITE": "cross-site",
        "SEC-FETCH-USER": "?1",
        "UPGRADE-INSECURE-REQUESTS": "1",
        "USER-AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36"
    }
    html = requests.get(f"https://www.tvtime.com/en/show/{tvtime_id}", headers=headers).content
    soup = BeautifulSoup(html, "lxml")
    name = soup.find("div", {"class": "container-fluid"}).find("h1").text.strip()
    return name


def get_tv_show_from_episode(episode_id):
    headers = {"Authorization": f"Bearer {token}"}
    endpoint = f"https://api.thetvdb.com/episodes/{episode_id}"
    json = requests.get(endpoint, headers=headers).json()
    series_id = json.get("data").get("series_id")

    endpoint = f"https://api.thetvdb.com/series/{series_id}"
    json = requests.get(endpoint, headers=headers).json()
    series_name = json.get("data").get("seriesName")
    return series_name


def attach_shows_to_episodes(df):
    for index, row in df.iterrows():
        row["show_name"] = get_tv_show_from_episode(row["episode_id"])

    return df


# Read the source files.
user_tv_show_data_df = pd.read_csv("data/user_tv_show_data.csv")
seen_episode_df = pd.read_csv("data/seen_episode.csv")

# Look up names of the shows on the tvtime.com website.
try:
    tv_shows_df = pd.read_csv("data/tv_shows.csv")
except FileNotFoundError:
    tv_shows_df = attach_names_to_tvshows(user_tv_show_data_df)
    tv_shows_df = tv_shows_df[["tv_show_id", "show_name"]]
    tv_shows_df.to_csv("data/tv_shows.csv")

# Link id_episode to id_tv_show.
try:
    tv_episodes_df = pd.read_csv("data/tv_episodes.csv")
except FileNotFoundError:
    tv_episodes_df = attach_shows_to_episodes(seen_episode_df)
