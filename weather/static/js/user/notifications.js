// User Notifications Handler
class NotificationManager {
    constructor() {
        this.notifications = [];
        this.unreadCount = 0;
        this.pollInterval = 30000; // Poll every 30 seconds
        this.pollTimer = null;
        this.dropdownOpen = false;
    }

    // Initialize notification manager
    init() {
        console.log('[Notifications] Initializing notification manager...');
        this.setupEventListeners();
        this.fetchNotifications();
        this.startPolling();
        console.log('[Notifications] Notification manager initialized');
    }

    // Setup event listeners
    setupEventListeners() {
        const bellButton = document.getElementById('notification-bell-btn');
        const dropdown = document.getElementById('notification-dropdown');
        const markAllReadBtn = document.getElementById('mark-all-read-btn');

        if (bellButton) {
            bellButton.addEventListener('click', (e) => {
                e.stopPropagation();
                this.toggleDropdown();
            });
        }

        if (markAllReadBtn) {
            markAllReadBtn.addEventListener('click', () => {
                this.markAllAsRead();
            });
        }

        // Close dropdown when clicking outside
        document.addEventListener('click', (e) => {
            if (dropdown && !dropdown.contains(e.target) && !bellButton.contains(e.target)) {
                this.closeDropdown();
            }
        });
    }

    // Toggle notification dropdown
    toggleDropdown() {
        const dropdown = document.getElementById('notification-dropdown');
        if (!dropdown) return;

        this.dropdownOpen = !this.dropdownOpen;

        if (this.dropdownOpen) {
            dropdown.classList.remove('hidden');
            this.fetchNotifications(); // Refresh notifications when opening
        } else {
            dropdown.classList.add('hidden');
        }
    }

    // Close dropdown
    closeDropdown() {
        const dropdown = document.getElementById('notification-dropdown');
        if (dropdown) {
            dropdown.classList.add('hidden');
            this.dropdownOpen = false;
        }
    }

    // Fetch notifications from API
    async fetchNotifications() {
        console.log('[Notifications] Fetching notifications...');
        try {
            const response = await fetch('/api/notifications/', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                }
            });

            console.log('[Notifications] Response status:', response.status);

            if (!response.ok) {
                throw new Error('Failed to fetch notifications');
            }

            const data = await response.json();
            console.log('[Notifications] Response data:', data);

