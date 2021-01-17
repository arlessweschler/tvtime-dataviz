import logging

from bs4 import BeautifulSoup

from helpers.utility import strip_html_tags, transform_length


class TvShowScraper:
    def __init__(self, body):
        self.html = BeautifulSoup(body, "lxml")

    def get_details(self, item):
        # OVERVIEW
        item['overview'] = self.html.find("div", {"class": 'inline canwrap'}).find('span').text
        # TYPE
        item["type"] = self.html.find("div", {"class": "subtext"}).find_all('a')[-1].text.split("(")[0].strip()
        # GENRES
        try:
            div = self.html.find_all("div", {"class": "see-more inline canwrap"})[1]
            genres = [a.text.strip() for a in div.find_all('a')]
            item["genres"] = "|".join(genres)
        except Exception:
            item["genres"] = None

        # YEARS
        years = self.html.find("a", {"title": "See more release dates"}).text[:-2].split("(")[1].split('–')
        item["start_year"] = years[0]
        try:
            if len(years[1]) < 4:
                item["end_year"] = None
            else:
                item["end_year"] = years[1]
        except Exception:
            item["end_year"] = None

        # N_EPISODES
        item["n_episodes"] = int(self.html.find_all("span", {"class": "bp_sub_heading"})[-1].text.split(" ")[0])

        # LENGTH
        try:
            item["ep_length"] = strip_html_tags(self.html.find("div", {"class": "subtext"}).find("time").text)
            item['ep_length'] = transform_length(item["ep_length"])
            if item['type'] == 'TV Mini-Series' and item['ep_length'] > 150:
                item['ep_length'] = int(item['ep_length'] / item['n_episodes'])
        except Exception:
            item['ep_length'] = None

        # N_SEASONS
        try:
            item["n_seasons"] = self.html.find("div", {"class": "seasons-and-year-nav"}).find('a').text
            if item["n_seasons"] == "Unknown":
                item["n_seasons"] = None
        except Exception:
            item["n_seasons"] = None

        # POPULARITY
        try:
            pop = self.html.find("div", {"class": "titleReviewBarSubItem"}).find("span").text
            pop = strip_html_tags(pop)
            item["popularity_rank"] = pop.split(" ")[0].replace(',', '')
        except Exception:
            item["popularity_rank"] = None

        # N_RATINGS
        item["n_ratings"] = self.html.find("div", {"class": "imdbRating"}).find('a').text.replace(',', '')

        # POSTER
        poster_url = self.html.find('div', {'class': 'poster'}).find('img')['src'].split('@._V1_')[0]
        item['poster'] = poster_url + '@._V1_'

        return item

    def get_ratings_page(self):
        return self.html.find("div", {"class": "imdbRating"}).find('a')["href"]
