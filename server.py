import logging

from colorama import Fore, Style
from flask import Flask, request, make_response, jsonify

from helpers.utility import get_time
from run_local import update_imdb_tv_series, update_tv_series, update_seen_tv_episodes, update_my_ratings, \
    create_imdb_csv

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask(__name__)


# default route
@app.route('/')
def index():
    return 'Hello World!'


# function for responses
def results():
    print("-" * 20)
    print(f"{Fore.CYAN}{get_time()} [SERVER] New request received.{Style.RESET_ALL}")


# create a route for webhook
@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    update_imdb_tv_series()
    create_imdb_csv()
    update_tv_series()
    update_seen_tv_episodes()
    update_my_ratings()
    return make_response(results())


# run the app
if __name__ == '__main__':
    app.run()
