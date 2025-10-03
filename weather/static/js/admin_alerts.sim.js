/**
 * Simple Admin Alerts JavaScript
 */

class AdminAlerts {
    constructor() {
        this.selectedUsers = [];
        this.init();
    }

    init() {
        this.bindEvents();
        this.initUserSelection();
    }

    bindEvents() {
        // Modal controls
        const addBtn = document.getElementById('add-alert-btn');
        const closeBtn = document.getElementById('close-alert-modal');
        const clearBtn = document.getElementById('clear-form');
        const alertForm = document.getElementById('alert-form');

        if (addBtn) {
            addBtn.addEventListener('click', () => this.showModal());
        }

        if (closeBtn) {
            closeBtn.addEventListener('click', () => this.hideModal());
        }

        if (clearBtn) {
            clearBtn.addEventListener('click', () => this.clearForm());
        }

        if (alertForm) {
            alertForm.addEventListener('submit', (e) => this.handleSubmit(e));
        }

        // User selection radio buttons
        const userRadios = document.querySelectorAll('input[name="user_selection"]');
        userRadios.forEach(radio => {
            radio.addEventListener('change', () => this.handleUserSelectionChange());
        });

        // User search
        const userSearch = document.getElementById('user-search');
        if (userSearch) {
            userSearch.addEventListener('input', () => this.filterUsers());
        }

        // User list items
        const userItems = document.querySelectorAll('.user-item');
        userItems.forEach(item => {
            item.addEventListener('click', () => this.toggleUserSelection(item));
        });

        // Close modal when clicking outside
        const modal = document.getElementById('alert-modal');
        if (modal) {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    this.hideModal();
                }
            });
        }
    }

    showModal() {
        const modal = document.getElementById('alert-modal');
        if (modal) {
            modal.classList.remove('hidden');
            document.body.style.overflow = 'hidden'; // Prevent background scrolling
        }
    }

    hideModal() {
        const modal = document.getElementById('alert-modal');
        if (modal) {
            modal.classList.add('hidden');
            document.body.style.overflow = ''; // Restore scrolling
        }
    }

    clearForm() {
        const form = document.getElementById('alert-form');
        if (form) {
            form.reset();
            this.handleUserSelectionChange(); // Reset location selection visibility
        }
    }

    handleUserSelectionChange() {
        const locationRadio = document.querySelector('input[name="user_selection"][value="location"]');
        const specificRadio = document.querySelector('input[name="user_selection"][value="specific"]');
        const locationDiv = document.getElementById('location-selection');
        const specificDiv = document.getElementById('specific-users-selection');

        if (locationRadio && locationDiv) {
            if (locationRadio.checked) {
                locationDiv.classList.remove('hidden');
            } else {
                locationDiv.classList.add('hidden');
            }
        }

        if (specificRadio && specificDiv) {
            if (specificRadio.checked) {
                specificDiv.classList.remove('hidden');
            } else {
                specificDiv.classList.add('hidden');
            }
        }
    }

    initUserSelection() {
        this.handleUserSelectionChange();
    }

    handleSubmit(e) {
        e.preventDefault();

        // Get form data
        const formData = this.getFormData();

        // Simple validation
        if (!formData.title || !formData.message) {
            alert('Please fill in all required fields');
            return;
        }

        // Show loading state
        const submitBtn = document.getElementById('send-alert');
        if (submitBtn) {
            submitBtn.textContent = 'Sending...';
            submitBtn.disabled = true;
        }

        // Simulate sending (replace with actual API call)
        setTimeout(() => {
            alert('Alert sent successfully!');
            this.clearForm();
            this.hideModal();

            // Reset button
            if (submitBtn) {
                submitBtn.textContent = 'Send Alert';
                submitBtn.disabled = false;
            }
        }, 1000);
    }

    filterUsers() {
        const searchTerm = document.getElementById('user-search')?.value.toLowerCase() || '';
        const userItems = document.querySelectorAll('.user-item');

        userItems.forEach(item => {
            const name = item.dataset.userName.toLowerCase();
            const email = item.dataset.userEmail.toLowerCase();

            if (name.includes(searchTerm) || email.includes(searchTerm)) {
                item.style.display = 'block';
            } else {
                item.style.display = 'none';
            }
        });
    }

    toggleUserSelection(userItem) {
        const userId = userItem.dataset.userId;
        const userName = userItem.dataset.userName;
        const userEmail = userItem.dataset.userEmail;

        const existingIndex = this.selectedUsers.findIndex(user => user.id === userId);

        if (existingIndex > -1) {
            // Remove user
            this.selectedUsers.splice(existingIndex, 1);
            userItem.classList.remove('bg-blue-100');
        } else {
            // Add user
            this.selectedUsers.push({ id: userId, name: userName, email: userEmail });
            userItem.classList.add('bg-blue-100');
        }

        this.updateSelectedUsersDisplay();
    }

    updateSelectedUsersDisplay() {
        const container = document.getElementById('user-tags');
        if (!container) return;

        container.innerHTML = this.selectedUsers.map(user => `
            <span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                ${user.name}
                <button type="button" class="ml-1 text-blue-400 hover:text-blue-600" onclick="window.adminAlerts.removeUser('${user.id}')">×</button>
            </span>
        `).join('');
    }

    removeUser(userId) {
        this.selectedUsers = this.selectedUsers.filter(user => user.id !== userId);
        const userItem = document.querySelector(`[data-user-id="${userId}"]`);
        if (userItem) {
            userItem.classList.remove('bg-blue-100');
        }
        this.updateSelectedUsersDisplay();
    }

    getFormData() {
        return {
            type: document.getElementById('alert-type')?.value || '',
            title: document.getElementById('alert-title')?.value || '',
            message: document.getElementById('alert-message')?.value || '',
            userSelection: document.querySelector('input[name="user_selection"]:checked')?.value || 'all',
            locations: Array.from(document.getElementById('target-areas')?.selectedOptions || [])
                .map(option => option.value),
            selectedUsers: this.selectedUsers
        };
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Initialize if we're on the alerts page
    if (document.getElementById('add-alert-btn')) {
        window.adminAlerts = new AdminAlerts();
        console.log('AdminAlerts initialized');
    }
});