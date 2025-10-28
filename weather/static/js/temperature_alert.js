/**
 * Temperature Alert Dialog Module
 * Fetches AI-generated temperature alerts from Django API and displays in modal
 */

/**
 * Fetch temperature alert data from Django API
 * @param {number} temperature - Temperature in Celsius
 * @param {string} location - Location name
 * @param {string} weatherCondition - Weather condition (optional)
 * @returns {Promise<object>} Alert data from API
 */
async function fetchTemperatureAlert(temperature, location, weatherCondition = null) {
    try {
        const response = await fetch('/api/temperature-alert/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                temperature: temperature,
                location: location,
                weather_condition: weatherCondition
            })
        });

        const data = await response.json();

        if (data.success && data.alert) {
            return data.alert;
        }

        return null; // No alert needed (comfortable temperature)

    } catch (error) {
        console.error('Error fetching temperature alert:', error);
        return null;
    }
}

/**
 * Show temperature alert dialog with AI-generated content
 * @param {object} alertData - Alert data from API
 */
function showTemperatureAlertDialog(alertData) {
    if (!alertData || !alertData.isExtreme) {
        return; // Don't show dialog for comfortable temperatures
    }

    const dialog = document.getElementById('temperature-alert-dialog');
    if (!dialog) {
        console.error('Temperature alert dialog element not found');
        return;
    }

    const dialogContent = document.getElementById('alert-dialog-content');
    const header = document.getElementById('alert-dialog-header');
    const icon = document.getElementById('alert-dialog-icon');
    const title = document.getElementById('alert-dialog-title');
    const subtitle = document.getElementById('alert-dialog-subtitle');
    const tempDisplay = document.getElementById('alert-temperature');
    const locationDisplay = document.getElementById('alert-location');
    const messageBox = document.getElementById('alert-message-box');
    const message = document.getElementById('alert-message');
    const recommendations = document.getElementById('alert-recommendations');
    const tempDisplayBox = document.getElementById('alert-temp-display');

    // Set header styling
    header.className = `rounded-t-lg px-4 py-3 flex items-center justify-between ${alertData.color} ${alertData.textColor}`;

    // Set icon and title
    icon.textContent = alertData.icon;
    title.textContent = `${alertData.level} Alert`;

    // Set temperature display
    tempDisplay.textContent = `${Math.round(alertData.temperature)}°C`;
    tempDisplay.className = `text-3xl font-bold ${alertData.color.replace('bg-', 'text-')}`;
    tempDisplayBox.className = `bg-white rounded-lg p-3 border-2 text-center ${alertData.borderColor || alertData.color.replace('bg-', 'border-')}`;
    locationDisplay.textContent = alertData.location;

    // Set message
    message.textContent = alertData.message;

    // Set message box color based on temperature
    if (alertData.temperature >= 30) {
        messageBox.className = 'bg-red-50 border-l-4 border-red-400 p-3 rounded';
        messageBox.querySelector('svg').className = 'w-4 h-4 text-red-400 mt-0.5 mr-2 flex-shrink-0';
        messageBox.querySelector('h4').className = 'font-semibold text-red-800 text-xs mb-1';
        messageBox.querySelector('p').className = 'text-xs text-red-700';
    } else {
        messageBox.className = 'bg-blue-50 border-l-4 border-blue-400 p-3 rounded';
        messageBox.querySelector('svg').className = 'w-4 h-4 text-blue-400 mt-0.5 mr-2 flex-shrink-0';
        messageBox.querySelector('h4').className = 'font-semibold text-blue-800 text-xs mb-1';
        messageBox.querySelector('p').className = 'text-xs text-blue-700';
    }

    // Set AI-generated recommendations
    if (alertData.recommendations && alertData.recommendations.length > 0) {
        recommendations.innerHTML = alertData.recommendations
            .map(rec => `
                <li class="flex items-start">
                    <svg class="w-3 h-3 mr-1.5 mt-0.5 text-green-500 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"></path>
                    </svg>
                    <span>${rec}</span>
                </li>
            `)
            .join('');
    } else {
        recommendations.innerHTML = '<li class="text-gray-500 text-xs">No specific recommendations available.</li>';
    }

    // Show dialog with animation
    dialog.classList.remove('hidden');
    setTimeout(() => {
        dialog.classList.add('opacity-100');
        dialogContent.classList.remove('scale-95');
        dialogContent.classList.add('scale-100');
    }, 10);
}

/**
 * Close temperature alert dialog
 * Uses Django backend to dismiss alert via session
 */
async function closeTemperatureAlertDialog() {
    const dialog = document.getElementById('temperature-alert-dialog');
    const dialogContent = document.getElementById('alert-dialog-content');

    if (!dialog || !dialogContent) return;

    // Call Django API to dismiss alert (sets session flag)
    try {
        await fetch('/api/dismiss-alert/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        console.log('Alert dismissed via Django session');
    } catch (error) {
        console.error('Error dismissing alert:', error);
    }

    // Hide with animation
    dialog.classList.remove('opacity-100');
    dialogContent.classList.remove('scale-100');
    dialogContent.classList.add('scale-95');

    setTimeout(() => {
        dialog.classList.add('hidden');
    }, 300);
}

/**
 * Check temperature and show alert if needed (Django session handles "show once")
 * @param {number} temperature - Temperature in Celsius
 * @param {string} location - Location name
 * @param {string} weatherCondition - Weather condition (optional)
 */
async function checkAndShowTemperatureAlert(temperature, location, weatherCondition = null) {
    // Django session now handles whether alert should show
    // No need for sessionStorage - backend manages this

    const alertData = await fetchTemperatureAlert(temperature, location, weatherCondition);
    if (alertData) {
        showTemperatureAlertDialog(alertData);
    }
}

// Initialize event listeners when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Close dialog on Escape key
    document.addEventListener('keydown', function(e) {
        const dialog = document.getElementById('temperature-alert-dialog');
        if (e.key === 'Escape' && dialog && !dialog.classList.contains('hidden')) {
            closeTemperatureAlertDialog();
        }
    });
});
