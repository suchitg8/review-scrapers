# coding: utf-8

# In[ ]:

import requests             
from celery import Celery
import json
from tripadvisor import scrape_tripadvisor
from yelp import scrape_yelp
from opentable import scrape_opentable
from thefork import scrape_thefork
from quandoo import scrape_quandoo

lang = 'en'
app = Celery('reviews_celery', broker='redis://localhost')


def get_reviews(site, resURL, resID):
    body = {
        "username": "reviewuser",
        "password": "^ev@pi4123"
    }
    headers = {
         'Content-Type': 'application/x-www-form-urlencoded',
    }
    url = "http://13.55.43.186/api/token/"
    response = requests.post(url, data = body, headers = headers, proxies={
            "http": "http://2ac7aa3a864e45cc9a6f722a22d42e9f:@proxy.crawlera.com:8010/"
    })

    print(response)
    accesstoken = response.json()['data']['access']
    
    headers = {
        "Authorization": "Bearer {}".format(accesstoken),
        "Content-Type": "application/json",

    }
    # body = 
    if site == 'tripadvisor':
        reviews = scrape_tripadvisor(resURL, resID)
    elif site == 'yelp':
        reviews = scrape_yelp(resURL, resID)
    elif site == 'opentable':
        reviews = scrape_opentable(resURL, resID)
    elif site == 'thefork':
        reviews = scrape_thefork(resURL, resID)
    elif site == 'quandoo':
        reviews = scrape_quandoo(resURL, resID)
    x = 0
    count = len(reviews)
    while x < count:
        print(count)
        if x + 50 < count:
            print(len(reviews[x:x + 50]))
            body = {
                "reviews": reviews[x:x + 50]
            }
        else:
            print(reviews[x:count])
            body = {
                "reviews": reviews[x:count]
            }
        print(body)
        url = "http://13.55.43.186/api/post-reviews/"
        response = requests.post(url, data = json.dumps(body), headers = headers)
        print(response)
        print(response.json())
        x = x + 50


@app.task
def tripadvisor_reviews(resURL, resID):
    get_reviews('tripadvisor', resURL, resID)

@app.task
def yelp_reviews(resURL, resID):
    get_reviews('yelp', resURL, resID)

@app.task
def opentable_reviews(resURL, resID):
    get_reviews('opentable', resURL, resID)

@app.task
def thefork_reviews(resURL, resID):
    get_reviews('thefork', resURL, resID)

@app.task
def quandoo_reviews(resURL, resID):
    get_reviews('quandoo', resURL, resID)
