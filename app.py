import json
from flask import Flask, render_template, url_for, request, jsonify, Response
from scrape import search

app = Flask(__name__)

@app.route("/")
@app.route("/home")
def index():
    return render_template("index.html")

@app.route("/products")
def products():
    query = request.args.get("q", "")
    return render_template("products.html", query=query)

@app.route("/api/search")
def api_search():
    query = request.args.get("q", "")
    if not query:
        return jsonify([])
    results = search(query)
    # If search() returns a JSON string, return it directly as JSON
    if isinstance(results, str):
        return Response(results, mimetype="application/json")
    # If it returns a Python list/dict, use jsonify
    return jsonify(results)

if __name__ == "__main__":
    app.run(debug=True)