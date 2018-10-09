from flask import Flask
app = Flask(__name__)


@app.route("/")
@app.route("/catalog")
def list_catalog():
    return "Default route. Entire categories and items will be listed here."


if __name__ == "__main__":
    app.debug = True
    app.run(host="0.0.0.0", port=5000)
