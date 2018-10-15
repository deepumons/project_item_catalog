from flask import Flask, render_template
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, Category, CategoryItem


app = Flask(__name__)

# Initialize the database connection, DB session
engine = create_engine('sqlite:///itemcatalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)


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
    session = DBSession()
    categories = session.query(Category).all()
    item = session.query(CategoryItem).filter_by(name = item_name).one()
    session.close()
    return render_template(
        "delete_item.html", categories=categories, item=item)


if __name__ == "__main__":
    app.secret_key = "some_secret_key"
    app.debug = True
    app.run(host="0.0.0.0", port=5000)
