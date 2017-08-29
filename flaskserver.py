from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import flash
from flask import jsonify
from flask import make_response
from flask import session as login_session

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError

from database_setup import Base
from database_setup import Restaurant
from database_setup import MenuItem

import string
import random
import json
import httplib2
import requests

CLIENT_ID = json.loads(
	open('client_secrets.json', 'r').read())['web']['client_id']

app = Flask(__name__)

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/')
@app.route('/restaurants/')
def showRestaurants():
	restaurants = session.query(Restaurant).all()

	state = ''.join(random.choice(string.ascii_uppercase + string.digits)
		for x in xrange(32))
	login_session['state'] = state

	user = login_session.get('username')

	return render_template('restaurants.html', 
		restaurants=restaurants, STATE=state, user=user)


@app.route('/restaurants/new', 
	methods=['GET', 'POST'])
def newRestaurant():
	state = ''.join(random.choice(string.ascii_uppercase + string.digits)
		for x in xrange(32))
	login_session['state'] = state

	user = login_session.get('username')

	if request.method == 'POST':
		newRest = Restaurant(
			name = request.form['name'])

		session.add(newRest)
		session.commit()
		flash('Restaurant created successfully!')

		return redirect(url_for('showRestaurants'))

	return render_template('new_restaurant.html', STATE=state, user=user)


@app.route('/restaurants/<int:restaurant_id>/edit/',
	methods=['GET', 'POST'])
def editRestaurant(restaurant_id):
	restaurant = session.query(Restaurant).filter_by(
		id=restaurant_id).one()

	state = ''.join(random.choice(string.ascii_uppercase + string.digits)
		for x in xrange(32))
	login_session['state'] = state

	user = login_session.get('username')

	if request.method == 'POST':
		restaurant.name = request.form['name']

		session.add(restaurant)
		session.commit()
		flash('Restaurant edited successfully!')

		return redirect(url_for('showRestaurants'))

	return render_template('edit_restaurant.html', restaurant=restaurant,
			STATE=state, user=user)


@app.route('/restaurants/<int:restaurant_id>/delete/',
	methods=['GET', 'POST'])
def deleteRestaurant(restaurant_id):
	restaurant = session.query(Restaurant).filter_by(
		id=restaurant_id).one()

	state = ''.join(random.choice(string.ascii_uppercase + string.digits)
		for x in xrange(32))
	login_session['state'] = state

	user = login_session.get('username')

	if request.method == 'POST':
		session.delete(restaurant)
		session.commit()
		flash('Restaurant deleted successfully!')

		return redirect(url_for('showRestaurants'))
	return render_template('delete_restaurant.html', restaurant=restaurant,
			STATE=state, user=user)


@app.route('/restaurants/<int:restaurant_id>/')
def showMenuItems(restaurant_id):
	restaurant = session.query(Restaurant).filter_by(
		id=restaurant_id).one()
	items = session.query(MenuItem).filter_by(restaurant_id =
		restaurant.id).all()
	apps = session.query(MenuItem).filter_by(restaurant_id =
		restaurant.id, course='Appetizer').all()
	entrees = session.query(MenuItem).filter_by(restaurant_id =
		restaurant.id, course='Entree').all()
	desserts = session.query(MenuItem).filter_by(restaurant_id =
		restaurant.id, course='Dessert').all()
	bevs = session.query(MenuItem).filter_by(restaurant_id =
		restaurant.id, course='Beverage').all()

	state = ''.join(random.choice(string.ascii_uppercase + string.digits)
		for x in xrange(32))
	login_session['state'] = state

	user = login_session.get('username')
	
	return render_template('menu.html', restaurant=restaurant,
			items=items, apps=apps, entrees=entrees, desserts=desserts, bevs=bevs,
			STATE=state, user=user)


@app.route('/restaurants/<int:restaurant_id>/new/',
	methods=['GET', 'POST'])
def newMenuItem(restaurant_id):
	restaurant = session.query(Restaurant).filter_by(
		id=restaurant_id).one()

	state = ''.join(random.choice(string.ascii_uppercase + string.digits)
		for x in xrange(32))
	login_session['state'] = state

	user = login_session.get('username')

	if request.method == 'POST':
		newItem = MenuItem(
			name = request.form['name'],
			course = request.form['course'],
			price = request.form['price'],
			description = request.form['description'],
			restaurant = restaurant,
			restaurant_id = restaurant_id)

		session.add(newItem)
		session.commit()
		flash('New menu item created!')

		return redirect(url_for('showMenuItems',
			restaurant_id = restaurant_id))

	return render_template('new_item.html', restaurant=restaurant,
			STATE=state, user=user)


@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/edit/',
	methods=['GET', 'POST'])
def editMenuItem(restaurant_id, menu_id):
	restaurant = session.query(Restaurant).filter_by(
		id=restaurant_id).one()

	item = session.query(MenuItem).filter_by(
		 id=menu_id).one()

	state = ''.join(random.choice(string.ascii_uppercase + string.digits)
		for x in xrange(32))
	login_session['state'] = state

	user = login_session.get('username')

	if request.method == 'POST':
		item.name = request.form['name']
		item.course = request.form['course']
		item.price = request.form['price']
		item.description = request.form['description']

		session.add(item)
		session.commit()
		flash('Menu item edited successfully!')

		return redirect(url_for('showMenuItems',
			restaurant_id = restaurant_id))

	return render_template('edit_item.html', restaurant=restaurant, item=item,
			STATE=state, user=user)


@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/delete/',
	methods=['GET', 'POST'])
