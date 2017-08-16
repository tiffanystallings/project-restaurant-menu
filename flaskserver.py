from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask import session as login_session

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, Restaurant, MenuItem

import string, random

app = Flask(__name__)

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/')
@app.route('/restaurants/')
def showRestaurants():
	restaurants = session.query(Restaurant).all()

	return render_template('restaurants.html', restaurants=restaurants)


@app.route('/restaurants/new', 
	methods=['GET', 'POST'])
def newRestaurant():
	if request.method == 'POST':
		newRest = Restaurant(
			name = request.form['name'])

		session.add(newRest)
		session.commit()
		flash('Restaurant created successfully!')

		return redirect(url_for('showRestaurants'))

	return render_template('new_restaurant.html')


@app.route('/restaurants/<int:restaurant_id>/edit/',
	methods=['GET', 'POST'])
def editRestaurant(restaurant_id):
	restaurant = session.query(Restaurant).filter_by(
		id=restaurant_id).one()

	if request.method == 'POST':
		restaurant.name = request.form['name']

		session.add(restaurant)
		session.commit()
		flash('Restaurant edited successfully!')

		return redirect(url_for('showRestaurants'))

	return render_template('edit_restaurant.html', restaurant=restaurant)


@app.route('/restaurants/<int:restaurant_id>/delete/',
	methods=['GET', 'POST'])
def deleteRestaurant(restaurant_id):
	restaurant = session.query(Restaurant).filter_by(
		id=restaurant_id).one()

	if request.method == 'POST':
		session.delete(restaurant)
		session.commit()
		flash('Restaurant deleted successfully!')

		return redirect(url_for('showRestaurants'))
	return render_template('delete_restaurant.html', restaurant=restaurant)


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
	
	return render_template('menu.html', restaurant=restaurant,
		items=items, apps=apps, entrees=entrees, desserts=desserts, bevs=bevs)


@app.route('/restaurants/<int:restaurant_id>/new/',
	methods=['GET', 'POST'])
def newMenuItem(restaurant_id):
	restaurant = session.query(Restaurant).filter_by(
		id=restaurant_id).one()

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

	return render_template('new_item.html', restaurant=restaurant)


@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/edit/',
	methods=['GET', 'POST'])
def editMenuItem(restaurant_id, menu_id):
	restaurant = session.query(Restaurant).filter_by(
		id=restaurant_id).one()

	item = session.query(MenuItem).filter_by(
		 id=menu_id).one()

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

	return render_template('edit_item.html', restaurant=restaurant, item=item)


@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/delete/',
	methods=['GET', 'POST'])
def deleteMenuItem(restaurant_id, menu_id):
	restaurant = session.query(Restaurant).filter_by(
		id=restaurant_id).one()

	item = session.query(MenuItem).filter_by(
		 id=menu_id).one()

	if request.method == 'POST':
		session.delete(item)
		session.commit()
		flash('Menu item deleted successfully!')

		return redirect(url_for('showMenuItems',
			restaurant_id = restaurant_id))

	return render_template('delete_item.html', item=item)


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
	state = ''.join(random.choice(string.ascii_uppercase + string.digits)
		for x in xrange(32))
	login_session['state'] = state
	return 'The current session state is %s' % login_session['state']


if __name__ == '__main__':
	app.secret_key = 'super_secret_key'
	app.debug = True
	app.run(host = '0.0.0.0', port = 5000)
