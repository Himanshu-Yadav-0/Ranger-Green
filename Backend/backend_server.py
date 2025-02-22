from flask_cors import CORS
from flask import Flask, request, jsonify
from pymongo import MongoClient
import requests
import json

app = Flask(__name__)
CORS(app)

# Setting up Connection to MongoDb Database for the Plant dataset
MONGO_URL = "mongodb://localhost:27017"
client = MongoClient(MONGO_URL)
db = client["plant_database"]
plants_collection = db["plants"]


#Setting up the API URL to ESP SERVER AND THRESHOLD MOISTURE UPDATE
ESP_SERVER_URL = "http://192.168.0.18.5001/sensor_data"
UPDATE_THRESHOLD_MOISTURE_URL = "http://192.168.0.18:5001/update_moisture"


if __name__ == '__main__':
    app.run(debug=True)