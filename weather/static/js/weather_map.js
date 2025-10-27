/**
 * Weather Map JavaScript - Clean Version
 */

let map, currentMarker, weatherTileLayer = null;
let alertMode = false, selectedLocation = null;

// OpenWeatherMap API configuration
const OPENWEATHER_API_KEY = window.OPENWEATHER_API_KEY_FROM_ENV || "c58e8978703203f1a7ad55379a588e2c"; // Fallback to hardcoded if not set
const OPENWEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5";

// Initialize map
function initMap() {
    map = L.map('weather-map').setView([14.651, 121.0437], 6);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);

    map.on('click', onMapClick);
    addWeatherTileLayer('temp');
    hideLoading();
    getCurrentLocation();
}

// Weather tile layer management
function addWeatherTileLayer(layerType = 'temp') {
    if (weatherTileLayer) map.removeLayer(weatherTileLayer);

    if (OPENWEATHER_API_KEY !== "YOUR_API_KEY_HERE") {
        const layerUrl = `https://tile.openweathermap.org/map/${layerType}_new/{z}/{x}/{y}.png?appid=${OPENWEATHER_API_KEY}`;
        weatherTileLayer = L.tileLayer(layerUrl, {
            opacity: 0.6,
            attribution: '© OpenWeatherMap'
        }).addTo(map);
    }
    updateMapLegend(layerType);
}

function updateMapLegend(layerType) {
    document.querySelectorAll('.legend-content').forEach(legend => legend.classList.add('hidden'));
    const selectedLegend = document.querySelector(`[data-legend="${layerType}"]`);
    if (selectedLegend) selectedLegend.classList.remove('hidden');
}

// Location handling
function getCurrentLocation() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            position => {
                const { latitude: lat, longitude: lng } = position.coords;
                map.setView([lat, lng], 10);
                showWeatherDetails(lat, lng);
            },
            () => showMessage('Unable to get location. Using default view.', 'warning')
        );
    }
}

function onMapClick(e) {
    const { lat, lng } = e.latlng;

    if (currentMarker) map.removeLayer(currentMarker);
    currentMarker = L.marker([lat, lng]).addTo(map);

    selectedLocation = { lat, lng };
    showWeatherDetails(lat, lng);
    updateUsersInArea();

    if (alertMode) toggleAlertOverlay(true);
}

async function searchLocation(query) {
    if (!query.trim() || OPENWEATHER_API_KEY === "YOUR_API_KEY_HERE") {
        showMessage('Please set your API key to use search functionality', 'error');
        return;
    }

    try {
        const geocodeUrl = `http://api.openweathermap.org/geo/1.0/direct?q=${encodeURIComponent(query)}&limit=1&appid=${OPENWEATHER_API_KEY}`;
        const response = await fetch(geocodeUrl);
        const data = await response.json();

        if (data && data.length > 0) {
            const location = data[0];
            map.setView([location.lat, location.lon], 10);

            if (currentMarker) map.removeLayer(currentMarker);
            currentMarker = L.marker([location.lat, location.lon]).addTo(map);

            showWeatherDetails(location.lat, location.lon);
            showMessage(`Found: ${location.name}, ${location.country}`, 'info');
        } else {
            showMessage('Location not found. Please try a different search term.', 'error');
        }
    } catch (error) {
        console.error('Geocoding error:', error);
        showMessage('Error searching for location. Please try again.', 'error');
    }
}

// Weather data handling
async function showWeatherDetails(lat, lng) {
    try {
        hideDefault();
        showWeatherSection();
        showLoadingState();
        updateCoordinates(lat, lng);

        if (OPENWEATHER_API_KEY === "YOUR_API_KEY_HERE") {
            showMessage('Please set your OpenWeatherMap API key to get real weather data', 'error');
            return;
        }

        const [currentData, forecastData, airQualityData] = await Promise.all([
            fetchWeatherData(`${OPENWEATHER_BASE_URL}/weather?lat=${lat}&lon=${lng}&appid=${OPENWEATHER_API_KEY}&units=metric`),
            fetchWeatherData(`${OPENWEATHER_BASE_URL}/forecast?lat=${lat}&lon=${lng}&appid=${OPENWEATHER_API_KEY}&units=metric`),
            fetchAirQuality(lat, lng)
        ]);

        updateWeatherDisplay(currentData, forecastData, airQualityData);
    } catch (error) {
        console.error('Weather API error:', error);
        showMessage('Error fetching weather data. Please try again.', 'error');
    }
}

async function fetchWeatherData(url) {
    const response = await fetch(url);
    return response.json();
}

