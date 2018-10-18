from flask import Flask, render_template, redirect, request, url_for, flash
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, Category, CategoryItem
from flask import session as login_session
import datetime

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


@app.route("/catalog/<string:category_name>/<string:item_name>/edit")
def edit_item(category_name, item_name):
    session = DBSession()
    categories = session.query(Category).all()
    item = session.query(CategoryItem).filter_by(name=item_name).one()
    session.close()
    return render_template(
        "edit_item.html", categories=categories, item=item,
        category_name=category_name)


@app.route("/catalog/<string:category_name>/<string:item_name>/delete")
def delete_item(category_name, item_name):
    session = DBSession()
    categories = session.query(Category).all()
    item = session.query(CategoryItem).filter_by(name=item_name).one()
    session.close()
    return render_template(
        "delete_item.html", categories=categories, item=item)


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
        if request.form['submit_button'] == 'cancel':
            return redirect(url_for('list_catalog'))
        else:
            # See if the user has entered any data before proceeding
            if request.form['name'] is None or request.form['name'] == '':
                flash("Please enter the name of the catalog item before
                      submiting the form.")
                return render_template(
                    "add_item.html", categories=categories)
            else:
                user_id = getUserID(login_session['email'])

                session = DBSession()
                category = session.query(Category).filter_by(
                            name=request.form['category']).one()

                newItem = CategoryItem(
                    name=request.form['name'],
                    description=request.form['description'],
                    date=datetime.datetime.now(),
                    category=category,
                    user_id=user_id)

                session.add(newItem)
                session.commit()
                session.close()

                flash("New item added successfully.")
                return redirect(url_for('list_catalog'))
    else:
        return render_template(
            "add_item.html", categories=categories)


def getUserID(email):
        session = DBSession()
        user = session.query(User).filter_by(email=email).one()
        session.close()
        return user.id


if __name__ == "__main__":
    app.secret_key = "some_secret_key"
    app.debug = True
    app.run(host="0.0.0.0", port=5000)
