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
ESP_SERVER_URL = "http://192.168.0.18:5001/sensor_data"
UPDATE_THRESHOLD_MOISTURE_URL = "http://192.168.0.18:5001/update_moisture"

#Loads JSON data from the json file as file
with open("plants_data2.json","r",encoding="utf-8")as file:
    plants_data = json.load(file)

# Adding dataset to the MongoDb Databse Here: plant_databse
def add_plant_data():
    if plants_collection.count_documents({})==0:
        plants_collection.insert_many(plants_data)
        print("Plant Dataset Added in the Databse")

#Creating Routes
#Home Route
@app.route('/')
def home():
    return "Backend Server is Running!!",200

#Fetch sensor data from ESP server 
@app.route('/fetch_sensor_data',methods=['GET'])
def fetch_sensor_data():
    try:
        sensor_response = requests.get(ESP_SERVER_URL,timeout=2)
        if sensor_response.status_code ==200:
            return sensor_response.json(),200
        else:
            return jsonify({"error":"Failed to fetch sensor data"}),500
    except Exception as e:
        return jsonify({"error":str(e)}), 500
    
@app.route('/compare_plant',methods=['POST'])
def compare_plant():
    try:
        data = request.json
        #this print statement is for debugging
        print(f"Received Data:{data}")
        plant_name = data.get("name","").lower()
        
        if not plant_name:
            return jsonify({"error":"Plant name is required"}),400
        # getting plant details
        plant = plants_collection.find_one({"name":{"$regex":f"^{plant_name}$","$options":"i"}})
        if not plant:
            #this print statement is for Debugging
            print(f"ERROR: plant '{plant_name}' not found in MongoDB!")
            return jsonify({"error":"Plant not found"}),404
        
        #this print statement is for Debugging
        print(f"Found Plant in DB:{plant}")
        plant["_id"] = str(plant["_id"]) #Convert ObjectId to String

        #Getting Real time sensor data from ESP Server
        try:
            sensor_response = requests.get(ESP_SERVER_URL,timeout =2)
            if(sensor_response.status_code==200):
                sensor_data = sensor_response.json()
            else:
                raise Exception("Failed to fetch real sensore data")
        except Exception as e:
            print(f"Sensor Fetch error:{e}")
        #getting Attribuites values
        soil_moisture = sensor_data.get("soil_moisture")
        temperature = sensor_data.get("temperature")
        humidity = sensor_data.get("humidity")
        light_intensity=sensor_data.get("light_intensity")

        # if the attribuites values are None then
        if soil_moisture is None:
            soil_moisture=0.0
        if temperature is None:
            temperature = 0.0
        if humidity is None:
            humidity = 0.0
        if light_intensity is None:
            light_intensity = 0.0
        
        #generation of Care Suggestions
        suggestions = []
        pump_status = "OFF"
        if soil_moisture < plant["ideal_moisture"]:
            suggestions.append("Increase watering 🌱💧")
            pump_status = "ON"
        elif soil_moisture > plant["ideal_moisture"]:
            suggestions.append("Reduce watering 🚫💧")
            pump_status = "OFF"

        if temperature < plant["ideal_temperature"]:
            suggestions.append("Increase temperature 🔥")
        elif temperature > plant["ideal_temperature"]:
            suggestions.append("Decrease temperature ❄️")

        if humidity < plant["ideal_humidity"]:
            suggestions.append("Increase humidity 🌫️")
        elif humidity > plant["ideal_humidity"]:
            suggestions.append("Decrease humidity 💨")

        if light_intensity < plant["ideal_light"]:
            suggestions.append("Move plant to more light ☀️")
        elif light_intensity > plant["ideal_light"]:
            suggestions.append("Move plant to shade 🌳")
        
        # Sending Updated moisture Data to ESP Server
        try:
            update_response = requests.post(UPDATE_THRESHOLD_MOISTURE_URL,json={"threshold":plant["ideal_moisture"]},timeout=2)
        except Exception as e:
            #for debugging
            print(f"Error sending Threshold value:{e}")

        return jsonify({
            "plant": plant,
            "sensor_data": {
                "soil_moisture": soil_moisture,
                "temperature": temperature,
                "humidity": humidity,
                "light_intensity": light_intensity
            },
            "suggestions": suggestions,
            "pump_status": pump_status
        }),200
    except Exception as e:
        # for debugging
        print(f"ERROR: {str(e)}")
        return jsonify({"error":str(e)}),500
    
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001,debug=True)