async function fetchAirQuality(lat, lng) {
    try {
        const airQualityUrl = `http://api.openweathermap.org/data/2.5/air_pollution?lat=${lat}&lon=${lng}&appid=${OPENWEATHER_API_KEY}`;
        const response = await fetch(airQualityUrl);
        return response.json();
    } catch (error) {
        console.warn('Air quality data not available:', error);
        return null;
    }
}

function updateWeatherDisplay(currentData, forecastData, airQualityData) {
    if (!currentData || currentData.cod !== 200) {
        showMessage('Weather data not available for this location', 'error');
        return;
    }

    // Update location and basic info
    const locationName = currentData.name ? `${currentData.name}, ${currentData.sys.country}` : 'Selected Location';
    updateElement('selected-location', locationName);
    updateElement('current-temp', `${Math.round(currentData.main.temp)}°C`);
    updateElement('current-humidity', `${currentData.main.humidity}%`);
    updateElement('weather-condition', currentData.weather[0].description);
    updateElement('feels-like', `${Math.round(currentData.main.feels_like)}°C`);

    // Update detailed metrics
    updateElement('humidity', `${currentData.main.humidity}%`);
    updateElement('wind-speed', `${Math.round(currentData.wind.speed * 3.6)} km/h`);
    updateElement('pressure', `${currentData.main.pressure} hPa`);
    updateElement('visibility', `${(currentData.visibility / 1000).toFixed(1)} km`);
    updateElement('precipitation', currentData.rain ? `${currentData.rain['1h'] || 0} mm` : '0 mm');
    updateElement('cloud-cover', `${currentData.clouds.all}%`);

    // Air quality
    if (airQualityData?.list?.[0]) {
        const aqi = airQualityData.list[0].main.aqi;
        const aqiLabels = ['Good', 'Fair', 'Moderate', 'Poor', 'Very Poor'];
        updateElement('air-quality', aqiLabels[aqi - 1] || '--');
    } else {
        updateElement('air-quality', '--');
    }

    updateHourlyForecast(forecastData);
    checkWeatherAlerts(currentData);
}

function updateHourlyForecast(forecastData) {
    const container = document.getElementById('hourly-forecast');
    if (!forecastData?.list) {
        container.innerHTML = '<div class="text-xs text-gray-500">Forecast not available</div>';
        return;
    }

    container.innerHTML = '';
    const forecasts = forecastData.list.slice(0, 8);

    forecasts.forEach(forecast => {
        const time = new Date(forecast.dt * 1000);
        const temp = Math.round(forecast.main.temp);
        const icon = getWeatherIcon(forecast.weather[0].main);

        const item = document.createElement('div');
        item.className = 'flex items-center justify-between text-xs py-1.5 px-2 hover:bg-blue-50 rounded';
        item.innerHTML = `
            <span class="text-gray-600 font-medium">${time.getHours().toString().padStart(2, '0')}:00</span>
            <span class="text-lg">${icon}</span>
            <span class="text-gray-800 font-medium">${temp}°</span>
        `;
        container.appendChild(item);
    });
}

function getWeatherIcon(condition) {
    const icons = {
        'Clear': '☀️', 'Clouds': '☁️', 'Rain': '🌧️', 'Drizzle': '🌦️',
        'Thunderstorm': '⛈️', 'Snow': '❄️', 'Mist': '🌫️', 'Fog': '🌫️', 'Haze': '🌫️'
    };
    return icons[condition] || '🌤️';
}

function checkWeatherAlerts(currentData) {
    const alertsContainer = document.getElementById('weather-alerts');
    const alertMessage = document.getElementById('alert-message');

    let alertText = '';
    if (currentData.wind?.speed > 10) {
        alertText = `Strong winds: ${Math.round(currentData.wind.speed * 3.6)} km/h`;
    } else if (currentData.main.humidity > 90) {
        alertText = 'High humidity levels detected';
    } else if (currentData.visibility < 1000) {
        alertText = 'Poor visibility conditions';
    }

    if (alertText) {
        alertMessage.textContent = alertText;
        alertsContainer.classList.remove('hidden');
    } else {
        alertsContainer.classList.add('hidden');
    }
}

// Utility functions
function hideLoading() {
    const loading = document.getElementById('map-loading');
    if (loading) loading.style.display = 'none';
}

function hideDefault() {
    const defaultInfo = document.getElementById('default-info');
    if (defaultInfo) defaultInfo.style.display = 'none';
}

function showWeatherSection() {
    const weatherDetails = document.getElementById('weather-details');
    if (weatherDetails) weatherDetails.classList.remove('hidden');
}

