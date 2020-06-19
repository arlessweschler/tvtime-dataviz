from sqlalchemy import Integer, String, Float
from sqlalchemy import create_engine, Column
from sqlalchemy.ext.declarative import declarative_base

import os
from pathlib import Path

Base = declarative_base()


def db_connect():
    """
    Performs database connection using database settings from settings.py.
    Returns sqlalchemy engine instance
    """
    path = Path(os.getcwd())
    return create_engine(f"sqlite:///{path.parent}/imdb.db", connect_args={'timeout': 15})


def create_table(engine):
    Base.metadata.create_all(engine)


class TvSeries(Base):
    __tablename__ = "page_links"

    id = Column(Integer, primary_key=True)
    name = Column('name', String(200))
    start_year = Column('start_year', Integer)
    rating = Column('rating', Float)

