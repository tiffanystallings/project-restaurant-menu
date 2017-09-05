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
from database_setup import User
from database_setup import Restaurant
from database_setup import MenuItem

import string
import random
import json
import httplib2
import os

import requests

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']

app = Flask(__name__)

engine = create_engine('sqlite:///restaurantmenuwithusers.db')
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
    user_id = login_session.get('user_id')
    provider = login_session.get('provider')

    return render_template('restaurants.html',
                           restaurants=restaurants, STATE=state, user=user,
                           user_id=user_id, provider=provider)


@app.route('/restaurants/new', methods=['GET', 'POST'])
def newRestaurant():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state

    user = login_session.get('username')
    provider = login_session.get('provider')

    if request.method == 'POST':
        newRest = Restaurant(name=request.form['name'],
                             user_id=login_session['user_id'])

        session.add(newRest)
        session.commit()
        flash('Restaurant created successfully!')

        return redirect(url_for('showRestaurants'))

    return render_template('new_restaurant.html', STATE=state,
                           user=user, provider=provider)


@app.route('/restaurants/<int:restaurant_id>/edit/',
           methods=['GET', 'POST'])
def editRestaurant(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()

    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state

    user = login_session.get('username')
    user_id = login_session.get('user_id')
    provider = login_session.get('provider')

    if request.method == 'POST':
        restaurant.name = request.form['name']

        session.add(restaurant)
        session.commit()
        flash('Restaurant edited successfully!')

        return redirect(url_for('showRestaurants'))

    return render_template('edit_restaurant.html', restaurant=restaurant,
                           STATE=state, user=user, user_id=user_id,
                           provider=provider)


@app.route('/restaurants/<int:restaurant_id>/delete/',
           methods=['GET', 'POST'])
def deleteRestaurant(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()

    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state

    user = login_session.get('username')
    user_id = login_session.get('user_id')
    provider = login_session.get('provider')

    if request.method == 'POST':
        session.delete(restaurant)
        session.commit()
        flash('Restaurant deleted successfully!')

        return redirect(url_for('showRestaurants'))

    return render_template('delete_restaurant.html', restaurant=restaurant,
                           STATE=state, user=user, user_id=user_id,
                           provider=provider)


@app.route('/restaurants/<int:restaurant_id>/')
def showMenuItems(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    items = session.query(MenuItem).filter_by(
        restaurant_id=restaurant.id).all()
    apps = session.query(MenuItem).filter_by(
        restaurant_id=restaurant.id, course='Appetizer').all()
    entrees = session.query(MenuItem).filter_by(
        restaurant_id=restaurant.id, course='Entree').all()
    desserts = session.query(MenuItem).filter_by(
        restaurant_id=restaurant.id, course='Dessert').all()
    bevs = session.query(MenuItem).filter_by(
        restaurant_id=restaurant.id, course='Beverage').all()

    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state

    user = login_session.get('username')
    user_id = login_session.get('user_id')
    provider = login_session.get('provider')

    return render_template('menu.html', restaurant=restaurant,
                           items=items, apps=apps, entrees=entrees,
                           desserts=desserts, bevs=bevs, STATE=state,
                           user=user, user_id=user_id, provider=provider)


@app.route('/restaurants/<int:restaurant_id>/new/',
           methods=['GET', 'POST'])
def newMenuItem(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(
        id=restaurant_id).one()

    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state

    user = login_session.get('username')
    user_id = login_session.get('user_id')
    provider = login_session.get('provider')

    if request.method == 'POST':
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

        return redirect(url_for('showMenuItems',
                                restaurant_id=restaurant_id))

    return render_template('new_item.html', restaurant=restaurant,
                           STATE=state, user=user, user_id=user_id,
                           provider=provider)


@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/edit/',
           methods=['GET', 'POST'])
def editMenuItem(restaurant_id, menu_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    item = session.query(MenuItem).filter_by(id=menu_id).one()

    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state

    user = login_session.get('username')
    user_id = login_session.get('user_id')
    provider = login_session.get('provider')

    if request.method == 'POST':
        item.name = request.form['name']
        item.course = request.form['course']
        item.price = request.form['price']
        item.description = request.form['description']

        session.add(item)
        session.commit()
        flash('Menu item edited successfully!')

        return redirect(url_for('showMenuItems',
                                restaurant_id=restaurant_id))

    return render_template('edit_item.html', restaurant=restaurant, item=item,
                           STATE=state, user=user, user_id=user_id,
                           provider=provider)


@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/delete/',
           methods=['GET', 'POST'])
def deleteMenuItem(restaurant_id, menu_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    item = session.query(MenuItem).filter_by(id=menu_id).one()

    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state

    user = login_session.get('username')
    user_id = login_session.get('user_id')
    provider = login_session.get('provider')

    if request.method == 'POST':
        session.delete(item)
        session.commit()
        flash('Menu item deleted successfully!')

        return redirect(url_for('showMenuItems',
                                restaurant_id=restaurant_id))

    return render_template('delete_item.html', item=item,
                           restaurant=restaurant, STATE=state, user=user,
                           user_id=user_id, provider=provider)


@app.route('/restaurants/JSON')
def restaurantsJSON():
    restaurants = session.query(Restaurant).all()

    return jsonify(Restaurants=[i.serialize for i in restaurants])


@app.route('/restaurants/<int:restaurant_id>/JSON')
def restaurantMenuJSON(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    items = session.query(MenuItem).filter_by(
        restaurant_id=restaurant_id).all()

    return jsonify(MenuItems=[i.serialize for i in items])


@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/JSON')
def menuItemJSON(restaurant_id, menu_id):
    restaurant = session.query(Restaurant).filter_by(
        id=restaurant_id).one()
    item = session.query(MenuItem).filter_by(id=menu_id).one()

    return jsonify(MenuItem=[item.serialize])


@app.route('/fbconnect', methods=['POST'])
def fbconnect():

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

#   Store gplus id from result
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


@app.route('/disconnect', methods=['POST'])
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gDisconnect()
            del login_session['gplus_id']

        if login_session['provider'] == 'facebook':
            fbDisconnect()
            del login_session['facebook_id']

        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']

        flash("You have successfully been logged out.")
        return redirect(url_for('showRestaurants'))

    else:
        flash("Logout failed -- you weren't logged in.")
        return redirect(url_for('showRestaurants'))


@app.route('/fbdisconnect', methods=['POST'])
def fbDisconnect():
    facebook_id = login_session['facebook_id']
    url = 'https://graph.facebook.com/%s/permissions' % facebook_id
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]

    response = make_response(json.dumps('Successfully disconnected'), 200)
    response.headers['Content-Type'] = 'application/json'

    return response


@app.route('/gdisconnect', methods=['POST'])
def gDisconnect():

    # Check if user is actually connected
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(json.dumps(
            'Current user is not logged in.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    response = make_response(json.dumps('Successfully disconnected'), 200)
    response.headers['Content-Type'] = 'application/json'

    return response


def createUser(login_session):
    newUser = User(name=login_session['username'],
                   email=login_session['email'],
                   picture=login_session['picture'])
    session.add(newUser)
    session.commit()

    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(
            email=login_session['email']).one()
        return user.id
    except:
        return None


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
