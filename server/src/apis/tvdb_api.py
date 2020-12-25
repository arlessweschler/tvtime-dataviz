import json
import os
import requests


# Get data from .env file or from environment vars.
tvdb_apikey = os.environ.get('tvdb_apikey')
tvdb_userkey = os.environ.get('tvdb_userkey')
tvdb_name = os.environ.get('tvdb_name')

# Headers for API requests.
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

# Retrieve token from API.
login_endpoint = "https://api.thetvdb.com/login"

data = {
    "apikey": tvdb_apikey,
    "userkey": tvdb_userkey,
    "username": tvdb_name
}
response = requests.post(login_endpoint, headers=headers, data=json.dumps(data)).content
token = json.loads(response).get("token")

headers["Authorization"] = f"Bearer {token}"


def get_episode_by_id(episode_id):
    endpoint = f"https://api.thetvdb.com/episodes/{episode_id}"
    response = requests.get(endpoint, headers=headers).content
    data = json.loads(response).get("data")
    tv_show = {
        "tvdb_id": episode_id,
        "aired_season": data["airedSeason"],
        "aired_episode": data["airedEpisodeNumber"],
        "name": data["episodeName"],
        "first_aired": data["firstAired"],
        "overview": data["overview"],
        "series_tvdb_id": data["seriesId"],
        "rating": data["contentRating"],
        "imdb_id": data["imdbId"],
        "tvdb_avg_rating": data["siteRating"],
        "tvdb_ratings": data["siteRatingCount"]
    }

    print(f"Episode {episode_id}: {data['episodeName']} retrieved.")
    return tv_show
