"""
Data cleaning and normalization module for weather data.
"""
import logging
from typing import Dict, List, Optional
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class WeatherDataCleaner:
    """Cleans and normalizes weather data."""
    
    # Valid ranges for weather data
    TEMP_MIN = -100  # Celsius
    TEMP_MAX = 60    # Celsius
    HUMIDITY_MIN = 0  # Percentage
    HUMIDITY_MAX = 100  # Percentage
    WIND_SPEED_MIN = 0  # m/s
    WIND_SPEED_MAX = 150  # m/s (extreme hurricane)
    PRESSURE_MIN = 800  # hPa
    PRESSURE_MAX = 1100  # hPa
    
    @staticmethod
    def is_valid_temperature(temp: Optional[float]) -> bool:
        """
        Check if temperature is within valid range.
        
        Args:
            temp: Temperature value in Celsius
            
        Returns:
            True if valid, False otherwise
        """
        if temp is None:
            return False
        return WeatherDataCleaner.TEMP_MIN <= temp <= WeatherDataCleaner.TEMP_MAX
    
    @staticmethod
    def is_valid_humidity(humidity: Optional[float]) -> bool:
        """
        Check if humidity is within valid range.
        
        Args:
            humidity: Humidity percentage
            
        Returns:
            True if valid, False otherwise
        """
        if humidity is None:
            return False
        return WeatherDataCleaner.HUMIDITY_MIN <= humidity <= WeatherDataCleaner.HUMIDITY_MAX
    
    @staticmethod
    def is_valid_wind_speed(wind_speed: Optional[float]) -> bool:
        """
        Check if wind speed is within valid range.
        
        Args:
            wind_speed: Wind speed in m/s
            
        Returns:
            True if valid, False otherwise
        """
        if wind_speed is None:
            return False
        return WeatherDataCleaner.WIND_SPEED_MIN <= wind_speed <= WeatherDataCleaner.WIND_SPEED_MAX
    
    @staticmethod
    def is_valid_pressure(pressure: Optional[float]) -> bool:
        """
        Check if pressure is within valid range.
        
        Args:
            pressure: Atmospheric pressure in hPa
            
        Returns:
            True if valid, False otherwise
        """
        if pressure is None:
            return False
        return WeatherDataCleaner.PRESSURE_MIN <= pressure <= WeatherDataCleaner.PRESSURE_MAX
    
    @staticmethod
    def normalize_city_name(city_name: Optional[str]) -> str:
        """
        Normalize city name to consistent format.
        
        Args:
            city_name: Raw city name
            
        Returns:
            Normalized city name
        """
        if not city_name:
            return "Unknown"
        
        # Strip whitespace and capitalize properly
        normalized = city_name.strip().title()
        return normalized
    
    @staticmethod
    def normalize_weather_condition(condition: Optional[str]) -> str:
        """
        Normalize weather condition to consistent format.
        
        Args:
            condition: Raw weather condition
            
        Returns:
            Normalized weather condition
        """
        if not condition:
            return "Unknown"
        
        # Convert to title case for consistency
        normalized = condition.strip().title()
        return normalized
    
    @staticmethod
    def clean_weather_record(record: Dict) -> Optional[Dict]:
        """
        Clean and validate a single weather record.
        
        Args:
            record: Raw weather data record
            
        Returns:
            Cleaned record or None if validation fails
        """
        try:
            # Extract and validate required fields
            city_name = WeatherDataCleaner.normalize_city_name(record.get('city_name'))
            temperature = record.get('temperature')
            humidity = record.get('humidity')
            wind_speed = record.get('wind_speed')
            weather_condition = WeatherDataCleaner.normalize_weather_condition(
                record.get('weather_condition')
            )
            
            # Validate critical fields
            if not WeatherDataCleaner.is_valid_temperature(temperature):
                logger.warning(f"Invalid temperature for {city_name}: {temperature}")
                return None
            
            if not WeatherDataCleaner.is_valid_humidity(humidity):
                logger.warning(f"Invalid humidity for {city_name}: {humidity}")
                return None
            
            if not WeatherDataCleaner.is_valid_wind_speed(wind_speed):
                logger.warning(f"Invalid wind speed for {city_name}: {wind_speed}")
                return None
            
            # Optional: validate pressure if present
            pressure = record.get('pressure')
            if pressure is not None and not WeatherDataCleaner.is_valid_pressure(pressure):
                logger.warning(f"Invalid pressure for {city_name}: {pressure}")
                pressure = None
            
            # Create cleaned record
            cleaned_record = {
                'city_name': city_name,
                'country': record.get('country', 'N/A').strip().upper(),
                'temperature': round(float(temperature), 2),
                'feels_like': round(float(record.get('feels_like', temperature)), 2),
                'weather_condition': weather_condition,
                'weather_description': record.get('weather_description', '').strip().title(),
                'humidity': int(humidity),
                'wind_speed': round(float(wind_speed), 2),
                'pressure': int(pressure) if pressure else None,
                'timestamp': record.get('timestamp', datetime.now()),
                'api_timestamp': record.get('api_timestamp', datetime.now())
            }
            
            return cleaned_record
            
        except Exception as e:
            logger.error(f"Error cleaning record: {str(e)}")
            return None
    
    @staticmethod
    def clean_weather_data(data_list: List[Dict]) -> List[Dict]:
        """
        Clean and normalize a list of weather records.
        
        Args:
            data_list: List of raw weather data records
            
        Returns:
            List of cleaned and validated records
        """
        cleaned_data = []
        total_records = len(data_list)
        
        logger.info(f"Starting data cleaning for {total_records} records...")
        
        for record in data_list:
            cleaned_record = WeatherDataCleaner.clean_weather_record(record)
            if cleaned_record:
                cleaned_data.append(cleaned_record)
        
        success_count = len(cleaned_data)
        failed_count = total_records - success_count
        
        logger.info(f"Data cleaning complete: {success_count} valid, {failed_count} invalid records")
        
        return cleaned_data
    
    @staticmethod
    def get_data_quality_report(data_list: List[Dict]) -> Dict:
        """
        Generate a data quality report.
        
        Args:
            data_list: List of weather data records
            
        Returns:
            Dictionary containing quality metrics
        """
        if not data_list:
            return {
                'total_records': 0,
                'valid_records': 0,
                'invalid_records': 0,
                'quality_percentage': 0.0
            }
        
        total = len(data_list)
        valid = sum(1 for record in data_list if WeatherDataCleaner.clean_weather_record(record))
        invalid = total - valid
        quality = (valid / total) * 100 if total > 0 else 0
        
        return {
            'total_records': total,
            'valid_records': valid,
            'invalid_records': invalid,
            'quality_percentage': round(quality, 2)
        }


if __name__ == "__main__":
    # Test data cleaning
    test_data = [
        {
            'city_name': 'new york',
            'country': 'us',
            'temperature': 25.5,
            'weather_condition': 'clear',
            'humidity': 65,
            'wind_speed': 5.2,
            'pressure': 1013,
            'feels_like': 24.8
        },
        {
            'city_name': 'invalid city',
            'temperature': 999,  # Invalid
            'humidity': 50,
            'wind_speed': 10
        }
    ]
    
    cleaner = WeatherDataCleaner()
    cleaned = cleaner.clean_weather_data(test_data)
    
    logger.info(f"Cleaned data: {cleaned}")
    logger.info(f"Quality report: {cleaner.get_data_quality_report(test_data)}")
