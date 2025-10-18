"""
Temperature Alert Service
Provides temperature analysis and safety recommendations using AI
"""

import requests
import json
import logging
from django.conf import settings
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class TemperatureAlertService:
    """Service class for generating temperature alerts and recommendations"""

    def __init__(self):
        self.api_key = settings.GROQ_API_KEY
        self.model = settings.GROQ_MODEL
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def get_temperature_category(self, temp_celsius: float) -> Dict[str, Any]:
        """
        Categorize temperature and return basic alert configuration
        """
        temp = float(temp_celsius)

        if temp >= 35:
            return {
                'level': 'Very Hot',
                'color': 'bg-red-600',
                'textColor': 'text-white',
                'borderColor': 'border-red-600',
                'icon': '🔥',
                'isExtreme': True,
                'severity': 'extreme_heat'
            }
        elif temp >= 30:
            return {
                'level': 'Hot',
                'color': 'bg-orange-500',
                'textColor': 'text-white',
                'borderColor': 'border-orange-500',
                'icon': '☀️',
                'isExtreme': True,
                'severity': 'high_heat'
            }
        elif temp < 0:
            return {
                'level': 'Freezing',
                'color': 'bg-purple-900',
                'textColor': 'text-white',
                'borderColor': 'border-purple-900',
                'icon': '🥶',
                'isExtreme': True,
                'severity': 'freezing'
            }
        elif temp < 10:
            return {
                'level': 'Very Cold',
                'color': 'bg-indigo-700',
                'textColor': 'text-white',
                'borderColor': 'border-indigo-700',
                'icon': '❄️',
                'isExtreme': True,
                'severity': 'very_cold'
            }
        elif temp < 15:
            return {
                'level': 'Cold',
                'color': 'bg-blue-600',
                'textColor': 'text-white',
                'borderColor': 'border-blue-600',
                'icon': '🧥',
                'isExtreme': True,
                'severity': 'cold'
            }
        else:
            return {
                'level': 'Comfortable',
                'color': 'bg-green-500',
                'textColor': 'text-white',
                'borderColor': 'border-green-500',
                'icon': '✨',
                'isExtreme': False,
                'severity': 'comfortable'
            }

    def get_ai_recommendations(self, temperature: float, location: str, weather_condition: str = None) -> Dict[str, Any]:
        """
        Use AI to generate temperature-specific safety recommendations
        """
        category = self.get_temperature_category(temperature)

        # Don't generate recommendations for comfortable temperatures
        if not category['isExtreme']:
            return None

        # Create prompt for AI to generate recommendations
        prompt = f"""You are a weather safety expert. Generate a temperature alert for the following conditions:

Location: {location}
Temperature: {temperature}°C
Temperature Category: {category['level']}
Weather Condition: {weather_condition or 'Not specified'}

Please provide:
1. A brief alert message (1-2 sentences) explaining the temperature risk
2. 5-7 specific, actionable safety recommendations for this temperature

Format your response as JSON:
{{
    "alert_message": "Brief description of the temperature risk",
    "recommendations": [
        "Recommendation 1",
        "Recommendation 2",
        ...
    ]
}}

Be specific and practical. Focus on health and safety."""

        try:
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a weather safety expert providing temperature-specific health and safety recommendations. Always respond with valid JSON only."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.7,
                "max_tokens": 500
            }

            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=payload,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                ai_response = result['choices'][0]['message']['content'].strip()

                # Try to parse JSON response
                try:
                    # Remove markdown code blocks if present
                    if '```json' in ai_response:
                        ai_response = ai_response.split('```json')[1].split('```')[0].strip()
                    elif '```' in ai_response:
                        ai_response = ai_response.split('```')[1].split('```')[0].strip()

                    alert_data = json.loads(ai_response)

                    # Combine category data with AI-generated content
                    return {
                        **category,
                        'message': alert_data.get('alert_message', 'Temperature alert for your safety.'),
                        'recommendations': alert_data.get('recommendations', []),
                        'temperature': temperature,
                        'location': location
                    }

                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse AI response as JSON: {e}")
                    logger.error(f"AI Response: {ai_response}")

                    # Return basic alert without AI recommendations
                    return self.get_fallback_alert(category, temperature, location)

            else:
                logger.error(f"AI API error: {response.status_code} - {response.text}")
                return self.get_fallback_alert(category, temperature, location)

        except Exception as e:
            logger.error(f"Error generating AI recommendations: {str(e)}")
            return self.get_fallback_alert(category, temperature, location)

    def get_fallback_alert(self, category: Dict, temperature: float, location: str) -> Dict[str, Any]:
        """
        Return a basic alert when AI recommendations cannot be generated
        """
        fallback_messages = {
            'extreme_heat': 'Extreme heat detected! This temperature can be dangerous to your health.',
            'high_heat': 'Hot weather conditions present. Stay cool and hydrated.',
            'freezing': 'Freezing temperatures! Extreme cold can be life-threatening.',
            'very_cold': 'Very cold temperatures! Take precautions to stay warm.',
            'cold': 'Cold weather conditions present. Dress warmly.'
        }

        fallback_recommendations = {
            'extreme_heat': [
                'Stay indoors during peak heat hours',
                'Drink plenty of water throughout the day',
                'Avoid strenuous outdoor activities',
                'Check on elderly neighbors and family',
                'Never leave children or pets in vehicles'
            ],
            'high_heat': [
                'Stay hydrated',
                'Seek shade when outdoors',
                'Wear light, loose-fitting clothing',
                'Apply sunscreen regularly',
                'Take frequent breaks if working outside'
            ],
            'freezing': [
                'Stay indoors as much as possible',
                'Dress in multiple warm layers',
                'Protect extremities from frostbite',
                'Keep emergency supplies ready',
                'Ensure pets have warm shelter'
            ],
            'very_cold': [
                'Minimize outdoor exposure',
                'Wear warm layers and cover exposed skin',
                'Watch for signs of hypothermia',
                'Keep heating systems functioning',
                'Check on vulnerable individuals'
            ],
            'cold': [
                'Dress in warm layers',
                'Wear a coat, hat, and gloves',
                'Limit time spent outdoors',
                'Keep your home heated',
                'Stay dry to avoid losing body heat'
            ]
        }

        severity = category.get('severity', 'comfortable')

        return {
            **category,
            'message': fallback_messages.get(severity, 'Temperature alert for your area.'),
            'recommendations': fallback_recommendations.get(severity, []),
            'temperature': temperature,
            'location': location
        }
