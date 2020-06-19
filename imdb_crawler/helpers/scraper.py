from bs4 import BeautifulSoup


class TvSeriesScraper:
    def __init__(self, body):
        self.html = BeautifulSoup(body, "lxml")

    def get_all_tv_series(self):
        divs = self.html.find_all("div", {"class": "lister-item-content"})
        infos = []
        for div in divs:
            name = div.find('a').text
            url = div.find('a')["href"]
            years = div.find_all("span")[1].text[1:-1].split('–')
            start_year = years[0]
            try:
                end_year = years[1]
            except IndexError:
                end_year = years[0]
            rating = div.find("strong").text
            infos.append([name, url, start_year, end_year, rating])
        return infos

    def get_next_page(self):
        try:
            url = self.html.find("a", {"class": "next-page"})["href"]
        except TypeError:
            url = None
        return url


class TvShowScraper:
    def __init__(self, body):
        self.html = BeautifulSoup(body, "lxml")

    def get_length(self):
        return self.html.find("div", {"class": "subtext"}).find("time").text
