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
from flask import jsonify
from flask import session as login_session

# Python core module imports
import os

# Local module imports
from mod_auth import *
from mod_crud import *


# Set up Flask for routing
app = Flask(__name__)


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
    restaurants = readRest()

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

    if request.method == 'POST':
        return createRest(request, login_session)
        
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
    restaurant = readRest(restaurant_id=restaurant_id)

    # Generate and store a state token
    state = makeState(login_session)

    # If a post request is received...
    if request.method == 'POST':
        return updateRest(request, login_session, restaurant)

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
    restaurant = readRest(restaurant_id=restaurant_id)

    # Generate and store a state token
    state = makeState(login_session)

    # If a post request is received...
    if request.method == 'POST':
        # Delete restaurant from the database
        return deleteRest(login_session, restaurant)

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
    restaurant = readRest(restaurant_id=restaurant_id)

    # Get menu items by restaurant ID
    items = readMenu(restaurant_id=restaurant_id)

    # Generate and store a state token.
    state = makeState(login_session)

    # Return menu template with login/welcome bar and lists all menu items of
    # a restaurant, divided by course.
    return render_template('menu.html', restaurant=restaurant,
                           items=items, STATE=state)


# Route for adding a new menu item
@app.route('/restaurants/<int:restaurant_id>/new/',
           methods=['GET', 'POST'])
def newMenuItem(restaurant_id):
    """
    Takes a restaurant id (int) as input.
    Gets a restaurant by id.
    Stores a state token for potential login.\
    Accepts post requests that add a menu item to the selected restaurant.
    Outputs a template with a login/welcome bar and a form for adding
    a new menu item to a restaurant.
    """

    # Get a restaurant by ID
    restaurant = readRest(restaurant_id=restaurant_id)

    # Generate a state token and store it
    state = makeState(login_session)

    # If a post request is received...
    if request.method == 'POST':
        # Create a new menu item based on form input
        return createItem(request, login_session, restaurant_id)

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
    restaurant = readRest(restaurant_id=restaurant_id)
    item = readMenu(menu_id=menu_id)

    # Generate and store a state token
    state = makeState(login_session)

    # If a post request is received...
    if request.method == 'POST':
        # Update selected menu item based on form inputs
        return updateItem(request, login_session, item)

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
    restaurant = readRest(restaurant_id=restaurant_id)
    item = readMenu(menu_id=menu_id)

    # Generate and store a state token
    state = makeState(login_session)

    # If a post request is received...
    if request.method == 'POST':
        # Delete the selected menu item
        return deleteItem(login_session, item)

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
    restaurants = readRest()

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

    # Get menu items by restaurant id.
    items = readMenu(restaurant_id=restaurant_id, combined=True)

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

    # Get remenu item by id
    item = readMenu(menu_id=menu_id)

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