            if (data.success) {
                this.notifications = data.notifications || [];
                this.unreadCount = data.unread_count || 0;
                console.log('[Notifications] Loaded notifications:', this.notifications.length, 'Unread:', this.unreadCount);
                this.updateUI();
            }
        } catch (error) {
            console.error('[Notifications] Error fetching notifications:', error);
            this.hideLoading();
        }
    }

    // Update UI with notifications
    updateUI() {
        this.updateBadge();
        this.renderNotifications();
        this.hideLoading();
    }

    // Update notification badge
    updateBadge() {
        const badge = document.getElementById('notification-badge');
        const dropdownBadge = document.getElementById('notification-badge-dropdown');

        if (badge) {
            if (this.unreadCount > 0) {
                badge.classList.remove('hidden');
                badge.textContent = this.unreadCount > 99 ? '99+' : this.unreadCount;
            } else {
                badge.classList.add('hidden');
            }
        }

        if (dropdownBadge) {
            dropdownBadge.textContent = this.unreadCount;
        }
    }

    // Render notifications in dropdown
    renderNotifications() {
        console.log('[Notifications] Rendering notifications...');
        const container = document.getElementById('notifications-container');
        const emptyState = document.getElementById('notifications-empty');

        console.log('[Notifications] Container found:', !!container);
        console.log('[Notifications] Empty state found:', !!emptyState);

        if (!container || !emptyState) {
            console.error('[Notifications] Required elements not found!');
            return;
        }

        console.log('[Notifications] Notification count:', this.notifications.length);

        if (this.notifications.length === 0) {
            console.log('[Notifications] No notifications, showing empty state');
            container.classList.add('hidden');
            emptyState.classList.remove('hidden');
            return;
        }

        console.log('[Notifications] Showing notifications');
        container.classList.remove('hidden');
        emptyState.classList.add('hidden');
        container.innerHTML = '';

        this.notifications.forEach((notification, index) => {
            console.log(`[Notifications] Rendering notification ${index + 1}:`, notification.title);
            const notificationElement = this.createNotificationElement(notification);
            container.appendChild(notificationElement);
        });

        console.log('[Notifications] Render complete');
    }

    // Create notification element
    createNotificationElement(notification) {
        const div = document.createElement('div');
        div.className = 'p-4 hover:bg-gray-50 transition-colors cursor-pointer';
        div.dataset.notificationId = notification.id;

        // Determine alert styling
        let alertColor = 'text-blue-600';
        let alertBg = 'bg-blue-50';
        let alertIcon = '📢';

        if (notification.alert_type === 'danger') {
            alertColor = 'text-red-600';
            alertBg = 'bg-red-50';
            alertIcon = '⚠️';
        } else if (notification.alert_type === 'warning') {
            alertColor = 'text-orange-600';
            alertBg = 'bg-orange-50';
            alertIcon = '⚠️';
        }

        const weatherIcon = this.getWeatherIcon(notification.weather_condition);
        const timeAgo = this.getTimeAgo(notification.sent_at);

        div.innerHTML = `
            <div class="flex items-start space-x-3">
                <div class="flex-shrink-0 ${alertBg} rounded-full w-10 h-10 flex items-center justify-center text-xl">
                    ${alertIcon}
                </div>
                <div class="flex-1 min-w-0">
                    <div class="flex items-start justify-between">
                        <h4 class="text-sm font-semibold ${alertColor} truncate">
                            ${this.escapeHtml(notification.title)}
                        </h4>
                        <button
                            class="ml-2 text-gray-400 hover:text-gray-600 flex-shrink-0"
                            onclick="notificationManager.markAsRead(${notification.id})"
                        >
                            <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                                <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"></path>
                            </svg>
                        </button>
                    </div>
                    <p class="text-xs text-gray-600 mt-1 line-clamp-2">
                        ${this.escapeHtml(notification.message)}
                    </p>
                    <div class="flex items-center justify-between mt-2">
                        <div class="flex items-center space-x-3 text-xs text-gray-500">
                            ${notification.temperature ? `
                                <span class="flex items-center">
                                    <span class="mr-1">${weatherIcon}</span>
                                    ${Math.round(notification.temperature)}°C
                                </span>
                            ` : ''}
                            ${notification.sent_by ? `
                                <span class="flex items-center">
                                    <svg class="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
                                        <path fill-rule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clip-rule="evenodd"></path>
                                    </svg>
                                    ${this.escapeHtml(notification.sent_by)}
                                </span>
                            ` : ''}
                        </div>
                        <span class="text-xs text-gray-400">${timeAgo}</span>
                    </div>
                </div>
            </div>
        `;

        return div;
    }

    // Get weather icon
    getWeatherIcon(condition) {
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

    // Get time ago string
    getTimeAgo(timestamp) {
        const date = new Date(timestamp);
        const now = new Date();
        const seconds = Math.floor((now - date) / 1000);

        if (seconds < 60) return 'Just now';
        if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
        if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
        if (seconds < 604800) return `${Math.floor(seconds / 86400)}d ago`;
        return date.toLocaleDateString();
    }

    // Escape HTML to prevent XSS
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // Mark notification as read
    async markAsRead(notificationId) {
        try {
            const response = await fetch('/api/notifications/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    notification_id: notificationId
                })
            });

            if (!response.ok) {
                throw new Error('Failed to mark notification as read');
            }

            const data = await response.json();

            if (data.success) {
                // Remove notification from list
                this.notifications = this.notifications.filter(n => n.id !== notificationId);
                this.unreadCount = Math.max(0, this.unreadCount - 1);
                this.updateUI();
            }
        } catch (error) {
            console.error('Error marking notification as read:', error);
        }
    }

    // Mark all notifications as read
    async markAllAsRead() {
        const promises = this.notifications.map(n => this.markAsRead(n.id));
        await Promise.all(promises);
    }

    // Hide loading state
    hideLoading() {
        const loading = document.getElementById('notifications-loading');
        if (loading) {
            loading.classList.add('hidden');
        }
    }

    // Start polling for new notifications
    startPolling() {
        this.pollTimer = setInterval(() => {
            this.fetchNotifications();
        }, this.pollInterval);
    }

    // Stop polling
    stopPolling() {
        if (this.pollTimer) {
            clearInterval(this.pollTimer);
            this.pollTimer = null;
        }
    }
}

// Initialize notification manager
let notificationManager;

document.addEventListener('DOMContentLoaded', function() {
    console.log('[Notifications] DOM loaded, creating notification manager...');

    // Check if required elements exist
    const bellBtn = document.getElementById('notification-bell-btn');
    const dropdown = document.getElementById('notification-dropdown');
    const badge = document.getElementById('notification-badge');
    const container = document.getElementById('notifications-container');
    const emptyState = document.getElementById('notifications-empty');
    const loading = document.getElementById('notifications-loading');

    console.log('[Notifications] Element check:');
    console.log('  - Bell button:', !!bellBtn);
    console.log('  - Dropdown:', !!dropdown);
    console.log('  - Badge:', !!badge);
    console.log('  - Container:', !!container);
    console.log('  - Empty state:', !!emptyState);
    console.log('  - Loading:', !!loading);

    notificationManager = new NotificationManager();
    notificationManager.init();

    // Export for global access
    window.notificationManager = notificationManager;
    console.log('[Notifications] Notification manager available globally');
    console.log('[Notifications] You can manually test by typing: notificationManager.fetchNotifications()');
});
