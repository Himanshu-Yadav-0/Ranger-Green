//DOMContentLoaded make it work as soon as the DOM is loaded
document.addEventListener('DOMContentLoaded',()=>{
    const plantNameInput = document.getElementById('plantName');
    const submitBtn = document.getElementById('submitBtn');
    const loadingIndicator = document.getElementById('loadingIndicator');
    const recommendedSection = document.getElementById('recommendedSection');
    const suggestionSection = document.getElementById('suggestionSection');

    // Elements for displaying the data on frontend
    const recommendedMoisture = document.getElementById('recommendedMoisture');
    const recommendedHumidity = document.getElementById('recommendedHumidity');
    const recommendedLight = document.getElementById('recommendedLight');
    const recommendedTemperature = document.getElementById('recommendedTemperature');
    const currentMoisture = document.getElementById('currentMoisture');
    const currentTemp = document.getElementById('currentTemp');
    const currentHumidity = document.getElementById('currentHumidity');
    const currentLight = document.getElementById('currentLight');
    const currentpumpstatus = document.getElementById('currentpumpstatus');
    const careSuggestion = document.getElementById('careSuggestion');

    let selectedPlant = "" // store plant name entered by user

    //fetch the sensor data only
    async function fetchSensorData(){
        try{
            const response = await fetch('http://192.168.0.52:5002/fetch_sensor_data')
            if (!response.ok) throw new Error('Network response was not ok')
            const data = await response.json()
            
            //updating ui, current readings
            currentMoisture.textContent = data.soil_moisture ? `${data.soil_moisture}%` : "No Data";
            currentTemp.textContent = data.temperature ? `${data.temperature}°C` : "No Data";
            currentHumidity.textContent = data.humidity ? `${data.humidity}%` : "No Data";
            currentLight.textContent = data.light_intensity ? `${data.light_intensity} lux` : "No Data";
            currentpumpstatus.textContent = data.pump_status ? `${data.pump_status}` : "No Data";

            //for debugging
            console.log("Updated Sensor Data:", data);
            //update care suggestions if a plant is selected
            if (selectedPlant) {
                fetchPlantData();  // Fetch updated care suggestions
            }
        }catch(error){
            console.log("Error fetching sensor data:",error)
        }
    }
    
})