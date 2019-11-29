import requests
from bs4 import BeautifulSoup 
import csv                  
from datetime import datetime
import json
import pdb
# Get ratings and reviews

def scrape_theforkau(url):
	session = requests.Session()
	session.headers.update({
		'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:57.0) Gecko/20100101 Firefox/57.0',
	})
	r = session.get(url)
	soup = BeautifulSoup(r.text, 'html.parser')
	pageNum = int(int(soup.find('h2', {'id': 'reviews'}).text.split(' ')[0]) / 10) + 1
	restaurantName = soup.find('h1', class_='restaurant-name').text.replace('  ', '').strip()
	restaurantAddress = soup.find('span', class_='street-address').text.strip() + soup.find('span', class_='locality').text.strip() + soup.find('span', class_='state').text.strip() + soup.find('span', class_='postcode').text.strip() + ', ' + soup.find('span', class_='country').text.strip()
	count = 0
	items = []
	for page in range(pageNum):
		pageurl = '{}?reviewsPage={}'
		r = session.get(pageurl.format(url, page + 1))
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

			reviewText = content.find('span', class_='comment')
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
				'restaurantName': restaurantName,
				'restaurantAddress': restaurantAddress,
				'reviewAuthor': author,
				'reviewRating': reviewRating,
				'reviewText': reviewText,
				'reviewDate': reviewDate, # 'ratingDate' instead of 'relativeDate'
			})
	return items
			# print(content.find('span', class_="user-name").find('a').text, content.find('span', class_='date').text, content.find('span', class_='value').find('span').text, content.find('span', class_='content').find('span'))
	# headers=['source', 'restaurantName', 'restaurantAddress', 'reviewText',
 #                           'reviewRating', 'reviewAuthor', 'reviewDate']
	# csv.register_dialect('myDialect',
	#   quoting=csv.QUOTE_ALL,
	#   skipinitialspace=True)
	# with open('1.csv', 'w') as f:
	# 	writer = csv.writer(f, dialect='myDialect')
	# 	soup = BeautifulSoup(r.text, 'html.parser')
	# 	allreviews = soup.find('div', class_='reviews-counter').text.strip().split('/')[1].replace(' reviews', '')
	# 	pageNum = int(int(allreviews)/ 20) + 1	
	# 	restaurantName = soup.find('h1', class_='restaurantSummary-name').text
	# 	restaurantAddress = soup.find('span', class_='restaurantSummary-address').text.strip().replace('            ', ' ').replace('\n', '')
	# 	resNum = url.split('/')[len(url.split('/')) - 1]
	# 	count = 0
	# 	items = []
	# 	apiurl = '{}/contentrates?sort=RESERVATION_DATE_DESC&page={}&restaurantId={}&filters%5Bwith_comments_only%5D=0&filters%5Bfood_reports_only%5D=0&filters%5Boccasion%5D=ALL'
	# 	for page in range(pageNum):
	# 		r = session.get(apiurl.format(url, page + 1, resNum), proxies={
	# 			"https": "https://98032165b2a443899140e15ce4f5d903:@proxy.crawlera.com:8010/"
	# 		}, verify=False)

	# 		soup = BeautifulSoup(r.json()['content'], 'html.parser')
	# 		for review in soup.findAll('div', class_='reviewItem--mainCustomer'):
	# 			count += 1
	# 			if count == 1:
	# 				print(review)
	# 			reviewDate = review.find('li', class_='reviewItem-date')
	# 			if reviewDate:
	# 				reviewDate = reviewDate.text.strip().replace('Meal date : ', '')
	# 				dateArr = reviewDate.split(' ')
	# 				day = dateArr[0]
	# 				month = dateArr[1]
	# 				year = dateArr[2]
	# 				if int(day) < 10:
	# 					day = '0' + day
	# 				reviewDate = datetime.strptime(day + ' ' + month + ' ' + year, '%d %b %Y')
	# 				reviewDate = datetime.strftime(reviewDate,'%d-%m-%Y')
	# 			else:
	# 				reviewDate = '08-08-2019'

	# 			reviewRating = review.find('span', class_='rating-ratingValue')
	# 			if reviewRating:
	# 				reviewRating = reviewRating.text
	# 			else:
	# 				reviewRating = ''

	# 			author = review.find('div', class_='reviewItem-profileDisplayName')
	# 			if author:
	# 				author = author.text.strip()
	# 			else:
	# 				author = ''
	# 			reviewText = review.find('div', class_='reviewItem-customerComment')	
	# 			if reviewText:
	# 				reviewText = reviewText.text.strip()
	# 			else:
	# 				reviewText = ''
	# 			if len(reviewDate) < 4:
	# 				reviewDate = '08-08-2019'

	# 			items.append({
	# 		            'source': 'thefork',
	# 		            'restaurantName': restaurantName,
	# 		            'restaurantAddress': restaurantAddress,
	# 		            'reviewAuthor': author,
	# 		            'reviewRating': reviewRating,
	# 		            'reviewText': reviewText,
	# 		            'reviewDate': reviewDate, # 'ratingDate' instead of 'relativeDate'
	# 		    })
	# 			writableItem = []
	# 			writableItem.append('yelp')
	# 			writableItem.append(restaurantName.encode('utf-8'))
	# 			writableItem.append(restaurantAddress.encode('utf-8'))
	# 			writableItem.append(reviewText.encode('utf-8'))
	# 			writableItem.append(reviewRating.encode('utf-8'))
	# 			writableItem.append(author.encode('utf-8'))
	# 			writableItem.append(reviewDate.encode('utf-8'))
	# 			writer.writerow(writableItem)
	# 			print(count, reviewDate)

	# 	print(count)
	# f.close()
	# return items
scrape_theforkau('https://www.thefork.com.au/restaurant/kingsleys-woolloomooloo-woolloomooloo')