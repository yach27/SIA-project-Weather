// Weather Alert Modal Functions

// Helper function to get weather icon
function getWeatherIcon(condition) {
    const icons = {
        'Clear': '☀️',
        'Clouds': '☁️',
        'Rain': '🌧️',
        'Drizzle': '🌦️',
        'Thunderstorm': '⛈️',
        'Snow': '❄️',
        'Mist': '🌫️',
        'Fog': '🌫️',
        'Haze': '🌫️'
    };
    return icons[condition] || '🌤️';
}

// Show weather alert modal
function showWeatherAlertModal(data) {
    const modal = document.getElementById('weather-alert-modal');
    const modalContent = document.getElementById('modal-content');

    // Populate modal with data
    document.getElementById('modal-user-initial').textContent = data.username.charAt(0).toUpperCase();
    document.getElementById('modal-username').textContent = data.username;
    document.getElementById('modal-email').textContent = data.email;
    document.getElementById('modal-weather-icon').textContent = data.weatherIcon;
    document.getElementById('modal-condition').textContent = data.description.charAt(0).toUpperCase() + data.description.slice(1);
    document.getElementById('modal-temperature').textContent = `${Math.round(data.temp)}°C`;
    document.getElementById('modal-alert-icon').textContent = data.alertIcon;
    document.getElementById('modal-alert-level').textContent = data.alertLevel;
    document.getElementById('modal-alert-message').value = data.alertMessage;

    // Store data for sending
    modal.dataset.alertData = JSON.stringify(data);

    // Show modal
    modal.classList.remove('hidden');

    // Trigger animation
    requestAnimationFrame(() => {
        modalContent.classList.remove('scale-95', 'opacity-0');
        modalContent.classList.add('scale-100', 'opacity-100');
    });
}

// Close modal function
function closeWeatherAlertModal() {
    const modal = document.getElementById('weather-alert-modal');
    const modalContent = document.getElementById('modal-content');

    // Animate out
    modalContent.classList.remove('scale-100', 'opacity-100');
    modalContent.classList.add('scale-95', 'opacity-0');

    // Hide after animation
    setTimeout(() => {
        modal.classList.add('hidden');
    }, 200);
}

// Send alert from modal
async function sendAlertFromModal() {
    const modal = document.getElementById('weather-alert-modal');
    const data = JSON.parse(modal.dataset.alertData);
    const customMessage = document.getElementById('modal-alert-message').value;
    const sendButton = document.getElementById('confirm-send-alert-btn');

    // Disable button and show loading
    sendButton.disabled = true;
    sendButton.innerHTML = '<div class="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin mx-auto"></div>';

    try {
        const alertResponse = await fetch('/api/admin/send-weather-alert/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                username: data.username,
                email: data.email,
                alert_type: data.alertType,
                title: data.alertType === 'danger' ? 'WEATHER ALERT' : 'Weather Update',
                message: customMessage,
                temperature: data.temp,
                weather_condition: data.condition,
                location: `${data.lat}, ${data.lon}`,
                latitude: data.lat,
                longitude: data.lon
            })
        });

        const alertResult = await alertResponse.json();

        if (alertResult.success) {
            closeWeatherAlertModal();
            showSuccessToast(`Weather alert sent to ${data.username}!`, 'The user will be notified about current weather conditions.');
            console.log('Alert sent successfully:', alertResult);
        } else {
            showErrorToast('Failed to send alert', alertResult.error);
            console.error('Alert sending failed:', alertResult);
        }
    } catch (error) {
        console.error('Error sending alert via API:', error);
        showErrorToast('Failed to send alert', 'Please try again.');
    } finally {
        // Re-enable button
        sendButton.disabled = false;
        sendButton.innerHTML = `
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"></path>
            </svg>
            <span>Send Alert</span>
        `;
    }
}

// Initialize modal event listeners
document.addEventListener('DOMContentLoaded', function() {
    const closeBtn = document.getElementById('close-modal-btn');
    const cancelBtn = document.getElementById('cancel-alert-btn');
    const backdrop = document.getElementById('modal-backdrop');
    const confirmBtn = document.getElementById('confirm-send-alert-btn');

    if (closeBtn) closeBtn.addEventListener('click', closeWeatherAlertModal);
    if (cancelBtn) cancelBtn.addEventListener('click', closeWeatherAlertModal);
    if (backdrop) backdrop.addEventListener('click', closeWeatherAlertModal);
    if (confirmBtn) confirmBtn.addEventListener('click', sendAlertFromModal);

    // ESC key to close modal
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            const modal = document.getElementById('weather-alert-modal');
            if (modal && !modal.classList.contains('hidden')) {
                closeWeatherAlertModal();
            }
        }
    });
});

// Toast notification functions
function showSuccessToast(title, message) {
    showToast(title, message, 'success');
}

function showErrorToast(title, message) {
    showToast(title, message, 'error');
}

function showToast(title, message, type = 'success') {
    // Create toast container if it doesn't exist
    let toastContainer = document.getElementById('toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toast-container';
        toastContainer.className = 'fixed top-4 right-4 z-[10000] flex flex-col gap-2';
        document.body.appendChild(toastContainer);
    }

    // Create toast element
    const toast = document.createElement('div');
    const bgColor = type === 'success' ? 'bg-green-500' : 'bg-red-500';
    const icon = type === 'success'
        ? '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>'
        : '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>';

    toast.className = `${bgColor} text-white px-6 py-4 rounded-lg shadow-2xl transform transition-all duration-300 translate-x-full opacity-0 max-w-md`;
    toast.innerHTML = `
        <div class="flex items-start gap-3">
            <div class="flex-shrink-0">
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    ${icon}
                </svg>
            </div>
            <div class="flex-1">
                <h4 class="font-semibold text-sm mb-1">${title}</h4>
                <p class="text-xs opacity-90">${message}</p>
            </div>
            <button onclick="this.parentElement.parentElement.remove()" class="flex-shrink-0 opacity-75 hover:opacity-100">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                </svg>
            </button>
        </div>
    `;

    toastContainer.appendChild(toast);

    // Animate in
    requestAnimationFrame(() => {
        toast.classList.remove('translate-x-full', 'opacity-0');
    });

    // Auto remove after 5 seconds
    setTimeout(() => {
        toast.classList.add('translate-x-full', 'opacity-0');
        setTimeout(() => {
            toast.remove();
            // Remove container if empty
            if (toastContainer.children.length === 0) {
                toastContainer.remove();
            }
        }, 300);
    }, 5000);
}
