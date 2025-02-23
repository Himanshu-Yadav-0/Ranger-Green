## libraries required
from flask_cors import CORS
from flask import Flask , request , jsonify

app = Flask(__name__)
CORS(app)

# Store latest Sensor data
latest_sensor_data = {}
moisture_threshold = 50.0 # default Threshold
pump_status = "OFF" # Default pump status

# Home Route
@app.route('/')
def home():
    return "ESP FLask server is Running"

# Api to Get Current Moisture Threshold 

@app.route('/moisture_threshold' , methods = ['GET'])
def get_moisture_threshold():
    global moisture_threshold
    return jsonify({"moisture_threshold":moisture_threshold}),200 

# API to Receive Sensor Data From Esp

@app.route("/sensor_data", methods=['POST'])
def receive_sensor_data():
    global latest_sensor_data, pump_status
    try:
        data = request.get_json()  # Explicitly parse JSON
        if not data:
            print("Error: Received empty JSON data")
            return jsonify({"error": "Empty JSON data"}), 400

        print("Received Sensor Data:", data)  # Debugging

        # Store the received sensor data
        latest_sensor_data = data

        # Extract soil moisture and update pump status
        soil_moisture = latest_sensor_data.get("soil_moisture")
        if soil_moisture is not None:
            try:
                soil_moisture = float(soil_moisture)  # Convert to float
                pump_status = "ON" if soil_moisture < moisture_threshold else "OFF"
            except ValueError:
                print("Error: Soil moisture is not a valid number")
                return jsonify({"error": "Invalid soil moisture value"}), 400

        return jsonify({"message": "Sensor data received", "pump_status": pump_status}), 200

    except Exception as e:
        print(f"Exception in /sensor_data: {str(e)}")
        return jsonify({"error": str(e)}), 500  # ✅ Corrected format

    
    # API TO GET LATEST SENSOR DATA
@app.route('/sensor_data',methods=['GET'])
def get_sensor_data():
    return jsonify(latest_sensor_data or{
        "soil_moistue":None,"temperature":None,
        "humidity":None, "light_intensity":None,
        "pump_status":"UNKNOWN"
    
    }),200

# update API to '/update_moisture'
@app.route('/update_moisture',methods=['GET',"POST"])
def handle_update_moisture():
    global moisture_threshold

    if request.method == 'GET':
        return jsonify({"threshold": moisture_threshold}),200
    elif request.method == "POST":
        data = request.json
        if "threshold" in data :
            moisture_threshold = float(data["threshold"])
            return jsonify({"message":"Threshold updated" ,"threshold":moisture_threshold}),200
        else:
            return jsonify({"error": "Missing Threshold Value"}),400

if __name__ == '__main__':
    app.run(host = '0.0.0.0' , port=5001 , debug=True)
