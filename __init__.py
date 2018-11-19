from flask import Flask, render_template, redirect, request, url_for
from flask import flash, jsonify
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, Category, CategoryItem
from flask import session as login_session
import datetime
import sqlalchemy.exc
# Imports related to creating anti-forgery token
import random
import string

# Imports for gconnect implementation
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

# Create a flask instance
app = Flask(__name__)

# Load the client secrets file and store locally
CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Item Catalog App"

# Initialize the database connection, DB session
#engine = create_engine('sqlite:///itemcatalog.db')
engine = create_engine('postgresql:///itemcatalog')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)


# All the routes for the application are defined here
# Route for /login and anti forgery token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


# Server side implemention for gconnect
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # Create this user in the local database if it doesn't already exist
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)

    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;\
        -webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    return output


@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        # return response
        flash("Unable to signout. Current user not connected.")
        return redirect(url_for('list_catalog'))

    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' \
        % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        # return response
        flash("You have logged out successfully.")
        return redirect(url_for('list_catalog'))

    else:
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        # return response
        flash("Unable to signout. Failed to revoke token for given user.")
        return redirect(url_for('list_catalog'))


@app.route("/")
@app.route("/catalog/")
def list_catalog():

    if 'user_id' not in login_session:
        add_item = False
    else:
        add_item = True

    session = DBSession()
    categories = session.query(Category).all()
    latest_items = session.query(
        CategoryItem).order_by(desc(CategoryItem.date))
    session.close()
    return render_template(
        "catalog.html", categories=categories, items=latest_items,
        add_item=add_item)


@app.route("/catalog/<string:category_name>/")
@app.route("/catalog/<string:category_name>/items/")
def list_category_items(category_name):
    session = DBSession()
    categories = session.query(Category).all()
    category = session.query(Category).filter_by(name=category_name).one()
    category_items = session.query(CategoryItem).filter_by(category=category)
    session.close()
    return render_template(
        "items.html", category_name=category_name, items=category_items,
        categories=categories)


@app.route("/catalog/<string:category_name>/<string:item_name>")
def list_item(category_name, item_name):
    session = DBSession()
    categories = session.query(Category).all()
    item = session.query(CategoryItem).filter_by(name=item_name).one()
    category_name = item.category.name
    session.close()
    return render_template(
        "item.html", categories=categories, item=item,
        category_name=category_name)


@app.route(
    "/catalog/<string:category_name>/<string:item_name>/edit",
    methods=['GET', 'POST'])
def edit_item(category_name, item_name):

    # Check if the user is logged in before going further
    if 'user_id' not in login_session:
        flash("You should login before you can edit a catalog item.")
        return redirect(url_for('list_catalog'))

    if request.method == 'POST':
        # If the user has pressed the cancel button, abort and go back
        if request.form['submit_button'] == 'Cancel':
            return redirect(url_for('list_catalog'))
        else:
            # See if the user has entered any data before proceeding
            if request.form['name'] is None or request.form['name'] == '':
                flash("Please enter the name of the catalog item before\
                submiting the form.")
                return redirect(url_for(
                    'edit_item', category_name=category_name,
                    item_name=item_name))

            session = DBSession()
            edited_item = session.query(CategoryItem).filter_by(
                name=item_name).one()
            category = session.query(Category).filter_by(
                        name=request.form['category']).one()

            # Check if the current user is the owner of item before editing
            if edited_item.user_id != getUserID(login_session['email']):
                flash("Item created by another user cannot be edited.")
                session.close()
                return redirect(url_for('list_catalog'))

            if request.form['name']:
                edited_item.name = request.form['name']
            if request.form['description']:
                edited_item.description = request.form['description']
            if request.form['category']:
                edited_item.category = category

            edited_item.date = datetime.datetime.now()

            session.add(edited_item)
            session.commit()
            session.close()

            flash("Item updated successfully.")
            return redirect(url_for('list_catalog'))
    else:
        session = DBSession()
        categories = session.query(Category).all()
        item = session.query(CategoryItem).filter_by(name=item_name).one()
        session.close()
        return render_template(
            "edit_item.html", categories=categories, item=item,
            category_name=category_name)


