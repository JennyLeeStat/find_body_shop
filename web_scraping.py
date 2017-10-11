import time
import urllib.request
from bs4 import BeautifulSoup
import json
from collections import defaultdict, Counter
from pprint import pprint
import pandas as pd


YELP_HOST = "https://www.yelp.com"
SEARCH_TERM = "Auto+Repair+Shop"
LOCATION = "Squirrel+Hill,+Pittsburgh,+PA"
PAGE_NUM_PATH = "&start="


url = "{}/search?find_desc={}&find_loc={}{}".format(
    YELP_HOST, SEARCH_TERM, LOCATION, PAGE_NUM_PATH
)

MAX_PAGE = 10

def get_hrefs(url, max_page=MAX_PAGE):
    hrefs = [ ]
    for i in range(max_page):
        if i == 0:
            search_url = url
        else:
            search_url = url + str(i * 10)

        page = urllib.request.urlopen(search_url).read()
        soup = BeautifulSoup(page)
        for j, link in enumerate(soup.findAll('a', {'class': "biz-name js-analytics-click"})):
            if j == 0:
                # First entry on every page is ad
                pass
            else:
                hrefs.append(link.get('href'))

        time.sleep(5)
    return hrefs

hrefs = get_hrefs(url)

def get_20_reviews(href):
    url = '{}{}'.format(YELP_HOST, href)
    page = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(page)

    # All reviews are inside this script tags
    reviews_script = soup.find("script", {'type': 'application/ld+json'})

    # Let's remove script tags
    tmp = str(reviews_script).split(">")[1]
    tmp = tmp.split("<")[0]
    reviews_json = json.loads(tmp)
    reviews = reviews_json.get('review')

    # Get store name from the title
    title = soup.find("title").text
    place_name = str(title).split("-")[0]

    return reviews, place_name

def get_ratings_table(href):
    url = '{}{}'.format(YELP_HOST, href)
    page = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(page)

    ratings = defaultdict(int)
    for i in range(1, 6):
        class_name = "histogram_row histogram_row--{}".format(i)
        rating_value = soup.find("tr", {"class": class_name})
        rating_count = rating_value.find("td", {"class": "histogram_count"}).text
        ratings[str(i)] = int(rating_count)
        print(str(i), rating_count)

    return ratings

ratings = get_ratings_table(hrefs[3])


class ParseYelpBizPage:

    def __init__(self, href):
        self.url = '{}{}'.format(YELP_HOST, href)
        self.page = urllib.request.urlopen(self.url).read()
        self.soup = BeautifulSoup(self.page)
        self.ratings = defaultdict(dict)

    def get_name(self):
        title = self.soup.find("title").text
        place_name = str(title).split("-")[ 0 ]
        return place_name

    def get_20_reviews(self):
        # All reviews are inside this script tags
        reviews_script = self.soup.find("script", {'type': 'application/ld+json'})

        # Let's remove script tags
        tmp = str(reviews_script).split(">")[ 1 ]
        tmp = tmp.split("<")[ 0 ]
        reviews_json = json.loads(tmp)
        reviews = reviews_json.get('review')
        return reviews

    def get_ratings_table(self):

        stars = ['five', 'four', 'three', 'two', 'one']
        for i in range(1, 6):
            class_name = "histogram_row histogram_row--{}".format(i)
            rating_value = self.soup.find("tr", {"class": class_name})
            rating_count = rating_value.find("td", {"class": "histogram_count"}).text
            self.ratings[ stars[i - 1] ] = int(rating_count)

        return self.ratings



result_dict = {}
for i, link in enumerate(hrefs):
    print("processing status: {}/{}".format(i + 1, len(hrefs)))
    yp = ParseYelpBizPage(link)
    name = yp.get_name()
    result_dict[name] = yp.get_ratings_table()
    time.sleep(5)



autoshop_ratings = pd.DataFrame.from_dict(result_dict, orient="index")
autoshop_ratings.to_csv("data/autoshop_ratings.csv")



