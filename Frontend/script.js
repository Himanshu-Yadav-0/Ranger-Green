document.addEventListener('DOMContentLoaded', () => {
    const plantNameInput = document.getElementById('plantName');
    const submitBtn = document.getElementById('submitBtn');
    const loadingIndicator = document.getElementById('loadingIndicator');
    const recommendedSection = document.getElementById('recommendedSection');
    const suggestionSection = document.getElementById('suggestionSection');

    // Elements for displaying data
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

    let selectedPlant = ""; // Store selected plant name
    

    // ✅ Fetch only sensor data
    async function fetchSensorData() {
        try {
            const response = await fetch('http://192.168.0.8:5001/fetch_sensor_data');
            if (!response.ok) throw new Error('Network response was not ok');
            const data = await response.json();

            currentMoisture.textContent = (data.soil_moisture !== undefined && data.soil_moisture !== null) ? `${data.soil_moisture}%` : "0%";
currentTemp.textContent = (data.temperature !== undefined && data.temperature !== null) ? `${data.temperature}°C` : "0°C";
currentHumidity.textContent = (data.humidity !== undefined && data.humidity !== null) ? `${data.humidity}%` : "0%";
currentLight.textContent = (data.light_intensity !== undefined && data.light_intensity !== null) ? `${data.light_intensity} lux` : "0 lux";
currentpumpstatus.textContent = (data.pump_status !== undefined && data.pump_status !== null) ? `${data.pump_status}` : "OFF";


            console.log("Updated Sensor Data:", data);

            // ✅ Only update care suggestions if a plant is selected
            if (selectedPlant) {
                fetchPlantData();  // Fetch updated care suggestions
            }
        } catch (error) {
            console.error('Error fetching sensor data:', error);
        }
    }

    // ✅ Fetch plant data & care suggestions when user selects a plant
    async function fetchPlantData() {
        if (!selectedPlant) return;

        try {
            const response = await fetch('http://192.168.0.8:5001/compare_plant', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name: selectedPlant })
            });

            if (!response.ok) throw new Error('Network response was not ok');
            const data = await response.json();

            recommendedSection.classList.remove('hidden');
            suggestionSection.classList.remove('hidden');

            recommendedMoisture.textContent = data.plant?.ideal_moisture ? `${data.plant.ideal_moisture}%` : "No Data";
            recommendedHumidity.textContent = data.plant?.ideal_humidity ? `${data.plant.ideal_humidity}%` : "No Data";
            recommendedLight.textContent = data.plant?.ideal_light ? `${data.plant.ideal_light} lux` : "No Data";
            recommendedTemperature.textContent = data.plant?.ideal_temperature ? `${data.plant.ideal_temperature}°C` : "No Data";

            // ✅ Now care suggestions update correctly
            careSuggestion.textContent = data.suggestions?.length ? data.suggestions.join(", ") : "No suggestion available";

            console.log("Updated Plant Data & Care Suggestions:", data);
        } catch (error) {
            console.error('Error fetching plant data:', error);
        }
    }

    // ✅ Start real-time sensor data updates
    fetchSensorData();
    setInterval(fetchSensorData, 2000);

    // ✅ Handle user input
    submitBtn.addEventListener('click', () => {
        selectedPlant = plantNameInput.value.trim();
        
        if (!selectedPlant) {
            alert('Please enter a plant name');
            return;
        }

        loadingIndicator.classList.remove('hidden');
        fetchPlantData().then(() => {
            loadingIndicator.classList.add('hidden');
        });
    });

    plantNameInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            submitBtn.click();
        }
    });
});
