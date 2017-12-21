#! /usr/bin/env python
# -*- coding: utf-8 -*-

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, User, Category, Item

# the folloiwing two lines are for postgres

# engine = create_engine('postgresql+psycopg2:
# //catalog:mypassword@localhost:5432/catalog')

# this is for sqlite

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

# Create a dummy user to initialize the database

user1 = User(name="Dummy User", email="dummyuser@gmail.com")
session.add(user1)
session.commit()

# Read all the categories from a txt file, and create categories in the
# database

with open("category.txt") as fp:
    for line in fp:
        if(len(line) > 0):
            newCategory = Category(name=line.strip())
            session.add(newCategory)
            session.commit()


# Read all the items from a txt file, and create items in the database

items = []
with open("item.txt") as fp:
    for line in fp:
        item = line.split("|")
        if(len(item) == 5):
            newItem = Item(name=item[0].strip(), description=item[1].strip(),
                           image=item[2].strip(), category_id=item[3].strip(),
                           user_id=item[4].strip())
            session.add(newItem)
            session.commit()
