"""
Weather data fetcher module for OpenWeatherMap API.
"""
import requests
import logging
from datetime import datetime
from typing import Dict, List, Optional
from app.src.config import WEATHER_API_KEY, WEATHER_API_BASE_URL

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class WeatherAPIFetcher:
    """Fetches weather data from OpenWeatherMap API."""
    
    def __init__(self, api_key: str = WEATHER_API_KEY):
        """
        Initialize the weather API fetcher.
        
        Args:
            api_key: OpenWeatherMap API key
        """
        self.api_key = api_key
        self.base_url = WEATHER_API_BASE_URL
        
        if not self.api_key:
            raise ValueError("Weather API key is not configured. Please check your .env file.")
    
    def fetch_weather_for_city(self, city_name: str) -> Optional[Dict]:
        """
        Fetch weather data for a single city.
        
        Args:
            city_name: Name of the city
            
        Returns:
            Dictionary containing weather data or None if request fails
        """
        try:
            params = {
                'q': city_name,
                'appid': self.api_key,
                'units': 'metric'  # Use metric units (Celsius, m/s)
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract required fields
            weather_data = {
                'city_name': data.get('name', city_name),
                'country': data.get('sys', {}).get('country', 'N/A'),
                'temperature': data.get('main', {}).get('temp'),
                'weather_condition': data.get('weather', [{}])[0].get('main', 'N/A'),
                'weather_description': data.get('weather', [{}])[0].get('description', 'N/A'),
                'humidity': data.get('main', {}).get('humidity'),
                'wind_speed': data.get('wind', {}).get('speed'),
                'pressure': data.get('main', {}).get('pressure'),
                'feels_like': data.get('main', {}).get('feels_like'),
                'timestamp': datetime.now(),
                'api_timestamp': datetime.fromtimestamp(data.get('dt', 0))
            }
            
            logger.info(f"Successfully fetched weather data for {city_name}")
            return weather_data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching weather for {city_name}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error for {city_name}: {str(e)}")
            return None
    
    def fetch_weather_for_cities(self, cities: List[str]) -> List[Dict]:
        """
        Fetch weather data for multiple cities.
        
        Args:
            cities: List of city names
            
        Returns:
            List of dictionaries containing weather data
        """
        weather_data_list = []
        total_cities = len(cities)
        
        logger.info(f"Starting to fetch weather data for {total_cities} cities...")
        
        for idx, city in enumerate(cities, 1):
            logger.info(f"Fetching {idx}/{total_cities}: {city}")
            weather_data = self.fetch_weather_for_city(city)
            
            if weather_data:
                weather_data_list.append(weather_data)
            
            # Small delay to avoid rate limiting (free tier: 60 calls/minute)
            # Uncomment if needed:
            # import time
            # time.sleep(1)
        
        logger.info(f"Successfully fetched data for {len(weather_data_list)} out of {total_cities} cities")
        return weather_data_list


def test_api_connection():
    """Test the API connection with a single city."""
    try:
        fetcher = WeatherAPIFetcher()
        result = fetcher.fetch_weather_for_city("London")
        
        if result:
            logger.info("API connection test successful!")
            logger.info(f"Sample data: {result}")
            return True
        else:
            logger.error("API connection test failed!")
            return False
    except Exception as e:
        logger.error(f"API connection test error: {str(e)}")
        return False


if __name__ == "__main__":
    # Test the API connection
    test_api_connection()
