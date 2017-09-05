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

# Google OAuth Imports
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError

# Imports from local database_setup.py file
from database_setup import Base
from database_setup import User
from database_setup import Restaurant
from database_setup import MenuItem

# Python core module imports
import string
import random
import json
import httplib2
import os

# Requests import
import requests


# Load Google OAuth client information.
CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']

# Set up Flask for routing
app = Flask(__name__)

# Prep the SQL server
engine = create_engine('sqlite:///restaurantmenuwithusers.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


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
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state

    # Get user info, if available.
    user = login_session.get('username')
    user_id = login_session.get('user_id')
    provider = login_session.get('provider')

    # Get template and pass user info to it.
    return render_template('restaurants.html',
                           restaurants=restaurants, STATE=state, user=user,
                           user_id=user_id, provider=provider)


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
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state

    # Check for user info.
    user = login_session.get('username')
    provider = login_session.get('provider')

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
    return render_template('new_restaurant.html', STATE=state,
                           user=user, provider=provider)


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
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state

    # Check for user info
    user = login_session.get('username')
    user_id = login_session.get('user_id')
    provider = login_session.get('provider')

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
                           STATE=state, user=user, user_id=user_id,
                           provider=provider)


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
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state

    # Check for user info
    user = login_session.get('username')
    user_id = login_session.get('user_id')
    provider = login_session.get('provider')

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
                           STATE=state, user=user, user_id=user_id,
                           provider=provider)


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
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state

    # Check for user info
    user = login_session.get('username')
    user_id = login_session.get('user_id')
    provider = login_session.get('provider')

    # Return menu template with login/welcome bar and lists all menu items of
    # a restaurant, divided by course.
    return render_template('menu.html', restaurant=restaurant,
                           items=items, apps=apps, entrees=entrees,
                           desserts=desserts, bevs=bevs, STATE=state,
                           user=user, user_id=user_id, provider=provider)


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
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state

    # Check for user info
    user = login_session.get('username')
    user_id = login_session.get('user_id')
    provider = login_session.get('provider')

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
                           STATE=state, user=user, user_id=user_id,
                           provider=provider)


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
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state

    # Check for user info
    user = login_session.get('username')
    user_id = login_session.get('user_id')
    provider = login_session.get('provider')

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
                           STATE=state, user=user, user_id=user_id,
                           provider=provider)


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
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state

    # Check for user info
    user = login_session.get('username')
    user_id = login_session.get('user_id')
    provider = login_session.get('provider')

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
                           restaurant=restaurant, STATE=state, user=user,
                           user_id=user_id, provider=provider)


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

    # Validate state token.
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store access token and app information.
    access_token = request.data
    print "access token received %s" % access_token
    app_id = json.loads(open('fb_client_secrets.json',
                             'r').read())['web']['app_id']
    app_secret = json.loads(open('fb_client_secrets.json',
                                 'r').read())['web']['app_secret']

    # Exchange token and client info long-term token
    url = 'https://graph.facebook.com/oauth/access_token?grant_type=' +
    'fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (
        app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Extract token from result
    token = result.split(',')[0].split(':')[1].replace('"', '')

    # Use token to get user info from API
    userinfo_url = 'https://graph.facebook.com/v2.8/me?access_token=' +
    '%s&fields=name,id,email' % token
    result = h.request(userinfo_url, 'GET')[1]
    data = json.loads(result)

    # Get user picture from Facebook
    pic_url = 'https://graph.facebook.com/v2.8/' +
    '%s/picture?redirect=0&height=200&width=200' % data["id"]
    result = h.request(pic_url, 'GET')[1]
    pic_data = json.loads(result)

    # Store everything in the login session.
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]
    login_session['picture'] = pic_data["data"]["url"]

    # Check if user is currently in database
    user_id = getUserID(login_session['email'])

    # If user is not in database, add user.
    if user_id is None:
        user_id = createUser(login_session)

    # Store user id in login session.
    login_session['user_id'] = user_id

    # Send response to ajax
    response = make_response(json.dumps('Login successful'), 200)
    response.headers['Content-Type'] = 'application/json'
    return response


