// Chat History Sidebar
document.addEventListener('DOMContentLoaded', function() {
    const sidebar = document.getElementById('chat-history-sidebar');
    const toggleBtn = document.getElementById('toggle-history-btn');
    const closeBtn = document.getElementById('close-history-sidebar');
    const historyItems = document.getElementById('history-items');
    const historyLoading = document.getElementById('history-loading');
    const historyEmpty = document.getElementById('history-empty');

    // Toggle sidebar
    toggleBtn.addEventListener('click', function() {
        sidebar.classList.toggle('translate-x-full');
        if (!sidebar.classList.contains('translate-x-full')) {
            loadChatHistory();
        }
    });

    closeBtn.addEventListener('click', function() {
        sidebar.classList.add('translate-x-full');
    });

    // Load chat history
    async function loadChatHistory() {
        historyLoading.classList.remove('hidden');
        historyItems.classList.add('hidden');
        historyEmpty.classList.add('hidden');

        try {
            const response = await fetch('/api/admin/chat-history/?limit=50');
            const data = await response.json();

            historyLoading.classList.add('hidden');

            if (data.success && data.conversations.length > 0) {
                historyItems.classList.remove('hidden');
                displayHistory(data.conversations);
            } else {
                historyEmpty.classList.remove('hidden');
            }
        } catch (error) {
            console.error('Failed to load chat history:', error);
            historyLoading.classList.add('hidden');
            historyEmpty.classList.remove('hidden');
        }
    }

    // Store conversations for reference
    let conversationsList = [];

    // Display history
    function displayHistory(conversations) {
        conversationsList = conversations; // Store for later access

        historyItems.innerHTML = conversations.map((session, index) => {
            const date = new Date(session.timestamp);
            const timeStr = date.toLocaleString('en-US', {
                month: 'short',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });

            const messageCount = session.message_count || 1;
            const firstMsg = session.first_message || session.messages[0].message;

            return `
                <div class="bg-gray-50 rounded-lg p-3 hover:bg-gray-100 transition-colors border border-gray-200 relative group"
                     data-conv-index="${index}">
                    <button class="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity bg-red-500 hover:bg-red-600 text-white rounded p-1 z-10"
                            data-delete-session="${session.session_id}"
                            data-delete-index="${index}"
                            title="Delete conversation">
                        <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                        </svg>
                    </button>
                    <div class="cursor-pointer" data-load-index="${index}">
                        <div class="flex items-start justify-between mb-2">
                            <p class="text-xs font-medium text-blue-600">${timeStr}</p>
                            <div class="flex items-center gap-2">
                                ${session.user_mentioned ? `<span class="text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded">${session.user_mentioned}</span>` : ''}
                                ${messageCount > 1 ? `<span class="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded">${messageCount} msgs</span>` : ''}
                            </div>
                        </div>
                        <p class="text-sm text-gray-800 font-medium mb-1 line-clamp-2">${firstMsg}</p>
                        <p class="text-xs text-gray-600 line-clamp-2">${session.messages[0].response.substring(0, 100)}...</p>
                    </div>
                </div>
            `;
        }).join('');

        // Add click handlers for loading conversations
        historyItems.querySelectorAll('[data-load-index]').forEach(item => {
            item.addEventListener('click', function() {
                const index = parseInt(this.dataset.loadIndex);
                const session = conversationsList[index];
                loadConversation(session);
            });
        });

        // Add click handlers for delete buttons
        historyItems.querySelectorAll('[data-delete-session]').forEach(btn => {
            btn.addEventListener('click', async function(e) {
                e.stopPropagation(); // Prevent loading conversation when clicking delete

                const sessionId = this.dataset.deleteSession;
                const index = parseInt(this.dataset.deleteIndex);

                if (!confirm('Are you sure you want to delete this conversation?')) {
                    return;
                }

                try {
                    const response = await fetch(`/api/admin/chat-history/`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': getCookie('csrftoken')
                        },
                        body: JSON.stringify({ session_id: sessionId })
                    });

                    const data = await response.json();

                    if (data.success) {
                        // Remove from UI
                        conversationsList.splice(index, 1);
                        displayHistory(conversationsList);
                        console.log('Conversation deleted');
                    } else {
                        alert('Failed to delete conversation: ' + (data.error || 'Unknown error'));
                    }
                } catch (error) {
                    console.error('Delete error:', error);
                    alert('Failed to delete conversation');
                }
            });
        });
    }

    // Helper function to get CSRF token
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

    // Load a specific conversation session
    function loadConversation(session) {
        // Clear current chat
        const chatMessages = document.getElementById('chat-messages');
        chatMessages.innerHTML = '';

        // Reset conversation history
        conversationHistory = [];

        // Load all messages in this session
        session.messages.forEach(msg => {
            addMessage(msg.message, true);
            addMessage(msg.response, false);

            // Add to conversation history for context
            conversationHistory.push(
                { role: 'user', content: msg.message },
                { role: 'assistant', content: msg.response }
            );

            // Restore last mentioned user from last message
            if (msg.user_mentioned) {
                lastMentionedUser = msg.user_mentioned;
            }
        });

        // Restore session ID - continue in same conversation thread
        currentSessionId = session.session_id;

        if (lastMentionedUser) {
            console.log('Restored context: last mentioned user =', lastMentionedUser);
        }

        // Close sidebar
        sidebar.classList.add('translate-x-full');

        console.log('Conversation loaded. You can continue chatting from here.');
    }

    // New Chat Button
    const newChatBtn = document.getElementById('new-chat-btn');
    if (newChatBtn) {
        newChatBtn.addEventListener('click', function() {
            // Clear chat messages
            const chatMessages = document.getElementById('chat-messages');
            if (chatMessages) {
                chatMessages.innerHTML = '';

                // Add welcome message
                setTimeout(() => {
                    addMessage("Hello! I'm ClimaChat, your AI weather assistant. I can help you check weather for any user location. How can I assist you today?", false);
                }, 300);
            }

            // Clear conversation history
            if (typeof conversationHistory !== 'undefined') {
                conversationHistory = [];
            }

            // Reset last mentioned user
            if (typeof lastMentionedUser !== 'undefined') {
                lastMentionedUser = null;
            }

            // Reset session ID - start fresh conversation thread
            currentSessionId = null;

            // Show notification
            console.log('Started new chat - session will be created on first message');
        });
    }
});
