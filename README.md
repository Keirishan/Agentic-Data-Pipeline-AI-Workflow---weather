# Weather Data Pipeline REST API

An automated weather data pipeline with REST API endpoints and AI-powered query capabilities. Automatically fetches weather data from OpenWeatherMap API, stores it in MySQL, and provides interactive API endpoints for testing with Postman.

## 🌟 Features

- 🔄 **Automatic Background Fetching** - Scheduler runs automatically on startup
- 🌍 **150+ Cities Worldwide** - Comprehensive global weather coverage
- 🧹 **Data Cleaning & Validation** - Ensures high-quality data
- 💾 **MySQL Database Storage** - Raw and cleaned data tables
- 🚀 **REST API** - FastAPI-based with automatic OpenAPI documentation
- 🤖 **AI Agent** - Natural language weather queries powered by OpenAI
- 📊 **Real-time Monitoring** - Health checks and status endpoints
- 🧪 **Postman Ready** - Easy testing with provided collection

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                 FastAPI Application                     │
├─────────────────────────────────────────────────────────┤
│  ┌──────────────┐              ┌──────────────────┐   │
│  │ REST API     │              │ Background       │   │
│  │ Endpoints    │              │ Scheduler        │   │
│  │              │              │ (APScheduler)    │   │
│  └──────────────┘              └──────────────────┘   │
│         │                              │               │
│         └────────┬─────────────────────┘              │
│                  ▼                                     │
│  ┌─────────────────────────────────────────────────┐  │
│  │     Core Components                              │  │
│  │  • WeatherAPIFetcher                            │  │
│  │  • WeatherDataCleaner                           │  │
│  │  • WeatherDatabase                              │  │
│  │  • WeatherAgent (AI)                            │  │
│  └─────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                        │
                        ▼
                ┌──────────────┐
                │  MySQL DB    │
                └──────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- MySQL Server running locally
- OpenWeatherMap API key ([Get one here](https://openweathermap.org/api))
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Create/edit `.env` file:

```env
# API Keys
OPENAI_API_KEY=your_openai_key_here
OpenWeatherMapAPI=your_weather_api_key_here

# MySQL Database Configuration
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=weather_data

# Scheduler Configuration (in minutes)
FETCH_INTERVAL_MINUTES=10

# API Server Configuration
API_HOST=0.0.0.0
API_PORT=8000
RUN_INITIAL_FETCH=true

WEATHER_API_BASE_URL=https://api.openweathermap.org/data/2.5/weather
```

### 3. Start the Server

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**What happens on startup:**

1. ✅ Database initialized (creates tables if needed)
2. ✅ Background scheduler started automatically
3. ✅ Initial weather data fetch executed
4. ✅ API becomes available at http://localhost:8000
5. ✅ Scheduler continues fetching data every N minutes

### 4. Access API Documentation

Open in your browser:

- **Interactive API Docs (Swagger UI)**: http://localhost:8000/docs
- **Alternative Docs (ReDoc)**: http://localhost:8000/redoc

## 📡 API Endpoints

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/agent/query` | Query AI agent with natural language |

## 🤖 AI Agent

The Weather AI Agent uses OpenAI's GPT-4 to answer weather questions in natural language.

### Example Queries

- "What is the current weather in Colombo?"
- "Compare weather in London and Paris"
- "Which city is the hottest right now?"
- "Has Mumbai been getting hotter over time?"
- "What's the average temperature in Tokyo?"

### Agent Features

✅ Natural language understanding  
✅ Queries stored database for fast responses  
✅ Falls back to live API when needed  
✅ Answers only weather-related questions  
✅ Provides averages, comparisons, and trends  

## ⏰ Background Scheduler

The scheduler runs **automatically** when you start the server:

```
Server Start
    ↓
Automatic Actions:
├─ Database initialized
├─ Scheduler created and started
├─ Initial fetch executed (if RUN_INITIAL_FETCH=true)
└─ Continues fetching every N minutes
    ↓
API Ready for Requests
```

### Configuration

Edit `.env` to customize:

```env
# Fetch every 5 minutes
FETCH_INTERVAL_MINUTES=5

# Skip initial fetch on startup
RUN_INITIAL_FETCH=false
```

## 📊 Database Schema

### weather_data_raw (Raw API responses)
```sql
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
);
```

### weather_data (Cleaned & normalized)
```sql
CREATE TABLE weather_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    city VARCHAR(100) NOT NULL,
    country VARCHAR(10),
    temperature DECIMAL(5, 2) NOT NULL,
    feels_like DECIMAL(5, 2),
    humidity INT,
    pressure INT,
    wind_speed DECIMAL(5, 2),
    description VARCHAR(100),
    timestamp DATETIME NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_city (city),
    INDEX idx_timestamp (timestamp)
);
```

## 🗂️ Project Structure

```
Agentic-Data-Pipeline-AI-Workflow---weather/
├── app/
│   ├── main.py                  # FastAPI application with lifespan events
│   └── src/
│       ├── __init__.py
│       ├── api_models.py        # Pydantic request/response models
│       ├── config.py            # Configuration management
│       ├── cities.py            # List of 150+ cities
│       ├── weather_fetcher.py   # OpenWeatherMap API client
│       ├── data_cleaner.py      # Data validation and normalization
│       ├── database.py          # MySQL database operations
│       ├── scheduler.py         # Pipeline orchestration
│       └── weather_agent.py     # AI Agent with OpenAI integration
├── docs/
│   ├── DATABASE_SCHEMA.md       # Database Schemas details
│   ├── RATIONALE.md
├── sql_script/
│   └── database_setup.sql       # Database initialization scripts
├── .env                         # Environment configuration
├── pyproject.toml               # Project metadata
├── install-and-run.ps1          # Windows installation & startup script
└── README.md                    # This file
```

## 📝 Example Workflow

### 1. Start Server
```bash
uvicorn app.main:app --port 8000 --reload
```

### 2. Monitor Logs
```
🚀 WEATHER DATA PIPELINE API - STARTING UP
📊 [1/5] Initializing database...
✅ Database initialized and tables created
⚙️  [2/5] Initializing weather data pipeline...
✅ Pipeline initialized (Interval: 10 minutes)
🤖 [3/5] Initializing AI agent...
✅ AI agent initialized successfully
⏰ [4/5] Setting up background scheduler...
✅ Background scheduler started successfully
🔄 [5/5] Running initial weather data fetch...
✅ Initial fetch completed successfully
✨ API SERVER IS READY!
🌐 Access API at: http://0.0.0.0:8000
📖 API docs at: http://localhost:8000/docs
```

### 3. Test Endpoints
```bash

# Query agent
curl -X POST http://localhost:8000/agent/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the weather in Paris?"}'
```

## 📚 Documentation

- **[DATABSE_SCHEMA](docs/DATABASE_SCHEMA.md)**
- **[RATIONALE](docs/RATIONALE.md)**

## 📄 License

MIT License

## 🔗 Resources

- **FastAPI Documentation**: https://fastapi.tiangolo.com
- **OpenWeatherMap API**: https://openweathermap.org/api
- **OpenAI API**: https://platform.openai.com/docs
- **APScheduler**: https://apscheduler.readthedocs.io


## 💻 Windows Quick Install

Use the provided PowerShell script to install and start automatically:

```powershell
.\install-and-run.ps1
```

This will:
1. ✅ Check Python and MySQL
2. ✅ Install all dependencies
3. ✅ Verify configuration
4. ✅ Start the server automatically

---

**Built with using FastAPI, APScheduler, and OpenAI**
