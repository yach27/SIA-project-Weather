// User Location Tracker - Sends location to server when user logs in
class UserLocationTracker {
    constructor() {
        this.init();
    }

    init() {
        if ('geolocation' in navigator) {
            navigator.geolocation.getCurrentPosition(
                (position) => this.sendLocation(position),
                (error) => console.log('Location access denied:', error)
            );
        }
    }

    async sendLocation(position) {
        try {
            const lat = position.coords.latitude;
            const lon = position.coords.longitude;

            // Get location name using reverse geocoding (Nominatim API)
            let locationName = '';
            try {
                const geoResponse = await fetch(
                    `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lon}&zoom=10`
                );
                const geoData = await geoResponse.json();

                // Extract city, state, or country from response
                if (geoData.address) {
                    const addr = geoData.address;
                    locationName = addr.city || addr.town || addr.village ||
                                   addr.municipality || addr.county ||
                                   addr.state || addr.country || 'Unknown';
                }
            } catch (geoError) {
                console.log('Reverse geocoding failed, using coordinates:', geoError);
            }

            const response = await fetch('/api/user-location/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCookie('csrftoken')
                },
                body: JSON.stringify({
                    latitude: lat,
                    longitude: lon,
                    location_name: locationName
                })
            });
            const data = await response.json();
            if (data.success) {
                console.log('Location updated successfully:', locationName);
            }
        } catch (error) {
            console.error('Failed to send location:', error);
        }
    }

    getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
}

// Auto-initialize on page load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => new UserLocationTracker());
} else {
    new UserLocationTracker();
}
