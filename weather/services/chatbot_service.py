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

    def get_chatbot_response(self, user_message: str, conversation_history: Optional[list] = None, user_location: str = None, current_weather_data: dict = None) -> Dict[str, Any]:
        """
        Get response from Groq API for the user message

        Args:
            user_message (str): The user's input message
            conversation_history (list, optional): Previous conversation messages
            user_location (str, optional): User's location for weather queries
            current_weather_data (dict, optional): Current weather data from the map

        Returns:
            Dict containing response data or error information
        """
        try:
            # If current weather data is provided (from map), use it directly for general queries
            weather_info = None
            detected_location = None
            if current_weather_data:
                # Format the weather data
                weather_info = (
                    f"Location: {current_weather_data.get('location', 'Unknown')}, "
                    f"Temperature: {current_weather_data.get('temperature', 'N/A')} "
                    f"(feels like {current_weather_data.get('feels_like', 'N/A')}), "
                    f"Condition: {current_weather_data.get('condition', 'N/A')}, "
                    f"Humidity: {current_weather_data.get('humidity', 'N/A')}, "
                    f"Wind: {current_weather_data.get('wind_speed', 'N/A')}, "
                    f"Pressure: {current_weather_data.get('pressure', 'N/A')}"
                )
            else:
                # Check if this is a weather query and get real weather data
                weather_result = self._check_weather_query(user_message, user_location)
                if isinstance(weather_result, dict):
                    weather_info = weather_result.get('weather_info')
                    detected_location = weather_result.get('location')
                else:
                    weather_info = weather_result

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
                    'weather_data': weather_info is not None,
                    'detected_location': detected_location
                }
            else:
                error_msg = f"API request failed with status {response.status_code}"
                logger.error(f"Groq API error: {error_msg}")

                # If we have weather data but AI failed, return formatted weather response
                if weather_info:
                    formatted_response = self._format_weather_response(weather_info, user_message)
                    return {
                        'success': True,
                        'response': formatted_response,
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

            # If we have weather data but AI timed out, return formatted weather response
            if weather_info:
                formatted_response = self._format_weather_response(weather_info, user_message)
                return {
                    'success': True,
                    'response': formatted_response,
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

            # If we have weather data but AI failed, return formatted weather response
            if weather_info:
                formatted_response = self._format_weather_response(weather_info, user_message)
                return {
                    'success': True,
                    'response': formatted_response,
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

            # If we have weather data but AI failed, return formatted weather response
            if weather_info:
                formatted_response = self._format_weather_response(weather_info, user_message)
                return {
                    'success': True,
                    'response': formatted_response,
                    'weather_data': True,
                    'fallback': True
                }

            return {
                'success': False,
                'error': str(e),
                'fallback_response': "I'm having technical difficulties. Please try again later."
            }

    def _format_weather_response(self, weather_info: str, user_message: str) -> str:
        """
        Format weather information into a conversational response

        Args:
            weather_info (str): Raw weather data string
            user_message (str): The user's original message

        Returns:
            str: Formatted conversational response
        """
        try:
            # Parse the weather info string to create a nice response
            # Weather info format: "Location: X, Temperature: Y°C (feels like Z°C), Condition: W, ..."

            # Extract key information using simple string parsing
            parts = {}
            for item in weather_info.split(', '):
                if ': ' in item:
                    key, value = item.split(': ', 1)
                    parts[key.strip()] = value.strip()

            location = parts.get('Location', 'the requested location')
            temp = parts.get('Temperature', 'N/A')
            feels_like = parts.get('feels like', 'N/A').replace(')', '')
            condition = parts.get('Condition', 'N/A')
            humidity = parts.get('Humidity', 'N/A')
            wind = parts.get('Wind', 'N/A')

            # Determine if asking about current weather or general query
            message_lower = user_message.lower()
            is_current = any(word in message_lower for word in ['now', 'current', 'today', 'right now'])

            if is_current:
                response = f"The current weather in {location} is {condition.lower()} with a temperature of {temp}"
            else:
                response = f"In {location}, it's currently {condition.lower()} with a temperature of {temp}"

            # Add feels like if different
            if feels_like and feels_like != 'N/A':
                response += f" (feels like {feels_like})"

            response += f". The humidity is at {humidity}"

            if wind and wind != 'N/A':
                response += f", and winds are blowing at {wind}"

            response += "."

            # Add a helpful closing
            if 'rain' in condition.lower() or 'storm' in condition.lower():
                response += " You might want to bring an umbrella!"
            elif 'clear' in condition.lower() or 'sunny' in condition.lower():
                response += " It's a great day to be outside!"

            return response

        except Exception as e:
            logger.error(f"Error formatting weather response: {str(e)}")
            # Fallback to simple format
            return f"Here's the weather information: {weather_info}"

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

    def _check_weather_query(self, user_message: str, user_location: str = None) -> Optional[dict]:
        """
        Check if the user message is asking for weather information and get real data

        Args:
            user_message (str): The user's message
            user_location (str, optional): User's saved location or detected location

        Returns:
            dict: Dictionary with 'weather_info' and 'location', or None if no weather query
        """
        message_lower = user_message.lower()

        # Weather query patterns
        weather_keywords = ['weather', 'temperature', 'temp', 'forecast', 'rain', 'sunny', 'cloudy', 'wind', 'humidity', 'today', 'now', 'tomorrow']
        location_patterns = [
            # Pattern: "weather today of X" - Most specific first
            r'(?:weather|temperature|temp)\s+(?:today|now|tonight|tomorrow)\s+(?:in|at|for|of)\s+([A-Za-z\s]+?)(?:\?|$|,|\.|!)',
            # Pattern: "weather in/of/at X"
            r'(?:weather|temperature|temp|humidity|wind|forecast)\s+(?:in|at|for|of)\s+([A-Za-z\s]+?)(?:\?|$|,|\.|!)',
            # Pattern: "in/of X weather"
            r'(?:in|at|for|of)\s+([A-Za-z\s]+?)\s+(?:weather|temperature|temp|humidity|wind|forecast)',
            # Pattern: "what/how is weather in X"
            r'(?:what.*?|how.*?)\s+(?:weather|temperature|temp|humidity|wind|forecast).*?(?:in|at|for|of)\s+([A-Za-z\s]+?)(?:\?|$|,|\.|!)',
            # Pattern: "X weather"
            r'([A-Za-z\s]+?)\s+(?:weather|temperature|temp|humidity|wind|forecast)(?:\?|$|,|\.|!)',
            # Pattern: "current/today weather in X"
            r'(?:current|today.*?)\s+(?:weather|temperature|temp|humidity|wind|forecast).*?(?:in|at|for|of)\s+([A-Za-z\s]+?)(?:\?|$|,|\.|!)',
            # Pattern: "the X weather"
            r'(?:the\s+)?([A-Za-z\s]+?)\s+(?:weather|temperature|temp|humidity|wind|forecast)(?:\s+today|\s+now|$|\?|!|,|\.)',
            # Pattern: "weather of/in X"
            r'(?:the\s+)?(?:weather|temperature|temp|humidity|wind|forecast)\s+(?:of|in|at|for)\s+([A-Za-z\s]+?)(?=\s+(?:today|now|tomorrow)|$|\?|!|,|\.)',
            # Follow-up patterns
            r'(?:how about|what about)\s+(?:the\s+)?(?:weather\s+(?:in|of|for)\s+)?([A-Za-z\s]+?)(?:\s+weather|$|\?|!|,|\.)',
            r'(?:and|also)\s+(?:the\s+)?(?:weather\s+(?:in|of|for)\s+)?([A-Za-z\s]+?)(?:\s+weather|$|\?|!|,|\.)',
        ]

        # Try pattern matching FIRST (more accurate for "weather in Tokyo" type queries)
        location = None
        for pattern in location_patterns:
            match = re.search(pattern, message_lower)
            if match:
                location = match.group(1).strip()
                # Remove time words from location
                time_words = ['today', 'now', 'tomorrow', 'tonight', 'morning', 'afternoon', 'evening']
                for word in time_words:
                    location = location.replace(word, '').strip()
                if location and len(location) > 2:  # Only use if location remains after cleaning
                    break

        # If pattern matching failed, look for capitalized words (city/country names)
        if not location:
            words = user_message.split()
            # Skip common words that are capitalized (sentence starters, pronouns, etc.)
            skip_words = ['I', 'What', "What's", 'When', 'Where', 'How', "How's", 'Why', 'Who', 'Is', 'Are', 'The', 'A', 'An', 'Tell', 'Show', 'Give', 'Can', 'Will', 'Would', 'Should', 'Could', 'My', 'Me', 'It']

            # Look for any capitalized words (potential city/country names)
            for i, word in enumerate(words):
                # Remove punctuation from word for checking
                clean_word = word.rstrip('?!.,;:')

                if clean_word in skip_words or len(clean_word) <= 1:
                    continue

                if clean_word[0].isupper():
                    # Check if it's followed by more capitalized words (multi-word place names)
                    location_parts = [clean_word]
                    for j in range(i + 1, len(words)):
                        if j < len(words) and words[j]:
                            next_word = words[j].rstrip('?!.,;:')
                            if len(next_word) > 0 and next_word[0].isupper() and next_word not in skip_words:
                                location_parts.append(next_word)
                            else:
                                break
                    location = ' '.join(location_parts)
                    if len(location) > 2:
                        break

        # Check if it's a weather query
        is_weather_query = any(keyword in message_lower for keyword in weather_keywords)

        # If still no location found but it's a weather query, use user's location
        if not location and is_weather_query and user_location:
            location = user_location

        # If we found a location, fetch weather for it
        if location:
            # Get weather data using the weather service
            try:
                from ..utils.weather_helpers import get_weather_for_chatbot
                weather_data = get_weather_for_chatbot(city=location)

                if weather_data['success']:
                    # Format comprehensive weather data for AI
                    formatted_data = f"Location: {weather_data['location']}, Temperature: {weather_data['temperature']} (feels like {weather_data['feels_like']}), Condition: {weather_data['condition']}, Humidity: {weather_data['humidity']}, Wind: {weather_data['wind_speed']}, Pressure: {weather_data['pressure']}, Visibility: {weather_data['visibility']}, Sunrise: {weather_data['sunrise']}, Sunset: {weather_data['sunset']}"
                    return {
                        'weather_info': formatted_data,
                        'location': location
                    }
                else:
                    # Try with Philippines suffix for local places
                    weather_data = get_weather_for_chatbot(city=f"{location},PH")
                    if weather_data['success']:
                        formatted_data = f"Location: {weather_data['location']}, Temperature: {weather_data['temperature']} (feels like {weather_data['feels_like']}), Condition: {weather_data['condition']}, Humidity: {weather_data['humidity']}, Wind: {weather_data['wind_speed']}, Pressure: {weather_data['pressure']}, Visibility: {weather_data['visibility']}, Sunrise: {weather_data['sunrise']}, Sunset: {weather_data['sunset']}"
                        return {
                            'weather_info': formatted_data,
                            'location': location
                        }
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