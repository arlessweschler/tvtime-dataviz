# tvtime-dataviz

tvtime-dataviz is a personal project created to improve my skills as a Data Scientist and to help me automatize how to choose which tv series to watch.

## Dataset creation

I created the dataset by using:
- a spider that crawls imdb.com looking for tv series and mini-series made after 1989 with at least 2.5k ratings;
- APIs from thetvdb.com;
- a data dump obtained from tvtime.com, a website I use to track the tv series I watch. I analyzed and extracted data about all the tv series and episodes I have watched over the last 6 years of my life.

I assigned a rating (integers from 1 to 10) to every tv series I have watched.

## Jupyter Notebooks

This repo contains two notebooks:
- analysis.ipynb contains data visualization I made to explore the dataset;
- prediction.ipynb contains data cleaning and a xgboost model trained to recommend me the next tv series to watch.

## Automatization and deployment on Heroku

I deployed a server on Heroku, using their PostGreSQL database to store the dataset.

The database is updated every night.

The recommendations can be seen at https://tv-series-recommender.herokuapp.com/

## To do
- Improving how to display the recommendations.
- Creating a timeline containing all the episodes watched.
