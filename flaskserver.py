from flask import Flask, render_template, request, redirect, url_for
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

app = Flask(__name__)

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/restaurants/<int:restaurant_id>/')
def showMenuItems(restaurant_id):
	restaurant = session.query(Restaurant).filter_by(
		id=restaurant_id).one()
	items = session.query(MenuItem).filter_by(restaurant_id =
		restaurant.id)
	
	return render_template('menu.html', restaurant=restaurant,
		items=items)


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

		return redirect(url_for('showMenuItems',
			restaurant_id = restaurant_id))
		
	return render_template('delete_item.html', item=item)

if __name__ == '__main__':
	app.debug = True
	app.run(host = '0.0.0.0', port = 5000)