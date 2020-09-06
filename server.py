import os
from multiprocessing.dummy import Process

from flask import Flask, request
from decouple import config

from crawlers.run_crawler import create_imdb_db
from helpers.helper import refine_db, show_predictions, improve_db, update_my_ratings, update_seen_tv_episodes
from model import train_model

app = Flask(__name__)

# Recognize if running in local on not.
try:
    db_password = config('db_password')
    LOCAL = True
except Exception:
    LOCAL = False


def update_i(local):
    create_imdb_db(local)
    refine_db(local)


def get_pwd(local):
    if local:
        pwd = config('pwd')
    else:
        pwd = os.environ['pwd']
    return pwd


@app.route('/')
def index():
    return show_predictions(LOCAL)


# Updates the IMDb database.
@app.route('/update-imdb', methods=['GET', 'POST'])
def update_imdb():
    if request.args.get('pwd') != get_pwd(LOCAL):
        return "Access denied."
    print("Updating IMDb.")
    process = Process(target=update_i, args=(LOCAL,))
    process.start()
    return "Updating IMDb database..."


# Updates the TVDb database.
@app.route('/update-tvdb', methods=['GET', 'POST'])
def update_tvdb():
    if request.args.get('pwd') != get_pwd(LOCAL):
        return "Access denied."
    print("Updating TVDb.")
    process = Process(target=improve_db, args=(LOCAL,))
    process.start()
    return "Updating TVDb database..."


# Updates my ratings.
@app.route('/update-ratings', methods=['GET', 'POST'])
def update_ratings():
    if request.args.get('pwd') != get_pwd(LOCAL):
        return "Access denied."
    print("Updating ratings.")
    process = Process(target=update_my_ratings, args=(LOCAL,))
    process.start()
    return "Updating my ratings..."


# Updates the tv episodes, only locally.
@app.route('/update-episodes', methods=['GET', 'POST'])
def update_episodes():
    if LOCAL:
        print("Updating episodes.")
        process = Process(target=update_seen_tv_episodes, args=(LOCAL,))
        process.start()
        return "Updating my episodes..."
    else:
        return 'Cannot perform this operation on the server!'


# Train model and update predictions.
@app.route('/train', methods=['GET', 'POST'])
def train():
    if request.args.get('pwd') != get_pwd(LOCAL):
        return "Access denied."
    print("Training model.")
    train_model(LOCAL)
    return "Model trained, predictions are available on <a href='/'>homepage</a>."


# run the app
if __name__ == '__main__':
    app.run()
