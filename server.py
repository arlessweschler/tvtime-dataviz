from multiprocessing.dummy import Process

from flask import Flask
from decouple import config

from crawlers.run_crawler import create_imdb_db
from run_local import improve_db, update_my_ratings, \
    refine_db, update_seen_tv_episodes
from train_model import train_model

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
    improve_db(local)


# TODO: Display predictions.
@app.route('/')
def index():
    return 'Predictions.'


# Updates the IMDb database.
@app.route('/update-imdb', methods=['GET', 'POST'])
def update_imdb():
    print("Updating IMDb.")
    process = Process(target=update_i, args=(LOCAL,))
    process.start()
    return "Updating IMDb database..."


# Updates the IMDb database.
@app.route('/rate', methods=['GET', 'POST'])
def update_ratings():
    print("Updating ratings.")
    process = Process(target=update_my_ratings, args=(LOCAL,))
    process.start()
    return "Updating my ratings..."


# Updates the IMDb database.
@app.route('/episodes', methods=['GET', 'POST'])
def update_episodes():
    print("Updating episodes.")
    process = Process(target=update_seen_tv_episodes, args=(LOCAL,))
    process.start()
    return "Updating my episodes..."


# Updates the IMDb database.
@app.route('/train', methods=['GET', 'POST'])
def train():
    print("Training model.")
    return train_model(LOCAL)


# run the app
if __name__ == '__main__':
    app.run()
