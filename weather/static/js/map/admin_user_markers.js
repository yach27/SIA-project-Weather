// Admin User Markers - Display user locations on admin map (Leaflet version)
class AdminUserMarkers {
    constructor(map) {
        this.map = map;
        this.userMarkers = [];
        this.loadUserLocations();
        // Refresh every 30 seconds
        setInterval(() => this.loadUserLocations(), 30000);
    }

    async loadUserLocations() {
        try {
            const response = await fetch('/api/admin/user-locations/');
            const data = await response.json();

            if (data.success) {
                this.clearMarkers();
                this.displayUsers(data.locations);
                console.log(`Loaded ${data.locations.length} user locations`);
            }
        } catch (error) {
            console.error('Failed to load user locations:', error);
        }
    }

    clearMarkers() {
        this.userMarkers.forEach(marker => this.map.removeLayer(marker));
        this.userMarkers = [];
    }

    displayUsers(locations) {
        locations.forEach(user => {
            // Create custom icon with user initial
            const icon = L.divIcon({
                className: 'user-marker-icon',
                html: `
                    <div style="
                        background-color: #3b82f6;
                        width: 36px;
                        height: 36px;
                        border-radius: 50%;
                        border: 3px solid white;
                        box-shadow: 0 2px 6px rgba(0,0,0,0.4);
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        color: white;
                        font-weight: bold;
                        font-size: 16px;
                        cursor: pointer;
                    ">
                        ${user.username.charAt(0).toUpperCase()}
                    </div>
                `,
                iconSize: [36, 36],
                iconAnchor: [18, 18]
            });

            // Create marker
            const marker = L.marker([user.latitude, user.longitude], { icon })
                .bindPopup(`
                    <div style="padding: 12px; min-width: 200px;">
                        <h3 style="margin: 0 0 8px 0; font-size: 14px; font-weight: 600; color: #1f2937;">
                            ${user.username}
                        </h3>
                        <p style="margin: 0; font-size: 12px; color: #6b7280;">
                            ${user.email}
                        </p>
                        ${user.location_name ? `
                            <p style="margin: 4px 0 0 0; font-size: 11px; color: #9ca3af;">
                                📍 ${user.location_name}
                            </p>
                        ` : ''}
                        <p style="margin: 8px 0 12px 0; font-size: 10px; color: #d1d5db;">
                            Last seen: ${new Date(user.updated_at).toLocaleString()}
                        </p>
                        <button
                            onclick="sendWeatherAlert('${user.username}', '${user.email}', ${user.latitude}, ${user.longitude})"
                            style="
                                width: 100%;
                                background: linear-gradient(to right, #ef4444, #dc2626);
                                color: white;
                                padding: 8px 12px;
                                border: none;
                                border-radius: 6px;
                                font-size: 12px;
                                font-weight: 600;
                                cursor: pointer;
                                display: flex;
                                align-items: center;
                                justify-content: center;
                                gap: 6px;
                                transition: all 0.2s;
                            "
                            onmouseover="this.style.background='linear-gradient(to right, #dc2626, #b91c1c)'"
                            onmouseout="this.style.background='linear-gradient(to right, #ef4444, #dc2626)'"
                        >
                            <svg style="width: 14px; height: 14px;" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.5 0L4.314 16.5c-.77.833.192 2.5 1.732 2.5z"></path>
                            </svg>
                            Send Weather Alert
                        </button>
                    </div>
                `, { maxWidth: 250 })
                .addTo(this.map);

            this.userMarkers.push(marker);
        });
    }
}

// Global function to send weather alert
window.sendWeatherAlert = async function(username, email, lat, lon) {
    // Fetch current weather data for the user's location
    try {
        const weatherResponse = await fetch(`https://api.openweathermap.org/data/2.5/weather?lat=${lat}&lon=${lon}&appid=${window.OPENWEATHER_API_KEY_FROM_ENV}&units=metric`);
        const weatherData = await weatherResponse.json();

        if (!weatherResponse.ok) {
            alert('Failed to fetch weather data');
            return;
        }

        const temp = weatherData.main.temp;
        const condition = weatherData.weather[0].main;
        const description = weatherData.weather[0].description;

        // Determine alert message based on weather
        let alertMessage = '';
        let alertType = 'info';
        let alertLevel = '';
        let alertIcon = '⚠️';
        let weatherIcon = getWeatherIcon(condition);

        if (temp >= 35) {
            alertType = 'danger';
            alertLevel = 'Extreme Heat';
            alertIcon = '🔥';
            alertMessage = `⚠️ EXTREME HEAT WARNING\n\nTemperature: ${Math.round(temp)}°C\nCondition: ${description}\n\nStay indoors, drink plenty of water, and avoid prolonged sun exposure!`;
        } else if (temp >= 30) {
            alertType = 'warning';
            alertLevel = 'High Temperature';
            alertIcon = '☀️';
            alertMessage = `☀️ HIGH TEMPERATURE ALERT\n\nTemperature: ${Math.round(temp)}°C\nCondition: ${description}\n\nStay cool and drink plenty of water.`;
        } else if (temp <= 10) {
            alertType = 'warning';
            alertLevel = 'Cold Weather';
            alertIcon = '❄️';
            alertMessage = `❄️ COLD WEATHER ALERT\n\nTemperature: ${Math.round(temp)}°C\nCondition: ${description}\n\nDress warmly and protect yourself from the cold.`;
        } else if (condition === 'Rain' || condition === 'Thunderstorm') {
            alertType = 'warning';
            alertLevel = condition;
            alertIcon = condition === 'Thunderstorm' ? '⛈️' : '🌧️';
            alertMessage = `🌧️ ${condition.toUpperCase()} ALERT\n\nTemperature: ${Math.round(temp)}°C\nCondition: ${description}\n\nCarry an umbrella and be cautious when traveling.`;
        } else {
            alertLevel = 'Normal';
            alertIcon = '✅';
            alertMessage = `🌤️ WEATHER UPDATE\n\nTemperature: ${Math.round(temp)}°C\nCondition: ${description}\n\nStay informed and plan accordingly.`;
        }

        // Show modal with weather data
        showWeatherAlertModal({
            username,
            email,
            lat,
            lon,
            temp,
            condition,
            description,
            alertMessage,
            alertType,
            alertLevel,
            alertIcon,
            weatherIcon
        });

    } catch (error) {
        console.error('Error sending alert:', error);
        alert('Failed to send weather alert. Please try again.');
    }
};

// Export for use in map initialization
window.AdminUserMarkers = AdminUserMarkers;
