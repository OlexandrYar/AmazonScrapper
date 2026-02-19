from flask import Flask, render_template, url_for, request
from scrape import search

app = Flask(__name__)

@app.route("/")
@app.route("/home")
def index():
    if request.method == "POST":
        searchText = request.form["searchRequest"]
        return search(searchText)
    else:
        return render_template("index.html")


@app.route("/products")
def testPage():
    return render_template("products.html")

if __name__ == "__main__":
    app.run(debug=True)