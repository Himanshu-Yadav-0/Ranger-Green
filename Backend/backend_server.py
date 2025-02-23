from flask_cors import CORS
from flask import Flask, request, jsonify
from pymongo import MongoClient
import requests
import json

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*", "methods": ["GET", "POST", "OPTIONS"]}})

# Setting up Connection to MongoDb Database for the Plant dataset
MONGO_URL = "mongodb://localhost:27017"
client = MongoClient(MONGO_URL)
db = client["plant_database"]
plants_collection = db["plants"]

# Global variable to store ESP IP
ESP_IP = None

# Loads JSON data from the json file as file
with open("plants_data2.json","r",encoding="utf-8") as file:
    plants_data = json.load(file)

# Adding dataset to the MongoDb Database
def add_plant_data():
    if plants_collection.count_documents({})==0:
        plants_collection.insert_many(plants_data)
        print("Plant Dataset Added in the Database")

# New route to set ESP IP
@app.route('/set-esp-ip', methods=['POST'])
def set_esp_ip():
    global ESP_IP
    data = request.json
    ESP_IP = data.get('esp_ip')
    if ESP_IP:
        return jsonify({"message": "ESP IP set successfully"}), 200
    return jsonify({"error": "Invalid ESP IP"}), 400

@app.route('/')
def home():
    return "Backend Server is Running!!", 200

@app.route('/fetch_sensor_data', methods=['GET'])
def fetch_sensor_data():
    global ESP_IP
    if not ESP_IP:
        return jsonify({"error": "ESP IP not configured"}), 400
    
    try:
        sensor_response = requests.get(f"http://{ESP_IP}/sensor_data", timeout=1)
        if sensor_response.status_code == 200:
            sensor_data = sensor_response.json()
            # Add battery percentage to response if not present
            if 'battery_percentage' not in sensor_data:
                sensor_data['battery_percentage'] = 0  # Default value if ESP doesn't send it
            return sensor_data, 200
        else:
            return jsonify({"error": "Failed to fetch sensor data"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/compare_plant', methods=['POST'])
def compare_plant():
    global ESP_IP
    if not ESP_IP:
        return jsonify({"error": "ESP IP not configured"}), 400
      
    try:
        data = request.json
        plant_name = data.get("name", "").lower()
        
        if not plant_name:
            return jsonify({"error": "Plant name is required"}), 400
            
        plant = plants_collection.find_one({"name": {"$regex": f"^{plant_name}$", "$options": "i"}})
        if not plant:
            return jsonify({"error": "Plant not found"}), 404
            
        plant["_id"] = str(plant["_id"])

        try:
            sensor_response = requests.get(f"http://{ESP_IP}/sensor_data", timeout=1)
            if sensor_response.status_code == 200:
                sensor_data = sensor_response.json()
            else:
                raise Exception("Failed to fetch real sensor data")
        except Exception as e:
            print(f"Sensor Fetch error: {e}")
            
        #getting Attribuites values
        # Convert sensor data to proper numeric types
        try:
            soil_moisture = float(sensor_data.get("soil_moisture", 0))
            temperature = float(sensor_data.get("temperature", 0))
            humidity = float(sensor_data.get("humidity", 0))  # If humidity should be int, convert later
            light_intensity = float(sensor_data.get("light_intensity", 0))
        except ValueError as e:
            print(f"Error converting sensor data: {e}")
            return jsonify({"error": "Invalid sensor data format"}), 400

# If humidity and light intensity should be integers
        humidity = int(humidity)
        light_intensity = int(light_intensity)
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
        
        # Update threshold moisture
        try:
            update_response = requests.post(
                f"http://{ESP_IP}/update_moisture",
                json={"threshold": plant["ideal_moisture"]},
                timeout=2
            )
        except Exception as e:
            print(f"Error sending Threshold value: {e}")

        return jsonify({
            "plant": plant,
            "sensor_data": sensor_data,
            "suggestions": suggestions,
            "pump_status": pump_status
        }), 200
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Add this new route to clear the ESP IP
@app.route('/clear-esp-ip', methods=['POST'])
def clear_esp_ip():
    global ESP_IP
    ESP_IP = None
    return jsonify({"message": "ESP IP cleared successfully"}), 200

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)