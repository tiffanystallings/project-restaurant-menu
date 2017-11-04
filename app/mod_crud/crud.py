# /app/mod_crud/crud.py

"""
Crud functionality handlers for the restaurant menu
application. Certain functions are protected by a login
requirement, so no user by the object's creator can
make changes.

User ID 2 (the second user created on the server after
the dummy user), acts as a Moderator and can edit any
content as they see fit.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from flask import flash
from flask import redirect
from flask import url_for
from flask import make_response

from models import db
from models import Restaurant
from models import MenuItem

import json



# Store declarative_base for easy referencing
# app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///restaurantmenuwithusers.db'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# db = SQLAlchemy(app)

# Create functions
def createRest(request, login_session):
    """
    Takes request object and login session object as inputs
    Checks for user login
    Returns an error if a user is not logged in
    Adds a restaurant to the database if user is logged in
    Returns a redirect to the main restaurants page.
    """
    # Check that user is logged in.
    if login_session.get('user_id') is not None:
        # Create a new restaurant in the database.
        newRest = Restaurant(name=request.form['name'],
                             user_id=login_session['user_id'])

        db.session.add(newRest)
        db.session.commit()

        flash('Restaurant created successfully!')

        return redirect(url_for('showRestaurants'))

    # User is not logged in. Send an error.
    else:
        response = make_response(json.dumps('Unauthorized access'), 401)
        return response


def createItem(request, login_session, restaurant):
    """
    Takes request and login session objects and
    a restaurant object as inputs
    Checks for user login
    If user is not logged in, respond with an error
    Adds a menu item to the database
    Returns a redirect to the menu page
    """

    # Check if user is authorized.
    if (restaurant.user_id == login_session['user_id'] or
            login_session['user_id'] == 2):
        # If so, add the menu item.
        newItem = MenuItem(
            name=request.form['name'],
            course=request.form['course'],
            price=request.form['price'],
            description=request.form['description'],
            restaurant=restaurant,
            restaurant_id=restaurant.id,
            user_id=login_session['user_id'])

        db.session.add(newItem)
        db.session.commit()
        flash('New menu item created!')

        # Redirect user to the menu page
        return redirect(url_for('showMenuItems',
                                restaurant_id=restaurant.id))

    # User is not logged in. Send an error.
    else:
        response = make_response(json.dumps('Unauthorized access'), 401)
        return response


# Read functions
def readRest(restaurant_id=None):
    """
    If called without inputs, returns all restaurant objects.
    If query is passed an ID integer, it will search the
    database for a restaurant by that ID and return that object.
    """
    if restaurant_id is None:
        return db.session.query(Restaurant).all()

    else:
        return db.session.query(Restaurant).filter_by(id=restaurant_id).one()


def readMenu(restaurant_id=None, menu_id=None, combined=False):
    """
    If called with a restaurant ID, returns a dictionary
    object that contains a restaurant menu sorted by course.
    Also includes a count of all menu items.
    If called with a restaurant ID and combined as True, returns
    a full list of all menu items at a restaurant.
    If called with a menu ID, returns a single menu item object.
    Returns None with no inputs.
    """
    if restaurant_id is not None and not combined:
        items = {
            'apps': session.query(MenuItem).filter_by(
                restaurant_id=restaurant_id, course='Appetizer').all(),
            'entrees': session.query(MenuItem).filter_by(
                restaurant_id=restaurant_id, course='Entree').all(),
            'desserts': session.query(MenuItem).filter_by(
                restaurant_id=restaurant_id, course='Dessert').all(),
            'bevs': session.query(MenuItem).filter_by(
                restaurant_id=restaurant_id, course='Beverage').all()
        }

        total = sum(len(v) for v in items.itervalues())
        items['total'] = total

        return items

    if restaurant_id is not None and combined:
        return db.session.query(MenuItem).filter_by(
            restaurant_id=restaurant_id).all()

    if menu_id is not None:
        return db.session.query(MenuItem).filter_by(id=menu_id).one()

    else:
        return None


# Update functions
def updateRest(request, login_session, restaurant):
    """
    Takes request, login_session, and restaurant objects
    as inputs. Checks that user is authorized to edit restaurant.
    Outputs a redirect on success, or an error on failure.
    """

    if (restaurant.user_id == login_session['user_id'] or
            login_session['user_id'] == 2):
        # Change the restaurant's name according to the form submission
        restaurant.name = request.form['name']

        db.session.add(restaurant)
        db.session.commit()
        flash('Restaurant edited successfully!')

        # Redirect user to landing page.
        return redirect(url_for('showRestaurants'))
    else:
        response = make_response(json.dumps('Unauthorized access'), 401)
        return response


def updateItem(request, login_session, item):
    if (item.user_id == login_session['user_id'] or
            login_session['user_id'] == 2):

        # Update selected menu item based on form inputs
        item.name = request.form['name']
        item.course = request.form['course']
        item.price = request.form['price']
        item.description = request.form['description']

        db.session.add(item)
        db.session.commit()
        flash('Menu item edited successfully!')

        # Redirect user to menu page
        return redirect(url_for('showMenuItems',
                                restaurant_id=item.restaurant_id))

    else:
        response = make_response(json.dumps('Unauthorized access'), 401)
        return response


# Delete functions
def deleteRest(login_session, restaurant):
    if (restaurant.user_id == login_session['user_id'] or
            login_session['user_id'] == 2):
        # SQLite doesn't auto-increment by default.
        # Working around this by deleting all menu items
        # assigned to a restaurant when
        # restaurant is deleted.
        items = readMenu(restaurant_id=restaurant.id, combined=True)
        for item in items:
            db.session.delete(item)
            db.session.commit()

        # Delete restaurant from the database
        db.session.delete(restaurant)
        db.session.commit()
        flash('Restaurant deleted successfully!')

        # Redirect user to landing page
        return redirect(url_for('showRestaurants'))

    else:
        response = make_response(json.dumps('Unauthorized access'), 401)
        return response


def deleteItem(login_session, item):
    if (item.user_id == login_session['user_id'] or
            login_session['user_id'] == 2):
        # Delete restaurant from the database
        db.session.delete(item)
        db.session.commit()
        flash('Menu item deleted successfully!')

        # Redirect user to landing page
        return redirect(url_for('showMenuItems',
                                restaurant_id=item.restaurant_id))

    else:
        response = make_response(json.dumps('Unauthorized access'), 401)
        return response
