# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup 
import csv                  
from datetime import datetime
import json
import pdb
import sys
reload(sys)
sys.setdefaultencoding('utf8')
# Get ratings and reviews
def for_theforkau(url, resid):
	print(url)
	session = requests.Session()
	session.headers.update({
		'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:57.0) Gecko/20100101 Firefox/57.0',
		'content-type': 'application/json',
		'accept': 'application/json',
		'cookie': 'CC=15101-cfd; cookiesPrivacyPolicyBanner=1; trackingId=3a15f0d2-df2e-4474-9861-eaab316aaf8b; G_ENABLED_IDPS=google; _sdsat_landing_page=https://www.thefork.com.au/restaurant/bondi-pizza-parramatta-r537189|1574147638868; _sdsat_session_count=1; _sdsat_traffic_source=https://c.datado.me/captcha/?initialCid=AHrlqAAAAAMAC-7b214cOa4AaMiKIQ%3D%3D&hash=4980A61279181687DE605B235F81B9&cid=VTNI3.AMDx.ZdnL3b.IcWS6LVQmWA.7YYqEk13L.g3SpcsTaqsrxQavvm97oCCUXgKn_5_YxMxnp.p6FfOuzHHZoJHjT39PUwoc~hIwu1I&t=fe; _ga=GA1.3.1360485143.1574147639; _gid=GA1.3.1069667302.1574147639; svisit=1; _hjid=037bee8b-3cb8-46c4-abb0-0ac605ee44d4; _gat=1; datadome=QSJaGh.2slQITi.E9eWD2d59cIN5_y_L-rCnKz2L9xX-sRlvCksofRSiu7ZZRIY~Qf.QJW~K1~EXNZAhIiQs8hc.AORy~xfd1LvhA9r3us; _sdsat_lt_pages_viewed=7; _sdsat_pages_viewed=7'
	})
	# r = session.get(url, proxies={
	# 		# "http": "https://2ac7aa3a864e45cc9a6f722a22d42e9f:@proxy.crawlera.com:8010/",
	# 		"https": "https://98032165b2a443899140e15ce4f5d903:@proxy.crawlera.com:8010/"

	# }, verify = False)
	rid = url.split('-')[-1].replace('r', '')
	print(url.split('-')[-1].replace('r', ''))
	overview = 'https://www.thefork.com.au/api/restaurants/529933?include=photos%2Cmenus%2Ctags%2CtagCategories%2Coffers%2Ccity%2CratingStats&filter%5Btags.category.id%5D=11%2C4%2C19%2C20%2C21%2C17%2C6%2C2%2C15%2C1%2C9%2C11%2C5%2C10%2C12%2C8'
	r = session.get(overview, proxies={
			"http": "http://2ac7aa3a864e45cc9a6f722a22d42e9f:@proxy.crawlera.com:8010/",
			"https": "https://2ac7aa3a864e45cc9a6f722a22d42e9f:@proxy.crawlera.com:8010/",
	}, verify = False)
	
	print(overview.format(rid), r.text)
	# print(r.text)
	soup = BeautifulSoup(r.text, 'html.parser')
	print(soup.findAll('link')[1])
	pageNum = int(int(soup.find('h2', {'id': 'reviews'}).text.split(' ')[0]) / 10) + 1
	restaurantName = soup.find('h1', class_='restaurant-name').text.replace('  ', '').strip().replace('\r', '').replace('\n', ' ')
	restaurantAddress = soup.find('span', class_='street-address').text.strip() + soup.find('span', class_='locality').text.strip() + soup.find('span', class_='state').text.strip() + soup.find('span', class_='postcode').text.strip() + ', ' + soup.find('span', class_='country').text.strip()
	count = 0
	items = []
	headers=['source', 'restaurantName', 'restaurantAddress', 'reviewText',
                           'reviewRating', 'reviewAuthor', 'reviewDate']
	csv.register_dialect('myDialect',
	  quoting=csv.QUOTE_ALL,
	  skipinitialspace=True)
	with open('thefork_' + restaurantName + '.csv', 'w') as f:
		writer = csv.writer(f, dialect='myDialect')
		for page in range(pageNum):
			pageurl = '{}?reviewsPage={}'
			r = session.get(pageurl.format(url, page + 1), proxies={
			# "http": "https://2ac7aa3a864e45cc9a6f722a22d42e9f:@proxy.crawlera.com:8010/",
			"https": "https://98032165b2a443899140e15ce4f5d903:@proxy.crawlera.com:8010/"

			}, verify = False)
			soup = BeautifulSoup(r.text, 'html.parser')
			reviews = soup.findAll('article', class_="review-item")
			for review in reviews:
				count += 1
				content = review.find('section', class_='diner-content')
				author = content.find('span', class_="user-name")
				if author:
					if author.find('a'):
						author = author.find('a').text
					else:
						author = author.find('span').text
				else:
					author = ''

				reviewRating = content.find('span', class_='value')
				if reviewRating:
					if reviewRating.find('span'):
						reviewRating = reviewRating.find('span').text
					else:
						reviewRating = ''
				else:
					reviewRating = ''

				reviewDate = content.find('span', class_='date')
				if reviewDate:
					reviewDate = reviewDate.text
					dateArr = reviewDate.split(', ')[1].split(' ')
					day = dateArr[0]
					month = dateArr[1]
					year = dateArr[2]
					if int(day) < 10:
						day = '0' + day
					reviewDate = datetime.strptime(day + ' ' + month + ' ' + year, '%d %b %Y')
					reviewDate = datetime.strftime(reviewDate,'%d-%m-%Y')
				else:
					reviewRaing = ''

				reviewText = content.find('div', class_='comment')
				# print(reviewText)
				if reviewText:
					if reviewText.find('span'):
						reviewText = reviewText.find('span').text
					else:
						reviewText = ''
				else:
					reviewText = ''

				print(count, restaurantAddress, restaurantName, author, reviewRating, reviewDate, reviewText)
				items.append({
					'source': 'thefork',
					# 'restaurantName': restaurantName,
					# 'restaurantAddress': restaurantAddress,
					'restaurantId': resid,
					'reviewAuthor': author,
					'reviewRating': reviewRating,
					'reviewText': reviewText,
					'reviewDate': reviewDate, # 'ratingDate' instead of 'relativeDate'
				})
				writableItem = []
				writableItem.append('thefork')
				writableItem.append(restaurantName.encode('utf-8'))
				writableItem.append(restaurantAddress.encode('utf-8'))
				writableItem.append(reviewText.encode('utf-8'))
				writableItem.append(reviewRating.encode('utf-8'))
				writableItem.append(author.encode('utf-8'))
				writableItem.append(reviewDate.encode('utf-8'))
				writer.writerow(writableItem)
		return items
