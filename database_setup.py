#! /usr/bin/env python
# -*- coding: utf-8 -*-

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
import datetime


Base = declarative_base()


class User(Base):
    """
    User table to store app users
    """

    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    picture = Column(String)


class Category(Base):
    """
    Category table to store the categories
    """

    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)

    @property
    def serialize(self):
        return {
            'name': self.name,
            'id': self.id,
        }


class Item(Base):
    """
    Item table to store the the items for each category
    """

    __tablename__ = 'item'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), unique=True, nullable=False)
    description = Column(String)
    image = Column(String)
    createdDate = Column(
        DateTime, default=datetime.datetime.utcnow, nullable=False)
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        return {
            'name': self.name,
            'id': self.id,
            'description': self.description,
            'category_id':  self.category_id,
            'user_id': self.user_id
        }

# create the tables

# the folloiwing two lines are for postgres

# engine = create_engine('postgresql+psycopg2:
# //catalog:mypassword@localhost:5432/catalog')

# this is for sqlite

engine = create_engine('sqlite:///catalog.db')
Base.metadata.create_all(engine)
