from multiprocessing.dummy import Process

from flask import Flask
from decouple import config

from crawlers.run_crawler import create_imdb_db
from run_local import improve_db, update_my_ratings, refine_db, update_seen_tv_episodes, show_predictions

from train_model import Model

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


# TODO: Display predictions.
@app.route('/')
def index():
    return show_predictions(LOCAL)


# Updates the IMDb database.
@app.route('/update-imdb', methods=['GET', 'POST'])
def update_imdb():
    print("Updating IMDb.")
    process = Process(target=update_i, args=(LOCAL,))
    process.start()
    return "Updating IMDb database..."


# Updates the TVDb database.
@app.route('/update-tvdb', methods=['GET', 'POST'])
def update_tvdb():
    print("Updating TVDb.")
    process = Process(target=improve_db, args=(LOCAL,))
    process.start()
    return "Updating TVDb database..."


# Updates my ratings.
@app.route('/update-ratings', methods=['GET', 'POST'])
def update_ratings():
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
    print("Training model.")
    Model().train_model(LOCAL)
    return "Model trained, predictions are available on <a href='/'>homepage</a>."


# run the app
if __name__ == '__main__':
    app.run()
