import json

import requests
from decouple import config

# Get data from .env file.
tvdb_apikey = config('tvdb_apikey')
tvdb_userkey = config('tvdb_userkey')
tvdb_name = config('tvdb_name')

# Retrieve token from API.
login_endpoint = "https://api.thetvdb.com/login"
headers = {
    "Content-Type": 'application/json',
    "Accept": 'application/json',
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US, en;q =0.9,it-IT;q=0.8,it;q=0.7,es;q=0.6,fr;q=0.5,nl;q=0.4,sv;q=0.3",
    "dnt": "1",
    "origin": "https://api.thetvdb.com",
    "referer": "https://api.thetvdb.com/swagger",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0(Windows NT 10.0; Win64; x64) AppleWebKit/537.36(KHTML, like Gecko) "
                  "Chrome/83.0.4103.116 Safari/537.36"
}
data = {
    "apikey": tvdb_apikey,
    "userkey": tvdb_userkey,
    "username": tvdb_name
}
response = requests.post(login_endpoint, headers=headers, data=json.dumps(data)).content
token = json.loads(response).get("token")

headers["Authorization"] = f"Bearer {token}"


def get_show_name_from_episode_id(episode_id):
    endpoint = f"https://api.thetvdb.com/episodes/{episode_id}"
    response1 = requests.get(endpoint, headers=headers).content
    series_id = json.loads(response1).get("data").get("seriesId")

    endpoint = f"https://api.thetvdb.com/series/{series_id}"
    response2 = requests.get(endpoint, headers=headers).content
    name = json.loads(response2).get("data").get("seriesName")
    return name


def attach_show_name_to_episodes(df):
    for index, row in df.iterrows():
        row["show_name"] = get_show_name_from_episode_id(row["episode_id"])
    return df


def get_series_by_id(series_id):
    endpoint = f"https://api.thetvdb.com/series/{series_id}"
    response = requests.get(endpoint, headers=headers).content
    data = json.loads(response).get("data")
    tv_show = {
        "tvdb_id": series_id,
        "series_name": data["seriesName"],
        "num_seasons": data["season"],
        "poster": f"https://artworks.thetvdb.com/banners/{data['poster']}",
        "banner": f"https://artworks.thetvdb.com/banners/{data['banner']}",
        "fanart": f"https://artworks.thetvdb.com/banners/{data['fanart']}",
        "status": data["status"],
        "first_aired": data["firstAired"],
        "network": data["network"],
        "runtime": data["runtime"],
        "genre": ", ".join(data["genre"]),
        "overview": data["overview"],
        "rating": data["rating"],
        "imdb_id": data["imdbId"],
        "tvdb_avg_rating": data["siteRating"],
        "tvdb_ratings": data["siteRatingCount"]
    }

    print(f"Show {series_id}: {data['seriesName']} retrieved.")
    return tv_show


def get_series_by_name(series_name):
    endpoint = f"https://api.thetvdb.com/search/series?name={series_name}"
    response = requests.get(endpoint, headers=headers).content
    data = json.loads(response).get("data")
    tv_show = None
    for el in data:
        if el.get("seriesName") == series_name:
            series_id = el.get("id")
            tv_show = get_series_by_id(series_id)
            break
    return tv_show
