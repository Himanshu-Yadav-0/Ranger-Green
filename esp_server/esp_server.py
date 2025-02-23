from flask_cors import CORS
from flask import Flask, request, jsonify

app = Flask(__name__)
CORS(app)

latest_sensor_data = {}
moisture_threshold = 50.0  # Default Threshold
pump_status = "OFF"  # Default pump status

@app.route('/')
def home():
    return "ESP Flask Server is Running"

@app.route('/moisture_threshold', methods=['GET'])
def get_moisture_threshold():
    return jsonify({"moisture_threshold": moisture_threshold}), 200

# API to Receive Sensor Data From Esp

@app.route("/sensor_data" , methods=['POST'])
def receive_sensor_data():
    global latest_sensor_data , pump_status
    try:
        data = request.get_json()  # Explicitly parse JSON
        if not data:
            print("Error: Received empty JSON data")
            return jsonify({"error": "Empty JSON data"}), 400

        print("Received Sensor Data:", data)  # Debugging

        # Store the received sensor data
        latest_sensor_data = data

        # Extract soil moisture and update pump status
        soil_moisture = float(latest_sensor_data.get("soil_moisture", 0))

        # update pump staus based on moisture level
        if soil_moisture is not None:
            pump_status = "ON" if soil_moisture < moisture_threshold else "OFF"
        print("Recived Sensor Data:", latest_sensor_data)
        return jsonify({"message" : "Sensor data received" , "pump_status":pump_status}),200
    except Exception as e:
        return jsonify({"error": str(e)}) , 500
    
    # API TO GET LATEST SENSOR DATA
@app.route('/sensor_data',methods=['GET'])
def get_sensor_data():
    return jsonify(latest_sensor_data or {
        "soil_moisture": None, "temperature": None,
        "humidity": None, "light_intensity": None,
        "pump_status": "UNKNOWN"
    }), 200

@app.route('/update_moisture', methods=['GET', "POST"])
def handle_update_moisture():
    global moisture_threshold

    if request.method == 'GET':
        return jsonify({"threshold": moisture_threshold}), 200
    elif request.method == "POST":
        data = request.json
        if "threshold" in data:
            moisture_threshold = float(data["threshold"])
            return jsonify({"message": "Threshold updated", "threshold": moisture_threshold}), 200
        else:
            return jsonify({"error": "Missing Threshold Value"}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
