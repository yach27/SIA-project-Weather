/**
 * Map Initialization Module
 * Main entry point for weather map initialization
 */

const MapInit = {
    /**
     * Initialize the weather map
     */
    init() {
        // Create map instance
        MapConfig.map = L.map('weather-map', {
            zoomControl: true,
            attributionControl: true,
            minZoom: 3,
            maxZoom: MapConfig.MAX_ZOOM
        }).setView(MapConfig.DEFAULT_CENTER, MapConfig.DEFAULT_ZOOM);

        // Initialize and add base layers
        MapLayers.init();
        const defaultLayer = MapLayers.getLayer('streets');
        defaultLayer.addTo(MapConfig.map);

        // Add layer switcher control
        MapLayers.addLayerControl();

        // Add default weather overlay
        WeatherOverlays.addWeatherLayer('temp');

        // Setup all event listeners
        MapControls.setupEventListeners();

        // Initialize admin features (if admin page and AdminFeatures is defined)
        if (typeof AdminFeatures !== 'undefined') {
            AdminFeatures.init();
        }

        // Initialize admin user markers (if admin page and class exists)
        if (typeof AdminUserMarkers !== 'undefined' && window.location.pathname.includes('/admin-map')) {
            new AdminUserMarkers(MapConfig.map);
        }

        // Hide loading indicator
        MapUtils.hideLoading();

        // Get user's current location
        MapControls.getCurrentLocation();

        console.log('Weather map initialized successfully');
    }
};

// Auto-initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Check if map container exists
    if (!document.getElementById('weather-map')) {
        console.log('Weather map container not found');
        return;
    }

    // Initialize the map
    MapInit.init();

    // Setup close button for weather popup
    const closeBtn = document.getElementById('close-popup');
    if (closeBtn) {
        closeBtn.addEventListener('click', () => {
            MapControls.hideWeatherPopup();
        });
    }
});

// Export for use in other modules
window.MapInit = MapInit;
