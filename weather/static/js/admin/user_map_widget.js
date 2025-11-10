// User Location Map Widget
document.addEventListener('DOMContentLoaded', function() {
    let userMap = null;
    let userMarkers = [];

    // Initialize map
    function initMap() {
        userMap = L.map('admin-chat-user-map', {
            zoomControl: true,
            attributionControl: false
        }).setView([14.5995, 120.9842], 6); // Philippines center

        // Add tile layer
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 18
        }).addTo(userMap);

        console.log('Chat user map initialized');
        loadUserLocations();
    }

    // Load user locations from API
    async function loadUserLocations() {
        const loadingEl = document.getElementById('chat-map-loading');
        if (loadingEl) loadingEl.classList.remove('hidden');

        try {
            const response = await fetch('/api/admin/user-locations/');
            const data = await response.json();

            if (data.success) {
                clearMarkers();
                displayUsers(data.locations);
                updateUserCount(data.locations.length);
                displayUserList(data.locations);
            }
        } catch (error) {
            console.error('Failed to load user locations:', error);
        } finally {
            if (loadingEl) loadingEl.classList.add('hidden');
        }
    }

    // Clear existing markers
    function clearMarkers() {
        userMarkers.forEach(marker => userMap.removeLayer(marker));
        userMarkers = [];
    }

    // Display users on map
    function displayUsers(locations) {
        if (!locations.length) return;

        const bounds = [];

        locations.forEach(user => {
            const icon = L.divIcon({
                className: 'user-marker-icon',
                html: `<div style="
                    background: #10b981;
                    width: 22px;
                    height: 22px;
                    border-radius: 50%;
                    border: 2px solid white;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.3);
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    color: white;
                    font-weight: bold;
                    font-size: 11px;
                    cursor: pointer;
                ">
                    ${user.username.charAt(0).toUpperCase()}
                </div>`,
                iconSize: [22, 22],
                iconAnchor: [11, 11]
            });

            const marker = L.marker([user.latitude, user.longitude], { icon })
                .bindPopup(`
                    <div style="padding: 8px; min-width: 160px;">
                        <h4 style="margin: 0 0 6px 0; font-size: 14px; font-weight: 600;">
                            ${user.username}
                        </h4>
                        <p style="margin: 0; font-size: 12px; color: #6b7280;">
                            ${user.email}
                        </p>
                        <p style="margin: 6px 0 0 0; font-size: 11px; color: #d1d5db;">
                            Last seen: ${new Date(user.updated_at).toLocaleString()}
                        </p>
                    </div>
                `)
                .addTo(userMap);

            userMarkers.push(marker);
            bounds.push([user.latitude, user.longitude]);
        });

        // Fit map to show all markers
        if (bounds.length > 0) {
            userMap.fitBounds(bounds, { padding: [30, 30] });
        }
    }

    // Update user count
    function updateUserCount(count) {
        const countEl = document.getElementById('active-users-count');
        if (countEl) {
            countEl.textContent = count;
        }
    }

    // Display user list
    function displayUserList(locations) {
        const userListEl = document.getElementById('user-list');
        if (!userListEl) return;

        if (!locations.length) {
            userListEl.innerHTML = '<p class="text-xs text-gray-500 text-center">No users online</p>';
            return;
        }

        userListEl.innerHTML = locations.map(user => `
            <div class="flex items-center justify-between p-1.5 bg-white rounded hover:bg-gray-50 transition-colors">
                <div class="flex items-center space-x-2">
                    <div class="w-5 h-5 bg-green-500 rounded-full flex items-center justify-center">
                        <span class="text-white text-xs font-medium">${user.username.charAt(0).toUpperCase()}</span>
                    </div>
                    <span class="text-xs font-medium text-gray-900">${user.username}</span>
                </div>
                <span class="text-xs text-gray-400">${new Date(user.updated_at).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</span>
            </div>
        `).join('');
    }

    // Refresh button
    const refreshBtn = document.getElementById('refresh-user-map');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', () => {
            loadUserLocations();
        });
    }

    // Toggle button
    const toggleBtn = document.getElementById('toggle-chat-map');
    const mapContent = document.getElementById('chat-map-content');
    let isCollapsed = false;

    if (toggleBtn && mapContent) {
        toggleBtn.addEventListener('click', () => {
            isCollapsed = !isCollapsed;

            if (isCollapsed) {
                mapContent.style.display = 'none';
                toggleBtn.innerHTML = '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 15l7-7 7 7"></path></svg>';
            } else {
                mapContent.style.display = 'block';
                toggleBtn.innerHTML = '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path></svg>';
                setTimeout(() => userMap.invalidateSize(), 300);
            }
        });
    }

    // Function to zoom to a specific user's location
    window.zoomToUser = function(username) {
        const marker = userMarkers.find(m => {
            const popupContent = m.getPopup().getContent();
            return popupContent.includes(username);
        });

        if (marker) {
            const latlng = marker.getLatLng();
            userMap.setView(latlng, 14, { animate: true }); // Zoom level 14 for detailed view
            marker.openPopup();
        }
    };

    // Initialize map
    initMap();

    // Auto-refresh every 30 seconds
    setInterval(loadUserLocations, 30000);
});
