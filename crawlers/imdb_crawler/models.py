from sqlalchemy import Integer, String
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
    return create_engine("sqlite:///../data/input/imdb.db", connect_args={'timeout': 15})


def create_table(engine):
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


class TvSeries(Base):
    __tablename__ = "tv_series"

    id = Column(String, primary_key=True)
    name = Column('name', String(200))
    type = Column(String(30))
    genres = Column('genres', String(200))
    start_year = Column('start_year', String(4))
    end_year = Column('end_year', String(4))
    ep_length = Column("ep_length", String(10))
    n_seasons = Column('n_seasons', Integer)
    n_episodes = Column('n_episodes', Integer)
    popularity_rank = Column('popularity_rank', Integer)
    n_ratings = Column('n_ratings', Integer)
    rating_avg = Column('rating_avg', String(3))
    rating_top1000 = Column('rating_top1000', String(3))
    rating_us = Column('rating_us', String(3))
    rating_row = Column('rating_row', String(3))
    rating_M = Column('rating_M', String(3))
    rating_F = Column('rating_F', String(3))
    rating_0to18 = Column('rating_0to18', String(3))
    rating_M_0to18 = Column('rating_M_0to18', String(3))
    rating_F_0to18 = Column('rating_F_0to18', String(3))
    rating_18to29 = Column('rating_18to29', String(3))
    rating_M_18to29 = Column('rating_M_18to29', String(3))
    rating_F_18to29 = Column('rating_F_18to29', String(3))
    rating_29to45 = Column('rating_29to45', String(3))
    rating_M_29to45 = Column('rating_M_29to45', String(3))
    rating_F_29to45 = Column('rating_F_29to45', String(3))
    rating_45to100 = Column('rating_45to100', String(3))
    rating_M_45to100 = Column('rating_M_45to100', String(3))
    rating_F_45to100 = Column('rating_F_45to100', String(3))
