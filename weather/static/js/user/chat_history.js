/**
 * User Chat History Management
 * Handles chat history sidebar, new chat creation, and session management
 */

// Chat history state
let chatHistorySessions = [];
let isHistorySidebarOpen = false;

// Generate unique session ID
function generateSessionId() {
    return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
}

// Initialize current session (will be called after DOM load)
function initializeChatHistory() {
    if (typeof currentSessionId === 'undefined' || !currentSessionId) {
        window.currentSessionId = generateSessionId();
    }
}

// Toggle history sidebar
function toggleHistorySidebar() {
    const sidebar = document.getElementById('chat-history-sidebar');
    if (!sidebar) return;

    isHistorySidebarOpen = !isHistorySidebarOpen;

    if (isHistorySidebarOpen) {
        sidebar.classList.remove('translate-x-full');
        loadChatHistory();
    } else {
        sidebar.classList.add('translate-x-full');
    }
}

// Close history sidebar
function closeHistorySidebar() {
    const sidebar = document.getElementById('chat-history-sidebar');
    if (!sidebar) return;

    sidebar.classList.add('translate-x-full');
    isHistorySidebarOpen = false;
}

// Load chat history from localStorage
function loadChatHistory() {
    const historyItems = document.getElementById('history-items');
    const historyLoading = document.getElementById('history-loading');
    const historyEmpty = document.getElementById('history-empty');

    if (!historyItems) return;

    // Show loading
    historyItems.classList.add('hidden');
    historyLoading.classList.remove('hidden');
    historyEmpty.classList.add('hidden');

    // Simulate loading delay
    setTimeout(() => {
        // Get sessions from localStorage
        const sessions = JSON.parse(localStorage.getItem('chatSessions') || '[]');
        chatHistorySessions = sessions.reverse(); // Most recent first

        historyLoading.classList.add('hidden');

        if (chatHistorySessions.length === 0) {
            historyEmpty.classList.remove('hidden');
            return;
        }

        // Display history items
        historyItems.classList.remove('hidden');
        historyItems.innerHTML = chatHistorySessions.map((session, index) => {
            const date = new Date(session.timestamp);
            const timeAgo = getTimeAgo(date);
            const preview = session.messages && session.messages.length > 0
                ? session.messages[0].content.substring(0, 60) + (session.messages[0].content.length > 60 ? '...' : '')
                : 'New conversation';

            const isActive = session.id === window.currentSessionId;

            return `
                <div class="bg-white rounded-xl p-4 border-2 ${isActive ? 'border-blue-500 bg-blue-50' : 'border-gray-200 hover:border-blue-300'} cursor-pointer transition-all hover:shadow-md group" onclick="loadChatSession('${session.id}')">
                    <div class="flex items-start justify-between mb-2">
                        <div class="flex items-center space-x-2 flex-1">
                            <div class="w-8 h-8 bg-gradient-to-br from-blue-400 to-indigo-500 rounded-lg flex items-center justify-center flex-shrink-0">
                                <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"></path>
                                </svg>
                            </div>
                            <div class="flex-1 min-w-0">
                                <p class="text-sm font-medium text-gray-900 truncate">${session.title || 'Chat Session'}</p>
                                <p class="text-xs text-gray-500">${timeAgo}</p>
                            </div>
                        </div>
                        <button onclick="deleteChatSession('${session.id}', event)" class="opacity-0 group-hover:opacity-100 p-1 hover:bg-red-100 rounded transition-all text-red-600" title="Delete">
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                            </svg>
                        </button>
                    </div>
                    <p class="text-xs text-gray-600 line-clamp-2">${preview}</p>
                    ${isActive ? '<div class="mt-2 text-xs text-blue-600 font-medium">● Active</div>' : ''}
                </div>
            `;
        }).join('');

    }, 500);
}

// Get time ago string
function getTimeAgo(date) {
    const seconds = Math.floor((new Date() - date) / 1000);

    const intervals = {
        year: 31536000,
        month: 2592000,
        week: 604800,
        day: 86400,
        hour: 3600,
        minute: 60
    };

    for (const [unit, secondsInUnit] of Object.entries(intervals)) {
        const interval = Math.floor(seconds / secondsInUnit);
        if (interval >= 1) {
            return interval === 1 ? `1 ${unit} ago` : `${interval} ${unit}s ago`;
        }
    }

    return 'Just now';
}

// Save current session to localStorage
function saveCurrentSession() {
    if (!window.currentSessionId || !window.conversationHistory || window.conversationHistory.length === 0) return;

    const sessions = JSON.parse(localStorage.getItem('chatSessions') || '[]');

    // Find existing session or create new one
    const sessionIndex = sessions.findIndex(s => s.id === window.currentSessionId);
    const sessionData = {
        id: window.currentSessionId,
        title: window.conversationHistory[0]?.content.substring(0, 50) || 'New Chat',
        messages: window.conversationHistory,
        timestamp: Date.now()
    };

    if (sessionIndex >= 0) {
        sessions[sessionIndex] = sessionData;
    } else {
        sessions.push(sessionData);
    }

    // Keep only last 50 sessions
    if (sessions.length > 50) {
        sessions.splice(0, sessions.length - 50);
    }

    localStorage.setItem('chatSessions', JSON.stringify(sessions));
}

