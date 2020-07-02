import requests
from decouple import config

api_key = config('tvdb')

url = "https://api.thetvdb.com/login"
headers = {'Content-Type': 'application/json',
            'Accept': 'application/json'}
data = {
  "apikey": api_key
}
token = requests.post(url, headers=headers, data=data)


def get_show_name_from_episode_id(episode_id):
    headers = {"Authorization": f"Bearer {token}",
               'Content-Type': 'application/json'}
    endpoint = f"https://api.thetvdb.com/episodes/{episode_id}"
    json = requests.get(endpoint, headers=headers).json()
    series_id = json.get("data").get("series_id")

    endpoint = f"https://api.thetvdb.com/series/{series_id}"
    json = requests.get(endpoint, headers=headers).json()
    name = json.get("data").get("seriesName")
    return name


def attach_show_name_to_episodes(df):
    for index, row in df.iterrows():
        row["show_name"] = get_show_name_from_episode_id(row["episode_id"])
    return df
