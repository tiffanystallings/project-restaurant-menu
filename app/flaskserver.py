#!/usr/bin/env python2
#
# flaskserver.py
# Restaurant Menu Project

"""
Initiates a web server that hosts URIs for a restaurant menu application
and accepts post requests that handle user logins and CRUD operations
on the database.
"""

# Flask Imports
from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import flash
from flask import jsonify
from flask import make_response
from flask import session as login_session

# SQL Alchemy Imports
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Imports from local database_setup.py file
from database_setup import Base
from database_setup import User
from database_setup import Restaurant
from database_setup import MenuItem

# Python core module imports
import json
import httplib2
import os

# Requests import
import requests

# Local module imports
from mod_auth import *


# Set up Flask for routing
app = Flask(__name__)

# Prep the SQL server
engine = create_engine('sqlite:///restaurantmenuwithusers.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Inject user info into all templates.
@app.context_processor
def injectUser():
    return dict(user = login_session.get('username'),
                user_id=login_session.get('user_id'),
                provider=login_session.get('provider'))


# Landing page route
@app.route('/')
@app.route('/restaurants/')
def showRestaurants():
    """
    Takes no inputs.
    Gets all restaurants from database.
    Creates a state token for potetial user login.
    Checks for user info.
    Outputs a template utilizing user info to welcome user and lists
    all restaurants in database.
    """

    # Get all restaurants.
    restaurants = session.query(Restaurant).all()

    # Store a state token
    state = makeState(login_session)

    # Get template and pass user info to it.
    return render_template('restaurants.html',
                           restaurants=restaurants, STATE=state)


# Add New Restaurant route
@app.route('/restaurants/new', methods=['GET', 'POST'])
def newRestaurant():
    """
    Takes no inputs.
    Stores a state token for potential user login.
    Checks for user info.
    Accepts post request, which creates a new restaurant
    in the database.
    Outputs a template that welcomes the user based on user info,
    and provides a form for adding new restaurants.
    """

    # Create and store a state token.
    state = makeState(login_session)

    # If a post request is received...
    if request.method == 'POST':
        # Create a new restaurant in the database.
        newRest = Restaurant(name=request.form['name'],
                             user_id=login_session['user_id'])

        session.add(newRest)
        session.commit()
        flash('Restaurant created successfully!')

        # Return to restaurants page.
        return redirect(url_for('showRestaurants'))

    # Get template and pass in user info
    return render_template('new_restaurant.html', STATE=state)


# Route for editing a restaurant
@app.route('/restaurants/<int:restaurant_id>/edit/',
           methods=['GET', 'POST'])
def editRestaurant(restaurant_id):
    """
    Takes a resaurant ID (int) as input.
    Gets a restaurant by ID.
    Creates a state token for potential user login.
    Checks for user info.
    Accepts post requests to edit a restaurant.
    Outputs a form template that uses user info to welcome users,
    and provides a form to edit restaurants.
    """

    # Get restaurant from database by ID
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()

    # Generate and store a state token
    state = makeState(login_session)

    # If a post request is received...
    if request.method == 'POST':
        # Change the restaurant's name according to the form submission
        restaurant.name = request.form['name']

        session.add(restaurant)
        session.commit()
        flash('Restaurant edited successfully!')

        # Redirect user to landing page.
        return redirect(url_for('showRestaurants'))

    # Pass in user info for login bar, and restaurant info for form template
    return render_template('edit_restaurant.html', restaurant=restaurant,
                           STATE=state)


# Route for deleting a restaurant.
@app.route('/restaurants/<int:restaurant_id>/delete/',
           methods=['GET', 'POST'])
def deleteRestaurant(restaurant_id):
    """
    Takes a restaurant ID (int) as input.
    Creates a state token to allow potential user login.
    Checks user info to welcome user.
    Accepts post requests to delete a restaurant.
    Outputs a template with a login/welcome bar and a form to confirm
    deletion of the restaurant.
    """

    # Get restaurant by ID
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()

    # Generate and store a state token
    state = makeState(login_session)

    # If a post request is received...
    if request.method == 'POST':
        # Delete restaurant from the database
        session.delete(restaurant)
        session.commit()
        flash('Restaurant deleted successfully!')

        # Redirect user to landing page
        return redirect(url_for('showRestaurants'))

    # Get template for deleting restaurant, pass in restaurant and user info
    return render_template('delete_restaurant.html', restaurant=restaurant,
                           STATE=state)


# Route for showing a restaurant's menu
@app.route('/restaurants/<int:restaurant_id>/')
def showMenuItems(restaurant_id):
    """
    Takes a restaurant id (int) as input.
    Gets a restaurant by id, and gets menu items linked to that restaurent.
    Splits menu items by course.
    Generates and stores a state token for potential user login.
    Checks for user info to welcome user.
    Outputs a page with a login/welcome bar and a list of a restaurant's
    menu items divided by course.
    """

    # Get restaurant by id
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()

    # Get menu items by id (used to check if a restaurant has added any menu
    # items yet inside the template.)
    items = session.query(MenuItem).filter_by(
        restaurant_id=restaurant.id).all()

    # Get menu items by restaurant ID and by course.
    apps = session.query(MenuItem).filter_by(
        restaurant_id=restaurant.id, course='Appetizer').all()
    entrees = session.query(MenuItem).filter_by(
        restaurant_id=restaurant.id, course='Entree').all()
    desserts = session.query(MenuItem).filter_by(
        restaurant_id=restaurant.id, course='Dessert').all()
    bevs = session.query(MenuItem).filter_by(
        restaurant_id=restaurant.id, course='Beverage').all()

    # Generate and store a state token.
    state = makeState(login_session)

    # Return menu template with login/welcome bar and lists all menu items of
    # a restaurant, divided by course.
    return render_template('menu.html', restaurant=restaurant,
                           items=items, apps=apps, entrees=entrees,
                           desserts=desserts, bevs=bevs, STATE=state)


# Route for adding a new menu item
@app.route('/restaurants/<int:restaurant_id>/new/',
           methods=['GET', 'POST'])
def newMenuItem(restaurant_id):
    """
    Takes a restaurant id (int) as input.
    Gets a restaurant by id.
    Stores a state token for potential login.
    Checks for user info to welcome user.
    Accepts post requests that add a menu item to the selected restaurant.
    Outputs a template with a login/welcome bar and a form for adding
    a new menu item to a restaurant.
    """

    # Get a restaurant by ID
    restaurant = session.query(Restaurant).filter_by(
        id=restaurant_id).one()

    # Generate a state token and store it
    state = makeState(login_session)

    # If a post request is received...
    if request.method == 'POST':
        # Create a new menu item based on form input
        newItem = MenuItem(
            name=request.form['name'],
            course=request.form['course'],
            price=request.form['price'],
            description=request.form['description'],
            restaurant=restaurant,
            restaurant_id=restaurant_id,
            user_id=restaurant.user_id)

        session.add(newItem)
        session.commit()
        flash('New menu item created!')

        # Redirect user to the menu page
        return redirect(url_for('showMenuItems',
                                restaurant_id=restaurant_id))

    # Return a page with a login/welcome bar and a form to add a
    # new menu item to the selected restaurant.
    return render_template('new_item.html', restaurant=restaurant,
                           STATE=state)


# Route for editing a menu item.
@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/edit/',
           methods=['GET', 'POST'])
