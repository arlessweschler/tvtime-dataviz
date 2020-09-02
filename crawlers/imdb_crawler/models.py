from sqlalchemy import Integer, String, Float
from sqlalchemy import create_engine, Column
from sqlalchemy.ext.declarative import declarative_base

import os
from pathlib import Path

Base = declarative_base()

from decouple import config


def db_connect(local):
    """
    Performs database connection using database settings from settings.py.
    Returns sqlalchemy engine instance
    """
    path = Path(os.getcwd())
    if int(local) == 1:
        # Get data from .env file.
        db_password = config('db_password')
        engine = create_engine(f"postgres+psycopg2://postgres:{db_password}@localhost:5432/tv_series")
    else:
        database_url = os.environ['DATABASE_URL']
        engine = create_engine(database_url)
    return engine


def create_table(engine):
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


class TvSeries(Base):
    __tablename__ = "imdb"

    id = Column(String, primary_key=True)
    name = Column('name', String)
    type = Column(String)
    genres = Column('genres', String)
    start_year = Column('start_year', Integer)
    end_year = Column('end_year', Integer)
    ep_length = Column("ep_length", Integer)
    n_seasons = Column('n_seasons', Integer)
    n_episodes = Column('n_episodes', Integer)
    popularity_rank = Column('popularity_rank', Integer)
    n_ratings = Column('n_ratings', Integer)
    rating_avg = Column('rating_avg', Float)
    rating_top1000 = Column('rating_top1000', Float)
    rating_us = Column('rating_us', Float)
    rating_row = Column('rating_row', Float)
    rating_M = Column('rating_M', Float)
    rating_F = Column('rating_F', Float)
    rating_0to18 = Column('rating_0to18', Float)
    rating_M_0to18 = Column('rating_M_0to18', Float)
    rating_F_0to18 = Column('rating_F_0to18', Float)
    rating_18to29 = Column('rating_18to29', Float)
    rating_M_18to29 = Column('rating_M_18to29', Float)
    rating_F_18to29 = Column('rating_F_18to29', Float)
    rating_29to45 = Column('rating_29to45', Float)
    rating_M_29to45 = Column('rating_M_29to45', Float)
    rating_F_29to45 = Column('rating_F_29to45', Float)
    rating_45to100 = Column('rating_45to100', Float)
    rating_M_45to100 = Column('rating_M_45to100', Float)
    rating_F_45to100 = Column('rating_F_45to100', Float)
