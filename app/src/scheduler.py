"""
Scheduler module for periodic weather data collection.
"""
import schedule
import time
import logging
from datetime import datetime
from app.src.config import FETCH_INTERVAL_MINUTES
from app.src.cities import get_cities
from app.src.weather_fetcher import WeatherAPIFetcher
from app.src.data_cleaner import WeatherDataCleaner
from app.src.database import WeatherDatabase

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class WeatherDataPipeline:
    """Orchestrates the weather data collection pipeline."""
    
    def __init__(self, interval_minutes: int = FETCH_INTERVAL_MINUTES):
        """
        Initialize the weather data pipeline.
        
        Args:
            interval_minutes: Interval between data fetches in minutes
        """
        self.interval_minutes = interval_minutes
        self.fetcher = WeatherAPIFetcher()
        self.cleaner = WeatherDataCleaner()
        self.database = WeatherDatabase()
        self.cities = get_cities()
        self.is_running = False
        
        logger.info(f"Weather pipeline initialized with {len(self.cities)} cities")
        logger.info(f"Fetch interval: {self.interval_minutes} minutes")
    
    def run_pipeline(self):
        """Execute the complete data pipeline: fetch -> save raw -> clean -> store cleaned."""
        try:
            start_time = datetime.now()
            logger.info(f"=== Pipeline execution started at {start_time} ===")
            
            # Step 1: Fetch weather data
            logger.info("Step 1: Fetching weather data from OpenWeatherMap API...")
            raw_data = self.fetcher.fetch_weather_for_cities(self.cities)
            logger.info(f"Fetched {len(raw_data)} records")
            
            if not raw_data:
                logger.warning("No data fetched, skipping pipeline execution")
                return
            
            # Step 2: Store raw data
            logger.info("Step 2: Storing raw data in weather_data_raw table...")
            if not self.database.connection or not self.database.connection.is_connected():
                self.database.connect()
            
            raw_inserted_count = self.database.insert_raw_weather_records_batch(raw_data)
            logger.info(f"Stored {raw_inserted_count} raw records")
            
            # Step 3: Clean and normalize data
            logger.info("Step 3: Cleaning and normalizing data...")
            cleaned_data = self.cleaner.clean_weather_data(raw_data)
            logger.info(f"Cleaned {len(cleaned_data)} valid records")
            
            if not cleaned_data:
                logger.warning("No valid data after cleaning, skipping cleaned data insert")
                return
            
            # Step 4: Store cleaned data
            logger.info("Step 4: Storing cleaned data in weather_data table...")
            cleaned_inserted_count = self.database.insert_weather_records_batch(cleaned_data)
            
            # Generate summary
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            logger.info(f"=== Pipeline execution completed at {end_time} ===")
            logger.info(f"Duration: {duration:.2f} seconds")
            logger.info(f"Records fetched: {len(raw_data)}")
            logger.info(f"Raw records stored: {raw_inserted_count}")
            logger.info(f"Records cleaned: {len(cleaned_data)}")
            logger.info(f"Cleaned records stored: {cleaned_inserted_count}")
            logger.info(f"Records inserted: {inserted_count}")
            logger.info(f"Total records in database: {self.database.get_record_count()}")
            
        except Exception as e:
            logger.error(f"Error in pipeline execution: {str(e)}")
    
    def start_scheduler(self):
        """Start the scheduler to run pipeline at specified intervals."""
        try:
            self.is_running = True
            
            # Schedule the job
            schedule.every(self.interval_minutes).minutes.do(self.run_pipeline)
            
            logger.info(f"Scheduler started. Pipeline will run every {self.interval_minutes} minutes")
            logger.info("Running initial pipeline execution...")
            
            # Run immediately on start
            self.run_pipeline()
            
            # Keep the scheduler running
            while self.is_running:
                schedule.run_pending()
                time.sleep(1)
                
        except KeyboardInterrupt:
            logger.info("Scheduler stopped by user")
            self.stop_scheduler()
        except Exception as e:
            logger.error(f"Error in scheduler: {str(e)}")
            self.stop_scheduler()
    
    def stop_scheduler(self):
        """Stop the scheduler."""
        self.is_running = False
        schedule.clear()
        
        if self.database.connection and self.database.connection.is_connected():
            self.database.disconnect()
        
        logger.info("Scheduler stopped and database connection closed")
    
    def update_interval(self, new_interval_minutes: int):
        """
        Update the fetch interval.
        
        Args:
            new_interval_minutes: New interval in minutes
        """
        self.interval_minutes = new_interval_minutes
        schedule.clear()
        schedule.every(self.interval_minutes).minutes.do(self.run_pipeline)
        logger.info(f"Fetch interval updated to {self.interval_minutes} minutes")


def run_once():
    """Run the pipeline once without scheduling."""
    logger.info("Running pipeline in single execution mode...")
    pipeline = WeatherDataPipeline()
    pipeline.run_pipeline()
    pipeline.database.disconnect()
    logger.info("Single execution completed")


def run_scheduler(interval_minutes: int = FETCH_INTERVAL_MINUTES):
    """
    Start the scheduler with specified interval.
    
    Args:
        interval_minutes: Interval between data fetches in minutes
    """
    logger.info(f"Starting scheduler with {interval_minutes} minute interval...")
    pipeline = WeatherDataPipeline(interval_minutes=interval_minutes)
    pipeline.start_scheduler()


if __name__ == "__main__":
    # Run the pipeline with scheduler
    run_scheduler()
