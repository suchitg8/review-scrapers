import csv     
import requests
import json
# Get ratings and reviews

def scrape_google(url):
	session = requests.Session()
	session.headers.update({
		'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:57.0) Gecko/20100101 Firefox/57.0',
	})
	r = session.get(url)
	soup = BeautifulSoup(r.text, features="html.parser")
	print(r.text)
	return page
scrape_google('https://www.google.com/search?ei=oFdNXdjrKIuGyAOW3IeADg&q=steersons&oq=steersons&gs_l=psy-ab.3..35i39l2j0l3j0i10.2229.3090..3254...0.0..0.251.1700.0j3j5......0....1..gws-wiz.......0i71j0i67j0i131j0i131i20i263j0i131i67.WX5eQ5TEMxc&ved=&uact=5#lrd=0x6b12ae477e5e1c59:0xa1d3a78a8436b9f,1,')