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


def update_db(local):
    create_imdb_db(local)
    refine_db(local)
    improve_db(local)
    train_model(local)


def get_pwd(local):
    if local:
        pwd = config('pwd')
    else:
        pwd = os.environ['pwd']
    return pwd


@app.route('/')
def index():
    return show_predictions(LOCAL)


# Updates the database and train model.
@app.route('/update', methods=['GET', 'POST'])
def update():
    if request.args.get('pwd') != get_pwd(LOCAL):
        return "Access denied."
    print("Updating database.")
    process = Process(target=update_db, args=(LOCAL,))
    process.start()
    return "Updating database..."


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


# run the app
if __name__ == '__main__':
    app.run()
