from multiprocessing.dummy import Process

from flask import Flask

from crawlers.run_crawler import create_imdb_db
from run_local import improve_db, update_my_ratings, \
    refine_db, update_seen_tv_episodes

app = Flask(__name__)

LOCAL = False


def update_i(local):
    create_imdb_db(local)
    refine_db(local)
    improve_db(local)


def update_r(local):
    update_my_ratings(local)


def update_e(local):
    update_seen_tv_episodes(local)


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
    process = Process(target=update_r, args=(LOCAL,))
    process.start()
    return "Updating my ratings..."


# Updates the IMDb database.
@app.route('/episodes', methods=['GET', 'POST'])
def update_episodes():
    print("Updating episodes.")
    process = Process(target=update_e, args=(LOCAL,))
    process.start()
    return "Updating my episodes..."


# run the app
if __name__ == '__main__':
    app.run()
