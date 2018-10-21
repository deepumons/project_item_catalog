from flask import Flask, render_template, redirect, request, url_for
from flask import flash, jsonify
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, Category, CategoryItem
from flask import session as login_session
import datetime
import sqlalchemy.exc

app = Flask(__name__)

# Initialize the database connection, DB session
engine = create_engine('sqlite:///itemcatalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)


# All the routes for the application are defined here
@app.route("/")
@app.route("/catalog/")
def list_catalog():
    # To be removed. Setting the session user_id for testing
    login_session['user_id'] = 1
    login_session['email'] = "urdeepak@gmail.com"
    # del login_session['user_id']
    # del login_session['email']
    # Test code ends

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
@app.route("/catalog/items/JSON")
def itemsJSON():
    session = DBSession()
    category_items = session.query(CategoryItem).all()
    session.close()
    return jsonify(CategoryItems=[item.serialize for item in category_items])


@app.route("/catalog/<string:item_name>/JSON")
def itemJSON(item_name):
    try:
        session = DBSession()
        category_item = session.query(CategoryItem).filter_by(
            name=item_name).one()
        session.close()
        return jsonify(CategoryItem=category_item.serialize)
    except sqlalchemy.orm.exc.NoResultFound:
        return("Error: There is no item with name '{}'".format(item_name))


def getUserID(email):
    try:
        session = DBSession()
        user = session.query(User).filter_by(email=email).one()
        session.close()
        return user.id
    except sqlalchemy.orm.exc.NoResultFound:
        return


if __name__ == "__main__":
    app.secret_key = "some_secret_key"
    app.debug = True
    app.run(host="0.0.0.0", port=5000)
