// Mini Map for User Locations in Admin Weather Map
class UserLocationsMiniMap {
    constructor() {
        this.minimap = null;
        this.markers = [];
        this.isCollapsed = false;
        this.init();
    }

    init() {
        // Initialize mini map
        const container = document.getElementById('user-locations-minimap');
        if (!container) return;

        this.minimap = L.map('user-locations-minimap', {
            zoomControl: false,
            attributionControl: false,
            dragging: false,
            scrollWheelZoom: false,
            doubleClickZoom: false,
            boxZoom: false,
            keyboard: false,
            tap: false
        }).setView([14.5995, 120.9842], 6); // Philippines center

        // Add base layer
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 10
        }).addTo(this.minimap);

        // Setup toggle button
        const toggleBtn = document.getElementById('toggle-minimap');
        if (toggleBtn) {
            toggleBtn.addEventListener('click', () => this.toggle());
        }

        // Load user locations
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
                this.updateCount(data.locations.length);
            }
        } catch (error) {
            console.error('Failed to load user locations for minimap:', error);
        }
    }

    clearMarkers() {
        this.markers.forEach(marker => this.minimap.removeLayer(marker));
        this.markers = [];
    }

    displayUsers(locations) {
        if (!locations.length) return;

        const bounds = [];

        locations.forEach(user => {
            const icon = L.divIcon({
                className: 'minimap-marker',
                html: `<div style="
                    background: #3b82f6;
                    width: 20px;
                    height: 20px;
                    border-radius: 50%;
                    border: 2px solid white;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.3);
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    color: white;
                    font-size: 10px;
                    font-weight: bold;
                ">${user.username.charAt(0).toUpperCase()}</div>`,
                iconSize: [20, 20],
                iconAnchor: [10, 10]
            });

            const marker = L.marker([user.latitude, user.longitude], { icon })
                .bindTooltip(user.username, { direction: 'top', offset: [0, -10] })
                .addTo(this.minimap);

            this.markers.push(marker);
            bounds.push([user.latitude, user.longitude]);
        });

        // Fit map to show all markers
        if (bounds.length > 0) {
            this.minimap.fitBounds(bounds, { padding: [20, 20] });
        }
    }

    updateCount(count) {
        const countEl = document.getElementById('minimap-user-count');
        if (countEl) {
            countEl.textContent = count;
        }
    }

    toggle() {
        const content = document.getElementById('minimap-content');
        const toggleBtn = document.getElementById('toggle-minimap');

        if (!content || !toggleBtn) return;

        this.isCollapsed = !this.isCollapsed;

        if (this.isCollapsed) {
            content.style.display = 'none';
            toggleBtn.innerHTML = '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 15l7-7 7 7"></path></svg>';
        } else {
            content.style.display = 'block';
            toggleBtn.innerHTML = '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path></svg>';
            // Refresh map size after showing
            setTimeout(() => this.minimap.invalidateSize(), 300);
        }
    }
}

// Initialize on page load
function initMiniMap() {
    const container = document.getElementById('user-locations-minimap');
    console.log('Mini map initialization check:', {
        containerExists: !!container,
        pathname: window.location.pathname
    });

    if (container) {
        console.log('Initializing user locations mini map...');
        try {
            new UserLocationsMiniMap();
            console.log('Mini map initialized successfully');
        } catch (error) {
            console.error('Error initializing mini map:', error);
        }
    }
}

// Wait for DOM to be ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initMiniMap);
} else {
    // DOM already loaded
    initMiniMap();
}

// Also try after a brief delay as fallback
setTimeout(initMiniMap, 1000);
