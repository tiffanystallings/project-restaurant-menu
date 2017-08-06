import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine


class Restaurant(Base):
	__tablename__ = 'restaurant'
	name = Column(
		String(80), nullable = False)
	id = Column(
		Integer, primary key = True)

class MenuItem(Base):
	__tablename__ = 'menu_item'

Base = declarative_base
engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.create_all(engine)