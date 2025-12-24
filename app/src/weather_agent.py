"""
Weather AI Agent using OpenAI Swarm SDK.
Answers weather-related questions using stored data with fallback to API.
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from openai import OpenAI
from app.src.config import OPENAI_API_KEY, WEATHER_API_KEY
from app.src.database import WeatherDatabase
from app.src.weather_fetcher import WeatherAPIFetcher

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class WeatherAgent:
    """AI Agent for weather queries using OpenAI with custom tools."""
    
    def __init__(self):
        """Initialize the weather agent."""
        if not OPENAI_API_KEY:
            raise ValueError("OpenAI API key not configured. Check your .env file.")
        
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.database = WeatherDatabase()
        self.weather_fetcher = WeatherAPIFetcher()
        
        # System prompt for weather-only responses
        self.system_prompt = """You are a helpful weather assistant that ONLY answers questions about weather.

Your capabilities:
1. Query stored weather data from a MySQL database
2. Provide current weather information for cities
3. Calculate weather statistics (averages, trends)
4. Answer questions about temperature, humidity, wind speed, and weather conditions
5. If database query fails, fall back to live API data

Important rules:
- ONLY answer weather-related questions
- For non-weather questions, politely refuse and redirect to weather topics
- Be conversational and helpful
- Provide temperature in Celsius
- Include relevant details like humidity, wind speed, and conditions
- When showing historical data, mention the time period

