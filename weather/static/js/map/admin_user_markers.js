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
                    <div style="padding: 8px; min-width: 180px;">
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
                        <p style="margin: 8px 0 0 0; font-size: 10px; color: #d1d5db;">
                            Last seen: ${new Date(user.updated_at).toLocaleString()}
                        </p>
                    </div>
                `)
                .addTo(this.map);

            this.userMarkers.push(marker);
        });
    }
}

// Export for use in map initialization
window.AdminUserMarkers = AdminUserMarkers;
