from flask import Flask, render_template
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, Category, CategoryItem


app = Flask(__name__)

# Initialize the database connection, DB session
engine = create_engine('sqlite:///itemcatalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)


# dictionary for a single category, categories, and items for testing
category = {'name': 'Soccer', 'id': '1'}
categories = [{'name': 'Soccer', 'id': '1'}, {'name': 'Basketball', 'id': '2'},
{'name': 'Baseball', 'id': '3'}, {'name': 'Frisbee', 'id': '4'},
{'name': 'Snowboarding', 'id': '5'}]
item = {'id': '1', 'name': 'Goggles', 'description': 'Polarized goggles.', 'category_id': '5', 'category_name': 'Snowboarding'}
items = [{'id': '1', 'name': 'Goggles', 'description': 'Polarized goggles.', 'category_id': '5', 'category_name': 'Snowboarding'},
{'id': '2', 'name': 'Snowboard', 'description': 'Awesome Snowboard.', 'category_id': '5', 'category_name': 'Snowboarding'},
{'id': '3', 'name': 'Two Shinguards', 'description': 'Shinguards x 2.', 'category_id': '1', 'category_name': 'Soccer'},
{'id': '4', 'name': 'Shinguard', 'description': 'High quality shinguard', 'category_id': '1', 'category_name': 'Soccer'},
{'id': '5', 'name': 'Bat', 'description': 'High quality red wood bat', 'category_id': '3', 'category_name': 'Baseball'}]


@app.route("/")
@app.route("/catalog/")
def list_catalog():
    session = DBSession()
    categories = session.query(Category).all()
    latest_items = session.query(CategoryItem).order_by(desc(CategoryItem.date))
    session.close()
    return render_template(
        "catalog.html", categories=categories, items=latest_items)


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
    item = session.query(CategoryItem).filter_by(name = item_name).one()
    category_name=item.category.name
    session.close()
    return render_template("item.html", categories=categories, item=item, category_name=category_name)


@app.route("/catalog/<string:category_name>/<string:item_name>/edit")
def edit_item(category_name, item_name):
    session = DBSession()
    categories = session.query(Category).all()
    item = session.query(CategoryItem).filter_by(name = item_name).one()
    category_name=item.category.name
    session.close()
    return render_template(
        "edit_item.html", categories=categories, item=item, category_name=category_name)


@app.route("/catalog/<string:category_name>/<string:item_name>/delete")
def delete_item(category_name, item_name):
    return render_template(
        "delete_item.html", categories=categories, item=items[0])


if __name__ == "__main__":
    app.secret_key = "some_secret_key"
    app.debug = True
    app.run(host="0.0.0.0", port=5000)
