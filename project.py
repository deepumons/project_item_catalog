from flask import Flask, render_template
app = Flask(__name__)


@app.route("/")
@app.route("/catalog")
def list_catalog():
    #return "Lists all categories and the latest added items."
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
