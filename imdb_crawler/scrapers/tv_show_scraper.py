from bs4 import BeautifulSoup

from imdb_crawler.helpers.utility import strip_html_tags


class TvShowScraper:
    def __init__(self, body):
        self.html = BeautifulSoup(body, "lxml")

    def get_details(self, item):
        # GENRES
        try:
            div = self.html.find_all("div", {"class": "see-more inline canwrap"})[1]
            genres = [a.text for a in div.find_all('a')]
            item["genres"] = "".join(genres).strip()
        except IndexError:
            item["genres"] = ""

        # LENGTH
        try:
            item["ep_length"] = strip_html_tags(self.html.find("div", {"class": "subtext"}).find("time").text)
        except AttributeError:
            item["ep_length"] = "None"

        # N_SEASONS
        item["n_seasons"] = self.html.find("div", {"class": "seasons-and-year-nav"}).find('a').text

        # POPULARITY
        try:
            pop = self.html.find("div", {"class": "titleReviewBarSubItem"}).find("span").text
            pop = strip_html_tags(pop)
            item["popularity_rank"] = pop.split(" ")[0].replace(',', '')
        except AttributeError:
            item["popularity_rank"] = 0

        # N_RATINGS
        item["n_ratings"] = self.html.find("div", {"class": "imdbRating"}).find('a').text.replace(',', '')

        return item

    def get_ratings_page(self):
        return self.html.find("div", {"class": "imdbRating"}).find('a')["href"]