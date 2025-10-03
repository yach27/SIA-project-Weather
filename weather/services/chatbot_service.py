"""
Weather Chatbot Service using Groq API
Handles all chatbot interactions and API calls
"""

import requests
import json
import logging
import re
from django.conf import settings
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class WeatherChatbotService:
    """Service class for handling weather chatbot interactions"""

    def __init__(self):
        self.api_key = settings.GROQ_API_KEY
        self.model = settings.GROQ_MODEL
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def get_system_prompt(self) -> str:
        """Return the system prompt for the weather chatbot"""
        return """You are ClimaChat, a helpful weather assistant chatbot with access to real-time weather data. Your primary role is to help users with weather-related queries.

Key guidelines:
- Always be friendly, helpful, and professional
- Focus on weather-related topics (current weather, forecasts, weather alerts, etc.)
- You have access to real weather data from OpenWeatherMap API
- When real weather data is provided in the context, use it to give accurate, current information
- If asked about non-weather topics, politely redirect to weather assistance
- Provide clear, concise responses with actual data when available
- If you need location information, ask for it clearly
- Present weather information in a conversational, easy-to-understand format

Example responses:
- For greetings: Welcome them and ask how you can help with weather
- For weather queries with data: Use the real data to provide current conditions, temperature, etc.
- For weather queries without data: Ask for location and explain what information you can provide
- For non-weather topics: Politely redirect to weather assistance

When you receive real weather data in the format [REAL WEATHER DATA: ...], use that information to provide accurate, current weather conditions.

Keep responses conversational but informative."""

    def get_chatbot_response(self, user_message: str, conversation_history: Optional[list] = None) -> Dict[str, Any]:
        """
        Get response from Groq API for the user message

        Args:
            user_message (str): The user's input message
            conversation_history (list, optional): Previous conversation messages

        Returns:
            Dict containing response data or error information
        """
        try:
            # Check if this is a weather query and get real weather data
            weather_info = self._check_weather_query(user_message)

            # Build messages array
            messages = [
                {"role": "system", "content": self.get_system_prompt()}
            ]

            # Add conversation history if provided
            if conversation_history:
                messages.extend(conversation_history)

            # If weather data is available, add it to the context
            if weather_info:
                weather_context = f"[REAL WEATHER DATA: {weather_info}]\n\nUser asks: {user_message}\n\nPlease use the real weather data provided above to answer accurately and conversationally."
                messages.append({"role": "user", "content": weather_context})
            else:
                messages.append({"role": "user", "content": user_message})

            # Prepare API request
            payload = {
                "model": self.model,
                "messages": messages,
                "max_tokens": 500,
                "temperature": 0.7,
                "top_p": 1,
                "stream": False
            }

            # Make API request
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=payload,
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                bot_response = data['choices'][0]['message']['content']

                return {
                    'success': True,
                    'response': bot_response,
                    'usage': data.get('usage', {}),
                    'model': data.get('model', self.model),
                    'weather_data': weather_info is not None
                }
            else:
                error_msg = f"API request failed with status {response.status_code}"
                logger.error(f"Groq API error: {error_msg}")

                # If we have weather data but AI failed, return weather data directly
                if weather_info:
                    return {
                        'success': True,
                        'response': weather_info,
                        'weather_data': True,
                        'fallback': True
                    }

                return {
                    'success': False,
                    'error': error_msg,
                    'fallback_response': self._get_fallback_response(user_message)
                }

        except requests.exceptions.Timeout:
            logger.error("Groq API request timed out")

            # If we have weather data but AI timed out, return weather data
            if weather_info:
                return {
                    'success': True,
                    'response': weather_info,
                    'weather_data': True,
                    'fallback': True
                }

            return {
                'success': False,
                'error': 'API request timed out',
                'fallback_response': "I'm experiencing some delays. Please try again in a moment."
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Groq API request error: {str(e)}")

            # If we have weather data but AI failed, return weather data
            if weather_info:
                return {
                    'success': True,
                    'response': weather_info,
                    'weather_data': True,
                    'fallback': True
                }

            return {
                'success': False,
                'error': str(e),
                'fallback_response': self._get_fallback_response(user_message)
            }
        except Exception as e:
            logger.error(f"Unexpected error in chatbot service: {str(e)}")

            # If we have weather data but AI failed, return weather data
            if weather_info:
                return {
                    'success': True,
                    'response': weather_info,
                    'weather_data': True,
                    'fallback': True
                }

            return {
                'success': False,
                'error': str(e),
                'fallback_response': "I'm having technical difficulties. Please try again later."
            }

    def _get_fallback_response(self, user_message: str) -> str:
        """
        Provide fallback responses when API is unavailable

        Args:
            user_message (str): The user's message

        Returns:
            str: Appropriate fallback response
        """
        message_lower = user_message.lower()

        if any(greeting in message_lower for greeting in ['hello', 'hi', 'hey', 'good morning', 'good afternoon']):
            return "Hello! I'm ClimaChat, your weather assistant. I'm currently experiencing some technical issues, but I'm here to help with weather information. How can I assist you today?"

        elif any(weather_word in message_lower for weather_word in ['weather', 'temperature', 'rain', 'snow', 'forecast']):
            return "I'd love to help you with weather information! I'm currently having some connectivity issues, but please try again in a moment. In the meantime, you can ask me about current weather, forecasts, or weather alerts for any location."

        elif 'help' in message_lower:
            return "I'm ClimaChat, your weather assistant! I can help with weather forecasts, current conditions, and weather alerts. Just ask me something like 'What's the weather in [city]?' or 'Weather forecast for [location]'. I'm currently experiencing some technical issues, so please be patient."

        else:
            return "I'm ClimaChat, your weather assistant! I'm currently experiencing some technical difficulties, but I'm here to help with weather-related questions. Please try again in a moment."

    def _check_weather_query(self, user_message: str) -> Optional[str]:
        """
        Check if the user message is asking for weather information and get real data

        Args:
            user_message (str): The user's message

        Returns:
            str: Weather information if found, None otherwise
        """
        message_lower = user_message.lower()

        # Weather query patterns
        weather_keywords = ['weather', 'temperature', 'temp', 'forecast', 'rain', 'sunny', 'cloudy', 'wind', 'humidity', 'today', 'now', 'tomorrow']
        location_patterns = [
            r'(?:weather|temperature|temp|humidity|wind|forecast)\s+(?:in|at|for|of)\s+([A-Za-z\s]+?)(?:\?|$|,|\.|!)',
            r'(?:in|at|for|of)\s+([A-Za-z\s]+?)\s+(?:weather|temperature|temp|humidity|wind|forecast)',
            r'(?:what.*?|how.*?)\s+(?:weather|temperature|temp|humidity|wind|forecast).*?(?:in|at|for|of)\s+([A-Za-z\s]+?)(?:\?|$|,|\.|!)',
            r'([A-Za-z\s]+?)\s+(?:weather|temperature|temp|humidity|wind|forecast)(?:\?|$|,|\.|!)',
            r'weather\s+(?:in|at|for|of)\s+([A-Za-z\s]+?)(?:\?|$|,|\.|!)',
            r'(?:current|today.*?)\s+(?:weather|temperature|temp|humidity|wind|forecast).*?(?:in|at|for|of)\s+([A-Za-z\s]+?)(?:\?|$|,|\.|!)',
            r'(?:the\s+)?([A-Za-z\s]+?)\s+(?:weather|temperature|temp|humidity|wind|forecast)(?:\s+today|\s+now|$|\?|!|,|\.)',
            r'(?:the\s+)?(?:weather|temperature|temp|humidity|wind|forecast)\s+(?:of|in|at|for)\s+([A-Za-z\s]+?)(?=\s+(?:today|now|tomorrow)|$|\?|!|,|\.)',
            r'(?:how about|what about)\s+(?:the\s+)?(?:weather\s+(?:in|of|for)\s+)?([A-Za-z\s]+?)(?:\s+weather|$|\?|!|,|\.)',
            r'(?:and|also)\s+(?:the\s+)?(?:weather\s+(?:in|of|for)\s+)?([A-Za-z\s]+?)(?:\s+weather|$|\?|!|,|\.)',
        ]

        # Check if it's a weather query or location follow-up
        is_weather_query = any(keyword in message_lower for keyword in weather_keywords)
        is_location_followup = any(phrase in message_lower for phrase in ['how about', 'what about', 'and', 'also'])

        if is_weather_query or is_location_followup:
            # Try to extract location
            location = None

            for pattern in location_patterns:
                match = re.search(pattern, message_lower)
                if match:
                    location = match.group(1).strip()
                    # Remove time words from location
                    time_words = ['today', 'now', 'tomorrow', 'tonight', 'morning', 'afternoon', 'evening']
                    for word in time_words:
                        location = location.replace(word, '').strip()
                    if location:  # Only use if location remains after cleaning
                        break

            # If no location found, check for direct mentions of place names
            if not location:
                # Simple location extraction - look for capitalized words that might be places
                words = user_message.split()
                for i, word in enumerate(words):
                    if word[0].isupper() and len(word) > 2:
                        # Check if it's followed by more capitalized words
                        location_parts = [word]
                        for j in range(i + 1, len(words)):
                            if j < len(words) and words[j][0].isupper():
                                location_parts.append(words[j])
                            else:
                                break
                        location = ' '.join(location_parts)
                        break

            if location:
                # Get weather data using the weather service
                try:
                    from ..views import get_weather_for_chatbot
                    weather_data = get_weather_for_chatbot(city=location)

                    if weather_data['success']:
                        # Format comprehensive weather data for AI
                        formatted_data = f"Location: {weather_data['location']}, Temperature: {weather_data['temperature']} (feels like {weather_data['feels_like']}), Condition: {weather_data['condition']}, Humidity: {weather_data['humidity']}, Wind: {weather_data['wind_speed']}, Pressure: {weather_data['pressure']}, Visibility: {weather_data['visibility']}, Sunrise: {weather_data['sunrise']}, Sunset: {weather_data['sunset']}"
                        return formatted_data
                    else:
                        # Try with Philippines suffix for local places
                        weather_data = get_weather_for_chatbot(city=f"{location},PH")
                        if weather_data['success']:
                            formatted_data = f"Location: {weather_data['location']}, Temperature: {weather_data['temperature']} (feels like {weather_data['feels_like']}), Condition: {weather_data['condition']}, Humidity: {weather_data['humidity']}, Wind: {weather_data['wind_speed']}, Pressure: {weather_data['pressure']}, Visibility: {weather_data['visibility']}, Sunrise: {weather_data['sunrise']}, Sunset: {weather_data['sunset']}"
                            return formatted_data
                        else:
                            return None  # Let AI handle this case

                except Exception as e:
                    logger.error(f"Error getting weather data: {str(e)}")
                    return None  # Let AI handle error cases

        return None

    def validate_api_key(self) -> bool:
        """
        Validate if the API key is working

        Returns:
            bool: True if API key is valid, False otherwise
        """
        try:
            test_payload = {
                "model": self.model,
                "messages": [{"role": "user", "content": "Hello"}],
                "max_tokens": 10
            }

            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=test_payload,
                timeout=10
            )

            return response.status_code == 200
        except:
            return False