from flask import Flask, render_template
app = Flask(__name__)

# dictionary for a single category, categories, and items for testing
category = {'name': 'Soccer', 'id': '1'}
categories = [{'name': 'Soccer', 'id': '1'}, {'name': 'Basketball', 'id': '2'},
{'name': 'Baseball', 'id': '3'}, {'name': 'Frisbee', 'id': '4'},
{'name': 'Snowboarding', 'id': '5'}]
items = [{'id': '1', 'title': 'Goggles', 'description': 'Polarized goggles.', 'category_id': '5'},
{'id': '2', 'title': 'Snowboard', 'description': 'Awesome Snowboard.', 'category_id': '5'},
{'id': '3', 'title': 'Two Shinguards', 'description': 'Shinguards x 2.', 'category_id': '1'},
{'id': '4', 'title': 'Shinguard', 'description': 'High quality shinguard', 'category_id': '1'},
{'id': '5', 'title': 'Bat', 'description': 'High quality red wood bat', 'category_id': '3'}]


@app.route("/")
@app.route("/catalog")
def list_catalog():
    return render_template("catalog.html")


@app.route("/catalog/<string:category_name>/")
@app.route("/catalog/<string:category_name>/items")
def list_category_items(category_name):
    return "Lists all items under the category: {}".format(category_name)


@app.route("/catalog/<string:category_name>/<string:item_name>")
def list_item(category_name, item_name):
    return "Lists item discription for: {}".format(item_name)


@app.route("/catalog/<string:category_name>/<string:item_name>/edit")
def edit_item(category_name, item_name):
    return "This page is used to edit {}".format(item_name)


@app.route("/catalog/<string:category_name>/<string:item_name>/delete")
def delete_item(category_name, item_name):
    return "This page is used to delete {}".format(item_name)


if __name__ == "__main__":
    app.debug = True
    app.run(host="0.0.0.0", port=5000)
