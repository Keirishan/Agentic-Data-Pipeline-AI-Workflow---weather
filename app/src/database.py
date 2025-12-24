"""
Database module for storing weather data in MySQL.
"""
import mysql.connector
from mysql.connector import Error
import logging
from typing import List, Dict, Optional
from datetime import datetime
from app.src.config import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class WeatherDatabase:
    """Manages MySQL database operations for weather data."""
    
    def __init__(self):
        """Initialize database connection parameters."""
        self.host = DB_HOST
        self.port = DB_PORT
        self.user = DB_USER
        self.password = DB_PASSWORD
        self.database = DB_NAME
        self.connection = None
    
    def connect(self) -> bool:
        """
        Establish connection to MySQL database.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database
            )
            
            if self.connection.is_connected():
                logger.info("Successfully connected to MySQL database")
                return True
            
        except Error as e:
            logger.error(f"Error connecting to MySQL database: {str(e)}")
            return False
    
    def disconnect(self):
        """Close database connection."""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            logger.info("MySQL database connection closed")
    
    def create_database(self):
        """Create the weather database if it doesn't exist."""
        try:
            # Connect without specifying database
            connection = mysql.connector.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password
            )
            
            cursor = connection.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.database}")
            logger.info(f"Database '{self.database}' created or already exists")
            
            cursor.close()
            connection.close()
            
        except Error as e:
            logger.error(f"Error creating database: {str(e)}")
    
    def create_table(self):
        """Create the weather_data tables if they don't exist."""
        # Raw data table
        create_raw_table_query = """
        CREATE TABLE IF NOT EXISTS weather_data_raw (
            id INT AUTO_INCREMENT PRIMARY KEY,
            city_name VARCHAR(100) NOT NULL,
            country VARCHAR(10),
            temperature DECIMAL(5, 2),
            feels_like DECIMAL(5, 2),
            weather_condition VARCHAR(50),
            weather_description VARCHAR(100),
            humidity INT,
            wind_speed DECIMAL(5, 2),
            pressure INT,
            timestamp DATETIME,
            api_timestamp DATETIME,
            fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_city_raw (city_name),
            INDEX idx_fetched_at (fetched_at)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """
        
        # Cleaned data table
        create_table_query = """
        CREATE TABLE IF NOT EXISTS weather_data (
            id INT AUTO_INCREMENT PRIMARY KEY,
            city_name VARCHAR(100) NOT NULL,
            country VARCHAR(10),
            temperature DECIMAL(5, 2) NOT NULL,
            feels_like DECIMAL(5, 2),
            weather_condition VARCHAR(50) NOT NULL,
            weather_description VARCHAR(100),
            humidity INT NOT NULL,
            wind_speed DECIMAL(5, 2) NOT NULL,
            pressure INT,
            timestamp DATETIME NOT NULL,
            api_timestamp DATETIME,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_city (city_name),
            INDEX idx_timestamp (timestamp),
            INDEX idx_created_at (created_at)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """
        
        try:
            if not self.connection or not self.connection.is_connected():
                self.connect()
            
            cursor = self.connection.cursor()
            
            # Create raw data table
            cursor.execute(create_raw_table_query)
            self.connection.commit()
            logger.info("Table 'weather_data_raw' created or already exists")
            
            # Create cleaned data table
            cursor.execute(create_table_query)
            self.connection.commit()
            logger.info("Table 'weather_data' created or already exists")
            
            cursor.close()
            
        except Error as e:
            logger.error(f"Error creating table: {str(e)}")
    
    def insert_raw_weather_record(self, record: Dict) -> bool:
        """
        Insert a single raw weather record into the raw data table.
        
        Args:
            record: Dictionary containing raw weather data
            
        Returns:
            True if insert successful, False otherwise
        """
        insert_query = """
        INSERT INTO weather_data_raw 
        (city_name, country, temperature, feels_like, weather_condition, 
         weather_description, humidity, wind_speed, pressure, timestamp, api_timestamp)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        try:
            if not self.connection or not self.connection.is_connected():
                self.connect()
            
            cursor = self.connection.cursor()
            
            values = (
                record.get('city_name'),
                record.get('country'),
                record.get('temperature'),
                record.get('feels_like'),
                record.get('weather_condition'),
                record.get('weather_description'),
                record.get('humidity'),
                record.get('wind_speed'),
                record.get('pressure'),
                record.get('timestamp'),
                record.get('api_timestamp')
            )
            
            cursor.execute(insert_query, values)
            self.connection.commit()
            cursor.close()
            
            return True
            
        except Error as e:
            logger.error(f"Error inserting raw record for {record.get('city_name')}: {str(e)}")
            return False
    
    def insert_raw_weather_records_batch(self, records: List[Dict]) -> int:
        """
        Insert multiple raw weather records into the raw data table.
        
        Args:
            records: List of dictionaries containing raw weather data
            
        Returns:
            Number of successfully inserted records
        """
        insert_query = """
        INSERT INTO weather_data_raw 
        (city_name, country, temperature, feels_like, weather_condition, 
         weather_description, humidity, wind_speed, pressure, timestamp, api_timestamp)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        success_count = 0
        
        try:
            if not self.connection or not self.connection.is_connected():
                self.connect()
            
            cursor = self.connection.cursor()
            
            for record in records:
                try:
                    values = (
                        record.get('city_name'),
                        record.get('country'),
                        record.get('temperature'),
                        record.get('feels_like'),
                        record.get('weather_condition'),
                        record.get('weather_description'),
                        record.get('humidity'),
                        record.get('wind_speed'),
                        record.get('pressure'),
                        record.get('timestamp'),
                        record.get('api_timestamp')
                    )
                    
                    cursor.execute(insert_query, values)
                    success_count += 1
                    
                except Error as e:
                    logger.error(f"Error inserting raw record for {record.get('city_name')}: {str(e)}")
                    continue
            
            self.connection.commit()
            cursor.close()
            
            logger.info(f"Successfully inserted {success_count} raw records out of {len(records)}")
            
        except Error as e:
            logger.error(f"Error in batch insert: {str(e)}")
        
        return success_count
    
    def insert_weather_record(self, record: Dict) -> bool:
        """
        Insert a single weather record into the database.
        
        Args:
            record: Dictionary containing weather data
            
        Returns:
            True if insert successful, False otherwise
        """
        insert_query = """
        INSERT INTO weather_data 
        (city_name, country, temperature, feels_like, weather_condition, 
         weather_description, humidity, wind_speed, pressure, timestamp, api_timestamp)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        try:
            if not self.connection or not self.connection.is_connected():
                self.connect()
            
            cursor = self.connection.cursor()
            
            values = (
                record.get('city_name'),
                record.get('country'),
                record.get('temperature'),
                record.get('feels_like'),
                record.get('weather_condition'),
                record.get('weather_description'),
                record.get('humidity'),
                record.get('wind_speed'),
                record.get('pressure'),
                record.get('timestamp'),
                record.get('api_timestamp')
            )
            
            cursor.execute(insert_query, values)
            self.connection.commit()
            cursor.close()
            
            return True
            
        except Error as e:
            logger.error(f"Error inserting record for {record.get('city_name')}: {str(e)}")
            return False
    
    def insert_weather_records_batch(self, records: List[Dict]) -> int:
        """
        Insert multiple weather records into the database.
        
        Args:
            records: List of dictionaries containing weather data
            
        Returns:
            Number of successfully inserted records
        """
        insert_query = """
        INSERT INTO weather_data 
        (city_name, country, temperature, feels_like, weather_condition, 
         weather_description, humidity, wind_speed, pressure, timestamp, api_timestamp)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        success_count = 0
        
        try:
            if not self.connection or not self.connection.is_connected():
                self.connect()
            
            cursor = self.connection.cursor()
            
            for record in records:
                try:
                    values = (
                        record.get('city_name'),
                        record.get('country'),
                        record.get('temperature'),
                        record.get('feels_like'),
                        record.get('weather_condition'),
                        record.get('weather_description'),
                        record.get('humidity'),
                        record.get('wind_speed'),
                        record.get('pressure'),
                        record.get('timestamp'),
                        record.get('api_timestamp')
                    )
                    
                    cursor.execute(insert_query, values)
                    success_count += 1
                    
                except Error as e:
                    logger.error(f"Error inserting record for {record.get('city_name')}: {str(e)}")
                    continue
            
            self.connection.commit()
            cursor.close()
            
            logger.info(f"Successfully inserted {success_count} out of {len(records)} records")
            
        except Error as e:
            logger.error(f"Error in batch insert: {str(e)}")
        
        return success_count
    
    def get_latest_records(self, limit: int = 10) -> List[Dict]:
        """
        Retrieve the most recent weather records.
        
        Args:
            limit: Maximum number of records to retrieve
            
        Returns:
            List of weather records
        """
        query = """
        SELECT * FROM weather_data 
        ORDER BY created_at DESC 
        LIMIT %s
        """
        
        try:
            if not self.connection or not self.connection.is_connected():
                self.connect()
            
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, (limit,))
            records = cursor.fetchall()
            cursor.close()
            
            return records
            
        except Error as e:
            logger.error(f"Error retrieving records: {str(e)}")
            return []
    
    def get_record_count(self) -> int:
        """
        Get the total number of records in the database.
        
        Returns:
            Total record count
        """
        query = "SELECT COUNT(*) as count FROM weather_data"
        
        try:
            if not self.connection or not self.connection.is_connected():
                self.connect()
            
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query)
            result = cursor.fetchone()
            cursor.close()
            
            return result['count'] if result else 0
            
        except Error as e:
            logger.error(f"Error getting record count: {str(e)}")
            return 0
    
    def test_connection(self) -> bool:
        """
        Test database connection.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            if self.connect():
                logger.info("Database connection test successful")
                self.disconnect()
                return True
            return False
        except Exception as e:
            logger.error(f"Database connection test failed: {str(e)}")
            return False


def initialize_database():
    """Initialize database and create necessary tables."""
    try:
        db = WeatherDatabase()
        
        # Create database
        db.create_database()
        
        # Connect and create table
        if db.connect():
            db.create_table()
            db.disconnect()
            logger.info("Database initialization complete")
            return True
        else:
            logger.error("Failed to initialize database")
            return False
            
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        return False


if __name__ == "__main__":
    # Test database setup
    initialize_database()
