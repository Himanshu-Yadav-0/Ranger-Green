#include <ESP8266WiFi.h>
#include <ArduinoJson.h>
#include <DHT.h>
#include <Wire.h>
#include <BH1750.h>
#include <ESP8266HTTPClient.h>

#define DHTPIN D4
#define DHTTYPE DHT11
#define SOIL_PIN A0
#define RELAY_PIN D5

const char *ssid = "Tanish";
const char *password = "Tanish11@#";
const char *serverUrl = "http://192.168.188.189:5001/sensor_data";
const char *thresholdUrl = "http://192.168.188.189:5001/update_moisture";

DHT dht(DHTPIN, DHTTYPE);
BH1750 lightMeter;
WiFiClient client;

float moistureThreshold = 50.0; // Default threshold

void setup()
{
    Serial.begin(115200);
    dht.begin();
    Wire.begin();
    lightMeter.begin();
    pinMode(RELAY_PIN, OUTPUT);
    digitalWrite(RELAY_PIN, HIGH); // Pump OFF by default

    WiFi.begin(ssid, password);
    Serial.print("Connecting to WiFi");
    while (WiFi.status() != WL_CONNECTED)
    {
        delay(500);
        Serial.print(".");
    }
    Serial.println("\n✅ Connected to WiFi!");
}

void loop()
{
    readAndProcessSensors();
    fetchMoistureThreshold();
    delay(2000); // Send data every 5 seconds
}

void readAndProcessSensors()
{
    float temperature = dht.readTemperature();
    float humidity = dht.readHumidity();
    float lightIntensity = lightMeter.readLightLevel();
    int rawSoilMoisture = analogRead(SOIL_PIN);

    float soilMoisturePercent = 100.0 - ((rawSoilMoisture / 1023.0) * 100.0);

    if (isnan(temperature) || isnan(humidity))
    {
        Serial.println("❌ Failed to read from DHT11 sensor!");
        return;
    }

    Serial.printf("🌱 Soil Moisture: %.2f%%\n", soilMoisturePercent);
    Serial.printf("🌡 Temperature: %.2f°C\n", temperature);
    Serial.printf("💧 Humidity: %.2f%%\n", humidity);
    Serial.printf("☀ Light Intensity: %.2f lux\n", lightIntensity);

    // Pump Control with Hysteresis
    float lowerThreshold = moistureThreshold - (moistureThreshold * 0.20); // 20% below threshold

    if (soilMoisturePercent < lowerThreshold)
    {
        digitalWrite(RELAY_PIN, LOW); // Pump ON
        Serial.println("🚰 Pump ON! (Soil moisture too low)");
    }
    else if (soilMoisturePercent >= moistureThreshold)
    {
        digitalWrite(RELAY_PIN, HIGH); // Pump OFF
        Serial.println("❌ Pump OFF! (Moisture threshold reached)");
    }

    sendDataToServer(temperature, humidity, lightIntensity, soilMoisturePercent);
}

void sendDataToServer(float temperature, float humidity, float lightIntensity, float soilMoisture)
{
    if (WiFi.status() == WL_CONNECTED)
    {
        HTTPClient http;
        http.begin(client, serverUrl);
        http.addHeader("Content-Type", "application/json");

        StaticJsonDocument<200> jsonDoc;
        jsonDoc["temperature"] = temperature;
        jsonDoc["humidity"] = humidity;
        jsonDoc["light_intensity"] = lightIntensity;
        jsonDoc["soil_moisture"] = soilMoisture;

        String payload;
        serializeJson(jsonDoc, payload);
        int httpResponseCode = http.POST(payload);

        Serial.printf("📡 Sent Data: %s\n", payload.c_str());
        Serial.printf("🌍 Server Response: %d\n", httpResponseCode);
        http.end();
    }
}

void fetchMoistureThreshold()
{
    if (WiFi.status() == WL_CONNECTED)
    {
        HTTPClient http;
        http.begin(client, thresholdUrl);
        int httpResponseCode = http.GET();

        if (httpResponseCode == 200)
        {
            String response = http.getString();
            StaticJsonDocument<200> jsonDoc;
            deserializeJson(jsonDoc, response);
            moistureThreshold = jsonDoc["threshold"];
            Serial.printf("🔄 Updated Moisture Threshold: %.2f%%\n", moistureThreshold);
        }

        http.end();
    }
}