"""Health Tips Service - Generates AI-powered health and safety tips based on weather data"""
import logging
import requests
import json
import re
from django.conf import settings
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class HealthTipsService:
    """Service for generating AI-powered health tips based on weather conditions"""

    def __init__(self):
        self.api_key = settings.GROQ_API_KEY
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"
        self.model = settings.GROQ_MODEL

    def generate_health_tips(self, weather_data: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate health and safety tips based on weather data using AI"""
        if not self.api_key:
            logger.warning("GROQ_API_KEY not configured, using fallback tips")
            return self._get_fallback_tips(weather_data)

        try:
            response = requests.post(
                self.api_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a health and safety expert. Generate concise health tips based on weather. Respond with ONLY valid JSON format: {\"tips\": [{\"title\": \"string\", \"description\": \"string (max 100 chars)\", \"category\": \"temperature|humidity|air|uv|general\"}]}. No markdown, no extra text."
                        },
                        {"role": "user", "content": self._build_prompt(weather_data)}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 600,
                    "response_format": {"type": "json_object"}
                },
                timeout=15
            )

            if response.status_code == 200:
                tips = self._parse_ai_response(response.json()['choices'][0]['message']['content'])
                if tips:
                    logger.info(f"Generated {len(tips)} AI health tips")
                    return tips
            else:
                logger.error(f"Groq API error: {response.status_code}")

        except requests.exceptions.Timeout:
            logger.error("Health tips API timeout")
        except Exception as e:
            logger.error(f"Error generating health tips: {str(e)}")

        return self._get_fallback_tips(weather_data)

    def _build_prompt(self, weather_data: Dict[str, Any]) -> str:
        """Build prompt for AI based on weather data"""
        temp = weather_data.get('temperature', 'N/A')
        feels_like = weather_data.get('feels_like', 'N/A')
        condition = weather_data.get('condition', 'N/A')
        humidity = weather_data.get('humidity', 'N/A')
        wind_speed = weather_data.get('wind_speed', 'N/A')
        air_quality = weather_data.get('air_quality', 'N/A')

        prompt = f"""Create 3-4 personalized health and safety tips based on current weather:

Weather Conditions:
- Temperature: {temp}°C (feels like {feels_like}°C)
- Condition: {condition}
- Humidity: {humidity}%
- Wind Speed: {wind_speed} km/h
- Air Quality Index: {air_quality} (1=Good, 5=Very Poor)

Requirements:
- Each tip must be specific to these conditions
- Title: Short, actionable (e.g., "Stay Hydrated", "Sun Protection")
- Description: Complete sentence, 60-100 characters, explain WHY or HOW
- Category: temperature, humidity, air, uv, or general

Return format: {{"tips": [{{"title": "Stay Hydrated", "description": "High temperatures increase water needs. Drink fluids regularly.", "category": "temperature"}}]}}"""

        return prompt

    def _parse_ai_response(self, response: str) -> List[Dict[str, str]]:
        """Parse AI response into structured tips"""
        import json
        import re

        try:
            # Clean response - remove markdown code blocks if present
            response = re.sub(r'```json\s*', '', response)
            response = re.sub(r'```\s*', '', response)
            response = response.strip()

            # Parse JSON
            data = json.loads(response)

            # Handle both array and object formats
            tips = None
            if isinstance(data, dict):
                # If it's an object, look for 'tips' key
                tips = data.get('tips', [])
            elif isinstance(data, list):
                # If it's already an array
                tips = data

            # Validate and structure tips
            if tips and isinstance(tips, list):
                valid_tips = []
                for tip in tips:
                    if isinstance(tip, dict) and 'title' in tip and 'description' in tip:
                        valid_tips.append({
                            'title': str(tip.get('title', ''))[:100],
                            'description': str(tip.get('description', ''))[:150],
                            'category': tip.get('category', 'general')
                        })

                if valid_tips:
                    logger.info(f"Parsed {len(valid_tips)} valid tips from AI response")
                    return valid_tips

            logger.warning(f"No valid tips found in response structure: {type(data)}")

        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {str(e)}, Response: {response[:200]}")
        except Exception as e:
            logger.error(f"Error parsing AI response: {str(e)}", exc_info=True)

        return []

    def _get_fallback_tips(self, weather_data: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate fallback tips when AI is unavailable"""
        tips = []

        temp = weather_data.get('temperature')
        humidity = weather_data.get('humidity')
        air_quality = weather_data.get('air_quality')

        # Temperature-based tip
        if temp is not None:
            if temp > 30:
                tips.append({
                    'title': 'Stay Hydrated',
                    'description': 'High temperatures require increased water intake. Drink fluids regularly.',
                    'category': 'temperature'
                })
            elif temp < 10:
                tips.append({
                    'title': 'Dress Warmly',
                    'description': 'Layer clothing to protect against cold temperatures.',
                    'category': 'temperature'
                })

        # Humidity-based tip
        if humidity is not None:
            if humidity > 70:
                tips.append({
                    'title': 'High Humidity Alert',
                    'description': 'Humid conditions may affect breathing. Take breaks if needed.',
                    'category': 'humidity'
                })

        # Air quality tip
        if air_quality is not None and air_quality != '--':
            try:
                aqi = int(air_quality)
                if aqi >= 3:
                    tips.append({
                        'title': 'Air Quality Notice',
                        'description': 'Consider limiting outdoor activities if you have respiratory issues.',
                        'category': 'air'
                    })
                else:
                    tips.append({
                        'title': 'Good Air Quality',
                        'description': 'Great conditions for outdoor activities and exercise.',
                        'category': 'air'
                    })
            except (ValueError, TypeError):
                pass

        # Default tip if no specific conditions
        if not tips:
            tips.append({
                'title': 'General Wellness',
                'description': 'Check weather conditions before planning outdoor activities.',
                'category': 'general'
            })

        return tips[:4]  # Limit to 4 tips
