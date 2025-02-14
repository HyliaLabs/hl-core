from flask import Flask, render_template, jsonify
import requests

app = Flask(__name__, static_folder="static", template_folder="templates")

API_URL = "http://127.0.0.1:5050/api/heatmap"

@app.route("/")
def index():
    return render_template("heatmap.html")

@app.route("/api/heatmap")
def heatmap():
    """Proxy für API-Datenabruf"""
    try:
        response = requests.get(API_URL)
        data = response.json()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)