# tvtime-dataviz

tvtime-dataviz is a personal project created to improve my skills as a Data Scientist and to help me automatize how to choose which tv series to watch.

## Dataset creation

I created the dataset by using:
- a **spider** that crawls *imdb.com* looking for tv series and mini-series made after 1989 with at least 2.5k ratings;
- **external APIs** from *thetvdb.com*;
- a **data dump** obtained from *tvtime.com*, a website I use to track the TV series I watch. I analyzed and extracted data about all the TV series and episodes I have watched over the last 6 years of my life.
- **personal ratings** (integers from 1 to 10) assigned to every TV series I have watched.

## Jupyter Notebooks

This repo contains two notebooks:
- *analysis.ipynb* contains data visualization I made to explore the dataset;
- *prediction.ipynb* contains data cleaning and a xgboost model trained to recommend me the next TV series to watch.

## Automatization and deployment on Heroku

A server deployed on Heroku updates every day a PostGreSQL database containing the dataset to be used by the model.

The TV series recommended by the model can be seen at https://tv-series-recommender.herokuapp.com/

## To do
- Improving how to display the recommendations.
- Creating a timeline containing all the episodes watched.
