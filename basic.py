from flask import Flask, request
from flask_restplus import Api, Resource, fields
from reviews_celery import tripadvisor_reviews, yelp_reviews, opentable_reviews, thefork_reviews, quandoo_reviews
flask_app = Flask(__name__)
app = Api(app = flask_app, 
		  version = "1.0", 
		  title = "Get Reviews", 
		  description = "You can get reviews for all restaurants from tripadvisor")
reviews = app.namespace('reviews', description='Main APIs')
model = app.model('Name Model', 
		  {'resURL': fields.String(required = True, 
					 description="url of the restaurant", 
					 help="resURL cannot be blank."),
		  'restaurantID': fields.String(required = True, 
					 description="id of the restaurant", 
					 help="resURL cannot be blank.")})
@reviews.route("/tripadvisor")
class Tripadvisor(Resource):
	@app.expect(model)		
	def post(self):
		resURL = request.json['resURL']
		restaurantID = request.json['restaurantID']

		tripadvisor_reviews.delay(resURL, restaurantID)
		return {
			"name" : resURL
		}

@reviews.route("/yelp")
class Yelp(Resource):
	@app.expect(model)		
	def post(self):
		resURL = request.json['resURL']
		restaurantID = request.json['restaurantID']
		yelp_reviews.delay(resURL, restaurantID)
		return {
			"name" : resURL
		}

@reviews.route("/opentable")
class Opentable(Resource):
	@app.expect(model)		
	def post(self):
		resURL = request.json['resURL']
		restaurantID = request.json['restaurantID']
		opentable_reviews.delay(resURL, restaurantID)
		return {
			"name" : resURL
		}

@reviews.route("/thefork")
class Thefork(Resource):
	@app.expect(model)		
	def post(self):
		resURL = request.json['resURL']
		restaurantID = request.json['restaurantID']

		thefork_reviews.delay(resURL, restaurantID)
		return {
			"name" : resURL
		}

@reviews.route("/quandoo")
class Quandoo(Resource):
	@app.expect(model)		
	def post(self):
		resURL = request.json['resURL']
		restaurantID = request.json['restaurantID']

		quandoo_reviews.delay(resURL, restaurantID)
		return {
			"name" : resURL
		}