// Load a chat session
function loadChatSession(sessionId) {
    const sessions = JSON.parse(localStorage.getItem('chatSessions') || '[]');
    const session = sessions.find(s => s.id === sessionId);

    if (!session) {
        console.error('Session not found:', sessionId);
        return;
    }

    // Save current session before switching
    saveCurrentSession();

    // Load the selected session
    window.currentSessionId = session.id;
    window.conversationHistory = session.messages || [];

    // Clear and reload chat
    const chatMessages = document.getElementById('chat-messages');
    if (chatMessages) {
        chatMessages.innerHTML = '';

        // Replay messages
        window.conversationHistory.forEach((msg) => {
            if (typeof window.addMessage === 'function') {
                window.addMessage(msg.content, msg.role === 'user');
            }
        });
    }

    // Close sidebar
    closeHistorySidebar();
}

// Delete a chat session
function deleteChatSession(sessionId, event) {
    if (event) {
        event.stopPropagation();
    }

    if (!confirm('Are you sure you want to delete this conversation?')) {
        return;
    }

    const sessions = JSON.parse(localStorage.getItem('chatSessions') || '[]');
    const filteredSessions = sessions.filter(s => s.id !== sessionId);
    localStorage.setItem('chatSessions', JSON.stringify(filteredSessions));

    // If deleting current session, start new one
    if (sessionId === window.currentSessionId) {
        startNewChat();
    }

    // Reload history
    loadChatHistory();
}

// Start a new chat
function startNewChat() {
    // Save current session before creating new one
    saveCurrentSession();

    // Reset chat state
    window.currentSessionId = generateSessionId();
    window.conversationHistory = [];

    // Clear chat UI
    const chatMessages = document.getElementById('chat-messages');
    if (chatMessages) {
        chatMessages.innerHTML = '';

        // Add welcome message
        if (typeof window.addMessage === 'function') {
            window.addMessage("Hello! I'm ClimaChat, your personal weather assistant. I can help you with current weather, forecasts, safety tips, and more. What would you like to know?", false);
        }
    }

    // Close sidebar if open
    closeHistorySidebar();
}

// Search history
function searchHistory(query) {
    const sessions = JSON.parse(localStorage.getItem('chatSessions') || '[]');
    const filteredSessions = sessions.filter(session => {
        const titleMatch = session.title?.toLowerCase().includes(query.toLowerCase());
        const messageMatch = session.messages?.some(msg =>
            msg.content.toLowerCase().includes(query.toLowerCase())
        );
        return titleMatch || messageMatch;
    });

    chatHistorySessions = filteredSessions.reverse();

    // Update display
    const historyItems = document.getElementById('history-items');
    if (historyItems && filteredSessions.length > 0) {
        loadChatHistory();
    }
}

// Event listeners
document.addEventListener('DOMContentLoaded', function() {
    // Toggle history button
    const toggleBtn = document.getElementById('toggle-history-btn');
    if (toggleBtn) {
        toggleBtn.addEventListener('click', toggleHistorySidebar);
    }

    // Close button
    const closeBtn = document.getElementById('close-history-sidebar');
    if (closeBtn) {
        closeBtn.addEventListener('click', closeHistorySidebar);
    }

    // New chat button
    const newChatBtn = document.getElementById('new-chat-btn');
    if (newChatBtn) {
        newChatBtn.addEventListener('click', startNewChat);
    }

    // Search input
    const searchInput = document.getElementById('history-search');
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            const query = e.target.value.trim();
            if (query) {
                searchHistory(query);
            } else {
                loadChatHistory();
            }
        });
    }

    // Close on outside click
    document.addEventListener('click', function(event) {
        const sidebar = document.getElementById('chat-history-sidebar');
        const toggleBtn = document.getElementById('toggle-history-btn');

        if (sidebar && toggleBtn && isHistorySidebarOpen) {
            if (!sidebar.contains(event.target) && !toggleBtn.contains(event.target)) {
                closeHistorySidebar();
            }
        }
    });

    // Auto-save on messages - wrap addMessage after it's defined
    setTimeout(() => {
        const originalAddMessage = window.addMessage;
        if (originalAddMessage && typeof originalAddMessage === 'function') {
            window.addMessage = function(...args) {
                const result = originalAddMessage.apply(this, args);
                // Save after each message
                setTimeout(() => saveCurrentSession(), 100);
                return result;
            };
        }
    }, 100);

    // Save before page unload
    window.addEventListener('beforeunload', function() {
        saveCurrentSession();
    });
});
