/**
 * Admin Features Module
 * Handles admin-specific map features like alert creation
 */

const AdminFeatures = {
    /**
     * Initialize admin features and event listeners
     */
    init() {
        const adminElements = [
            ['alert-mode-toggle', 'click', () => this.toggleAlertMode()],
            ['close-alert-overlay', 'click', () => this.toggleAlertOverlay(false)],
            ['send-quick-alert', 'click', () => this.sendAlert()],
            ['cancel-quick-alert', 'click', () => this.toggleAlertOverlay(false)],
            ['create-alert-btn', 'click', () => this.createAlertClick()],
            ['view-users-btn', 'click', () => this.viewUsersClick()]
        ];

        adminElements.forEach(([id, event, handler]) => {
            const element = document.getElementById(id);
            if (element) {
                element.addEventListener(event, handler);
            }
        });

        console.log('Admin features initialized');
    },

    /**
     * Toggle alert creation mode
     */
    toggleAlertMode() {
        MapConfig.alertMode = !MapConfig.alertMode;
        const btn = document.getElementById('alert-mode-toggle');

        if (!btn) return;

        if (MapConfig.alertMode) {
            btn.classList.add('alert-mode-active', 'bg-red-600', 'text-white');
            btn.classList.remove('bg-white', 'text-gray-700');
            btn.textContent = '🚨 Alert Mode ON';
            MapUtils.showMessage('Alert mode activated. Click on map to create alerts.', 'info');
        } else {
            btn.classList.remove('alert-mode-active', 'bg-red-600', 'text-white');
            btn.classList.add('bg-white', 'text-gray-700');
            btn.textContent = '🚨 Alert Mode';
            this.toggleAlertOverlay(false);
            MapUtils.showMessage('Alert mode deactivated.', 'info');
        }
    },

    /**
     * Show/hide alert creation overlay
     */
    toggleAlertOverlay(show) {
        const overlay = document.getElementById('alert-creation-overlay');
        if (overlay) {
            overlay.classList.toggle('hidden', !show);
        }
    },

    /**
     * Send weather alert
     */
    sendAlert() {
        const alertMessage = document.getElementById('quick-alert-message')?.value;

        if (!alertMessage?.trim()) {
            MapUtils.showMessage('Please enter an alert message.', 'error');
            return;
        }

        if (!MapConfig.selectedLocation) {
            MapUtils.showMessage('Please select a location on the map.', 'error');
            return;
        }

        MapUtils.showMessage('Sending alert...', 'info');

        // Simulate sending alert
        setTimeout(() => {
            this.toggleAlertOverlay(false);
            MapUtils.showMessage('Alert sent successfully!', 'success');
            const messageInput = document.getElementById('quick-alert-message');
            if (messageInput) {
                messageInput.value = '';
            }
        }, 1500);
    },

    /**
     * Handle create alert button click
     */
    createAlertClick() {
        if (MapConfig.selectedLocation) {
            this.toggleAlertOverlay(true);
        } else {
            MapUtils.showMessage('Please select a location first.', 'error');
        }
    },

    /**
     * Handle view users button click
     */
    viewUsersClick() {
        if (MapConfig.selectedLocation) {
            MapUtils.showMessage('User management feature coming soon.', 'info');
            MapControls.updateUsersInArea();
        } else {
            MapUtils.showMessage('Please select a location first.', 'error');
        }
    }
};

// Export for use in other modules
window.AdminFeatures = AdminFeatures;
