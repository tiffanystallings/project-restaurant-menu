#!/usr/bin/env python2
#
# database_setup.py
# Restaurant Menu Project

"""
Establishes a database with tables for Users, Restaurants, and MenuItems
Class declarations extend the SQL Alchemy declarative_base to allow for the
easy creation of new rows in the database.
"""

# Standard Library imports
import sys

# SQL Alchemy imports
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

from flask import Flask
from flask_sqlalchemy import SQLAlchemy


# Store declarative_base for easy referencing
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///restaurantmenuwithusers.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class User(db.Model):
    """
    Extends Base
    Establishes the user table
    Stores user's name, id, email, and picture.
    """
    __tablename__ = 'user'
    name = db.Column(db.String(80), nullable=False)
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(250))
    picture = db.Column(db.String(250))


class Restaurant(db.Model):
    """
    Extends Base
    Establishes restaurant table
    Stores restaurant name, id, and user_id of the user who
    created the restaurant.
    """
    __tablename__ = 'restaurant'
    name = db.Column(db.String(80), nullable=False)
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship(User)

    # Serialize table for JSON API endpoint
    @property
    def serialize(self):
        """
        Takes self as input.
        Outputs a dictionary containing restaurant name and id.
        """
        return {
            'name': self.name,
            'id': self.id
        }


class MenuItem(db.Model):
    """
    Extends Base
    Establishes menu_item table
    Stores menu item name, id, course, description, price,
    id of the restaurant it's linked to, and the id of the user
    who created it.
    """
    __tablename__ = 'menu_item'
    name = db.Column(db.String(80), nullable=False)
    id = db.Column(db.Integer, primary_key=True)
    course = db.Column(db.String(250))
    description = db.Column(db.String(250))
    price = db.Column(db.String(8))
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurant.id'))
    restaurant = db.relationship(Restaurant)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship(User)

    # Serialize table for JSON API endpoint
    @property
    def serialize(self):
        """
        Takes self as input
        Outputs a dictionary storing the menu item information
        """
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'course': self.course,
            'restaurant_id': self.restaurant_id
        }

