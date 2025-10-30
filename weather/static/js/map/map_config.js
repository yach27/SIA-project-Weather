/**
 * Map Configuration
 * Central configuration for weather map
 */

const MapConfig = {
    // API Configuration
    OPENWEATHER_API_KEY: window.OPENWEATHER_API_KEY_FROM_ENV || "c58e8978703203f1a7ad55379a588e2c",
    OPENWEATHER_BASE_URL: "https://api.openweathermap.org/data/2.5",

    // Default Map Settings
    DEFAULT_CENTER: [14.651, 121.0437], // Philippines
    DEFAULT_ZOOM: 6,
    MAX_ZOOM: 19,

    // Map State
    map: null,
    currentMarker: null,
    weatherTileLayer: null,
    alertMode: false,
    selectedLocation: null,
    currentBaseLayer: 'streets'
};

// Export for use in other modules
window.MapConfig = MapConfig;
