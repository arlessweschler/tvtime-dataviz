import os
from multiprocessing.dummy import Process

from flask import Flask, request

from helpers.helper import refine_db, show_predictions, update_my_ratings, update_seen_tv_episodes
from model import train_model
from run_crawler import run_imdb_crawler

app = Flask('server')


# Recognize if running in local on not.
LOCAL = os.environ['DEBUG']


def update_db(local):
    run_imdb_crawler(local)
    refine_db(local)
    train_model(local)


@app.route('/')
def index():
    return 'Ciaone'


@app.route('/show')
def show():
    return show_predictions(LOCAL)


# Updates the database and train model.
@app.route('/update', methods=['GET', 'POST'])
def update():
    if request.args.get('pwd') != os.environ['pwd']:
        return "Access denied."
    process = Process(target=update_db, args=(LOCAL,))
    process.start()
    return "Updating database..."


# Train model.
@app.route('/train', methods=['GET', 'POST'])
def train():
    if request.args.get('pwd') != os.environ['pwd']:
        return "Access denied."
    process = Process(target=train_model, args=(LOCAL,))
    process.start()
    return "Training model..."


# Updates my ratings.
@app.route('/update-ratings', methods=['GET', 'POST'])
def update_ratings():
    if request.args.get('pwd') != os.environ['pwd']:
        return "Access denied."
    process = Process(target=update_my_ratings, args=(LOCAL,))
    process.start()
    return "Updating my ratings..."


# Updates the tv episodes, only locally.
@app.route('/update-episodes', methods=['GET', 'POST'])
def update_episodes():
    if LOCAL:
        process = Process(target=update_seen_tv_episodes, args=(LOCAL,))
        process.start()
        return "Updating my episodes..."
    else:
        return 'Cannot perform this operation on the server!'


# run the app
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
