/**
 * Map Layers Module
 * Handles different base map layers (streets, satellite, terrain, dark)
 */

const MapLayers = {
    baseLayers: {},

    /**
     * Initialize all base layers
     */
    init() {
        this.baseLayers = {
            'streets': L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '© OpenStreetMap contributors',
                maxZoom: 19
            }),
            'satellite': L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
                attribution: 'Tiles © Esri — Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community',
                maxZoom: 18
            }),
            'terrain': L.tileLayer('https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png', {
                attribution: 'Map data: © OpenStreetMap contributors, SRTM | Map style: © OpenTopoMap',
                maxZoom: 17
            }),
            'dark': L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
                attribution: '© OpenStreetMap contributors © CARTO',
                maxZoom: 19,
                subdomains: 'abcd'
            }),
            'light': L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
                attribution: '© OpenStreetMap contributors © CARTO',
                maxZoom: 19,
                subdomains: 'abcd'
            })
        };

        return this.baseLayers;
    },

    /**
     * Get a specific base layer
     */
    getLayer(layerName) {
        return this.baseLayers[layerName] || this.baseLayers['streets'];
    },

    /**
     * Switch to a different base layer
     */
    switchLayer(layerName) {
        const map = MapConfig.map;
        if (!map) return;

        // Remove current base layer
        const currentLayer = this.baseLayers[MapConfig.currentBaseLayer];
        if (currentLayer && map.hasLayer(currentLayer)) {
            map.removeLayer(currentLayer);
        }

        // Add new base layer
        const newLayer = this.getLayer(layerName);
        newLayer.addTo(map);
        MapConfig.currentBaseLayer = layerName;

        console.log(`Switched to ${layerName} map layer`);
    },

    /**
     * Add layer switcher control to map
     */
    addLayerControl() {
        const map = MapConfig.map;
        if (!map) return;

        // Create custom layer control
        const layerControl = L.control({ position: 'topright' });

        layerControl.onAdd = function() {
            const div = L.DomUtil.create('div', 'leaflet-bar leaflet-control');
            div.innerHTML = `
                <select id="map-layer-select" class="bg-white border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
                    <option value="streets">Streets</option>
                    <option value="satellite">Satellite</option>
                    <option value="terrain">Terrain</option>
                    <option value="dark">Dark</option>
                    <option value="light">Light</option>
                </select>
            `;

            // Prevent map interaction when clicking control
            L.DomEvent.disableClickPropagation(div);

            return div;
        };

        layerControl.addTo(map);

        // Add event listener for layer switching
        setTimeout(() => {
            const select = document.getElementById('map-layer-select');
            if (select) {
                select.addEventListener('change', (e) => {
                    MapLayers.switchLayer(e.target.value);
                });
            }
        }, 100);
    }
};

// Export for use in other modules
window.MapLayers = MapLayers;
