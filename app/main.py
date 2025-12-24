import logging
import time
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Optional, List
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from app.src.config import FETCH_INTERVAL_MINUTES,RUN_INITIAL_FETCH,API_HOST,API_PORT
from app.src.database import initialize_database, WeatherDatabase
from app.src.scheduler import WeatherDataPipeline
from app.src.weather_agent import WeatherAgent
from app.src.api_schemas import AgentQueryRequest,AgentQueryResponse
import re
import uvicorn
from app.src.api_schemas import WeatherInfo

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global scheduler and pipeline instances
scheduler: Optional[BackgroundScheduler] = None
pipeline: Optional[WeatherDataPipeline] = None
database: Optional[WeatherDatabase] = None
agent: Optional[WeatherAgent] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifespan context manager.
    Handles application startup and shutdown events.
    
    On startup:
        - Initialize database
        - Create background scheduler
        - Start automatic weather data fetching
        - Optionally run initial fetch
    
    On shutdown:
        - Stop scheduler gracefully
        - Close database connections
    """
    global scheduler, pipeline, database, agent
    
    # ========== STARTUP ==========
    logger.info("=" * 80)
    logger.info("🚀 WEATHER DATA PIPELINE API - STARTING UP")
    logger.info("=" * 80)
    
    try:
        # Step 1: Initialize database
        logger.info("📊 [1/5] Initializing database...")
        if initialize_database():
            logger.info("✅ Database initialized and tables created")
            database = WeatherDatabase()
        else:
            logger.error("❌ Database initialization failed!")
            raise Exception("Database initialization failed")
        
        # Step 2: Initialize weather data pipeline
        logger.info(f"⚙️  [2/5] Initializing weather data pipeline...")
        pipeline = WeatherDataPipeline(interval_minutes=FETCH_INTERVAL_MINUTES)
        logger.info(f"✅ Pipeline initialized (Interval: {FETCH_INTERVAL_MINUTES} minutes)")
        
        # Step 3: Initialize AI agent
        logger.info("🤖 [3/5] Initializing AI agent...")
        try:
            agent = WeatherAgent()
            logger.info("✅ AI agent initialized successfully")
        except Exception as e:
            logger.warning(f"⚠️  AI agent initialization failed: {str(e)}")
            logger.warning("Agent endpoints will return errors")
        
        # Step 4: Create and start background scheduler
        logger.info("⏰ [4/5] Setting up background scheduler...")
        scheduler = BackgroundScheduler()
        
        scheduler.add_job(
            func=pipeline.run_pipeline,
            trigger=IntervalTrigger(minutes=FETCH_INTERVAL_MINUTES),
            id='weather_fetch_job',
            name='Fetch and process weather data',
            replace_existing=True,
            max_instances=1  # Prevent overlapping executions
        )
        
        scheduler.start()
        logger.info(f"✅ Background scheduler started successfully")
        logger.info(f"📅 Next scheduled run: {scheduler.get_job('weather_fetch_job').next_run_time}")
        
        # Step 5: Optional initial fetch
        if RUN_INITIAL_FETCH:
            logger.info("🔄 [5/5] Running initial weather data fetch...")
            try:
                pipeline.run_pipeline()
                logger.info("✅ Initial fetch completed successfully")
            except Exception as e:
                logger.error(f"❌ Initial fetch failed: {str(e)}")
        else:
            logger.info("⏭️  [5/5] Initial fetch skipped (RUN_INITIAL_FETCH=false)")
        
        logger.info("=" * 80)
        logger.info("✨ API SERVER IS READY!")
        logger.info(f"🌐 Access API at: http://{API_HOST}:{API_PORT}")
        logger.info(f"📖 API docs at: http://localhost:{API_PORT}/docs")
        logger.info(f"🔄 Auto-fetch interval: Every {FETCH_INTERVAL_MINUTES} minutes")
        logger.info("=" * 80)
        
    except Exception as e:
        logger.error(f"❌ STARTUP FAILED: {str(e)}")
        raise
    
    # Application is running...
    yield
    
    # ========== SHUTDOWN ==========
    logger.info("=" * 80)
    logger.info("🛑 WEATHER DATA PIPELINE API - SHUTTING DOWN")
    logger.info("=" * 80)
    
    # Stop scheduler
    if scheduler and scheduler.running:
        logger.info("⏸️  Stopping background scheduler...")
        scheduler.shutdown(wait=True)
        logger.info("✅ Scheduler stopped gracefully")
    
    # Close database connections
    if database and database.connection:
        logger.info("🔌 Closing database connections...")
        database.close()
        logger.info("✅ Database connections closed")
    
    logger.info("=" * 80)
    logger.info("👋 SHUTDOWN COMPLETE")
    logger.info("=" * 80)


# Create FastAPI application with lifespan
app = FastAPI(
    title="Weather AI Agent API",
    description="""
    **AI-Powered Weather Query Agent**
    
    This API provides:
    - 🤖 AI-powered weather query agent using OpenAI
    - 📊 Automatic periodic weather data fetching in background
    - 💾 Database storage of weather data for intelligent responses
    
    **Usage:**
    - Send natural language questions about weather
    - Agent queries the database for fast, accurate responses
    - Falls back to live API when needed
    """,
    version="2.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)


# ==================== API ENDPOINTS ====================

@app.get("/", tags=["Info"])
async def root():
    """
    API information endpoint.
    
    Returns:
        Basic API information and available endpoints
    """
    return {
        "name": "Weather AI Agent API",
        "version": "2.1.0",
        "description": "AI-powered weather query agent with natural language processing",
        "endpoints": {
            "agent_query": "/agent/query",
            "documentation": "/docs"
        },
        "status": "running"
    }


@app.post("/agent/query", response_model=AgentQueryResponse, tags=["AI Agent"])
async def query_agent(request: AgentQueryRequest):
    """
    Query the AI agent with a weather-related question.
    
    The agent can:
    - Answer questions about current weather
    - Provide historical weather data
    - Compare weather between cities
    - Calculate averages and trends
    
    **Example queries:**
    - "What is the current weather in Colombo?"
    - "Compare weather in London and Paris"
    - "Has Mumbai been getting hotter?"
    
    Args:
        request: Query request with user question
    
    Returns:
        - Agent's response
        - Processing time
        - Timestamp
    """
    try:
        if not agent:
            raise HTTPException(
                status_code=503,
                detail="AI agent not initialized. Check OpenAI API key configuration."
            )
        
        logger.info(f"🤖 Agent query received: {request.query}")
        start_time = time.time()
        
        # Check if this is a simple current weather query
        query_lower = request.query.lower()
        weather_data = None
        
        # Extract city name from common query patterns
        
        # Try multiple patterns to extract city name
        patterns = [
            r'weather\s+in\s+([\w\s]+?)(?:[?.!]|$)',  # "weather in Colombo"
            r'weather\s+(?:at|for)\s+([\w\s]+?)(?:[?.!]|$)',  # "weather at/for Colombo"
            r'current\s+weather\s+in\s+([\w\s]+?)(?:[?.!]|$)',  # "current weather in Colombo"
            r'temperature\s+in\s+([\w\s]+?)(?:[?.!]|$)',  # "temperature in Colombo"
            r'conditions?\s+in\s+([\w\s]+?)(?:[?.!]|$)',  # "conditions in Colombo"
        ]
        
        city_name = None
        for pattern in patterns:
            city_match = re.search(pattern, query_lower)
            if city_match:
                city_name = city_match.group(1).strip().title()
                break
        
        if city_name:
            logger.info(f"🔍 Extracting structured data for city: {city_name}")
            
            # Query database for structured data
            try:
                if not database.connection or not database.connection.is_connected():
                    database.connect()
                
                cursor = database.connection.cursor(dictionary=True)
                query = """
                    SELECT city, temperature, feels_like, description as condition, 
                           humidity, wind_speed, pressure
                    FROM weather_data
                    WHERE city = %s
                    ORDER BY timestamp DESC
                    LIMIT 1
                """
                cursor.execute(query, (city_name,))
                result = cursor.fetchone()
                cursor.close()
                
                if result:
                    weather_data = WeatherInfo(
                        temperature=float(result['temperature']) if result['temperature'] else None,
                        condition=result['condition'],
                        humidity=result['humidity'],
                        wind_speed=float(result['wind_speed']) if result['wind_speed'] else None,
                        pressure=result['pressure'],
                        feels_like=float(result['feels_like']) if result['feels_like'] else None,
                        city=result['city']
                    )
                    logger.info(f"✅ Structured data found for {city_name}")
                else:
                    logger.warning(f"⚠️  No data found for city: {city_name}")
            except Exception as e:
                logger.warning(f"Failed to fetch structured data: {str(e)}")
        
        # Process query with agent
        response = agent.chat(request.query)
        
        processing_time = time.time() - start_time
        
        logger.info(f"✅ Agent response generated in {processing_time:.2f} seconds")
        
        return AgentQueryResponse(
            query=request.query,
            response=response,
            weather_data=weather_data,
            timestamp=datetime.now(),
            processing_time_seconds=round(processing_time, 2)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Agent query failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Agent query failed: {str(e)}")


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unhandled errors."""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": str(exc),
            "timestamp": datetime.now().isoformat()
        }
    )


if __name__ == "__main__":
    
    logger.info("Starting Weather Data Pipeline API...")
    uvicorn.run(
        "app.main:app",
        host=API_HOST,
        port=API_PORT,
        reload=True,
        log_level="info"
    )
