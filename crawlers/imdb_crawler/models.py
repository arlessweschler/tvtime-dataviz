from sqlalchemy import Integer, String
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
    __tablename__ = "tv_series"

    id = Column(String, primary_key=True)
    name = Column('name', String)
    type = Column(String)
    genres = Column('genres', String)
    start_year = Column('start_year', String)
    end_year = Column('end_year', String)
    ep_length = Column("ep_length", String)
    n_seasons = Column('n_seasons', String)
    n_episodes = Column('n_episodes', Integer)
    popularity_rank = Column('popularity_rank', Integer)
    n_ratings = Column('n_ratings', Integer)
    rating_avg = Column('rating_avg', String)
    rating_top1000 = Column('rating_top1000', String)
    rating_us = Column('rating_us', String)
    rating_row = Column('rating_row', String)
    rating_M = Column('rating_M', String)
    rating_F = Column('rating_F', String)
    rating_0to18 = Column('rating_0to18', String)
    rating_M_0to18 = Column('rating_M_0to18', String)
    rating_F_0to18 = Column('rating_F_0to18', String)
    rating_18to29 = Column('rating_18to29', String)
    rating_M_18to29 = Column('rating_M_18to29', String)
    rating_F_18to29 = Column('rating_F_18to29', String)
    rating_29to45 = Column('rating_29to45', String)
    rating_M_29to45 = Column('rating_M_29to45', String)
    rating_F_29to45 = Column('rating_F_29to45', String)
    rating_45to100 = Column('rating_45to100', String)
    rating_M_45to100 = Column('rating_M_45to100', String)
    rating_F_45to100 = Column('rating_F_45to100', String)