# Route for Google Plus Login
@app.route('/gconnect', methods=['POST'])
def gconnect():
    """
    Takes no inputs
    Validates state token and exchanges access token for
    user information.
    Outputs an error if one occurs, or a successful login mesage.
    """

    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Obtain authorization code
    id_token = request.data
    url = ('https://www.googleapis.com/oauth2/v3/tokeninfo?id_token=%s'
           % id_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])

    # If there was an error, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store gplus id from result
    gplus_id = result['sub']

    # Verify valid access token
    if result['aud'] != CLIENT_ID:
        response = make_response(json.dumps(
            "Token's client ID does not match app's."), 401)
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

    # Store user information in login_session.
    login_session['provider'] = 'google'
    login_session['gplus_id'] = result['sub']
    login_session['username'] = result['given_name']
    login_session['picture'] = result['picture']
    login_session['email'] = result['email']

    # Check if user is currently in database
    user_id = getUserID(login_session['email'])

    # If user is not in database, add user.
    if user_id is None:
        user_id = createUser(login_session)

    # Store user id in login session.
    login_session['user_id'] = user_id

    # Send response to ajax
    response = make_response(json.dumps('Login successful'), 200)
    response.headers['Content-Type'] = 'application/json'
    return response


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

    # Check that user is actually logged in
    if 'provider' in login_session:
        # Check for google login, disconnect from google if true
        if login_session['provider'] == 'google':
            gDisconnect()
            del login_session['gplus_id']

        # Check for facebook login, disconnect from facebook if true
        if login_session['provider'] == 'facebook':
            fbDisconnect()
            del login_session['facebook_id']

        # Clear user info from login_session
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']

        flash("You have successfully been logged out.")

        # Redirect user to landing page.
        return redirect(url_for('showRestaurants'))

    # User is not logged in -- redirect to landing page.
    else:
        flash("Logout failed -- you weren't logged in.")
        return redirect(url_for('showRestaurants'))


# Route for Facebook Disconnect
@app.route('/fbdisconnect', methods=['POST'])
def fbDisconnect():
    """
    Takes no inputs
    Revokes Facebook access token
    Returns a response object on success
    """

    # Send access token revocation to Facebook
    facebook_id = login_session['facebook_id']
    url = 'https://graph.facebook.com/%s/permissions' % facebook_id
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]

    # Return a response object
    response = make_response(json.dumps('Successfully disconnected'), 200)
    response.headers['Content-Type'] = 'application/json'

    return response


# Route for Google Disconnect
@app.route('/gdisconnect', methods=['POST'])
def gDisconnect():
    """
    Takes no inputs
    Checks if user was logged in with google and throws an error if not
    Returns a response object
    """

    # Check if user is actually connected
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(json.dumps(
            'Current user is not logged in.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Sends the OK to ajax, triggering disconnection on client-side javascript.
    response = make_response(json.dumps('Successfully disconnected'), 200)
    response.headers['Content-Type'] = 'application/json'

    return response


# User Helper functions:
def createUser(login_session):
    """
    Takes login_session (dict) as input
    Uses information in the login_session to add a new user to the
    User database.
    Gets newly added user from the database.
    Outputs the user ID
    """

    # Create new user based on login sesssion information
    newUser = User(name=login_session['username'],
                   email=login_session['email'],
                   picture=login_session['picture'])
    session.add(newUser)
    session.commit()

    # Gets newly added user from the database
    user = session.query(User).filter_by(email=login_session['email']).one()

    # Returns user ID
    return user.id


def getUserInfo(user_id):
    """
    Takes user ID (int) as input
    Gets user by ID
    Outputs user object
    """

    # Get user by ID and return
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    """
    Takes user email (str) as input.
    If user is in the database, outputs user id.
    If not, outputs None.
    """

    try:
        # Get user from database by email and return user id
        user = session.query(User).filter_by(
            email=login_session['email']).one()
        return user.id
    except:
        # User not found. Return none.
        return None


# Server is being run -- send host and port info.
if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
