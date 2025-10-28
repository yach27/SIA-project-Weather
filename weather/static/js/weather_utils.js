/**
 * Reusable Weather Utility Functions
 * Used across dashboard, admin, and other weather-related pages
 */

// Get user's current location and execute callback
function getUserLocation(callback, fallbackLat = 14.5995, fallbackLon = 120.9842) {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            (position) => {
                callback(position.coords.latitude, position.coords.longitude);
            },
            (error) => {
                console.error('Geolocation error:', error.message);
                callback(fallbackLat, fallbackLon);
            }
        );
    } else {
        console.log('Geolocation not supported');
        callback(fallbackLat, fallbackLon);
    }
}

// Fetch weather data from OpenWeather API
async function fetchWeatherData(lat, lon, apiKey) {
    try {
        const response = await fetch(
            `https://api.openweathermap.org/data/2.5/weather?lat=${lat}&lon=${lon}&units=metric&appid=${apiKey}`
        );
        const data = await response.json();

        if (data && data.main) {
            return {
                location: `${data.name}, ${data.sys.country}`,
                temperature: Math.round(data.main.temp),
                feels_like: Math.round(data.main.feels_like),
                condition: data.weather[0].description,
                condition_main: data.weather[0].main,
                humidity: data.main.humidity,
                wind_speed: Math.round(data.wind.speed * 3.6), // Convert m/s to km/h
                wind_deg: data.wind.deg,
                pressure: data.main.pressure,
                visibility: (data.visibility / 1000).toFixed(1), // Convert m to km
                coordinates: { lat: data.coord.lat, lon: data.coord.lon },
                icon: data.weather[0].icon
            };
        }
        return null;
    } catch (error) {
        console.error('Error fetching weather:', error);
        return null;
    }
}

// Helper: Get humidity status
function getHumidityStatus(humidity) {
    if (humidity < 30) return 'Low';
    if (humidity < 60) return 'Normal';
    if (humidity < 80) return 'High';
    return 'Very High';
}

// Helper: Get wind direction
function getWindDirection(deg) {
    const directions = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'];
    const index = Math.round(deg / 45) % 8;
    return directions[index];
}

// Helper: Get pressure status
function getPressureStatus(pressure) {
    if (pressure < 1000) return 'Low';
    if (pressure < 1020) return 'Normal';
    return 'High';
}

// Helper: Get visibility status
function getVisibilityStatus(visibility) {
    if (visibility < 2) return 'Poor';
    if (visibility < 10) return 'Moderate';
    return 'Good';
}

// Get CSRF token for POST requests
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
