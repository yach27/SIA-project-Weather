/**
 * Map Controls Module
 * Handles map interactions, search, location services, and click events
 */

const MapControls = {
    /**
     * Get user's current location and center map
     */
    getCurrentLocation() {
        if (!navigator.geolocation) {
            MapUtils.showMessage('Geolocation is not supported by your browser', 'error');
            return;
        }

        navigator.geolocation.getCurrentPosition(
            (position) => {
                const { latitude: lat, longitude: lng } = position.coords;
                const map = MapConfig.map;

                if (map) {
                    // Center map on user's location
                    map.setView([lat, lng], 12);

                    // Remove existing marker if any
                    if (MapConfig.currentMarker) {
                        map.removeLayer(MapConfig.currentMarker);
                    }

                    // Add marker at user's current location
                    MapConfig.currentMarker = L.marker([lat, lng]).addTo(map);
                    MapConfig.selectedLocation = { lat, lng };

                    // Show weather popup
                    this.showWeatherPopup();

                    // Fetch and display weather data
                    WeatherData.showWeatherDetails(lat, lng);

                    MapUtils.showMessage('Located your position!', 'success');
                }
            },
            (error) => {
                console.error('Geolocation error:', error);
                MapUtils.showMessage('Unable to get location. Using default view.', 'warning');
            }
        );
    },

    /**
     * Handle map click events
     */
    onMapClick(e) {
        const { lat, lng } = e.latlng;
        const map = MapConfig.map;

        // Remove existing marker
        if (MapConfig.currentMarker && map) {
            map.removeLayer(MapConfig.currentMarker);
        }

        // Add new marker
        MapConfig.currentMarker = L.marker([lat, lng]).addTo(map);
        MapConfig.selectedLocation = { lat, lng };

        // Show weather info popup
        this.showWeatherPopup();

        // Fetch and display weather data
        WeatherData.showWeatherDetails(lat, lng);

        // Update users in area (admin feature)
        this.updateUsersInArea();

        // If in alert mode, show alert overlay
        if (MapConfig.alertMode) {
            AdminFeatures.toggleAlertOverlay(true);
        }
    },

    /**
     * Show weather info popup
     */
    showWeatherPopup() {
        const popup = document.getElementById('weather-info-popup');
        if (popup) {
            popup.classList.remove('hidden');
        }
    },

    /**
     * Hide weather info popup
     */
    hideWeatherPopup() {
        const popup = document.getElementById('weather-info-popup');
        if (popup) {
            popup.classList.add('hidden');
        }
    },

    /**
     * Search for a location by name
     */
    async searchLocation(query) {
        if (!query.trim()) {
            MapUtils.showMessage('Please enter a location to search', 'warning');
            return;
        }

        const apiKey = MapConfig.OPENWEATHER_API_KEY;
        if (apiKey === "YOUR_API_KEY_HERE") {
            MapUtils.showMessage('Please set your API key to use search functionality', 'error');
            return;
        }

        try {
            MapUtils.showMessage('Searching...', 'info');

            const geocodeUrl = `http://api.openweathermap.org/geo/1.0/direct?q=${encodeURIComponent(query)}&limit=1&appid=${apiKey}`;
            const response = await fetch(geocodeUrl);
            const data = await response.json();

            if (data && data.length > 0) {
                const location = data[0];
                const map = MapConfig.map;

                if (map) {
                    map.setView([location.lat, location.lon], 10);

                    // Remove old marker
                    if (MapConfig.currentMarker) {
                        map.removeLayer(MapConfig.currentMarker);
                    }

                    // Add new marker
                    MapConfig.currentMarker = L.marker([location.lat, location.lon]).addTo(map);

                    // Show weather details
                    WeatherData.showWeatherDetails(location.lat, location.lon);
                    MapUtils.showMessage(`Found: ${location.name}, ${location.country}`, 'info');
                }
            } else {
                MapUtils.showMessage('Location not found. Please try a different search term.', 'error');
            }
        } catch (error) {
            console.error('Geocoding error:', error);
            MapUtils.showMessage('Error searching for location. Please try again.', 'error');
        }
    },

    /**
     * Refresh weather data for current location
     */
    refreshWeatherData() {
        if (MapConfig.currentMarker) {
            const latlng = MapConfig.currentMarker.getLatLng();
            WeatherData.showWeatherDetails(latlng.lat, latlng.lng);
            MapUtils.showMessage('Weather data refreshed!', 'info');
        } else {
            MapUtils.showMessage('Please select a location first', 'warning');
        }
    },

    /**
     * Update users count in selected area (placeholder for admin feature)
     */
    updateUsersInArea() {
        const usersElement = document.getElementById('users-in-area');
        if (usersElement && MapConfig.selectedLocation) {
            // In a real application, this would fetch actual user count from database
            usersElement.textContent = `-- users`;
        }
    },

    /**
     * Setup all map event listeners
     */
    setupEventListeners() {
        const map = MapConfig.map;
        if (!map) return;

        // Map click event
        map.on('click', this.onMapClick.bind(this));

        // Search input
        const searchInput = document.getElementById('location-search');
        if (searchInput) {
            searchInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && e.target.value.trim()) {
                    this.searchLocation(e.target.value.trim());
                    e.target.value = '';
                }
            });
        }

        // Weather layer selector
        const layerSelect = document.getElementById('weather-layer-select');
        if (layerSelect) {
            layerSelect.addEventListener('change', (e) => {
                WeatherOverlays.addWeatherLayer(e.target.value);
            });
        }

        // Current location button
        const currentLocationBtn = document.getElementById('current-location-btn');
        if (currentLocationBtn) {
            currentLocationBtn.addEventListener('click', () => {
                this.getCurrentLocation();
            });
        }

        // Refresh button
        const refreshBtn = document.getElementById('refresh-btn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => {
                this.refreshWeatherData();
            });
        }

        console.log('Map event listeners initialized');
    }
};

// Export for use in other modules
window.MapControls = MapControls;
