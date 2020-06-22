from bs4 import BeautifulSoup

from imdb_crawler.items import TvSeriesItem


class TvSeriesScraper:
    def __init__(self, body):
        self.html = BeautifulSoup(body, "lxml")

    def get_all_tv_series_items(self):
        divs = self.html.find_all("div", {"class": "lister-item-content"})
        infos = []
        for div in divs:
            tv_series_item = TvSeriesItem()
            tv_series_item["name"] = div.find('a').text
            tv_series_item["url"] = div.find('a')["href"]

            years = div.find_all("span")[1].text[1:-1].split('–')
            tv_series_item["start_year"] = years[0]
            try:
                tv_series_item["end_year"] = years[1]
            except IndexError:
                tv_series_item["end_year"] = years[0]
            tv_series_item["rating_avg"] = div.find("strong").text
            infos.append(tv_series_item)
        return infos

    def get_next_page(self):
        try:
            url = self.html.find("a", {"class": "next-page"})["href"]
        except TypeError:
            url = None
        return url