def editMenuItem(restaurant_id, menu_id):
    """
    Takes two inputs: a restaurant id (int), and a menu item id (int)
    Gets a restaurant and menu item by their ids.
    Generates a state token for potential user login.
    Checks for user info.
    Accepts post requests that update the selected menu item.
    Outputs a page with login/welcome bar and a form for editing a
    restaurant menu item.
    """

    # Get restaurant and menu item by ID.
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    item = session.query(MenuItem).filter_by(id=menu_id).one()

    # Generate and store a state token
    state = makeState(login_session)

    # If a post request is received...
    if request.method == 'POST':
        # Update selected menu item based on form inputs
        item.name = request.form['name']
        item.course = request.form['course']
        item.price = request.form['price']
        item.description = request.form['description']

        session.add(item)
        session.commit()
        flash('Menu item edited successfully!')

        # Redirect user to menu page
        return redirect(url_for('showMenuItems',
                                restaurant_id=restaurant_id))

    # Return a page with a login/welcome bar and a form for editing the
    # selected menu item.
    return render_template('edit_item.html', restaurant=restaurant, item=item,
                           STATE=state)


# Route for deleting a menu item.
@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/delete/',
           methods=['GET', 'POST'])
def deleteMenuItem(restaurant_id, menu_id):
    """
    Takes two inputs: A restaurant ID (int) and a menu item ID (int)
    Gets a restaurant and menu item by their IDs.
    Generates a state token for potential user login.
    Checks for user info to welcome user
    Accepts posts requests that delete the selected menu item.
    Outputs a page with a login/welcome bar and a form for deleting
    the selected menu item.
    """

    # Get restaurant and menu item by IDs
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    item = session.query(MenuItem).filter_by(id=menu_id).one()

    # Generate and store a state token
    state = makeState(login_session)

    # If a post request is received...
    if request.method == 'POST':
        # Delete the selected menu item
        session.delete(item)
        session.commit()
        flash('Menu item deleted successfully!')

        # Redirect user to the menu page
        return redirect(url_for('showMenuItems',
                                restaurant_id=restaurant_id))

    # Return a page with a login/welcome bar and a form for deleting the
    # selected menu item.
    return render_template('delete_item.html', item=item,
                           restaurant=restaurant, STATE=state)


