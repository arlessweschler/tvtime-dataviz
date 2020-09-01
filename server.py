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
    # update_tv_series()
    # update_seen_tv_episodes()
    # update_my_ratings()


def update_t(local):
    improve_db(local)


# TODO: Display predictions.
@app.route('/')
def index():
    return 'Predictions.'


# Updates the IMDb database.
@app.route('/update-imdb', methods=['GET', 'POST'])
def update_imdb():
    print("Updating IMDb.")
    process = Process(target=update_i, args=(False,))
    process.start()
    return "Updating IMDb database..."


# Updates the TVDb csv file.
@app.route('/update-tvdb', methods=['GET', 'POST'])
def update_tvdb():
    print("Updating TVDb.")
    process = Process(target=update_t, args=(False,))
    process.start()
    return "Updating TVDb database..."


# run the app
if __name__ == '__main__':
    app.run()
