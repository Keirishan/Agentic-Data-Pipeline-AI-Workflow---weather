"""
Pydantic models for API request/response validation.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class AgentQueryRequest(BaseModel):
    """Agent query request model."""
    query: str = Field(..., description="User's weather-related question", min_length=1, max_length=500)
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "What is the current weather in Colombo?"
            }
        }


class WeatherInfo(BaseModel):
    """Structured weather information model."""
    temperature: Optional[float] = Field(None, description="Temperature in Celsius")
    condition: Optional[str] = Field(None, description="Weather condition")
    humidity: Optional[int] = Field(None, description="Humidity percentage")
    wind_speed: Optional[float] = Field(None, description="Wind speed in m/s")
    pressure: Optional[int] = Field(None, description="Atmospheric pressure in hPa")
    feels_like: Optional[float] = Field(None, description="Feels like temperature")
    city: Optional[str] = Field(None, description="City name")


class AgentQueryResponse(BaseModel):
    """Agent query response model."""
    query: str = Field(..., description="Original user query")
    response: str = Field(..., description="Agent's response")
    weather_data: Optional[WeatherInfo] = Field(None, description="Structured weather data if available")
    timestamp: datetime = Field(..., description="Response timestamp")
    processing_time_seconds: Optional[float] = Field(None, description="Query processing time")