import requests
from bs4 import BeautifulSoup

headers = {
    "ACCEPT": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "ACCEPT-ENCODING": "gzip, deflate, br",
    "ACCEPT-LANGUAGE": "en-US,en;q=0.9,it-IT;q=0.8,it;q=0.7,es;q=0.6,fr;q=0.5,nl;q=0.4,sv;q=0.3",
    "DNT": "1",
    "REFERER": "https://www.google.com/",
    "SEC-FETCH-DEST": "document",
    "SEC-FETCH-MODE": "navigate",
    "SEC-FETCH-SITE": "cross-site",
    "SEC-FETCH-USER": "?1",
    "UPGRADE-INSECURE-REQUESTS": "1",
    "USER-AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36"
}


# Given a TV show ID, it returns the name of the show.
def get_series_name_by_id(series_id):
    html = requests.get(f"https://www.tvtime.com/en/show/{series_id}", headers=headers).content
    soup = BeautifulSoup(html, "lxml")
    name = soup.find("div", {"class": "container-fluid"}).find("h1").text.strip()
    return name


# Given a episode ID, it returns names of the series and episode.
def get_show_name_from_episode_scrape(episode_id):
    url = f"http://thetvdb.com/?tab=episode&id={episode_id}"
    html = requests.get(url, headers=headers).content
    soup = BeautifulSoup(html, "lxml")
    series_name = soup.find("div", {"class": "page-toolbar"}).find_all('a')[2].text
    episode_name = soup.find("h1", {"class": "translated_title"}).text.strip()
    return series_name, episode_name


# Given a list of shows names and an episode ID, it returns ID and name of the show, name and ref of the episode.
def get_show_name_from_episode_id(shows_ids, episode_id):
    for show_id in shows_ids:
        try:
            url = f"https://www.tvtime.com/en/show/{show_id}/episode/{episode_id}"
            html = requests.get(url, headers=headers).content
            soup = BeautifulSoup(html, "lxml")
            show_name = soup.find("div", {"class": "info-box"}).find("h3").text.strip()
            episode_ref = soup.find("div", {"class": "info-box"}).find("h2").text.strip()
            episode_name = soup.find("div", {"class": "basic-infos"}).find("span").text.strip()
            return show_id, show_name, episode_name, episode_ref
        except Exception:
            pass


# Given a show and episode ID, it returns name and ref of the episode.
def get_episode_name_from_id(show_id, episode_id):
    url = f"https://www.tvtime.com/en/show/{show_id}/episode/{episode_id}"
    html = requests.get(url, headers=headers).content
    soup = BeautifulSoup(html, "lxml")
    episode_ref = soup.find("div", {"class": "info-box"}).find("h2").text.strip()
    episode_name = soup.find("div", {"class": "basic-infos"}).find("span").text.strip()
    return episode_name, episode_ref


def assign_names_to_episodes(episodes_df):
    episodes_df["episode_ref"] = ""
    episodes_df["episode_name"] = ""
    for index, row in episodes_df.iterrows():
        row["episode_name"], row["episode_ref"] = get_episode_name_from_id(row["show_id"], row["episode_id"])


def get_show_names_from_episode_id(episodes_df):
    # Get list of episodes ids.
    episodes_ids = episodes_df["episode_id"].tolist()

    episodes_df["show_name"] = "empty"
    episodes_df["episode_name"] = "empty"

    for i, episode_id in enumerate(episodes_ids):
        try:
            show_name, episode_name = get_show_name_from_episode_scrape(episode_id)
            episodes_df["show_name"][i] = show_name
            episodes_df["episode_name"][i] = episode_name
            print(f"{i} - Ep {episode_id} - {show_name}: {episode_name}")
        except Exception:
            pass

    return episodes_df



