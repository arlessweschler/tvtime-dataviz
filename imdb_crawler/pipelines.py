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
        tv_series.start_year = item["start_year"]
        tv_series.rating = item["rating"]
        tv_series.length = item["length"]
        try:
            session.add(tv_series)
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

        return item
