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
#define SDA_PIN D2
#define SCL_PIN D1

const char *ssid = "Tanish";
const char *password = "Tanish11@#";
const char *serverUrl = "http://192.168.188.189:5001/sensor_data";
const char *thresholdUrl = "http://192.168.188.189:5001/update_moisture";

DHT dht(DHTPIN, DHTTYPE);
BH1750 lightMeter;
WiFiClient client;

float moistureThreshold = 50.0;
bool pumpActivated = false;
bool pumpStatus = false;

void setup()
{
    Serial.begin(115200);
    dht.begin();
    Wire.begin();
    lightMeter.begin();
    pinMode(RELAY_PIN, OUTPUT);
    digitalWrite(RELAY_PIN, HIGH);

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
    delay(3000);
}

void readAndProcessSensors()
{
    float temperature = dht.readTemperature();
    float humidity = dht.readHumidity();
    float lightIntensity = lightMeter.readLightLevel();
    int rawSoilMoisture = analogRead(SOIL_PIN);

    float soilMoisturePercent = 100.0 - ((rawSoilMoisture / 1023.0) * 100.0);

    // Handle sensor failures
    String tempValue = isnan(temperature) ? "none" : String(temperature, 2);
    String humidityValue = isnan(humidity) ? "none" : String(humidity, 2);
    String lightValue = (lightIntensity < 0) ? "none" : String(lightIntensity, 2);
    String soilValue = (rawSoilMoisture < 0 || rawSoilMoisture > 1023) ? "none" : String(soilMoisturePercent, 2);

    Serial.printf("🌱 Soil Moisture: %s%%\n", soilValue.c_str());
    Serial.printf("🌡 Temperature: %s°C\n", tempValue.c_str());
    Serial.printf("💧 Humidity: %s%%\n", humidityValue.c_str());
    Serial.printf("☀ Light Intensity: %s lux\n", lightValue.c_str());

    float lowerThreshold = moistureThreshold * 0.80;

    if (!pumpActivated)
    {
        if (soilMoisturePercent < moistureThreshold)
        {
            pumpActivated = true;
            Serial.println("✅ Pump control activated after first threshold breach!");
        }
    }
    else
    {
        if (soilMoisturePercent < lowerThreshold)
        {
            digitalWrite(RELAY_PIN, LOW);
            pumpStatus = true;
            Serial.println("🚰 Pump ON! (Soil moisture too low)");
        }
        else if (soilMoisturePercent >= moistureThreshold)
        {
            digitalWrite(RELAY_PIN, HIGH);
            pumpStatus = false;
            Serial.println("❌ Pump OFF! (Moisture threshold reached)");
        }
    }

    sendDataToServer(tempValue, humidityValue, lightValue, soilValue, pumpStatus);
}

void sendDataToServer(String temperature, String humidity, String lightIntensity, String soilMoisture, bool pumpStatus)
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
        jsonDoc["pump_status"] = pumpStatus ? "ON" : "OFF";

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
