/**
 * Weather Overlays Module
 * Simple and clean weather layer management using OpenWeatherMap tiles
 */

const WeatherOverlays = {
    currentLayerType: null,
    currentLayer: null,

    /**
     * Add weather layer to map
     */
    addWeatherLayer(layerType = 'temp') {
        const map = MapConfig.map;
        if (!map) return;

        // Remove existing layer
        this.removeWeatherLayer();

        const apiKey = MapConfig.OPENWEATHER_API_KEY;
        if (apiKey === "YOUR_API_KEY_HERE") {
            console.warn('Please set your OpenWeatherMap API key');
            return;
        }

        this.currentLayerType = layerType;

        // Add OpenWeatherMap tile layer
        const layerUrl = `https://tile.openweathermap.org/map/${layerType}_new/{z}/{x}/{y}.png?appid=${apiKey}`;

        this.currentLayer = L.tileLayer(layerUrl, {
            opacity: 0.6,
            attribution: '© OpenWeatherMap',
            maxZoom: 19
        }).addTo(map);

        MapConfig.weatherTileLayer = this.currentLayer;
        this.updateLegend(layerType);

        console.log(`Added ${layerType} weather layer`);
    },

    /**
     * Update map legend
     */
    updateLegend(layerType) {
        document.querySelectorAll('.legend-content').forEach(legend => {
            legend.classList.add('hidden');
        });

        const selectedLegend = document.querySelector(`[data-legend="${layerType}"]`);
        if (selectedLegend) {
            selectedLegend.classList.remove('hidden');
        }
    },

    /**
     * Get available weather layers
     */
    getAvailableLayers() {
        return {
            'temp': {
                name: 'Temperature',
                description: 'Temperature overlay',
                icon: '🌡️'
            },
            'precipitation': {
                name: 'Rain',
                description: 'Precipitation',
                icon: '🌧️'
            },
            'clouds': {
                name: 'Clouds',
                description: 'Cloud coverage',
                icon: '☁️'
            },
            'wind': {
                name: 'Wind',
                description: 'Wind speed',
                icon: '💨'
            },
            'pressure': {
                name: 'Pressure',
                description: 'Atmospheric pressure',
                icon: '📊'
            }
        };
    },

    /**
     * Remove weather layer
     */
    removeWeatherLayer() {
        const map = MapConfig.map;
        if (!map) return;

        if (this.currentLayer) {
            map.removeLayer(this.currentLayer);
            this.currentLayer = null;
        }

        if (MapConfig.weatherTileLayer) {
            try {
                map.removeLayer(MapConfig.weatherTileLayer);
            } catch (e) {
                // Layer already removed
            }
            MapConfig.weatherTileLayer = null;
        }
    },

    /**
     * Toggle layer visibility
     */
    toggleWeatherLayer() {
        if (this.currentLayer) {
            const currentOpacity = this.currentLayer.options.opacity;
            this.currentLayer.setOpacity(currentOpacity === 0.6 ? 0 : 0.6);
        }
    },

    /**
     * Set layer opacity
     */
    setOpacity(opacity) {
        if (this.currentLayer) {
            this.currentLayer.setOpacity(opacity);
        }
    }
};

// Export
window.WeatherOverlays = WeatherOverlays;
