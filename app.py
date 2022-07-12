from flask import Flask, render_template, request, jsonify, redirect, url_for
from pymongo import MongoClient
import requests

app = Flask(__name__)

client = MongoClient('54.180.93.142', 27017, username="test", password="sparta")
db = client.userdb


@app.route('/')
def main():
    return render_template("main.html")


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)