def deleteMenuItem(restaurant_id, menu_id):
	restaurant = session.query(Restaurant).filter_by(
		id=restaurant_id).one()

	item = session.query(MenuItem).filter_by(
		 id=menu_id).one()

	state = ''.join(random.choice(string.ascii_uppercase + string.digits)
		for x in xrange(32))
	login_session['state'] = state

	user = login_session.get('username')

	if request.method == 'POST':
		session.delete(item)
		session.commit()
		flash('Menu item deleted successfully!')

		return redirect(url_for('showMenuItems',
			restaurant_id = restaurant_id))

	return render_template('delete_item.html', item=item,
			STATE=state, user=user)


@app.route('/restaurants/JSON')
def restaurantsJSON():
	restaurants = session.query(Restaurant).all()

	return jsonify(Restaurants=[i.serialize for i in restaurants])


@app.route('/restaurants/<int:restaurant_id>/JSON')
def restaurantMenuJSON(restaurant_id):
	restaurant = session.query(Restaurant).filter_by(
		id=restaurant_id).one()
	items = session.query(MenuItem).filter_by(restaurant_id =
		restaurant_id).all()

	return jsonify(MenuItems=[i.serialize for i in items])


@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/JSON')
def menuItemJSON(restaurant_id, menu_id):
	restaurant = session.query(Restaurant).filter_by(
		id=restaurant_id).one()
	item = session.query(MenuItem).filter_by(id=menu_id).one()

	return jsonify(MenuItem=[item.serialize])


@app.route('/login/')
def showLogin():
	"""
	Takes no inputs
	Creates an anti-forgery state token
	Returns a login webpage
	"""

	state = ''.join(random.choice(string.ascii_uppercase + string.digits)
		for x in xrange(32))
	login_session['state'] = state
	return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
	"""
	Takes no inputs
	Connects the user through their google
	account.
	Returns an error if one occurs, or a 
	successful login mesage.
	"""

	# Validate state token
	if request.args.get('state') != login_session['state']:
		response = make_response(json.dumps('Invalid state parameter'),
			401)
		response.headers['Content-Type'] = 'application/json'
		return response
	# Obtain authorization code
	id_token = request.data

#	try:
#		# Upgrade code to a credentials object
#		oauth_flow = flow_from_clientsecrets('client_secrets.json',
#			scope='')
#		oauth_flow.redirect_uri = 'postmessage'
#		credentials = oauth_flow.step2_exchange(code)
#
#	except FlowExchangeError:
#		# Upgrade failed
#		response = make_response(json.dumps(
#			'Failed to upgrade the authorization code.'), 401)
#		response.headers['Content-Type'] = 'application/json'
#		return response
#
#	# Check that access token is valid
#	access_token = credentials.access_token
	url = ('https://www.googleapis.com/oauth2/v3/tokeninfo?id_token=%s' 
		% id_token)
	h = httplib2.Http()
	result = json.loads(h.request(url, 'GET')[1])
	print(result)

	# If there was an error, abort.
	if result.get('error') is not None:
		response = make_response(json.dumps(result.get('error')),
			500)
		response.headers['Content-Type'] = 'application/json'
		return response

#	# Verify that the access token is for the intended user
	gplus_id = result['sub']
#	if result['user_id'] != gplus_id:
#		response = make_response(json.dumps(
#			"Token's user ID doesn't match given user ID."), 401)
#		response.headers['Content-Type'] = 'application/json'
#		return response

	# Verify valid access token
	if result['aud'] != CLIENT_ID:
		response = make_response(json.dumps(
			"Token's client ID does not match app's."), 401)
		print "Token's client ID does not match app's."
		response.headers['Content-Type'] = 'application/json'
		return response

	# Access token is good. Check if user is already logged in.
	stored_access_token = login_session.get('access_token')
	stored_gplus_id = login_session.get('gplus_id')
	if stored_access_token is not None and gplus_id == stored_gplus_id:
		response = make_response(json.dumps(
			'Current user is already connected.'), 200)
		response.headers['Content-Type'] = 'application/json'
		return response

	# Login successful. Store access token for later use.
	login_session['access_token'] = id_token
	login_session['gplus_id'] = result['sub']

#	# Get user info
#	userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
#	params = {'access_token': credentials.access_token, 'alt': 'json'}
#	answer = requests.get(userinfo_url, params=params)
#
#	data = answer.json()
#	print(data)

	login_session['username'] = result['given_name']
	login_session['picture'] = result['picture']
	login_session['email'] = result['email']

	# Show welcome message
	output = ''
	output += '<h1>Welcome, '
	output += login_session['username']
	output += '!</h1>'
	output += '<img src="'
	output += login_session['picture']
	output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
	flash("you are now logged in as %s" % login_session['username'])
	print "done!"

	return output


@app.route('/gdisconnect', methods=['POST'])
def gDisconnect():

	# Check if user is actually connected
	access_token = login_session.get('access_token')
	if access_token is None:
		response = make_response(json.dumps(
			'Current user is not logged in.'), 401)
		response.headers['Content-Type'] = 'application/json'
		return response

	# Revoke active token.
#	url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
#	h = httplib2.Http()
#	result = h.request(url, 'GET')[0]
#
#	if result['status'] == '200':
	# Reset the user's session.
	del login_session['access_token']
	del login_session['gplus_id']
	del login_session['username']
	del login_session['picture']
#
	response = make_response(json.dumps('Successfully disconnected'),
			200)
	response.headers['Content-Type'] = 'application/json'
#
	flash('You are now logged out.')
	return response
#
#	# Token was invalid
#	else:
#		response = make_response(json.dumps(
#			'Failed to revoke user token'), 400)
#		response.headers['Content-Type'] = 'application/json'
#		return response



if __name__ == '__main__':
	app.secret_key = 'super_secret_key'
	app.debug = True
	app.run(host = '0.0.0.0', port = 5000)