@app.route("/catalog/<string:category_name>/<string:item_name>/delete",
           methods=['GET', 'POST'])
def delete_item(category_name, item_name):
    # Check if the user is logged in before going further
    if 'user_id' not in login_session:
        flash("You should login before you can delete a catalog item.")
        return redirect(url_for('list_catalog'))

    session = DBSession()
    categories = session.query(Category).all()
    item = session.query(CategoryItem).filter_by(name=item_name).one()
    session.close()

    if request.method == 'POST':
        # If the user has pressed the cancel button, abort and go back
        if request.form['submit_button'] == 'Cancel':
            return redirect(url_for('list_catalog'))
        else:
            # Check if the current user is same as the user who crated the item
            if item.user_id != getUserID(login_session['email']):
                    flash("Item created by another user cannot be deleted.")
                    return redirect(url_for('list_catalog'))
            else:
                session = DBSession()
                session.delete(item)
                session.commit()
                session.close()
                flash("Item has been deleted.")
                return redirect(url_for('list_catalog'))
    else:
            return render_template(
                "delete_item.html", categories=categories, item=item,
                category_name=category_name)


@app.route("/catalog/add", methods=['GET', 'POST'])
def add_item():
    # Check if the user is logged in before going further
    if 'user_id' not in login_session:
        flash("You should login before you can create a catalog item.")
        return redirect(url_for('list_catalog'))

    session = DBSession()
    categories = session.query(Category).all()
    session.close()

    if request.method == 'POST':
        # If the user has pressed the cancel button, abort and go back
        if request.form['submit_button'] == 'Cancel':
            return redirect(url_for('list_catalog'))
        else:
            # See if the user has entered any data before proceeding
            if request.form['name'] is None or request.form['name'] == '':
                flash("Please enter the name of the catalog item before\
                submiting the form.")
                return render_template(
                    "add_item.html", categories=categories)
            else:
                try:
                    session = DBSession()
                    category = session.query(Category).filter_by(
                                name=request.form['category']).one()

                    newItem = CategoryItem(
                        name=request.form['name'],
                        description=request.form['description'],
                        date=datetime.datetime.now(),
                        category=category,
                        user_id=getUserID(login_session['email']))

                    session.add(newItem)
                    session.commit()
                    session.close()

                    flash("New item added successfully.")
                    return redirect(url_for('list_catalog'))
                except sqlalchemy.exc.IntegrityError:
                    flash("Unable to save the catalog Item. Please ensure \
                    that the item Name is unique.")
                    return render_template(
                        "add_item.html", categories=categories)
    else:
        return render_template(
            "add_item.html", categories=categories)


# JSON API endpoint for categories
@app.route("/catalog/categories/JSON")
def categoriesJSON():
    session = DBSession()
    categories = session.query(Category).all()
    session.close()
    return jsonify(Categories=[category.serialize for category in categories])


# JSON API endpoint for category items
@app.route("/catalog/<string:category_name>/items/JSON")
def itemsJSON(category_name):
    session = DBSession()
    category = session.query(Category).filter_by(name=category_name).one()
    category_items = session.query(
        CategoryItem).filter_by(category=category).all()
    session.close()
    return jsonify(CategoryItems=[item.serialize for item in category_items])


@app.route("/catalog/<string:category_name>/<string:item_name>/JSON")
def itemJSON(category_name, item_name):
    try:
        session = DBSession()
        category_item = session.query(CategoryItem).filter_by(
            name=item_name).one()
        session.close()
        return jsonify(CategoryItem=category_item.serialize)
    except sqlalchemy.orm.exc.NoResultFound:
        return("Error: There is no item with name '{}'".format(item_name))


# Methods to manage user sessions
def getUserID(email):
    try:
        session = DBSession()
        user = session.query(User).filter_by(email=email).one()
        session.close()
        return user.id
    except sqlalchemy.orm.exc.NoResultFound:
        return None


def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'])
    session = DBSession()
    session.add(newUser)
    session.commit()
    session.close()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


if __name__ == "__main__":
    #app.secret_key = "some_secret_key"
    #app.debug = True
    #app.run(host="0.0.0.0", port=5000)
	app.run()	
