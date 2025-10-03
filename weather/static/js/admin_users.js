/**
 * Admin Users Management - Minimal Version
 */

class AdminUsers {
    constructor() {
        this.users = [];
        this.filters = { search: '', status: 'all', role: 'all' };
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadUsers();
    }

    bindEvents() {
        const events = [
            ['user-search', 'input', (e) => this.filter('search', e.target.value)],
            ['status-filter', 'change', (e) => this.filter('status', e.target.value)],
            ['role-filter', 'change', (e) => this.filter('role', e.target.value)],
            ['refresh-users', 'click', () => this.loadUsers()],
            ['close-user-modal', 'click', () => this.toggleModal(false)]
        ];

        events.forEach(([id, event, handler]) => {
            const el = document.getElementById(id);
            if (el) el.addEventListener(event, handler);
        });

        document.addEventListener('click', (e) => {
            const { action, userId } = e.target.dataset;
            if (action) this.handleAction(action, userId);
        });
    }

    loadUsers() {
        const names = ['John Doe', 'Jane Smith', 'Mike Johnson', 'Sarah Wilson', 'David Brown'];
        const locations = ['New York', 'Chicago', 'Los Angeles', 'Houston', 'Philadelphia'];
        const statuses = ['active', 'inactive', 'suspended'];
        const roles = ['user', 'admin'];

        this.users = Array.from({ length: 5 }, (_, i) => ({
            id: i + 1,
            name: names[i],
            email: `user${i + 1}@example.com`,
            status: statuses[i % 3],
            role: roles[i % 2],
            location: locations[i],
            lastActive: new Date(Date.now() - i * 24 * 60 * 60 * 1000).toISOString().split('T')[0]
        }));

        this.render();
    }

    filter(type, value) {
        this.filters[type] = value;
        this.render();
    }

    render() {
        const filtered = this.users.filter(user => {
            const { search, status, role } = this.filters;
            return (!search || user.name.toLowerCase().includes(search.toLowerCase()) || user.email.toLowerCase().includes(search.toLowerCase())) &&
                   (status === 'all' || user.status === status) &&
                   (role === 'all' || user.role === role);
        });

        const tbody = document.getElementById('users-table-body');
        tbody.innerHTML = filtered.map(user => `
            <tr class="hover:bg-gray-50">
                <td class="px-6 py-4"><input type="checkbox" class="user-checkbox" data-user-id="${user.id}"></td>
                <td class="px-6 py-4">
                    <div class="flex items-center">
                        <div class="w-10 h-10 bg-blue-500 rounded-full flex items-center justify-center text-white font-medium">
                            ${user.name.split(' ').map(n => n[0]).join('')}
                        </div>
                        <div class="ml-4">
                            <div class="text-sm font-medium text-gray-900">${user.name}</div>
                            <div class="text-sm text-gray-500">${user.email}</div>
                        </div>
                    </div>
                </td>
                <td class="px-6 py-4"><span class="inline-flex px-2 py-1 text-xs font-semibold rounded-full ${this.getStatusClass(user.status)}">${user.status}</span></td>
                <td class="px-6 py-4"><span class="inline-flex px-2 py-1 text-xs font-medium rounded-full ${user.role === 'admin' ? 'bg-purple-100 text-purple-800' : 'bg-gray-100 text-gray-800'}">${user.role}</span></td>
                <td class="px-6 py-4 text-sm text-gray-500">${user.location}</td>
                <td class="px-6 py-4 text-sm text-gray-500">${user.lastActive}</td>
                <td class="px-6 py-4 text-sm space-x-1">
                    <button data-action="view" data-user-id="${user.id}" class="text-blue-600 hover:text-blue-800">View</button>
                    <button data-action="suspend" data-user-id="${user.id}" class="text-yellow-600 hover:text-yellow-800">${user.status === 'suspended' ? 'Unsuspend' : 'Suspend'}</button>
                    <button data-action="delete" data-user-id="${user.id}" class="text-red-600 hover:text-red-800">Delete</button>
                </td>
            </tr>
        `).join('');

        document.getElementById('total-count').textContent = filtered.length;
        document.getElementById('showing-count').textContent = filtered.length;
    }

    handleAction(action, userId) {
        const user = this.users.find(u => u.id == userId);
        if (!user) return;

        switch (action) {
            case 'view':
                document.getElementById('user-details-content').innerHTML = `
                    <div class="space-y-4">
                        <div class="flex items-center space-x-4">
                            <div class="w-16 h-16 bg-blue-500 rounded-full flex items-center justify-center text-white text-xl font-bold">
                                ${user.name.split(' ').map(n => n[0]).join('')}
                            </div>
                            <div>
                                <h4 class="text-lg font-semibold">${user.name}</h4>
                                <p class="text-gray-600">${user.email}</p>
                            </div>
                        </div>
                        <div class="grid grid-cols-2 gap-4 text-sm">
                            <div><span class="font-medium">Status:</span> ${user.status}</div>
                            <div><span class="font-medium">Role:</span> ${user.role}</div>
                            <div><span class="font-medium">Location:</span> ${user.location}</div>
                            <div><span class="font-medium">Last Active:</span> ${user.lastActive}</div>
                        </div>
                    </div>
                `;
                this.toggleModal(true);
                break;
            case 'suspend':
                user.status = user.status === 'suspended' ? 'active' : 'suspended';
                this.render();
                break;
            case 'delete':
                if (confirm('Delete this user?')) {
                    this.users = this.users.filter(u => u.id != userId);
                    this.render();
                }
                break;
        }
    }

    getStatusClass(status) {
        return {
            active: 'bg-green-100 text-green-800',
            inactive: 'bg-gray-100 text-gray-800',
            suspended: 'bg-red-100 text-red-800'
        }[status] || 'bg-gray-100 text-gray-800';
    }

    toggleModal(show) {
        document.getElementById('user-modal').classList.toggle('hidden', !show);
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('users-table-body')) {
        window.adminUsers = new AdminUsers();
    }
});