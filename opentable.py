import requests
from bs4 import BeautifulSoup 
import csv                  
from datetime import datetime
import json
# Get ratings and reviews

def scrape_opentable(url, resid):
	session = requests.Session()
	session.headers.update({
		'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
		'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
		"accept-encoding": "gzip, deflate, br",
		"cookie": "lsCKE=cbref=1; otuvid=16276F20-09CC-427F-BF39-80A57E7ED16D; notice_preferences=100; notice_behavior=none; spredCKE=redcount=0; _ga=GA1.2.1446288772.1565124174; _gid=GA1.2.367145729.1565124179; _gac_UA-52354388-1=1.1565124179.CjwKCAjwyqTqBRAyEiwA8K_4O5H6bD247WaLTEhXDv9Y9IdKG6Mcuwi_gDNOI3zbUHWyc1zjT0abRhoC6boQAvD_BwE; lvCKE=lvmreg=%2C0&histmreg=2%2C1%7C%2C0; OT-SessionId=06301187-cf51-454a-8ecb-24f95cae37bc; OT-Session-Update-Date=1565174094; ftc=x=2019-08-07T11%3A34%3A54&c=1&pt1=1&pt2=1&er=4094&p1ca=ruths-chris-steak-house-seattle&p1q=corrid%3D61579279-287d-4a0a-b17c-ec8270a0100e; ak_bmsc=983479D58A83342311849BE3AB5916FBB81BB3E84C7900004EA94A5DDD2FD329~plpmjBp+p0MNw9WQ4qnGzhuUInD+lV3ulYwNhxCX3K33etlprudpuQRzqWKOK54k8BWdCXa+Ho27gd/3cXRS3faUrOLo5YrVdjikuLGKlEg4DopUp4vRteH3MAhlVNkojGwglYoktjJppjg4dmEH5/Of3KK4Wqg4Ha3HORG8CsOaqkmhlLF4bA7TWyqZehV5MDuwuY4P7COrkigtShpyJmIJy7pQLrtQZZFmNlVzxX55K8acw4gnM00dNqa74nAw3b"
	})
	r = session.get(url, proxies={
			# "http": "http://2ac7aa3a864e45cc9a6f722a22d42e9f:@proxy.crawlera.com:8010/",
			# "https": "https://2ac7aa3a864e45cc9a6f722a22d42e9f:@proxy.crawlera.com:8010/",
	})

	soup = BeautifulSoup(r.text, 'html.parser')
	restaurantName = soup.findAll('h1')[0].text
	rid = soup.findAll('div', class_='reviewBodyContainer')[0].attrs['id'].split('-')[4]
	if soup.findAll('a', class_='_3ddfcf5c')[1].find('span'):
		restaurantAddress = soup.findAll('a', class_='_3ddfcf5c')[1].find('span').text
	else:
		restaurantAddress = soup.findAll('a', class_='_3ddfcf5c')[0].find('span').text

	session = requests.Session()
	session.headers.update({
		'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
		'Accept': 'application/vnd.oc.unrendered+json'

	})
	pages = 1
	pageNum = 1
	count = 0
	items = []
	headers=['source', 'restaurantName', 'restaurantAddress', 'reviewText',
                           'reviewRating', 'reviewAuthor', 'reviewDate']
	csv.register_dialect('myDialect',
	  quoting=csv.QUOTE_ALL,
	  skipinitialspace=True)
	with open('opentable_' + restaurantName + '.csv', 'w') as f:
		writer = csv.writer(f, dialect='myDialect')

		while pageNum <= pages:

			apiURL = 'https://oc-registry.opentable.com/v2/oc-reviews-restaurant-profile-feed/1.1.2292?rid={}&culture=en-US&page={}&includeCSS=true&sortBy=newestreview&clickFilterbyOverallRating=true&deemphasizeReviewToolbarIcons=false&showReviewerPhotos=false&anonymousId=16276F20-09CC-427F-BF39-80A57E7ED16D&bucketABTests=true&__ot_conservedHeaders=x2YPvT6POzqVVB9%2B77Ms1CArazmxItFabCE24bSmZx24x1Rw%2Bx8sHwW77XgZcc%2F6w3wkr%2BeWK2T7Q%2BS9NsOlLhu%2BjxuUPwZPrOIhfLK7a9XynP2QEUlfA9pzVuoq2GIv6NUf4a04AIBoc7K2%2BunnO3vvNs0rY5pM%2BnHUqoa4JfgFh7Vwv4nPgM3LVbIG9aPjNg%2BaI2L6O00%3D&__oc_Retry=0'
			r = session.get(apiURL.format(rid, pageNum))
			# soup = BeautifulSoup(r.text, 'html.parser')
			if pageNum == 1:
				pages = r.json()['data']['paginationData']['totalPages']
				print(pages)
			pageNum += 1
			if 'data' not in r.json():
				continue
			reviews = r.json()['data']['reviews']
			for review in reviews:
				count += 1
				reviewDate = review['dateDined']
				reviewDate = datetime.strptime(reviewDate, '%Y-%m-%d')
				reviewDate = datetime.strftime(reviewDate,'%d-%m-%Y')
				author = review['reviewer']['displayName']
				# reviewText = review['reviewText'].replace('<br />', ' ').replace('&amp;', '&').replace('&quot;', ' ').replace('&#039;', " ").replace("\'", " ").encode('utf-8')
				reviewText = review['reviewText'].replace('<br />', ' ').replace('&amp;', '&').replace('&quot;', ' ').replace('&#039;', " ").replace("\'", " ")
				
				rating = review['rating']['overall']
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
scrape_opentable('https://www.opentable.com.au/r/the-grounds-of-the-city-sydney', 222)