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


# Store declarative_base for easy referencing
Base = declarative_base()


class User(Base):
    """
    Extends Base
    Establishes the user table
    Stores user's name, id, email, and picture.
    """
    __tablename__ = 'user'
    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    email = Column(String(250))
    picture = Column(String(250))


class Restaurant(Base):
    """
    Extends Base
    Establishes restaurant table
    Stores restaurant name, id, and user_id of the user who
    created the restaurant.
    """
    __tablename__ = 'restaurant'
    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

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


class MenuItem(Base):
    """
    Extends Base
    Establishes menu_item table
    Stores menu item name, id, course, description, price,
    id of the restaurant it's linked to, and the id of the user
    who created it.
    """
    __tablename__ = 'menu_item'
    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    course = Column(String(250))
    description = Column(String(250))
    price = Column(String(8))
    restaurant_id = Column(Integer, ForeignKey('restaurant.id'))
    restaurant = relationship(Restaurant)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

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

# Initialize database and tables
engine = create_engine('sqlite:///restaurantmenuwithusers.db')
Base.metadata.create_all(engine)
