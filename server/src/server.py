import os
from multiprocessing.dummy import Process

from flask import Flask, request

from helpers.helper import refine_db, show_predictions, update_my_ratings, update_seen_tv_episodes
from model import train_model
from run_crawler import run_imdb_crawler

app = Flask('server')


def update_db():
    run_imdb_crawler()
    refine_db()
    train_model()


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


# Updates the tv episodes, only locally.
@app.route('/update-episodes', methods=['GET', 'POST'])
def update_episodes():
    if LOCAL:
        process = Process(target=update_seen_tv_episodes, args=())
        process.start()
        return "Updating my episodes..."
    else:
        return 'Cannot perform this operation on the server!'


# run the app
if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')
