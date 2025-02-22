//DOMContentLoaded make it work as soon as the DOM is loaded
document.addEventListener('DOMContentLoaded',()=>{
    alert("HIIII")
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
    // sending post req to the backend server to get the ideal data of the plant name in response and then show it on ui
    async function fetchPlantData() {
        if(!selectedPlant)return

        try{
            const response = await fetch('http://192.168.0.52:5002/compare_plant',{
                method: 'POST',
                headers:{'Content-Type':'application/json'},
                body:JSON.stringify({name:selectedPlant})
            })
            if(!response.ok) throw new Error('Network response was not ok')
            const data = await response.json()
            
            //showing the recommended section and care section
            recommendedSection.classList.remove('hidden');
            suggestionSection.classList.remove('hidden');

            //adding data to the recommended sections
            recommendedMoisture.textContent = data.plant?.ideal_moisture ? `${data.plant.ideal_moisture}%` : "No Data";
            recommendedHumidity.textContent = data.plant?.ideal_humidity ? `${data.plant.ideal_humidity}%` : "No Data";
            recommendedLight.textContent = data.plant?.ideal_light ? `${data.plant.ideal_light} lux` : "No Data";
            recommendedTemperature.textContent = data.plant?.ideal_temperature ? `${data.plant.ideal_temperature}°C` : "No Data";

            //updating care suggestions
            careSuggestion.textContent=data.suggestions?.length ? data.suggestions.join(","):"No suggestion available"
        }
        catch(error){
            console.log("Error fetching plant data:",error);
            
        }

        //start real time sensor data updates
        fetchSensorData();
        setInterval(fetchSensorData,2000)
    }

        //user input handel
        submitBtn.addEventListener('click',()=>{
            selectedPlant= plantNameInput.value.trim()

            if(!selectedPlant){
                alert('please enter a plant name')
                return
            }
            //loading indicator
            loadingIndicator.classList.remove('hidden');
            fetchPlantData().then(() => {
                loadingIndicator.classList.add('hidden');
            });
        })

        plantNameInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    submitBtn.click();
                }
            });

        
})