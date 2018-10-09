from flask import Flask
app = Flask(__name__)


@app.route("/")
@app.route("/catalog")
def list_catalog():
    return "Lists all categories and the latest added items."


@app.route("/catalog/<string:category>/")
@app.route("/catalog/<string:category>/items")
def list_category_items(category):
    return "Lists all items under the category: {}".format(category)


if __name__ == "__main__":
    app.debug = True
    app.run(host="0.0.0.0", port=5000)