function updateCoordinates(lat, lng) {
    updateElement('selected-coords', `${lat.toFixed(4)}, ${lng.toFixed(4)}`);
    updateElement('selected-time', new Date().toLocaleString());
}

function showLoadingState() {
    const elements = ['current-temp', 'current-humidity', 'weather-condition', 'humidity', 'wind-speed', 'pressure', 'visibility', 'air-quality'];
    elements.forEach(id => updateElement(id, '...'));
}

function updateElement(id, value) {
    const element = document.getElementById(id);
    if (element) element.textContent = value;
}

function showMessage(message, type = 'info') {
    const messageDiv = document.createElement('div');
    const bgColor = type === 'error' ? 'bg-red-500' : type === 'warning' ? 'bg-yellow-500' : 'bg-blue-500';
    messageDiv.className = `fixed top-4 right-4 ${bgColor} text-white px-4 py-2 rounded-lg shadow-lg z-50 transition-opacity duration-300`;
    messageDiv.textContent = message;

    document.body.appendChild(messageDiv);
    setTimeout(() => {
        messageDiv.style.opacity = '0';
        setTimeout(() => messageDiv.remove(), 300);
    }, 5000);
}

function refreshWeatherData() {
    if (currentMarker) {
        const latlng = currentMarker.getLatLng();
        showWeatherDetails(latlng.lat, latlng.lng);
        showMessage('Weather data refreshed!', 'info');
    } else {
        showMessage('Please select a location first', 'warning');
    }
}

// Admin functions
function initAdminFeatures() {
    const adminElements = [
        ['alert-mode-toggle', 'click', toggleAlertMode],
        ['close-alert-overlay', 'click', () => toggleAlertOverlay(false)],
        ['send-quick-alert', 'click', sendAlert],
        ['cancel-quick-alert', 'click', () => toggleAlertOverlay(false)],
        ['create-alert-btn', 'click', () => selectedLocation ? toggleAlertOverlay(true) : showMessage('Please select a location first.', 'error')],
        ['view-users-btn', 'click', () => selectedLocation ? (showMessage('User management feature coming soon.', 'info'), updateUsersInArea()) : showMessage('Please select a location first.', 'error')]
    ];

    adminElements.forEach(([id, event, handler]) => {
        const element = document.getElementById(id);
        if (element) element.addEventListener(event, handler);
    });
}

function toggleAlertMode() {
    alertMode = !alertMode;
    const btn = document.getElementById('alert-mode-toggle');

    if (alertMode) {
        btn.classList.add('alert-mode-active');
        btn.textContent = '🚨 Alert Mode ON';
        showMessage('Alert mode activated. Click on map to create alerts.', 'info');
    } else {
        btn.classList.remove('alert-mode-active');
        btn.textContent = '🚨 Alert Mode';
        toggleAlertOverlay(false);
        showMessage('Alert mode deactivated.', 'info');
    }
}

function toggleAlertOverlay(show) {
    const overlay = document.getElementById('alert-creation-overlay');
    if (overlay) overlay.classList.toggle('hidden', !show);
}

function sendAlert() {
    const alertMessage = document.getElementById('quick-alert-message')?.value;

    if (!alertMessage?.trim()) {
        showMessage('Please enter an alert message.', 'error');
        return;
    }

    if (!selectedLocation) {
        showMessage('Please select a location on the map.', 'error');
        return;
    }

    showMessage('Sending alert...', 'info');
    setTimeout(() => {
        toggleAlertOverlay(false);
        showMessage('Alert sent successfully!', 'info');
        document.getElementById('quick-alert-message').value = '';
    }, 1500);
}

function updateUsersInArea() {
    const usersElement = document.getElementById('users-in-area');
    if (usersElement && selectedLocation) {
        // In a real application, this would fetch actual user count from your database
        // For now, show a placeholder until real user data is implemented
        usersElement.textContent = `-- users`;
    }
}

// Event listeners
document.addEventListener('DOMContentLoaded', function() {
    if (!document.getElementById('weather-map')) return;

    initMap();

    // Main controls
    const controls = [
        ['location-search', 'keypress', e => e.key === 'Enter' && e.target.value.trim() && (searchLocation(e.target.value.trim()), e.target.value = '')],
        ['weather-layer-select', 'change', e => addWeatherTileLayer(e.target.value)],
        ['current-location-btn', 'click', getCurrentLocation],
        ['refresh-btn', 'click', refreshWeatherData]
    ];

    controls.forEach(([id, event, handler]) => {
        const element = document.getElementById(id);
        if (element) element.addEventListener(event, handler);
    });

    initAdminFeatures();
});