/**
 * Admin User Management Actions
 * Handles view, edit, and delete operations for users
 */

let currentUserId = null;
let originalUserData = null; // Store original user data for comparison

// View User Details
function viewUser(userId) {
    console.log('viewUser called with userId:', userId);
    currentUserId = userId;

    // Fetch user details from backend
    fetch(`/admin-users/${userId}/`)
        .then(response => {
            console.log('Response status:', response.status);
            console.log('Response OK:', response.ok);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('User data received:', data);
            console.log('Data success flag:', data.success);

            if (data.success && data.user) {
                console.log('About to populate modal with user:', data.user);

                // Verify modal exists before populating
                const modal = document.getElementById('viewUserModal');
                if (!modal) {
                    console.error('View user modal element not found in DOM!');
                    showErrorToast('Error', 'Modal not found. Please refresh the page.');
                    return;
                }

                populateViewUserModal(data.user);
                console.log('Modal populated, now opening...');
                openViewUserModal();
            } else {
                console.error('Error from backend:', data.error);
                showErrorToast('Error', data.error || 'Failed to load user details');
            }
        })
        .catch(error => {
            console.error('Fetch error:', error);
            console.error('Error stack:', error.stack);
            showErrorToast('Error', 'Failed to load user details');
        });
}

function populateViewUserModal(user) {
    console.log('Populating modal with user:', user);

    // Helper function to safely set element text
    const setElementText = (id, value) => {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = value || '--';
        } else {
            console.warn(`Element with id '${id}' not found`);
        }
    };

    // Avatar
    const avatar = document.getElementById('viewUserAvatar');
    if (avatar && user.username) {
        avatar.textContent = user.username.charAt(0).toUpperCase();
    }

    // Basic Info
    const fullName = `${user.first_name || ''} ${user.last_name || ''}`.trim();
    setElementText('viewUserName', fullName || user.username || 'Unknown');
    setElementText('viewUserEmail', user.email || '--');

    // Status Badge
    const statusBadge = document.getElementById('viewUserStatus');
    if (statusBadge) {
        if (user.is_active) {
            statusBadge.className = 'px-3 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800';
            statusBadge.textContent = 'Active';
        } else {
            statusBadge.className = 'px-3 py-1 text-xs font-semibold rounded-full bg-red-100 text-red-800';
            statusBadge.textContent = 'Inactive';
        }
    } else {
        console.warn('Status badge element not found');
    }

    // Role Badge
    const roleBadge = document.getElementById('viewUserRole');
    if (roleBadge) {
        roleBadge.textContent = user.is_staff ? 'Admin' : 'User';
    } else {
        console.warn('Role badge element not found');
    }

    // Account Information
    setElementText('viewUsername', user.username || '--');
    setElementText('viewFullName', `${user.first_name || ''} ${user.middle_name || ''} ${user.last_name || ''}`.trim() || '--');
    setElementText('viewEmail', user.email || '--');
    setElementText('viewPhone', user.phone_number || '--');
    setElementText('viewDateJoined', user.date_joined || '--');
    setElementText('viewLastLogin', user.last_login || '--');

    // Location
    setElementText('viewLocation', user.location || '--');
}

function openViewUserModal() {
    const modal = document.getElementById('viewUserModal');
    if (modal) {
        modal.classList.remove('hidden');
        console.log('View user modal opened successfully');
    } else {
        console.error('View user modal element not found!');
        showErrorToast('Error', 'Modal element not found. Please refresh the page.');
    }
}

function closeViewUserModal() {
    document.getElementById('viewUserModal').classList.add('hidden');
    currentUserId = null;
}

function editUserFromView() {
    const userId = currentUserId; // Save userId before closing modal
    closeViewUserModal();
    editUser(userId);
}

// Edit User
function editUser(userId) {
    currentUserId = userId;

    // Fetch user details from backend
    fetch(`/admin-users/${userId}/`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                populateEditUserModal(data.user);
                openEditUserModal();
            } else {
                showErrorToast('Error', data.error || 'Failed to load user details');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showErrorToast('Error', 'Failed to load user details');
        });
}

function populateEditUserModal(user) {
    // Store original user data for comparison
    originalUserData = {
        first_name: user.first_name,
        middle_name: user.middle_name || '',
        last_name: user.last_name,
        username: user.username,
        email: user.email,
        phone_number: user.phone_number || '',
        role: user.is_staff ? 'admin' : 'user',
        is_active: user.is_active ? 'true' : 'false'
    };

    document.getElementById('editUserId').value = user.id;
    document.getElementById('editFirstName').value = user.first_name;
    document.getElementById('editMiddleName').value = user.middle_name || '';
    document.getElementById('editLastName').value = user.last_name;
    document.getElementById('editUsername').value = user.username;
    document.getElementById('editEmail').value = user.email;
    document.getElementById('editPhone').value = user.phone_number || '';
    document.getElementById('editRole').value = user.is_staff ? 'admin' : 'user';
    document.getElementById('editStatus').value = user.is_active ? 'true' : 'false';
    document.getElementById('editNewPassword').value = '';
}

function openEditUserModal() {
    document.getElementById('editUserModal').classList.remove('hidden');
}