def for_thefork(url, resid):
	session = requests.Session()
	session.headers.update({
		'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:57.0) Gecko/20100101 Firefox/57.0',
	})
	r = session.get(url, proxies={
			# "http": "https://2ac7aa3a864e45cc9a6f722a22d42e9f:@proxy.crawlera.com:8010/",
			"https": "https://98032165b2a443899140e15ce4f5d903:@proxy.crawlera.com:8010/"

	}, verify=False)

	# pdb.set_trace()
	headers=['source', 'restaurantName', 'restaurantAddress', 'reviewText',
                           'reviewRating', 'reviewAuthor', 'reviewDate']
	csv.register_dialect('myDialect',
	  quoting=csv.QUOTE_ALL,
	  skipinitialspace=True)
	soup = BeautifulSoup(r.text, 'html.parser')
	allreviews = soup.find('div', class_='reviews-counter').text.strip().split('/')[1].replace(' reviews', '')
	pageNum = int(int(allreviews)/ 20) + 1	
	restaurantName = soup.find('h1', class_='restaurantSummary-name').text
	with open('thefork_' + restaurantName + '.csv', 'w') as f:
		writer = csv.writer(f, dialect='myDialect')
		restaurantAddress = soup.find('span', class_='restaurantSummary-address').text.strip().replace('            ', ' ').replace('\n', '')
		resNum = url.split('/')[len(url.split('/')) - 1]
		count = 0
		items = []
		apiurl = '{}/contentrates?sort=RESERVATION_DATE_DESC&page={}&restaurantId={}&filters%5Bwith_comments_only%5D=0&filters%5Bfood_reports_only%5D=0&filters%5Boccasion%5D=ALL'
		for page in range(pageNum):
			r = session.get(apiurl.format(url, page + 1, resNum), proxies={
				"https": "https://98032165b2a443899140e15ce4f5d903:@proxy.crawlera.com:8010/"
			}, verify=False)

			soup = BeautifulSoup(r.json()['content'], 'html.parser')
			for review in soup.findAll('div', class_='reviewItem--mainCustomer'):
				count += 1
				if count == 1:
					print(review)
				reviewDate = review.find('li', class_='reviewItem-date')
				if reviewDate:
					reviewDate = reviewDate.text.strip().replace('Meal date : ', '')
					dateArr = reviewDate.split(' ')
					day = dateArr[0]
					month = dateArr[1]
					year = dateArr[2]
					if int(day) < 10:
						day = '0' + day
					reviewDate = datetime.strptime(day + ' ' + month + ' ' + year, '%d %b %Y')
					reviewDate = datetime.strftime(reviewDate,'%d-%m-%Y')
				else:
					reviewDate = '08-08-2019'

				reviewRating = review.find('span', class_='rating-ratingValue')
				if reviewRating:
					reviewRating = reviewRating.text
				else:
					reviewRating = ''

				author = review.find('div', class_='reviewItem-profileDisplayName')
				if author:
					author = author.text.strip()
				else:
					author = ''
				reviewText = review.find('div', class_='reviewItem-customerComment')	
				if reviewText:
					reviewText = reviewText.text.strip()
				else:
					reviewText = ''
				if len(reviewDate) < 4:
					reviewDate = '08-08-2019'

				items.append({
			            'source': 'thefork',
			            # 'restaurantName': restaurantName,
			            # 'restaurantAddress': restaurantAddress,
		            	'restaurantId': resid,

			            'reviewAuthor': author,
			            'reviewRating': reviewRating,
			            'reviewText': reviewText,
			            'reviewDate': reviewDate, # 'ratingDate' instead of 'relativeDate'
			    })
				writableItem = []
				writableItem.append('thefork')
				writableItem.append(restaurantName.encode('utf-8'))
				writableItem.append(restaurantAddress.encode('utf-8'))
				writableItem.append(reviewText.encode('utf-8'))
				writableItem.append(reviewRating.encode('utf-8'))
				writableItem.append(author.encode('utf-8'))
				writableItem.append(reviewDate.encode('utf-8'))
				writer.writerow(writableItem)
				print(count, reviewDate)

		print(count)
	f.close()
	return items
def scrape_thefork(url, resid):
	print(url.split('/'))	
	if url.split('/')[2] == 'www.thefork.com':
		return for_thefork(url, resid)
	else:
		return for_theforkau(url, resid)
scrape_thefork('https://www.thefork.com.au/restaurant/claire-s-kitchen-at-le-salon-r529933', 4444)
