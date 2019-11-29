from urllib.request import urlopen
from bs4 import BeautifulSoup 
import csv                  
from datetime import datetime

# Get ratings and reviews

def scrape_yelp(url, resid):
	url2 = url
	page = urlopen(url2)
	soup = BeautifulSoup(page, features="html.parser")
	print(url)
	pageOptions = soup.findAll('div', {'class': 'page-option'})
	if pageOptions:
		num_pages = int(pageOptions[len(pageOptions) - 1].find('a', {'class': 'pagination-links_anchor'}).text.strip())
	else:
		num_pages = 1
	end = num_pages * 20
	# end = 20
	restaurantAddress = soup.find('address').text.strip()
	restaurantName = ''
	for name in soup.findAll('h1', {"class":"biz-page-title"}):
		restaurantName += name.text
		restaurantName += ' '
	start = 0
	filename = 'yelp_'+ restaurantName + '.csv'
	headers=['source', 'restaurantName', 'restaurantAddress', 'reviewText',
	                       'reviewRating', 'reviewAuthor', 'reviewDate']
	csv.register_dialect('myDialect',
	  quoting=csv.QUOTE_ALL,
	  skipinitialspace=True)
	items = []
	with open(filename, 'w', encoding='utf-8') as f:
		writer = csv.writer(f, dialect='myDialect')
		writer.writerow(headers)
		while (start < end):
			if start == 0:
				url = url2
			else:
				url = url2 + '?start=' + str(start)
			start +=20

			page = urlopen(url)
			soup = BeautifulSoup(page, features="html.parser")


			print(restaurantName)
			for reviewBody in soup.findAll('div',{"class":"review review--with-sidebar"}):

				reviewDate = reviewBody.find('div', {'class': 'biz-rating'}).find('span', {'class': 'rating-qualifier'})
				if reviewDate:
					reviewDate = reviewDate.text.replace('Updated review', '').strip()

					if int(reviewDate.split('/')[0]) >= 10:
						month = reviewDate.split('/')[0]
					else: 
						month = '0' + reviewDate.split('/')[0]
					if int(reviewDate.split('/')[1]) >= 10:
						day = reviewDate.split('/')[1]
					else:
						day = '0' + reviewDate.split('/')[1]
					year = reviewDate.split('/')[2]
					reviewDate = month + '-' + day + '-' + year
				else:
					reviewDate = ''

				author = reviewBody.find('a', {'class': 'user-display-name'})
				if author:
					author = author.text
				else:
					author = ''

				reviewText = reviewBody.find('p')
				if reviewText:
					reviewText = reviewText.text
				else:
					reviewText = ''

				rating = reviewBody.find('div', {'class': 'rating-large'})
				if rating:
					rating = rating.get("title").replace('star rating', '').strip()
				else:
					rating = ''

				writableItem = []
				writableItem.append('yelp')
				writableItem.append(restaurantName.encode('utf-8'))
				writableItem.append(restaurantAddress.encode('utf-8'))
				writableItem.append(reviewText.encode('utf-8'))
				writableItem.append(rating.encode('utf-8'))
				writableItem.append(author.encode('utf-8'))
				writableItem.append(reviewDate.encode('utf-8'))
				writer.writerow(writableItem)
				items.append({
		            'source': 'yelp',
		            'restaurantId': resid,
		            # 'restaurantName': restaurantName,
		            # 'restaurantAddress': restaurantAddress,
		            'reviewAuthor': author,
		            'reviewRating': rating,
		            'reviewText': reviewText,
		            'reviewDate': reviewDate, # 'ratingDate' instead of 'relativeDate'
		        })
				print(writableItem)
	f.close()
	return items