For unrelated questions, respond with:
"I'm a weather assistant and can only help with weather-related questions. Please ask me about weather conditions, temperatures, forecasts, or climate data for various cities."
"""
        
        # Define available tools
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_current_weather",
                    "description": "Get the most recent weather data for a specific city from the database",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "city_name": {
                                "type": "string",
                                "description": "The name of the city (e.g., 'London', 'Colombo', 'Galle')"
                            }
                        },
                        "required": ["city_name"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_weather_history",
                    "description": "Get historical weather data for a city within a specific time period",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "city_name": {
                                "type": "string",
                                "description": "The name of the city"
                            },
                            "days": {
                                "type": "integer",
                                "description": "Number of days to look back (e.g., 7 for last week)",
                                "default": 1
                            }
                        },
                        "required": ["city_name"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_average_temperature",
                    "description": "Calculate average temperature for a city over a specific time period",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "city_name": {
                                "type": "string",
                                "description": "The name of the city"
                            },
                            "days": {
                                "type": "integer",
                                "description": "Number of days to calculate average for",
                                "default": 7
                            }
                        },
                        "required": ["city_name"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "compare_cities_weather",
                    "description": "Compare current weather between multiple cities",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "city_names": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of city names to compare"
                            }
                        },
                        "required": ["city_names"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_live_weather",
                    "description": "Fallback: Get live weather data directly from OpenWeatherMap API if database query fails",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "city_name": {
                                "type": "string",
                                "description": "The name of the city"
                            }
                        },
                        "required": ["city_name"]
                    }
                }
            }
        ]
        
        logger.info("Weather Agent initialized successfully")
    
    def get_current_weather(self, city_name: str) -> Dict[str, Any]:
        """Get the most recent weather data for a city."""
        try:
            if not self.database.connection or not self.database.connection.is_connected():
                self.database.connect()
            
            query = """
                SELECT city_name, country, temperature, feels_like, 
                       weather_condition, weather_description, humidity, 
                       wind_speed, pressure, timestamp, created_at
                FROM weather_data 
                WHERE city_name LIKE %s
                ORDER BY created_at DESC 
                LIMIT 1
            """
            
            cursor = self.database.connection.cursor(dictionary=True)
            cursor.execute(query, (f"%{city_name}%",))
            result = cursor.fetchone()
            cursor.close()
            
            if result:
                return {
                    "success": True,
                    "data": {
                        "city": result["city_name"],
                        "country": result["country"],
                        "temperature": float(result["temperature"]),
                        "feels_like": float(result["feels_like"]),
                        "condition": result["weather_condition"],
                        "description": result["weather_description"],
                        "humidity": result["humidity"],
                        "wind_speed": float(result["wind_speed"]),
                        "pressure": result["pressure"],
                        "timestamp": result["timestamp"].strftime("%Y-%m-%d %H:%M:%S"),
                        "data_age": str(datetime.now() - result["created_at"])
                    }
                }
            else:
                return {
                    "success": False,
                    "error": f"No data found for {city_name}",
                    "fallback": "try_live_api"
                }
                
        except Exception as e:
            logger.error(f"Error querying weather for {city_name}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "fallback": "try_live_api"
            }
    
    def get_weather_history(self, city_name: str, days: int = 7) -> Dict[str, Any]:
        """Get historical weather data for a city."""
        try:
            if not self.database.connection or not self.database.connection.is_connected():
                self.database.connect()
            
            since_date = datetime.now() - timedelta(days=days)
            
            query = """
                SELECT temperature, humidity, wind_speed, weather_condition,
                       timestamp, created_at
                FROM weather_data 
                WHERE city_name LIKE %s AND created_at >= %s
                ORDER BY created_at DESC
            """
            
            cursor = self.database.connection.cursor(dictionary=True)
            cursor.execute(query, (f"%{city_name}%", since_date))
            results = cursor.fetchall()
            cursor.close()
            
            if results:
                return {
                    "success": True,
                    "city": city_name,
                    "days": days,
                    "record_count": len(results),
                    "data": [
                        {
                            "temperature": float(r["temperature"]),
                            "humidity": r["humidity"],
                            "wind_speed": float(r["wind_speed"]),
                            "condition": r["weather_condition"],
                            "time": r["created_at"].strftime("%Y-%m-%d %H:%M:%S")
                        }
                        for r in results
                    ]
                }
            else:
                return {
                    "success": False,
                    "error": f"No historical data found for {city_name} in the last {days} days"
                }
                
        except Exception as e:
            logger.error(f"Error querying history for {city_name}: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def get_average_temperature(self, city_name: str, days: int = 7) -> Dict[str, Any]:
        """Calculate average temperature for a city."""
        try:
            if not self.database.connection or not self.database.connection.is_connected():
                self.database.connect()
            
            since_date = datetime.now() - timedelta(days=days)
            
            query = """
                SELECT 
                    AVG(temperature) as avg_temp,
                    MIN(temperature) as min_temp,
                    MAX(temperature) as max_temp,
                    COUNT(*) as record_count
                FROM weather_data 
                WHERE city_name LIKE %s AND created_at >= %s
            """
            
            cursor = self.database.connection.cursor(dictionary=True)
            cursor.execute(query, (f"%{city_name}%", since_date))
            result = cursor.fetchone()
            cursor.close()
            
            if result and result["record_count"] > 0:
                return {
                    "success": True,
                    "city": city_name,
                    "period": f"last {days} days",
                    "average_temperature": round(float(result["avg_temp"]), 2),
                    "min_temperature": round(float(result["min_temp"]), 2),
                    "max_temperature": round(float(result["max_temp"]), 2),
                    "data_points": result["record_count"]
                }
            else:
                return {
                    "success": False,
                    "error": f"No data found for {city_name} in the last {days} days"
                }
                
        except Exception as e:
            logger.error(f"Error calculating average for {city_name}: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def compare_cities_weather(self, city_names: List[str]) -> Dict[str, Any]:
        """Compare current weather between cities."""
        try:
            comparisons = []
            
            for city in city_names:
                weather = self.get_current_weather(city)
                if weather.get("success"):
                    comparisons.append(weather["data"])
            
            if comparisons:
                return {
                    "success": True,
                    "cities_compared": len(comparisons),
                    "data": comparisons
                }
            else:
                return {
                    "success": False,
                    "error": "Could not retrieve data for any of the specified cities"
                }
                
        except Exception as e:
            logger.error(f"Error comparing cities: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def get_live_weather(self, city_name: str) -> Dict[str, Any]:
        """Fallback: Get live weather from OpenWeatherMap API."""
        try:
            logger.info(f"Falling back to live API for {city_name}")
            
            result = self.weather_fetcher.fetch_weather_for_city(city_name)
            
            if result:
                return {
                    "success": True,
                    "source": "live_api",
                    "data": {
                        "city": result["city_name"],
                        "country": result["country"],
                        "temperature": result["temperature"],
                        "feels_like": result["feels_like"],
                        "condition": result["weather_condition"],
                        "description": result["weather_description"],
                        "humidity": result["humidity"],
                        "wind_speed": result["wind_speed"],
                        "pressure": result["pressure"],
                        "timestamp": result["timestamp"].strftime("%Y-%m-%d %H:%M:%S")
                    }
                }
            else:
                return {
                    "success": False,
                    "error": f"Could not retrieve weather data for {city_name} from API"
                }
                
        except Exception as e:
            logger.error(f"Error with live API for {city_name}: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def execute_tool(self, tool_name: str, arguments: Dict) -> str:
        """Execute a tool and return formatted results."""
        try:
            if tool_name == "get_current_weather":
                result = self.get_current_weather(arguments["city_name"])
                
                # Fallback to live API if needed
                if not result.get("success") and result.get("fallback") == "try_live_api":
                    result = self.get_live_weather(arguments["city_name"])
                
                return str(result)
            
            elif tool_name == "get_weather_history":
                result = self.get_weather_history(
                    arguments["city_name"],
                    arguments.get("days", 7)
                )
                return str(result)
            
            elif tool_name == "get_average_temperature":
                result = self.get_average_temperature(
                    arguments["city_name"],
                    arguments.get("days", 7)
                )
                return str(result)
            
            elif tool_name == "compare_cities_weather":
                result = self.compare_cities_weather(arguments["city_names"])
                return str(result)
            
            elif tool_name == "get_live_weather":
                result = self.get_live_weather(arguments["city_name"])
                return str(result)
            
            else:
                return f"Unknown tool: {tool_name}"
                
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {str(e)}")
            return f"Error: {str(e)}"
    
    def chat(self, user_message: str) -> str:
        """Process a user message and return the agent's response."""
        try:
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_message}
            ]
            
            # Initial API call
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                tools=self.tools,
                temperature=0.7
            )
            
            # Process response
            while response.choices[0].finish_reason == "tool_calls":
                message = response.choices[0].message
                messages.append(message)
                
                # Execute tool calls
                for tool_call in message.tool_calls:
                    function_name = tool_call.function.name
                    arguments = eval(tool_call.function.arguments)
                    
                    logger.info(f"Executing tool: {function_name} with args: {arguments}")
                    
                    result = self.execute_tool(function_name, arguments)
                    
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": function_name,
                        "content": result
                    })
                
                # Get next response
                response = self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages,
                    tools=self.tools,
                    temperature=0.7
                )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error in chat: {str(e)}")
            return f"I apologize, but I encountered an error: {str(e)}"
    
    def close(self):
        """Clean up resources."""
        if self.database.connection:
            self.database.disconnect()


def run_interactive_agent():
    """Run the agent in interactive mode."""
    print("=" * 60)
    print("Weather AI Agent - Interactive Mode")
    print("=" * 60)
    print("\nI can answer questions about weather for various cities.")
    print("Examples:")
    print("  - What is the current weather in Colombo?")
    print("  - What was the average temperature in Galle last week?")
    print("  - Compare weather in London and Paris")
    print("\nType 'exit' or 'quit' to stop.\n")
    print("=" * 60)
    
    agent = WeatherAgent()
    
    try:
        while True:
            user_input = input("\n🌤️  You: ").strip()
            
            if user_input.lower() in ['exit', 'quit', 'bye']:
                print("\n👋 Goodbye!")
                break
            
            if not user_input:
                continue
            
            print("\n🤖 Agent: ", end="", flush=True)
            response = agent.chat(user_input)
            print(response)
            
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    finally:
        agent.close()


if __name__ == "__main__":
    run_interactive_agent()
