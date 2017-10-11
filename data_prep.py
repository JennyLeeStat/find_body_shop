import os
import time
import pandas as pd
import urllib.request
import json
from collections import Counter, defaultdict
from pprint import pprint

API_KEY = "AIzaSyCEn8mAyOQEUZ8h8gIYaQ-7YY6vVe3iV5o"
API_HOST = "https://maps.googleapis.com/maps/api/place"
TEXT_SEARCH_PATH = "/textsearch"
DETAIL_SEARCH_PATH = "/details"
QUERY_TERM = "auto+repair+in+pittsburgh"


text_search_url = "{}{}/json?query={}&key={}".format(API_HOST,
                                    TEXT_SEARCH_PATH, QUERY_TERM, API_KEY)

def get_json(url):
    search_result = urllib.request.urlopen(url)
    json_body = search_result.read()
    return json.loads(json_body.decode("utf-8"))


def place_search(url, max_page=10):
    res = [ ]
    page = 0

    while page < max_page:

        decoded = get_json(url)

        for shop in decoded[ 'results' ]:
            if 'rating' not in shop:
                # Ignore if response doesn't have the rating key
                pass
            else:
                res.append([shop['place_id'], shop['rating']])


        next_token = decoded['next_page_token']
        url = url + "&pagetoken=" + next_token
        page += 1
        # Google API doesn't allow instant data retrieval
        time.sleep(5)

    return res

text_search_result = place_search(text_search_url)
text_search_result = pd.DataFrame(text_search_result,
                                  columns = ['place_id', 'avg_rating'])

def place_details(res):
    detail_res = defaultdict(dict)

    for id in res.place_id:

        detail_url = "{}{}/json?key={}&placeid={}".format(API_HOST,
                              DETAIL_SEARCH_PATH, API_KEY, id)
        decoded = get_json(detail_url)
        detail_res[id]['name'] = decoded.get('result').get('name')
        detail_res[id]['phone'] = decoded.get('result').get('international_phone_number')
        reviews = decoded.get('result').get('reviews')
        ratings = Counter()

        for i, _ in enumerate(reviews):
            r = reviews[i]['rating']
            ratings[r] += 1

        detail_res[id]['ratings'] = ratings

    return detail_res

detail_search_res = place_details(text_search_result)
detail_search_res_df = pd.DataFrame.from_dict(detail_search_res, orient='index')
ratings = detail_search_res_df['ratings'].apply(pd.Series)
detail_search_res_df = pd.concat([detail_search_res_df.drop(['ratings'], axis=1), ratings], axis=1)
detail_search_res_df






