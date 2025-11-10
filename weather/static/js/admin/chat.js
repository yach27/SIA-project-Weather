// Global variables and functions accessible to all scripts
let conversationHistory = [];
let lastMentionedUser = null;
let currentSessionId = null;  // Track current conversation session

// Generate unique session ID
function generateSessionId() {
    return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
}

function getCurrentTime() {
    const now = new Date();
    return now.toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit',
        hour12: false
    });
}

function addMessage(content, isUser = true, isLoading = false) {
    const chatMessages = document.getElementById('chat-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `flex ${isUser ? 'justify-end' : 'justify-start'}`;

    const time = getCurrentTime();
    let messageContent = '';

    if (isLoading) {
        messageContent = `
            <div class="max-w-xs lg:max-w-md bg-gray-100 text-gray-900 rounded-lg px-3 py-2">
                <p class="text-xs text-gray-500 mb-1">Weather Bot</p>
                <div class="flex items-center space-x-1">
                    <div class="flex space-x-1">
                        <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                        <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.1s;"></div>
                        <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.2s;"></div>
                    </div>
                    <span class="text-xs text-gray-500 ml-2">Thinking...</span>
                </div>
            </div>
        `;
    } else {
        messageContent = `
            <div class="max-w-xs lg:max-w-md ${isUser ? 'bg-blue-500 text-white' : 'bg-gray-100 text-gray-900'} rounded-lg px-3 py-2">
                ${!isUser ? '<p class="text-xs text-gray-500 mb-1">Weather Bot</p>' : ''}
                <p class="text-sm whitespace-pre-wrap">${content}</p>
                <p class="text-xs ${isUser ? 'text-blue-100' : 'text-gray-500'} mt-1">${time}</p>
            </div>
        `;
    }

    messageDiv.innerHTML = messageContent;
    chatMessages.appendChild(messageDiv);

    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;

    return messageDiv;
}

function removeMessage(messageElement) {
    if (messageElement && messageElement.parentNode) {
        messageElement.parentNode.removeChild(messageElement);
    }
}

// Real-time weather chatbot using Groq API
document.addEventListener('DOMContentLoaded', function() {
    const chatInput = document.getElementById('chat-input');
    const sendBtn = document.getElementById('send-btn');
    const chatMessages = document.getElementById('chat-messages');

    let isLoading = false;

    async function sendMessageToAPI(message) {
        try {
            // Fetch user locations for admin context
            let userLocationsData = [];
            let weatherDataForUser = null;

            try {
                const locResponse = await fetch('/api/admin/user-locations/');
                const locData = await locResponse.json();
                if (locData.success) {
                    userLocationsData = locData.locations;

                    // Check if message mentions a user and weather-related keywords
                    const weatherKeywords = ['weather', 'temperature', 'temp', 'rain', 'sunny', 'cloud', 'condition', 'hot', 'cold', 'humid'];
                    const hasWeatherWord = weatherKeywords.some(word => message.toLowerCase().includes(word));

                    // Check for follow-up affirmations
                    const affirmations = ['yes', 'yeah', 'yep', 'sure', 'ok', 'okay', 'yup'];
                    const isAffirmation = affirmations.some(word => message.toLowerCase().trim() === word);

                    let targetUser = null;

                    // If affirmation and we have a last mentioned user, use that user
                    if (isAffirmation && lastMentionedUser) {
                        targetUser = userLocationsData.find(loc => loc.username === lastMentionedUser);
                    } else if (hasWeatherWord || message.toLowerCase().includes('where')) {
                        // Find which user is mentioned
                        for (const loc of userLocationsData) {
                            if (message.toLowerCase().includes(loc.username.toLowerCase())) {
                                targetUser = loc;
                                lastMentionedUser = loc.username;
                                break;
                            }
                        }
                    } else {
                        // Check if any username is mentioned for future follow-up
                        for (const loc of userLocationsData) {
                            if (message.toLowerCase().includes(loc.username.toLowerCase())) {
                                lastMentionedUser = loc.username;
                                break;
                            }
                        }
                    }

                    // Fetch weather if we have a target user
                    if (targetUser) {
                        // Zoom map to user's location
                        if (window.zoomToUser) {
                            window.zoomToUser(targetUser.username);
                        }

                        // Fetch weather
                        try {
                            const weatherResponse = await fetch(`https://api.openweathermap.org/data/2.5/weather?lat=${targetUser.latitude}&lon=${targetUser.longitude}&appid=${OPENWEATHER_API_KEY}&units=metric`);
                            const weatherData = await weatherResponse.json();

                            if (weatherResponse.ok) {
                                weatherDataForUser = {
                                    username: targetUser.username,
                                    location: targetUser.location_name || 'Unknown',
                                    temperature: weatherData.main.temp,
                                    feels_like: weatherData.main.feels_like,
                                    condition: weatherData.weather[0].description,
                                    humidity: weatherData.main.humidity,
                                    wind_speed: weatherData.wind.speed,
                                    pressure: weatherData.main.pressure
                                };
                            }
                        } catch (err) {
                            console.error('Error fetching weather:', err);
                        }
                    }
                }
            } catch (e) {
                console.error('Could not fetch user locations:', e);
            }

            // Generate session ID if starting new conversation
            if (!currentSessionId) {
                currentSessionId = generateSessionId();
            }

            const requestData = {
                message: message,
                conversation_history: conversationHistory,
                user_locations: userLocationsData,
                user_weather_data: weatherDataForUser,
                is_admin: true,
                save_to_history: true,
                session_id: currentSessionId
            };

            const response = await fetch('/api/chatbot/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestData)
            });

            const data = await response.json();

            if (data.success) {
                // Add to conversation history
                conversationHistory.push(
                    { role: 'user', content: message },
                    { role: 'assistant', content: data.response }
                );

                // Keep only last 10 exchanges (20 messages) for context
                if (conversationHistory.length > 20) {
                    conversationHistory = conversationHistory.slice(-20);
                }

                return {
                    success: true,
                    response: data.response,
                    fallback: data.fallback || false
                };
            } else {
                console.error('API returned error:', data.error);
                throw new Error(data.error || 'Unknown error');
            }
        } catch (error) {
            console.error('Chatbot API error:', error);
            return {
                success: false,
                response: "I'm experiencing some technical difficulties right now. Please try again in a moment, or ask me about weather information!"
            };
        }
    }

    async function sendMessage() {
        if (isLoading) return;

        const message = chatInput.value.trim();
        if (!message) return;

        // Disable input while processing
        isLoading = true;
        chatInput.disabled = true;
        sendBtn.disabled = true;
        sendBtn.innerHTML = '<div class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>';

        // Add user message
        addMessage(message, true);
        chatInput.value = '';

        // Add loading indicator
        const loadingMessage = addMessage('', false, true);

        try {
            // Send to API
            const result = await sendMessageToAPI(message);

            // Remove loading indicator
            removeMessage(loadingMessage);

            // Add bot response
            addMessage(result.response, false);
        } catch (error) {
            // Remove loading indicator
            removeMessage(loadingMessage);

            // Add error message
            addMessage("I'm sorry, I'm having trouble right now. Please try again later!", false);
        } finally {
            // Re-enable input
            isLoading = false;
            chatInput.disabled = false;
            sendBtn.disabled = false;
            sendBtn.innerHTML = `
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"></path>
                </svg>
            `;
            chatInput.focus();
        }
    }

    // Clear default "no messages" content on first message
    function clearDefaultContent() {
        const defaultContent = chatMessages.querySelector('.text-center');
        if (defaultContent) {
            chatMessages.innerHTML = '';
        }
    }

    // Event listeners
    sendBtn.addEventListener('click', function() {
        clearDefaultContent();
        sendMessage();
    });

    chatInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            clearDefaultContent();
            sendMessage();
        }
    });

    // Add welcome message on load
    setTimeout(() => {
        clearDefaultContent();
        addMessage("Hello! I'm ClimaChat, your AI weather assistant powered by Llama 3.3. I'm here to help you with weather information, forecasts, and weather-related questions. How can I assist you today?", false);
    }, 500);
});
