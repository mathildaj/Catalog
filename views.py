#! /usr/bin/env python
# -*- coding: utf-8 -*-

from database_setup import Base, User, Category, Item

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, asc, desc

from flask import Flask, jsonify, request, render_template, url_for, flash
from flask import redirect, session, make_response

# the new oauthlib is needed for the google authentication to work
# please run the following commands to install the library
# pip install Flask-OAuthlib
# pip install --user flask-oauthlib
from flask_oauthlib.client import OAuth

from functools import wraps

import json
import httplib2

# Create database engine and session

# the folloiwing two lines are for postgres

# engine = create_engine('postgresql+psycopg2:
# //catalog:mypassword@localhost:5432/catalog')

# this is for sqlite

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
db_session = DBSession()

'''
Create flask app
The following authorization uses the newest flask oauth library as of Dec 2017
Thanks to https://github.com/lepture/flask-oauthlib

'''

# OAuth with Google
# Logout of this app will NOT log you out of Google
# And that is by design

app = Flask(__name__)
app.config['GOOGLE_ID'] = "replace with your CLIENT_ID"
app.config['GOOGLE_SECRET'] = "replace with your CLIENT_SECRET"
app.debug = True
app.secret_key = 'development'
oauth = OAuth(app)

google = oauth.remote_app(
    'google',
    consumer_key=app.config.get('GOOGLE_ID'),
    consumer_secret=app.config.get('GOOGLE_SECRET'),
    request_token_params={
        'scope': 'email'
    },
    base_url='https://www.googleapis.com/oauth2/v1/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'google_token' not in session:
            flash("You have no permission to access this page!")
            return redirect(url_for('login'))
        else:
            return f(*args, **kwargs)

    return decorated_function


@app.route('/login')
def login():
    return google.authorize(callback=url_for('authorized', _external=True))


@app.route('/logout')
def logout():
    if 'google_token' not in session:
        response = make_response(
            json.dumps('Current user is not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Execute HTTP GET request to revoke current token.
    access_token = session['access_token']
    # Please keep the url line in one line, even though it is not PEP8
    url = "https://accounts.google.com/o/oauth2/revoke?token={0}".format(
        access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] == '200':
        # Reset the user's session. Use pop to avoid KeyError if not exists
        session.pop('google_token', None)
        session.pop('email', None)
        session.pop('name', None)
        session.pop('picture', None)
        session.pop('access_token', None)

        flash('You have been successfully logged out.')
        return redirect(url_for('showAll'))
    else:
        # If the given token was invalid.
        response = make_response(
            json.dumps('Invalid user token'), 400)
        # json.dumps(url), 400)
        response.headers['Content-Type'] = 'application/json'
        session.pop('google_token', None)
        session.pop('email', None)
        session.pop('name', None)
        session.pop('picture', None)
        session.pop('access_token', None)

        return response


@app.route('/login/authorized')
def authorized():
    resp = google.authorized_response()
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )
    # get the user info from the google response data, save in session

    session['google_token'] = (resp['access_token'], '')
    # the access_token is only used in logout, which does not have extra format
    # of the google_token as (token, '')
    session['access_token'] = resp['access_token']
    me = google.get('userinfo')
    session['email'] = me.data['email']
    session['name'] = me.data['name']
    session['picture'] = me.data['picture']

    # if the google user is not already signed up with the app, create
    # a new user for the app.
    if getUser(session) is None:
        createUser(session)

    return redirect(url_for('showAll'))


@google.tokengetter
def get_google_oauth_token():
    return session.get('google_token')

# End of Google OAuth

'''

Helper methods for Authenication

'''


def createUser(session):
    newUser = User(
        name=session['name'],
        email=session['email'],
        picture=session['picture']
    )
    db_session.add(newUser)
    db_session.commit()
    flash('Added new user.')
    user = db_session.query(User).filter_by(email=session['email']).first()
    return user


def getUser(session):
    user = db_session.query(User).filter_by(email=session['email']).first()
    if user is None:
        return None
    return user


def getItem(item_id):
    item = db_session.query(Item).filter_by(id=item_id).first()
    return item

'''

RESTFUL routes

'''
# Create route for the landing page


@app.route('/')
def showLandingPage():
    return render_template("landing.html")


# Create route for all categories

@app.route('/catalog')
def showAll():
    categories = db_session.query(Category).order_by(asc(Category.id))
    items = db_session.query(Category, Item).filter(
        Category.id == Item.category_id).order_by(
        desc(Item.createdDate)).limit(10)
    return render_template("catalog.html",
                           categories=categories,
                           items=items)


# Create route for showing a category and all its items

@app.route('/catalog/<int:category_id>')
@app.route('/catalog/<int:category_id>/items')
def showCategory(category_id):
    categories = db_session.query(Category).order_by(asc(Category.id))
    category = db_session.query(Category).filter_by(id=category_id).first()
    # if category does not exist, redirect
    if category is None:
        flash("The category does NOT exist!")
        return redirect(url_for('showAll'))
    # the order category_id=category.id is important, can't be reversed
    items = db_session.query(Item).filter_by(category_id=category.id).order_by(
        desc(Item.createdDate))
    return render_template('category.html',
                           categories=categories,
                           category=category,
                           items=items)


# Create route for showing details for an item

@app.route('/catalog/<int:category_id>/<int:item_id>')
def showItem(category_id, item_id):
    categories = db_session.query(Category).order_by(asc(Category.id))
    category = db_session.query(Category).filter_by(id=category_id).first()
    item = db_session.query(Item).filter_by(id=item_id).first()

    # if category or item does not exist, redirect
    if category is None or item is None:
        flash("The category or item does NOT exist!")
        return redirect(url_for('showAll'))

    return render_template('item.html',
                           categories=categories,
                           category=category,
                           item=item)


# Create route for editing an item

@app.route('/catalog/<int:category_id>/<int:item_id>/edit',
           methods=['GET', 'POST'])
@login_required
def editItem(category_id, item_id):
    # if user is NOT the creator of this item, he can not edit
    item = getItem(item_id)
    if item is None:
        return render_template('noAccess.html')
    creator_id = item.user_id
    if creator_id is None:
        return render_template('noAccess.html')
    item_creator = db_session.query(User).filter_by(id=creator_id).first()
    if item_creator is None:
        return render_template('noAccess.html')
    if(session['email'] is None or session['email'] != item_creator.email):
        return render_template('noAccess.html')

    category = db_session.query(Category).filter_by(id=category_id).first()
    itemToEdit = db_session.query(Item).filter_by(id=item_id).first()

    # if category or item does not exist, redirect
    if category is None or itemToEdit is None:
        flash("The category or item does NOT exist!")
        return redirect(url_for('showAll'))

    # if all checks out, modify the item and save to database
    if request.method == 'POST':
        # for this application, I am NOT allowing the user to modify the item's
        # category or upload a new image. These features can be added in the
        # future release
        if request.form['name']:
            itemToEdit.name = request.form['name']
        if request.form['description']:
            itemToEdit.description = request.form['description']
        db_session.add(itemToEdit)
        db_session.commit()
        flash("The item is modified!")
        return redirect(url_for('showAll'))
    else:
        return render_template('editItem.html',
                               category=category,
                               item=itemToEdit)


# Create route for creating a new item

@app.route('/catalog/items/new', methods=['GET', 'POST'])
@login_required
def newItem():
    # if user can not be found, deny access
    user = getUser(session)
    if user is None:
        return render_template('noAccess.html')

    # when all checks out, add the new item and save to the database
    categories = db_session.query(Category).order_by(asc(Category.id))
    if request.method == 'POST':
        # for this application, I am NOT allowing user to upload a new image.
        # The feature can be added in the future release
        # It is adding a default cat image right now
        if request.form['name']:
            newName = request.form['name']
        if request.form['description']:
            newDescription = request.form['description']
        if request.form['category']:
            newCategory = request.form['category']

        itemToAdd = Item(name=newName,
                         description=newDescription,
                         category_id=newCategory,
                         user_id=user.id)

        db_session.add(itemToAdd)
        db_session.commit()
        flash("The item is added!")
        return redirect(url_for('showAll'))
    else:
        return render_template('newItem.html',
                               categories=categories)


# Create route for deleting an item

@app.route('/catalog/<int:category_id>/<int:item_id>/delete',
           methods=['GET', 'POST'])
@login_required
def deleteItem(category_id, item_id):
    # if user is NOT the creator of this item, he can not delete
    item = getItem(item_id)
    if item is None:
        return render_template('noAccess.html')
    creator_id = item.user_id
    if creator_id is None:
        return render_template('noAccess.html')
    item_creator = db_session.query(User).filter_by(id=creator_id).first()
    if item_creator is None:
        return render_template('noAccess.html')
    if(session['email'] is None or session['email'] != item_creator.email):
        return render_template('noAccess.html')

    category = db_session.query(Category).filter_by(id=category_id).first()
    itemToDelete = db_session.query(Item).filter_by(id=item_id).first()

    # if category or item does not exist, redirect
    if category is None or itemToDelete is None:
        flash("The category or item does NOT exist!")
        return redirect(url_for('showAll'))

    # when all checks out, delete the item and commit to database
    if request.method == 'POST':
        db_session.delete(itemToDelete)
        db_session.commit()
        flash("The item is deleted!")
        return redirect(url_for('showAll'))

    else:
        return render_template('deleteItem.html',
                               category=category,
                               item=itemToDelete)


# API Endpoint for the catalog

@app.route('/catalog.json')
def get_catalog_json():
    categories = db_session.query(Category).order_by(asc(Category.id))
    # get all the categories
    categories_dict = [cat.serialize for cat in categories]
    # add all the items for each category
    for cat in range(len(categories_dict)):
        items = [item.serialize for item in db_session.query(Item).filter_by
                 (category_id=categories_dict[cat]["id"])]
        if items:
            categories_dict[cat]["Item"] = items
    # return the json object
    return jsonify(Category=categories_dict)


# API Endpoint for an item

@app.route('/category/<int:category_id>/item/<int:item_id>/JSON')
def get_item_json(category_id, item_id):
    category = db_session.query(Category).filter_by(id=category_id).first()
    item = db_session.query(Item).filter_by(id=item_id).first()
    return jsonify(Category=category.serialize, Item=item.serialize)


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
