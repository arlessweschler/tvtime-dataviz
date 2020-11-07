import requests
from bs4 import BeautifulSoup

headers = {
    "ACCEPT-ENCODING": "gzip, deflate, br",
    "ACCEPT-LANGUAGE": "en-US,en;q=0.9,it-IT;q=0.8,it;q=0.7,es;q=0.6,fr;q=0.5,nl;q=0.4,sv;q=0.3",
    "DNT": "1",
    "REFERER": "https://www.google.com/",
    "SEC-FETCH-DEST": "document",
    "SEC-FETCH-MODE": "navigate",
    "SEC-FETCH-SITE": "cross-site",
    "SEC-FETCH-USER": "?1",
    "UPGRADE-INSECURE-REQUESTS": "1",
    "USER-AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/83.0.4103.116 Safari/537.36"
}


# Given a TV show ID, it returns the name of the show.
def get_series_name_from_series_id(series_id):
    html = requests.get(f"https://www.tvtime.com/en/show/{series_id}", headers=headers).content
    soup = BeautifulSoup(html, "lxml")
    name = soup.find("div", {"class": "container-fluid"}).find("h1").text.strip()
    return name


# Given a episode ID, it returns names of the series and episode.
def get_series_name_from_episode_id(episode_id):
    url = f"http://thetvdb.com/?tab=episode&id={episode_id}"
    html = requests.get(url, headers=headers).content
    soup = BeautifulSoup(html, "lxml")
    series_name = soup.find("div", {"class": "page-toolbar"}).find_all('a')[2].text
    episode_name = soup.find("h1", {"class": "translated_title"}).text.strip()
    return series_name, episode_name


# Given a show and episode ID, it returns name and ref of the episode.
def get_episode_name_from_episode_id(series_id, episode_id):
    url = f"https://www.tvtime.com/en/show/{series_id}/episode/{episode_id}"
    html = requests.get(url, headers=headers).content
    soup = BeautifulSoup(html, "lxml")
    episode_ref = soup.find("div", {"class": "info-box"}).find("h2").text.strip()
    episode_name = soup.find("div", {"class": "basic-infos"}).find("span").text.strip()
    return episode_name, episode_ref
