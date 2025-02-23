# Ranger-Green

## 🌿 About Ranger-Green
Ranger-Green is an AI-driven IoT Smart Plant Monitor designed to help automate and optimize plant care. Using a combination of sensors and intelligent analysis, Ranger-Green monitors soil moisture, temperature, humidity, and light levels to ensure plants receive the optimal environment to thrive.

## 🚀 Features
- **Soil Moisture Monitoring** – Detects soil moisture levels and alerts when watering is needed.
- **Temperature & Humidity Sensing** – Monitors environmental conditions in real-time.
- **Light Intensity Measurement** – Ensures plants receive adequate light.
- **Web Dashboard** – View real-time data and control settings through an interactive dashboard.

## 🛠️ Tech Stack
- **Hardware:** NodeMCU ESP8266, DHT11, BH1750, Soil Moisture Sensor, Battery & BMS.
- **Backend & Database:** Flask, MongoDB.
- **Frontend:** Web Dashboard (HTML, CSS, JavaScript, AJAX).
- **Communication Protocols:** MQTT, HTTP.

## 📂 Project Structure
```
Ranger-Green/
│── Backend/          # Flask API (Python)
│── Frontend/         # Web Dashboard (HTML, CSS, JS)
│── esp_code/         # ESP8266 Code (C++)
│── esp_server/       # ESP Server Code (Python)
│── .gitignore        # Git Ignore File
│── README.md         # Project Overview
```

## 🔧 Setup Guide
### 1️⃣ Prerequisites
- NodeMCU ESP8266
- Arduino IDE (with ESP8266 Board Package)
- Python 3.x & Flask
- MongoDB Compass

### 2️⃣ Clone the Repository
```sh
git clone https://github.com/sidanacode/Ranger-Green.git
cd Ranger-Green
```

### 3️⃣ Flash the ESP8266 Firmware
- Open `esp_code/` in Arduino IDE.
- Install required libraries (`PubSubClient`, etc.).
- Configure WiFi credentials.
- Upload the code to ESP8266.

### 4️⃣ Setup the ESP Server
- Navigate to `Backend/` and install dependencies:
  ```sh
  pip install -r requirements.txt
  ```
- Run the Flask server:
  ```sh
  python esp_server.py
  ```

### 5️⃣ View Data on the Web Dashboard
- Navigate to `Frontend/` and start a local server:
  ```sh
  python -m http.server or Just double click on Index.html or Use live server.
  ```
- Connect to the Flask backend by Entering the IP of your ESP server, fetch real-time sensor data.

## 📊 Data Flow
1. **ESP8266 collects sensor data** → 2. **Sends data to ESP Server (via MQTT/HTTP)** → 3. **ESP Server serves the Real time sensor data to BACKEND Server** → 4. **BACKEND Server Load data into MongoDB and Processes the data and sends it to Frontend**→ 5. **Web Dashboard displays data in real-time**.

## 🤝 Contributing
### Team Contributions
- **Tanish Sidana** – Built the ESP Server and Arduino code.
- **Himanshu Yadav** – Built the FRONTEND and BACKEND Server of the web dashboard.
- **Rajveer Singh Shekawat & Geet Gaggar** – Built the circuit and casing system for the device.

We welcome contributions! Feel free to fork this repo, make changes, and submit a pull request.

## 📜 License
This project is open-source and available under the [MIT License](LICENSE).

---
📬 **Stay Connected**  
🚀 GitHub: [sidanacode](https://github.com/sidanacode)  
🚀 GitHub: [Himanshu-Yadav-0](https://github.com/Himanshu-Yadav-0)  


