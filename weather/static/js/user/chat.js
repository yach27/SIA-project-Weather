// Global variables accessible to chat_history.js
window.conversationHistory = [];
window.currentSessionId = null;

document.addEventListener('DOMContentLoaded', function() {
    // Initialize chat history
    if (typeof initializeChatHistory === 'function') {
        initializeChatHistory();
    }

    const chatInput = document.getElementById('chat-input');
    const sendBtn = document.getElementById('send-btn');
    const chatMessages = document.getElementById('chat-messages');
    const weatherMapPanel = document.getElementById('weather-map-panel');
    const weatherDataDisplay = document.getElementById('weather-data-display');

    let isLoading = false;
    let weatherMap = null;
    let userLocation = null;
    let currentWeatherData = null;
    let userLocationWeatherData = null;

    async function getUserLocation() {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                async function(position) {
                    const lat = position.coords.latitude;
                    const lon = position.coords.longitude;

                    try {
                        const response = await fetch(`https://api.openweathermap.org/geo/1.0/reverse?lat=${lat}&lon=${lon}&limit=1&appid=${OPENWEATHER_API_KEY}`);
                        const data = await response.json();
                        if (data && data.length > 0) {
                            userLocation = data[0].name;
                            await fetchAndDisplayWeather(lat, lon);
                        }
                    } catch (error) {
                        console.error('Could not get location name:', error);
                    }
                },
                function(error) {
                    console.error('Geolocation error:', error.message);
                }
            );
        }
    }

    async function fetchAndDisplayWeather(lat, lon) {
        try {
            const response = await fetch(`https://api.openweathermap.org/data/2.5/weather?lat=${lat}&lon=${lon}&units=metric&appid=${OPENWEATHER_API_KEY}`);
            const data = await response.json();

            if (data && data.main) {
                const weatherInfo = {
                    location: `${data.name}, ${data.sys.country}`,
                    temperature: `${Math.round(data.main.temp)}°C`,
                    feels_like: `${Math.round(data.main.feels_like)}°C`,
                    condition: data.weather[0].description.charAt(0).toUpperCase() + data.weather[0].description.slice(1),
                    condition_main: data.weather[0].main,
                    humidity: `${data.main.humidity}%`,
                    wind_speed: `${Math.round(data.wind.speed * 3.6)} km/h`,
                    pressure: `${data.main.pressure} hPa`,
                    coordinates: {
                        lat: data.coord.lat,
                        lon: data.coord.lon
                    }
                };

                displayWeatherData(weatherInfo);
                userLocationWeatherData = weatherInfo;
            }
        } catch (error) {
            console.error('Error fetching weather:', error);
        }
    }

    getUserLocation();

    function getCurrentTime() {
        const now = new Date();
        return now.toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit',
            hour12: true
        });
    }

    function initWeatherMap() {
        if (weatherMap) {
            weatherMap.remove();
        }

        weatherMap = L.map('chat-weather-map').setView([14.5995, 120.9842], 6);

        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors'
        }).addTo(weatherMap);

        return weatherMap;
    }

    function displayWeatherData(weatherData) {
        currentWeatherData = weatherData;

        weatherMapPanel.classList.remove('hidden');

        const tempValue = parseFloat(weatherData.temperature);
        const tempAlert = getTemperatureAlert(tempValue);

        // Check and show temperature alert dialog if extreme
        if (tempAlert.isExtreme) {
            checkAndShowTemperatureAlert(tempValue, weatherData.location, weatherData.condition_main);
        }

        const weatherHtml = `
            <div class="bg-white rounded-lg p-3 shadow-sm space-y-3">
                <div class="flex items-center justify-between mb-2">
                    <h4 class="font-semibold text-gray-900">${weatherData.location}</h4>
                    <span class="text-2xl">${getWeatherIcon(weatherData.condition_main)}</span>
                </div>

                <div class="${tempAlert.color} ${tempAlert.textColor} rounded-lg p-3 text-center">
                    <div class="flex items-center justify-center space-x-2 mb-1">
                        <span class="text-xl">${tempAlert.icon}</span>
                        <span class="font-bold text-lg">${tempAlert.level}</span>
                    </div>
                    <p class="text-xs opacity-90">${tempAlert.message}</p>
                </div>

                <div class="space-y-2 text-sm">
                    <div class="flex justify-between">
                        <span class="text-gray-600">Temperature:</span>
                        <span class="font-medium">${weatherData.temperature}</span>
                    </div>
                    <div class="flex justify-between">
                        <span class="text-gray-600">Feels like:</span>
                        <span>${weatherData.feels_like}</span>
                    </div>
                    <div class="flex justify-between">
                        <span class="text-gray-600">Condition:</span>
                        <span>${weatherData.condition}</span>
                    </div>
                    <div class="flex justify-between">
                        <span class="text-gray-600">Humidity:</span>
                        <span>${weatherData.humidity}</span>
                    </div>
                    <div class="flex justify-between">
                        <span class="text-gray-600">Wind:</span>
                        <span>${weatherData.wind_speed}</span>
                    </div>
                    <div class="flex justify-between">
                        <span class="text-gray-600">Pressure:</span>
                        <span>${weatherData.pressure}</span>
                    </div>
                </div>
            </div>
        `;

        weatherDataDisplay.innerHTML = weatherHtml;

        if (weatherData.coordinates) {
            if (!weatherMap) {
                initWeatherMap();
            }

            const lat = weatherData.coordinates.lat;
            const lon = weatherData.coordinates.lon;

            weatherMap.setView([lat, lon], 10);

            weatherMap.eachLayer(function(layer) {
                if (layer instanceof L.Marker || layer.options.opacity === 0.6) {
                    weatherMap.removeLayer(layer);
                }
            });

            const marker = L.marker([lat, lon]).addTo(weatherMap);
            marker.bindPopup(`
                <strong>${weatherData.location}</strong><br>
                ${weatherData.condition}<br>
                ${weatherData.temperature}
            `).openPopup();

            L.tileLayer(`https://tile.openweathermap.org/map/temp_new/{z}/{x}/{y}.png?appid=${OPENWEATHER_API_KEY}`, {
                opacity: 0.6
            }).addTo(weatherMap);
        }
    }

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

    function getTemperatureAlert(tempCelsius) {
        const temp = parseFloat(tempCelsius);

        if (temp >= 35) {
            return {
                level: 'Very Hot',
                color: 'bg-red-600',
                textColor: 'text-white',
                icon: '🔥',
                message: 'Extreme heat! Stay hydrated and avoid prolonged sun exposure.',
                isExtreme: true
            };
        } else if (temp >= 30) {
            return {
                level: 'Hot',
                color: 'bg-orange-500',
                textColor: 'text-white',
                icon: '☀️',
                message: 'Hot weather. Stay cool and drink plenty of water.',
                isExtreme: true
            };
        } else if (temp >= 25) {
            return {
                level: 'Warm',
                color: 'bg-yellow-400',
                textColor: 'text-gray-800',
                icon: '🌤️',
                message: 'Pleasant warm weather.',
                isExtreme: false
            };
        } else if (temp >= 20) {
            return {
                level: 'Comfortable',
                color: 'bg-green-500',
                textColor: 'text-white',
                icon: '✨',
                message: 'Comfortable temperature.',
                isExtreme: false
            };
        } else if (temp >= 15) {
            return {
                level: 'Cool',
                color: 'bg-blue-400',
                textColor: 'text-white',
                icon: '🌬️',
                message: 'Cool weather. Consider a light jacket.',
                isExtreme: false
            };
        } else if (temp >= 10) {
            return {
                level: 'Cold',
                color: 'bg-blue-600',
                textColor: 'text-white',
                icon: '🧥',
                message: 'Cold weather. Wear warm clothing.',
                isExtreme: true
            };
        } else if (temp >= 0) {
            return {
                level: 'Very Cold',
                color: 'bg-indigo-700',
                textColor: 'text-white',
                icon: '❄️',
                message: 'Very cold! Bundle up and stay warm.',
                isExtreme: true
            };
        } else {
            return {
                level: 'Freezing',
                color: 'bg-purple-900',
                textColor: 'text-white',
                icon: '🥶',
                message: 'Freezing temperatures! Dress warmly and limit outdoor exposure.',
                isExtreme: true
            };
        }
    }

    // Make addMessage globally accessible for chat_history.js
    window.addMessage = function addMessage(content, isUser = true, isLoading = false) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `flex ${isUser ? 'justify-end' : 'justify-start'}`;

        const time = getCurrentTime();
        let messageContent = '';

        if (isLoading) {
            messageContent = `
                <div class="max-w-xs lg:max-w-md bg-gray-100 text-gray-900 rounded-lg px-4 py-3">
                    <div class="flex items-center space-x-2">
                        <div class="flex space-x-1">
                            <div class="w-2 h-2 bg-blue-400 rounded-full animate-bounce"></div>
                            <div class="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style="animation-delay: 0.1s;"></div>
                            <div class="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style="animation-delay: 0.2s;"></div>
                        </div>
                        <span class="text-xs text-gray-500 ml-2">ClimaChat is thinking...</span>
                    </div>
                </div>
            `;
        } else {
            messageContent = `
                <div class="max-w-sm lg:max-w-lg xl:max-w-xl ${isUser ? 'bg-blue-500 text-white' : 'bg-gray-100 text-gray-900'} rounded-lg px-4 py-3 break-words">
                    ${!isUser ? '<p class="text-xs text-gray-500 mb-1">ClimaChat</p>' : ''}
                    <p class="text-sm whitespace-pre-wrap leading-relaxed">${content}</p>
                    <p class="text-xs ${isUser ? 'text-blue-100' : 'text-gray-500'} mt-1">${time}</p>
                </div>
            `;
        }

        messageDiv.innerHTML = messageContent;
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        return messageDiv;
    };

    function removeMessage(messageElement) {
        if (messageElement && messageElement.parentNode) {
            messageElement.parentNode.removeChild(messageElement);
        }
    }

    async function sendMessageToAPI(message) {
        try {
            const payload = {
                message: message,
                conversation_history: window.conversationHistory,
                user_location: userLocation
            };

            const generalQuestions = ['weather today', 'current weather', 'weather now', 'what is the weather', 'whats the weather', "what's the weather", 'how is the weather', 'hows the weather', "how's the weather"];
            const locationQuestions = ['my location', 'my current location', 'current location', 'here', 'my area', 'my place', 'where i am'];

            const isGeneralQuestion = generalQuestions.some(q => message.toLowerCase().includes(q));
            const isLocationQuestion = locationQuestions.some(q => message.toLowerCase().includes(q));

            if (isLocationQuestion && userLocationWeatherData) {
                payload.current_weather_data = userLocationWeatherData;
            } else if (isGeneralQuestion && currentWeatherData) {
                payload.current_weather_data = currentWeatherData;
            }

            const response = await fetch('/api/chatbot/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(payload)
            });

            const data = await response.json();

            if (data.success) {
                window.conversationHistory.push(
                    { role: 'user', content: message },
                    { role: 'assistant', content: data.response }
                );

                if (window.conversationHistory.length > 20) {
                    window.conversationHistory = window.conversationHistory.slice(-20);
                }

                if (data.weather_info) {
                    displayWeatherData(data.weather_info);
                }

                return {
                    success: true,
                    response: data.response,
                    fallback: data.fallback || false,
                    weather_data: data.weather_data || false,
                    weather_info: data.weather_info || null
                };
            } else {
                throw new Error(data.error || 'Unknown error');
            }
        } catch (error) {
            console.error('Chatbot API error:', error);
            return {
                success: false,
                response: "I'm experiencing some technical difficulties right now. Please try again in a moment!"
            };
        }
    }

    async function sendMessage(message = null) {
        if (isLoading) return;

        const messageText = message || chatInput.value.trim();
        if (!messageText) return;

        isLoading = true;
        chatInput.disabled = true;
        sendBtn.disabled = true;
        sendBtn.innerHTML = '<div class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>';

        addMessage(messageText, true);
        if (!message) chatInput.value = '';

        const loadingMessage = addMessage('', false, true);

        try {
            const result = await sendMessageToAPI(messageText);
            removeMessage(loadingMessage);
            addMessage(result.response, false);
        } catch (error) {
            removeMessage(loadingMessage);
            addMessage("I'm sorry, I'm having trouble right now. Please try again later!", false);
        } finally {
            isLoading = false;
            chatInput.disabled = false;
            sendBtn.disabled = false;
            sendBtn.innerHTML = `
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"></path>
                </svg>
                <span>Send</span>
            `;
            chatInput.focus();
        }
    }

    function clearDefaultContent() {
        const defaultContent = chatMessages.querySelector('.text-center');
        if (defaultContent) {
            chatMessages.innerHTML = '';
        }
    }

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

    setTimeout(() => {
        initWeatherMap();
    }, 100);

    setTimeout(() => {
        clearDefaultContent();
        addMessage("Hello! I'm ClimaChat, your personal weather assistant. I can help you with current weather, forecasts, safety tips, and more. What would you like to know?", false);
    }, 500);
});
