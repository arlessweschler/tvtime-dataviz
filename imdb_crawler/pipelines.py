from sqlalchemy.orm import sessionmaker

from imdb_crawler.models import db_connect, create_table, TvSeries


class ImdbCrawlerPipeline:
    def __init__(self):
        """
        Initializes database connection and sessionmaker
        Creates tables
        """
        engine = db_connect()
        create_table(engine)
        self.Session = sessionmaker(bind=engine)

    def process_item(self, item, spider):
        """
        This method is called for every item pipeline component
        """
        session = self.Session()

        tv_series = TvSeries()
        tv_series.name = item["name"]
        tv_series.url = item["url"]
        tv_series.genres = item["genres"]
        tv_series.start_year = item["start_year"]
        tv_series.end_year = item["end_year"]
        tv_series.ep_length = item["ep_length"]
        tv_series.n_seasons = item["n_seasons"]
        tv_series.popularity_rank = item["popularity_rank"]
        tv_series.n_ratings = item["n_ratings"]
        tv_series.rating_avg = item["rating_avg"]
        tv_series.rating_top1000 = item["rating_top1000"]
        tv_series.rating_us = item["rating_us"]
        tv_series.rating_row = item["rating_row"]
        tv_series.rating_M = item["rating_M"]
        tv_series.rating_F = item["rating_F"]
        tv_series.rating_0to18 = item["rating_0to18"]
        tv_series.rating_M_0to18 = item["rating_M_0to18"]
        tv_series.rating_F_0to18 = item["rating_F_0to18"]
        tv_series.rating_18to29 = item["rating_18to29"]
        tv_series.rating_M_18to29 = item["rating_M_18to29"]
        tv_series.rating_F_18to29 = item["rating_F_18to29"]
        tv_series.rating_29to45 = item["rating_29to45"]
        tv_series.rating_M_29to45 = item["rating_M_29to45"]
        tv_series.rating_F_29to45 = item["rating_F_29to45"]
        tv_series.rating_45to100 = item["rating_45to100"]
        tv_series.rating_M_45to100 = item["rating_M_45to100"]
        tv_series.rating_F_45to100 = item["rating_F_45to100"]
        try:
            if 0 < int(tv_series.popularity_rank) < 1500:
                session.add(tv_series)
                session.commit()
                print(f"Inserted {tv_series.name}")
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

        return item
