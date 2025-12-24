CREATE DATABASE IF NOT EXISTS weather_data

USE weather_data;

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