import os
from multiprocessing.dummy import Process

from flask import Flask, request

from helpers.helper import refine_db, show_predictions, update_my_ratings, update_tmdb_bq  # update_seen_tv_episodes
from model import train_model
from run_crawler import run_imdb_crawler

import logging
logging.basicConfig(format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S', level=logging.INFO)

app = Flask('server')


def update_db():
    run_imdb_crawler()
    logging.info('Crawler stopped.')
    refine_db()
    logging.info('DB refined.')
    train_model()
    logging.info('Model trained.')


@app.route('/')
def index():
    return 'Ciaone'


@app.route('/show')
def show():
    return show_predictions()


# Updates the database and train model.
@app.route('/update', methods=['GET', 'POST'])
def update():
    if request.args.get('pwd') != os.environ['pwd']:
        return "Access denied."
    process = Process(target=update_db, args=())
    process.start()
    return "Updating database..."


# Updates the database and train model.
@app.route('/update-tmdb', methods=['GET', 'POST'])
def update_tmdb():
    if request.args.get('pwd') != os.environ['pwd']:
        return "Access denied."
    process = Process(target=update_tmdb_bq, args=())
    process.start()
    return "Updating database..."


# Train model.
@app.route('/train', methods=['GET', 'POST'])
def train():
    if request.args.get('pwd') != os.environ['pwd']:
        return "Access denied."
    process = Process(target=train_model, args=())
    process.start()
    return "Training model..."


# Updates my ratings.
@app.route('/update-ratings', methods=['GET', 'POST'])
def update_ratings():
    if request.args.get('pwd') != os.environ['pwd']:
        return "Access denied."
    process = Process(target=update_my_ratings, args=())
    process.start()
    return "Updating my ratings..."


# # Updates the tv episodes, only locally.
# @app.route('/update-episodes', methods=['GET', 'POST'])
# def update_episodes():
#     process = Process(target=update_seen_tv_episodes, args=())
#     process.start()
#     return "Updating my episodes..."


# run the app
if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=os.environ.get('PORT', '5000'))