function closeEditUserModal() {
    document.getElementById('editUserModal').classList.add('hidden');
    currentUserId = null;
}

function deleteUserFromEdit() {
    const userId = document.getElementById('editUserId').value;
    closeEditUserModal();
    deleteUser(userId);
}

// Handle Edit Form Submission
document.addEventListener('DOMContentLoaded', function() {
    const editForm = document.getElementById('editUserForm');
    if (editForm) {
        editForm.addEventListener('submit', function(e) {
            e.preventDefault();

            const userId = document.getElementById('editUserId').value;
            const newPassword = document.getElementById('editNewPassword').value;

            const formData = {
                first_name: document.getElementById('editFirstName').value,
                middle_name: document.getElementById('editMiddleName').value,
                last_name: document.getElementById('editLastName').value,
                username: document.getElementById('editUsername').value,
                email: document.getElementById('editEmail').value,
                phone_number: document.getElementById('editPhone').value,
                role: document.getElementById('editRole').value,
                is_active: document.getElementById('editStatus').value,
                new_password: newPassword,
            };

            // Check if anything has changed
            const hasChanges =
                formData.first_name !== originalUserData.first_name ||
                formData.middle_name !== originalUserData.middle_name ||
                formData.last_name !== originalUserData.last_name ||
                formData.username !== originalUserData.username ||
                formData.email !== originalUserData.email ||
                formData.phone_number !== originalUserData.phone_number ||
                formData.role !== originalUserData.role ||
                formData.is_active !== originalUserData.is_active ||
                (newPassword && newPassword.trim() !== '');

            // If no changes, show info message and return
            if (!hasChanges) {
                showInfoToast('No Changes', 'No changes were made to the user information');
                return;
            }

            fetch(`/admin-users/${userId}/edit/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify(formData)
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showSuccessToast('Success!', 'User updated successfully');
                    closeEditUserModal();
                    setTimeout(() => {
                        location.reload(); // Reload to show updated data
                    }, 1000); // Delay reload to show toast
                } else {
                    showErrorToast('Error', data.error || 'Failed to update user');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showErrorToast('Error', 'Failed to update user');
            });
        });
    }
});

// Delete User
function deleteUser(userId) {
    currentUserId = userId;

    // Fetch user details to show in confirmation modal
    fetch(`/admin-users/${userId}/`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                populateDeleteUserModal(data.user);
                openDeleteUserModal();
            } else {
                showErrorToast('Error', data.error || 'Failed to load user details');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showErrorToast('Error', 'Failed to load user details');
        });
}

function populateDeleteUserModal(user) {
    document.getElementById('deleteUserId').value = user.id;

    const avatar = document.getElementById('deleteUserAvatar');
    if (avatar) {
        avatar.textContent = user.username.charAt(0).toUpperCase();
    }

    document.getElementById('deleteUserName').textContent = `${user.first_name} ${user.last_name}` || user.username;
    document.getElementById('deleteUserEmail').textContent = user.email;

    // Reset confirmation input
    document.getElementById('deleteConfirmText').value = '';
}

function openDeleteUserModal() {
    document.getElementById('deleteUserModal').classList.remove('hidden');
}

function closeDeleteUserModal() {
    document.getElementById('deleteUserModal').classList.add('hidden');
    document.getElementById('deleteConfirmText').value = '';
    currentUserId = null;
}

function confirmDeleteUser() {
    const userId = document.getElementById('deleteUserId').value;
    const confirmText = document.getElementById('deleteConfirmText').value;

    if (confirmText !== 'DELETE') {
        showErrorToast('Confirmation Required', 'Please type DELETE to confirm');
        return;
    }

    fetch(`/admin-users/${userId}/delete/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showSuccessToast('Success!', data.message || 'User deleted successfully');
            closeDeleteUserModal();
            setTimeout(() => {
                location.reload(); // Reload to show updated user list
            }, 1000); // Delay reload to show toast
        } else {
            showErrorToast('Error', data.error || 'Failed to delete user');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showErrorToast('Error', 'Failed to delete user');
    });
}

// Utility function to get CSRF token
function getCookie(name) {
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

// Toast notification functions
function showSuccessToast(title, message) {
    showToast(title, message, 'success');
}

function showErrorToast(title, message) {
    showToast(title, message, 'error');
}

function showInfoToast(title, message) {
    showToast(title, message, 'info');
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
    let bgColor, icon;

    if (type === 'success') {
        bgColor = 'bg-green-500';
        icon = '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>';
    } else if (type === 'error') {
        bgColor = 'bg-red-500';
        icon = '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>';
    } else { // info
        bgColor = 'bg-blue-500';
        icon = '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>';
    }

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

// Close modals when clicking outside
document.addEventListener('click', function(event) {
    const viewModal = document.getElementById('viewUserModal');
    const editModal = document.getElementById('editUserModal');
    const deleteModal = document.getElementById('deleteUserModal');

    if (event.target === viewModal) {
        closeViewUserModal();
    }
    if (event.target === editModal) {
        closeEditUserModal();
    }
    if (event.target === deleteModal) {
        closeDeleteUserModal();
    }
});

// Close modals with Escape key
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        closeViewUserModal();
        closeEditUserModal();
        closeDeleteUserModal();
    }
});
