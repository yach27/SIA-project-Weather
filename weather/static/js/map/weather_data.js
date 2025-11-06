/**
 * Weather Data Module
 * Handles fetching and displaying weather information
 */

const WeatherData = {
    /**
     * Fetch and display weather details for a location
     */
    async showWeatherDetails(lat, lng) {
        try {
            // Show loading state and update coordinates
            MapUtils.showLoadingState();
            MapUtils.updateCoordinates(lat, lng);

            const apiKey = MapConfig.OPENWEATHER_API_KEY;
            if (apiKey === "YOUR_API_KEY_HERE") {
                MapUtils.showMessage('Please set your OpenWeatherMap API key to get real weather data', 'error');
                return;
            }

            const baseUrl = MapConfig.OPENWEATHER_BASE_URL;

            // Fetch all weather data in parallel
            const [currentData, forecastData, airQualityData] = await Promise.all([
                this.fetchWeatherData(`${baseUrl}/weather?lat=${lat}&lon=${lng}&appid=${apiKey}&units=metric`),
                this.fetchWeatherData(`${baseUrl}/forecast?lat=${lat}&lon=${lng}&appid=${apiKey}&units=metric`),
                this.fetchAirQuality(lat, lng)
            ]);

            this.updateWeatherDisplay(currentData, forecastData, airQualityData);
        } catch (error) {
            console.error('Weather API error:', error);
            MapUtils.showMessage('Error fetching weather data. Please try again.', 'error');
        }
    },

    /**
     * Fetch weather data from API
     */
    async fetchWeatherData(url) {
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    },

    /**
     * Fetch air quality data
     */
    async fetchAirQuality(lat, lng) {
        try {
            const apiKey = MapConfig.OPENWEATHER_API_KEY;
            const airQualityUrl = `http://api.openweathermap.org/data/2.5/air_pollution?lat=${lat}&lon=${lng}&appid=${apiKey}`;
            const response = await fetch(airQualityUrl);
            return response.json();
        } catch (error) {
            console.warn('Air quality data not available:', error);
            return null;
        }
    },


    /**
     * Update UI with weather data
     */
    updateWeatherDisplay(currentData, forecastData, airQualityData) {
        if (!currentData || currentData.cod !== 200) {
            MapUtils.showMessage('Weather data not available for this location', 'error');
            return;
        }

        // Update location and basic info
        const locationName = currentData.name
            ? `${currentData.name}, ${currentData.sys.country}`
            : 'Selected Location';

        MapUtils.updateElement('selected-location', locationName);
        MapUtils.updateElement('current-temp', `${Math.round(currentData.main.temp)}°C`);
        MapUtils.updateElement('current-humidity', `${currentData.main.humidity}%`);
        MapUtils.updateElement('weather-condition', currentData.weather[0].description);
        MapUtils.updateElement('feels-like', `${Math.round(currentData.main.feels_like)}°C`);

        // Update detailed metrics
        MapUtils.updateElement('humidity', `${currentData.main.humidity}%`);
        MapUtils.updateElement('wind-speed', `${Math.round(currentData.wind.speed * 3.6)} km/h`);
        MapUtils.updateElement('pressure', `${currentData.main.pressure} hPa`);
        MapUtils.updateElement('visibility', `${(currentData.visibility / 1000).toFixed(1)} km`);
        MapUtils.updateElement('precipitation', currentData.rain ? `${currentData.rain['1h'] || 0} mm` : '0 mm');
        MapUtils.updateElement('cloud-cover', `${currentData.clouds.all}%`);

        // UV Index - Use calculated estimate based on location and weather
        const uvIndex = this.calculateUVIndex(currentData);
        MapUtils.updateElement('uv-index', uvIndex);

        // Air quality
        if (airQualityData?.list?.[0]) {
            const aqi = airQualityData.list[0].main.aqi;
            const aqiLabels = ['Good', 'Fair', 'Moderate', 'Poor', 'Very Poor'];
            MapUtils.updateElement('air-quality', aqiLabels[aqi - 1] || '--');
        } else {
            MapUtils.updateElement('air-quality', '--');
        }

        // Update hourly forecast
        this.updateHourlyForecast(forecastData);

        // Check for weather alerts
        this.checkWeatherAlerts(currentData);
    },

    /**
     * Update hourly forecast display
     */
    updateHourlyForecast(forecastData) {
        const container = document.getElementById('hourly-forecast');
        if (!container) return;

        if (!forecastData?.list) {
            container.innerHTML = '<div class="text-xs text-gray-500">Forecast not available</div>';
            return;
        }

        container.innerHTML = '';
        const forecasts = forecastData.list.slice(0, 8);

        forecasts.forEach(forecast => {
            const time = new Date(forecast.dt * 1000);
            const temp = Math.round(forecast.main.temp);
            const icon = this.getWeatherIcon(forecast.weather[0].main);

            const item = document.createElement('div');
            item.className = 'flex items-center justify-between text-xs py-1.5 px-2 hover:bg-blue-50 rounded transition-colors';
            item.innerHTML = `
                <span class="text-gray-600 font-medium">${time.getHours().toString().padStart(2, '0')}:00</span>
                <span class="text-lg">${icon}</span>
                <span class="text-gray-800 font-medium">${temp}°</span>
            `;
            container.appendChild(item);
        });
    },

    /**
     * Get weather icon emoji
     */
    getWeatherIcon(condition) {
        const icons = {
            'Clear': '☀️',
            'Clouds': '☁️',
            'Rain': '🌧️',
            'Drizzle': '🌦️',
            'Thunderstorm': '⛈️',
            'Snow': '❄️',
            'Mist': '🌫️',
            'Fog': '🌫️',
            'Haze': '🌫️'
        };
        return icons[condition] || '🌤️';
    },

    /**
     * Calculate UV Index based on location and weather conditions
     */
    calculateUVIndex(currentData) {
        const clouds = currentData.clouds?.all || 0;
        const lat = currentData.coord?.lat || 0;
        const absLat = Math.abs(lat);

        // Base UV by latitude (assume midday for current conditions)
        let baseUV = 0;

        // Tropical regions (0-23°) - High UV
        if (absLat < 23) {
            baseUV = 7;
        }
        // Subtropical (23-40°) - Moderate to High UV
        else if (absLat < 40) {
            baseUV = 5;
        }
        // Temperate (40-66°) - Moderate UV
        else if (absLat < 66) {
            baseUV = 3;
        }
        // Polar (66°+) - Low UV
        else {
            baseUV = 2;
        }

        // Reduce by cloud cover (heavy clouds can reduce UV by 50-80%)
        const cloudFactor = 1 - (clouds / 150);
        let uv = Math.round(baseUV * cloudFactor);

        // Ensure UV is within realistic range
        uv = Math.min(11, Math.max(1, uv));

        // Get level description
        let level = 'Low';
        if (uv >= 11) level = 'Extreme';
        else if (uv >= 8) level = 'Very High';
        else if (uv >= 6) level = 'High';
        else if (uv >= 3) level = 'Moderate';

        return `${uv} (${level})`;
    },


    /**
     * Check and display weather alerts
     */
    checkWeatherAlerts(currentData) {
        const alertsContainer = document.getElementById('weather-alerts');
        const alertMessage = document.getElementById('alert-message');

        if (!alertsContainer || !alertMessage) return;

        let alertText = '';

        // Check for severe weather conditions
        if (currentData.wind?.speed > 10) {
            alertText = `⚠️ Strong winds: ${Math.round(currentData.wind.speed * 3.6)} km/h`;
        } else if (currentData.main.humidity > 90) {
            alertText = '💧 High humidity levels detected';
        } else if (currentData.visibility < 1000) {
            alertText = '🌫️ Poor visibility conditions';
        } else if (currentData.main.temp > 35) {
            alertText = '🔥 Extreme heat warning';
        } else if (currentData.main.temp < 5) {
            alertText = '❄️ Cold weather alert';
        }

        if (alertText) {
            alertMessage.textContent = alertText;
            alertsContainer.classList.remove('hidden');
        } else {
            alertsContainer.classList.add('hidden');
        }
    }
};

// Export for use in other modules
window.WeatherData = WeatherData;
