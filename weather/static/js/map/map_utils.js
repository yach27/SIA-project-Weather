/**
 * Map Utilities Module
 * Helper functions for UI updates, messages, and common operations
 */

const MapUtils = {
    /**
     * Update HTML element content
     */
    updateElement(id, value) {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = value;
        }
    },

    /**
     * Show loading state for weather data
     */
    showLoadingState() {
        const elements = [
            'current-temp', 'current-humidity', 'weather-condition',
            'humidity', 'wind-speed', 'pressure', 'visibility', 'air-quality'
        ];
        elements.forEach(id => this.updateElement(id, '...'));
    },

    /**
     * Update coordinates display
     */
    updateCoordinates(lat, lng) {
        this.updateElement('selected-coords', `${lat.toFixed(4)}, ${lng.toFixed(4)}`);
        this.updateElement('selected-time', new Date().toLocaleString());
    },

    /**
     * Hide map loading indicator
     */
    hideLoading() {
        const loading = document.getElementById('map-loading');
        if (loading) {
            loading.style.display = 'none';
        }
    },

    /**
     * Hide default info message
     */
    hideDefault() {
        const defaultInfo = document.getElementById('default-info');
        if (defaultInfo) {
            defaultInfo.style.display = 'none';
        }
    },

    /**
     * Show weather details section
     */
    showWeatherSection() {
        const weatherDetails = document.getElementById('weather-details');
        if (weatherDetails) {
            weatherDetails.classList.remove('hidden');
        }
    },

    /**
     * Show notification message
     */
    showMessage(message, type = 'info') {
        const messageDiv = document.createElement('div');

        const bgColors = {
            'error': 'bg-red-500',
            'warning': 'bg-yellow-500',
            'info': 'bg-blue-500',
            'success': 'bg-green-500'
        };

        const bgColor = bgColors[type] || bgColors['info'];

        messageDiv.className = `fixed top-4 right-4 ${bgColor} text-white px-4 py-3 rounded-lg shadow-lg z-50 transition-opacity duration-300 flex items-center space-x-2`;

        const icons = {
            'error': '❌',
            'warning': '⚠️',
            'info': 'ℹ️',
            'success': '✅'
        };

        messageDiv.innerHTML = `
            <span class="text-lg">${icons[type] || icons['info']}</span>
            <span>${message}</span>
        `;

        document.body.appendChild(messageDiv);

        setTimeout(() => {
            messageDiv.style.opacity = '0';
            setTimeout(() => messageDiv.remove(), 300);
        }, 5000);
    },

    /**
     * Format timestamp to readable time
     */
    formatTime(timestamp) {
        const date = new Date(timestamp * 1000);
        return date.toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit',
            hour12: true
        });
    },

    /**
     * Format date to readable string
     */
    formatDate(timestamp) {
        const date = new Date(timestamp * 1000);
        return date.toLocaleDateString('en-US', {
            weekday: 'short',
            month: 'short',
            day: 'numeric'
        });
    },

    /**
     * Get temperature color based on value
     */
    getTemperatureColor(temp) {
        if (temp >= 35) return 'text-red-600';
        if (temp >= 30) return 'text-orange-600';
        if (temp >= 25) return 'text-yellow-600';
        if (temp >= 20) return 'text-green-600';
        if (temp >= 15) return 'text-blue-600';
        if (temp >= 10) return 'text-indigo-600';
        return 'text-purple-600';
    },

    /**
     * Debounce function for search input
     */
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
};

// Export for use in other modules
window.MapUtils = MapUtils;
