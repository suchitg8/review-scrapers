import requests
from bs4 import BeautifulSoup 
import csv                  
from datetime import datetime
import json
# Get ratings and reviews

def scrape_quandoo(url, resid):
	urlparse = url.split('/')
	rId = urlparse[len(urlparse) - 1].split('-')
	rId = rId[len(rId) - 1]
	print(rId)
	session = requests.Session()
	session.headers.update({
		'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
		'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
		"accept-encoding": "gzip, deflate, br",
	})
	
	r = session.get(url, proxies={
			# "http": "http://2ac7aa3a864e45cc9a6f722a22d42e9f:@proxy.crawlera.com:8010/",
			# "https": "https://2ac7aa3a864e45cc9a6f722a22d42e9f:@proxy.crawlera.com:8010/",
	})
	# print(r.text)
	soup = BeautifulSoup(r.text, 'html.parser')
	restaurantName = soup.find('h1').text
	addresslist = soup.find('div', class_='sc-1s6eao5-1 ecUUnt').findAll('div')
	restaurantAddress = addresslist[1].text + ',' + addresslist[2].text
	apiurl = 'https://9100-api.quandoo.com/portal/merchants/{}/reviews?locale=en&offset=0&limit=20&sortBy='
	r = session.get(apiurl.format(rId), proxies={
			# "http": "http://2ac7aa3a864e45cc9a6f722a22d42e9f:@proxy.crawlera.com:8010/",
			# "https": "https://2ac7aa3a864e45cc9a6f722a22d42e9f:@proxy.crawlera.com:8010/",
	})
	total = r.json()['total']
	print(restaurantName, restaurantAddress, total)

	offset = 0
	items = []
	headers=['source', 'restaurantName', 'restaurantAddress', 'reviewText',
                           'reviewRating', 'reviewAuthor', 'reviewDate']
	count = 0
	csv.register_dialect('myDialect',
	  quoting=csv.QUOTE_ALL,
	  skipinitialspace=True)
	with open('quandoo_' + restaurantName + '.csv', 'w') as f:
		writer = csv.writer(f, dialect='myDialect')

		while offset <= total:

			apiURL = 'https://9100-api.quandoo.com/portal/merchants/{}/reviews?locale=en&offset={}&limit=20&sortBy='
			r = session.get(apiURL.format(rId, offset))
			# soup = BeautifulSoup(r.text, 'html.parser')
			offset = offset + 20
			reviews = r.json()['reviews']
			for review in reviews:
				count += 1
				reviewDate = review['datePublished'].split('T')[0]
				reviewDate = datetime.strptime(reviewDate, '%Y-%m-%d')
				reviewDate = datetime.strftime(reviewDate,'%d-%m-%Y')
				# print(review['customer'])
				if review['customer']['firstName']:
					firstName = review['customer']['firstName']
				else:
					firstName = ''
				if review['customer']['name']:
					name = review['customer']['name']
				else:
					name = ''
				author = firstName + ' ' + name
				reviewText = review['description']
				rating = review['rating']
				items.append({
					'source': 'opentable',
					# 'restaurantName': restaurantName,
					# 'restaurantAddress': restaurantAddress,
		            'restaurantId': resid,

					'reviewAuthor': author,
					'reviewRating': rating,
					'reviewText': reviewText,
					'reviewDate': reviewDate, # 'ratingDate' instead of 'relativeDate'
				})
				writableItem = []
				writableItem.append('opentable')
				writableItem.append(restaurantName.encode('utf-8'))
				writableItem.append(restaurantAddress.encode('utf-8'))
				writableItem.append(reviewText.encode('utf-8'))
				writableItem.append(rating)
				writableItem.append(author.encode('utf-8'))
				writableItem.append(reviewDate.encode('utf-8'))
				writer.writerow(writableItem)
				print(count, reviewDate, author, reviewText, rating)
		return items
scrape_quandoo('https://www.quandoo.ch/en/place/hiltl-schweiz-9994', 1111)