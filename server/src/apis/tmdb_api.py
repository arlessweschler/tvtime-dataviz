import json
import logging
import os

import requests

API_KEY = os.environ.get('TMDB_API_KEY')


def get_tv_id_by_tvdb(show_id, id_type):
    endpoint = f"https://api.themoviedb.org/3/find/{show_id}?api_key={API_KEY}&external_source={id_type}"
    response = requests.get(endpoint).content
    data = json.loads(response)
    logging.debug(f'[TMDb API] Obtained tmdb_id of {show_id}')
    return data.get('tv_results')[0].get('id')


def get_tv_show(tmdb_id):
    endpoint = f"https://api.themoviedb.org/3/tv/{tmdb_id}?api_key={API_KEY}"
    response = requests.get(endpoint).content
    data = json.loads(response)
    logging.debug(f'[TMDb API] Obtained data of {data["name"].upper()}')
    relevant_info = {
        'creators': '|'.join([x['name'] for x in data.get('created_by')]) if data.get('created_by') else None,
        'networks': '|'.join([x['name'] for x in data.get('networks')]) if data.get('networks') else None,
        'language': data.get('original_language'),
        'overview': data.get('overview'),
        'production_companies': '|'.join([x['name'] for x in data.get('production_companies')]) if data.get('production_companies') else None,
    }
    return relevant_info


# def get_session_token():
#     response = requests.post(
#         "https://api.themoviedb.org/4/auth/request_token",
#         headers={
#             'Authorization': f'Bearer {API_KEY_4}',
#             'Content-Type': 'application/json;charset=utf-8',
#         }
#     ).content
#     data = json.loads(response)
#     request_token = data.get('request_token')
#     print(f'REQUEST TOKEN: https://www.themoviedb.org/auth/access?request_token={request_token}')
#     time.sleep(10)
#     response = requests.post(
#         "https://api.themoviedb.org/4/auth/access_token",
#         headers={
#             'Authorization': f'Bearer {API_KEY_4}',
#             'Content-Type': 'application/json;charset=utf-8',
#         },
#         data=json.dumps({
#             "request_token": request_token
#         })
#     ).content
#     data = json.loads(response)
#     pprint(data)
#     access_token = data.get('access_token')
#     print(f'ACCESS TOKEN: {access_token}')