# JSON API endpoint route to list all restaurants.
@app.route('/restaurants/JSON')
def restaurantsJSON():
    """
    Takes no inputs
    Gets all restaurants
    Outputs a JSON of all restaurants
    """

    # Get all restaurants
    restaurants = session.query(Restaurant).all()

    # Return a JSON object by iterating through the restaurants object
    return jsonify(Restaurants=[i.serialize for i in restaurants])


# JSON API endpoint to list a restaurant's menu
@app.route('/restaurants/<int:restaurant_id>/JSON')
def restaurantMenuJSON(restaurant_id):
    """
    Takes a restaurant id (int) as input.
    Gets restaurant and menu items by restaurant id.
    Outputs a JSON of all menu items at selected restaurant.
    """

    # Get restaurant by ID, get menu items by restaurant id.
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    items = session.query(MenuItem).filter_by(
        restaurant_id=restaurant_id).all()

    # Return a JSON by iterating though items
    return jsonify(MenuItems=[i.serialize for i in items])


# JSON API endpoint to view a specific menu item details
@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/JSON')
def menuItemJSON(restaurant_id, menu_id):
    """
    Takes two inputs: a restaurant id (int) and a menu item id (int)
    Gets restaurant and menu item by their ids
    Outputs a JSON of the details of the selected menu item
    """

    # Get restaurant and menu item by id
    restaurant = session.query(Restaurant).filter_by(
        id=restaurant_id).one()
    item = session.query(MenuItem).filter_by(id=menu_id).one()

    # Return a JSON of the menu item details
    return jsonify(MenuItem=[item.serialize])


# Route for Facebook Login
@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    """
    Takes no inputs
    Validates state token and exchanges the short term
    access token for the long term access token. Uses that
    token to access user information.
    Outputs a response object, either error or success.
    """

    return fbauth(request, login_session)


# Route for Google Plus Login
@app.route('/gconnect', methods=['POST'])
def gconnect():
    """
    Takes no inputs
    Validates state token and exchanges access token for
    user information.
    Outputs an error if one occurs, or a successful login mesage.
    """

    return gauth(request, login_session)


# Route for disconnecting user
@app.route('/disconnect', methods=['POST'])
def disconnect():
    """
    Takes no inputs.
    Checks which provider user is logged in with and processes
    disconnection accordingly.
    Clears user info from login_session.
    Returns a redirect response object and flash message
    """

    return clearSession(login_session)


# Server is being run -- send host and port info.
if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    port = int(os.environ.get("PORT", 5000))
    app.debug = True
    app.run(host='0.0.0.0', port=port)
