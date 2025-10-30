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
            const response = await fetch('/api/user-location/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCookie('csrftoken')
                },
                body: JSON.stringify({
                    latitude: position.coords.latitude,
                    longitude: position.coords.longitude,
                    location_name: ''
                })
            });
            const data = await response.json();
            if (data.success) {
                console.log('Location updated successfully');
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
