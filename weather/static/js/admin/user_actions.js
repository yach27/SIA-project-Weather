/**
 * Admin User Management Actions
 * Handles view, edit, and delete operations for users
 */

let currentUserId = null;

// View User Details
function viewUser(userId) {
    currentUserId = userId;

    // Fetch user details from backend
    fetch(`/admin-users/${userId}/`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                populateViewUserModal(data.user);
                openViewUserModal();
            } else {
                alert('Error loading user details: ' + (data.error || 'Unknown error'));
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Failed to load user details');
        });
}

function populateViewUserModal(user) {
    // Avatar
    const avatar = document.getElementById('viewUserAvatar');
    if (avatar) {
        avatar.textContent = user.username.charAt(0).toUpperCase();
    }

    // Basic Info
    document.getElementById('viewUserName').textContent = `${user.first_name} ${user.last_name}` || user.username;
    document.getElementById('viewUserEmail').textContent = user.email;

    // Status Badge
    const statusBadge = document.getElementById('viewUserStatus');
    if (user.is_active) {
        statusBadge.className = 'px-3 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800';
        statusBadge.textContent = 'Active';
    } else {
        statusBadge.className = 'px-3 py-1 text-xs font-semibold rounded-full bg-red-100 text-red-800';
        statusBadge.textContent = 'Inactive';
    }

    // Role Badge
    const roleBadge = document.getElementById('viewUserRole');
    if (user.is_staff) {
        roleBadge.textContent = 'Admin';
    } else {
        roleBadge.textContent = 'User';
    }

    // Account Information
    document.getElementById('viewUsername').textContent = user.username;
    document.getElementById('viewFullName').textContent = `${user.first_name} ${user.middle_name || ''} ${user.last_name}`.trim() || '--';
    document.getElementById('viewEmail').textContent = user.email;
    document.getElementById('viewPhone').textContent = user.phone_number || '--';
    document.getElementById('viewDateJoined').textContent = user.date_joined;
    document.getElementById('viewLastLogin').textContent = user.last_login;

    // Location
    document.getElementById('viewLocation').textContent = user.location;
    document.getElementById('viewCoordinates').textContent = user.coordinates;
}

function openViewUserModal() {
    document.getElementById('viewUserModal').classList.remove('hidden');
}

function closeViewUserModal() {
    document.getElementById('viewUserModal').classList.add('hidden');
    currentUserId = null;
}

function editUserFromView() {
    closeViewUserModal();
    editUser(currentUserId);
}

// Edit User
function editUser(userId) {
    currentUserId = userId;

    // Fetch user details from backend
    fetch(`/admin-users/${userId}/`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                populateEditUserModal(data.user);
                openEditUserModal();
            } else {
                alert('Error loading user details: ' + (data.error || 'Unknown error'));
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Failed to load user details');
        });
}

function populateEditUserModal(user) {
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
            const formData = {
                first_name: document.getElementById('editFirstName').value,
                middle_name: document.getElementById('editMiddleName').value,
                last_name: document.getElementById('editLastName').value,
                username: document.getElementById('editUsername').value,
                email: document.getElementById('editEmail').value,
                phone_number: document.getElementById('editPhone').value,
                role: document.getElementById('editRole').value,
                is_active: document.getElementById('editStatus').value,
                new_password: document.getElementById('editNewPassword').value,
            };

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
                    alert('User updated successfully!');
                    closeEditUserModal();
                    location.reload(); // Reload to show updated data
                } else {
                    alert('Error updating user: ' + (data.error || 'Unknown error'));
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Failed to update user');
            });
        });
    }
});

// Delete User
function deleteUser(userId) {
    currentUserId = userId;

    // Fetch user details to show in confirmation modal
    fetch(`/admin-users/${userId}/`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                populateDeleteUserModal(data.user);
                openDeleteUserModal();
            } else {
                alert('Error loading user details: ' + (data.error || 'Unknown error'));
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Failed to load user details');
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
        alert('Please type DELETE to confirm');
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
            alert(data.message || 'User deleted successfully!');
            closeDeleteUserModal();
            location.reload(); // Reload to show updated user list
        } else {
            alert('Error deleting user: ' + (data.error || 'Unknown error'));
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Failed to delete user');
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
