import requests             
from bs4 import BeautifulSoup 
import csv                  
import webbrowser
import io
import json
from datetime import datetime

resID = ''
def display(content, filename='output.html'):
    with open(filename, 'wb') as f:
        f.write(content)
        webbrowser.open(filename)

def get_soup(session, url, show=False):
    r = session.get(url)
    if show:
        display(r.content, 'temp.html')

    if r.status_code != 200: # not OK
        print('[get_soup] status code:', r.status_code)
    else:
        return BeautifulSoup(r.text, 'html.parser')
    
def post_soup(session, url, params, show=False):
    '''Read HTML from server and convert to Soup'''

    r = session.post(url, data=params)
    
    if show:
        display(r.content, 'temp.html')

    if r.status_code != 200: # not OK
        print('[post_soup] status code:', r.status_code)
    else:
        return BeautifulSoup(r.text, 'html.parser')
    
def scrape_tripadvisor(url, resid, lang='en'):
    resID = resid
    # create session to keep all cookies (etc.) between requests
    session = requests.Session()

    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:57.0) Gecko/20100101 Firefox/57.0',
    })


    items = parse(session, url + '?filterLang=' + lang)

    return items

def parse(session, url):
    '''Get number of reviews and start getting subpages with reviews'''

    print('[parse] url:', url)

    soup = get_soup(session, url)

    if not soup:
        print('[parse] no soup:', url)
        return
    # num_reviews = soup.find('a', class_='last')

    # num_reviews = soup.find('a', class_='last').attrs['data-offset']
    # print(soup.find('a', class_='last').attrs['data-offset'])

    # num_reviews = soup.find('span', class_='reviews_header_count').text # get text
    # num_reviews = num_reviews[1:-1] 
    # num_reviews = num_reviews.replace(',', '')
    # num_reviews = int(num_reviews) # convert text into integer
    # print('[parse] num_reviews ALL:', num_reviews)
    # num_reviews = 5
    url_template = url.replace('.html', '-or{}.html')
    print('[parse] url_template:', url_template)

    items = []

    offset = 0

    filename = 'tripadvisor_'+ url.split('Reviews-')[1][:-5] + '__' + lang + '.csv'

    headers=['source', 'restaurantName', 'restaurantAddress', 'reviewText',
                           'reviewRating', 'reviewAuthor', 'reviewDate']
    csv.register_dialect('myDialect',
      quoting=csv.QUOTE_ALL,
      skipinitialspace=True)
    with open(filename, 'w') as f:
        writer = csv.writer(f, dialect='myDialect')
        writer.writerow(headers)
        writableItem = []
        firstItem = []
        while(True):
            subpage_url = url_template.format(offset)

            subpage_items = parse_reviews(session, subpage_url)
            if not subpage_items:
                break
            count = 0
            if len(subpage_items) == 10 and len(firstItem) == 10:
                for i in range(10):
                    if firstItem[i]['reviewText'] == subpage_items[i]['reviewText']:
                        count += 1
                if count == 10:
                    break
                print(count)
            if firstItem == []:
                firstItem = subpage_items
            items += subpage_items
            for item in subpage_items:
                writableItem = []
                writableItem.append(item['source'].encode('utf-8'))
                writableItem.append(item['restaurantName'].encode('utf-8'))
                writableItem.append(item['restaurantAddress'].encode('utf-8'))
                writableItem.append(item['reviewText'].encode('utf-8'))
                writableItem.append(item['reviewRating'].encode('utf-8'))
                writableItem.append(item['reviewAuthor'].encode('utf-8'))
                writableItem.append(item['reviewDate'].encode('utf-8'))
                writer.writerow(writableItem)
            offset += 10
            if len(subpage_items) < 10:
                break
    f.close()
    return items

def get_reviews_ids(soup):

    items = soup.find_all('div', attrs={'data-reviewid': True})

    if items:
        reviews_ids = [x.attrs['data-reviewid'] for x in items][::2]
        print('[get_reviews_ids] data-reviewid:', reviews_ids)
        return reviews_ids
    
def get_more(session, reviews_ids):

    url = 'https://www.tripadvisor.com/OverlayWidgetAjax?Mode=EXPANDED_HOTEL_REVIEWS_RESP&metaReferer=Hotel_Review'

    payload = {
        'reviews': ','.join(reviews_ids), # ie. "577882734,577547902,577300887",
        #'contextChoice': 'DETAIL_HR', # ???
        'widgetChoice': 'EXPANDED_HOTEL_REVIEW_HSX', # ???
        'haveJses': 'earlyRequireDefine,amdearly,global_error,long_lived_global,apg-Hotel_Review,apg-Hotel_Review-in,bootstrap,desktop-rooms-guests-dust-en_US,responsive-calendar-templates-dust-en_US,taevents',
        'haveCsses': 'apg-Hotel_Review-in',
        'Action': 'install',
    }

    soup = post_soup(session, url, payload)

    return soup

def parse_reviews(session, url):
    '''Get all reviews from one page'''

    print('[parse_reviews] url:', url)

    soup =  get_soup(session, url)
    if not soup:
        print('[parse_reviews] no soup:', url)
        return

    restaurant_name = soup.find('h1', class_='ui_header')
    if restaurant_name:
        restaurant_name = restaurant_name.text
    else:
        restaurant_name = ''

    restaurant_address = soup.find('span', class_='locality')
    if restaurant_address:
        restaurant_address = restaurant_address.text
    else:
        restaurant_address = ''
    reviews_ids = get_reviews_ids(soup)
    if not reviews_ids:
        return

    soup = get_more(session, reviews_ids)
    
    if not soup:
        print('[parse_reviews] no soup:', url)
        return

    items = []

    for idx, review in enumerate(soup.find_all('div', class_='reviewSelector')):

        badgets = review.find_all('span', class_='badgetext')
        if len(badgets) > 0:
            contributions = badgets[0].text
        else:
            contributions = '0'

        if len(badgets) > 1:
            helpful_vote = badgets[1].text
        else:
            helpful_vote = '0'
        user_loc = review.select_one('div.userLoc strong')
        if user_loc:
            user_loc = user_loc.text
        else:
            user_loc = ''
        author = review.select_one('div.info_text div')
        if author:
            author = author.text
        else:
            author = ''
        bubble_rating = review.select_one('span.ui_bubble_rating')
        if bubble_rating:
            bubble_rating = bubble_rating['class']
            bubble_rating = bubble_rating[1].split('_')[-1]
        else:
            bubble_rating = ''

        reviewDate = review.find('span', class_='ratingDate')
        if reviewDate:
            reviewDate = reviewDate['title']
            reviewDate = datetime.strptime(reviewDate, '%B %d, %Y')
            reviewDate = datetime.strftime(reviewDate,'%d-%m-%Y')
        else:
            reviewDate = ''
        item = {
            'source': 'tripadvisor',
            # 'restaurantName': restaurant_name,
            # 'restaurantAddress': restaurant_address,
            'restaurantId': resID,
            'reviewAuthor': author,
            'reviewRating': str(float(bubble_rating) / 10),
            'reviewText': review.find('p', class_='partial_entry').text,
            'reviewDate': reviewDate, # 'ratingDate' instead of 'relativeDate'
        }

        items.append(item)
        print('\n--- review ---\n')
        for key,val in item.items():
            print(' ', key, ':', val)
    return items
