from multiprocessing.dummy import Process
from threading import Thread

from colorama import Fore, Style
from flask import Flask, request, make_response, jsonify

from crawlers.run_crawler import create_imdb_db
from helpers.utility import get_time
from run_local import improve_db, update_seen_tv_episodes, update_my_ratings, \
    refine_db

app = Flask(__name__)


def update_i(local):
    create_imdb_db(local)
    refine_db(local)
    improve_db(local)


def update_r(local):
    update_my_ratings(local)


# TODO: Display predictions.
@app.route('/')
def index():
    return 'Predictions.'


# Updates the IMDb database.
@app.route('/update-imdb', methods=['GET', 'POST'])
def update_imdb():
    print("Updating IMDb.")
    process = Process(target=update_i, args=(True,))
    process.start()
    return "Updating IMDb database..."


# Updates the IMDb database.
@app.route('/rate', methods=['GET', 'POST'])
def update_imdb():
    print("Updating ratings.")
    process = Process(target=update_r, args=(True,))
    process.start()
    return "Updating my ratings..."


# run the app
if __name__ == '__main__':
    app.run()
