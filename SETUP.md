# Weather AI Agent - Setup Instructions

Complete setup guide to get the Weather AI Agent running on your machine.

---

## 📋 Prerequisites

Before starting, ensure you have the following installed:

### Required Software
1. **Python**
2. **uv**
3. **MySQL Server**
4. **Git**

### Install uv (Fast Python Package Manager)

```bash
# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

## 🚀 Installation Steps

### Step 1: Clone the Repository

```bash
# Clone the repository
git clone https://github.com/Keirishan/Agentic-Data-Pipeline-AI-Workflow---weather
cd Agentic-Data-Pipeline-AI-Workflow---weather
```
---

### Step 2: Set Up MySQL Database

#### Option A: Using MySQL Workbench (GUI)

1. Open **MySQL Workbench**
2. Connect to your local MySQL server
3. Set root password if not already set
4. Database will be created automatically by the application

#### Option B: Using Command Line

```bash
# Start MySQL service (Windows)
net start MySQL80

# Login to MySQL
mysql -u root -p

# The application will create the database automatically
# But you can create it manually if preferred:
CREATE DATABASE IF NOT EXISTS weather_data;
exit;
```

#### Verify MySQL is Running

```bash
# Windows
mysql --version
mysql -u root -p -e "SELECT 1;"
```

---

### Step 3: Install Python Dependencies

#### Using uv

```bash
# Sync dependencies from pyproject.toml
uv sync

# This will:
# ✅ Create a virtual environment automatically (.venv)
# ✅ Install all dependencies from pyproject.toml
# ✅ Create/update uv.lock file for reproducible builds
```
**Note**: With `uv`, you don't need to manually activate the virtual environment. Use `uv run` to automatically run commands in the environment.

---

### Step 4: Configure Environment Variables

#### Create `.env` File

Create a file named `.env` in the project root directory:

#### Add Configuration

Open `.env` in your text editor and add the following:

```env
# ============================================
# API KEYS (REQUIRED)
# ============================================

# OpenAI API Key - Get from: https://platform.openai.com/api-keys
OPENAI_API_KEY=sk-proj-your-actual-key-here

# OpenWeatherMap API Key - Get from: https://openweathermap.org/api
OpenWeatherMapAPI=your-openweathermap-key-here

# ============================================
# DATABASE CONFIGURATION
# ============================================

DB_HOST=localhost
DB_PORT=3306
DB_USER=your-mysql-username-here
DB_PASSWORD=your-mysql-password-here
DB_NAME=weather_data

# ============================================
# SCHEDULER CONFIGURATION
# ============================================

# How often to fetch weather data (in minutes)
FETCH_INTERVAL_MINUTES=10

# Run initial fetch on startup (true/false)
RUN_INITIAL_FETCH=true

# ============================================
# API SERVER CONFIGURATION
# ============================================

API_HOST=0.0.0.0
API_PORT=8000

# ============================================
# EXTERNAL API CONFIGURATION
# ============================================

WEATHER_API_BASE_URL=https://api.openweathermap.org/data/2.5/weather
```
---
### Step 5: Initialize Database (Automatic)

The database will be initialized automatically when you first run the application. Tables will be created automatically.

If you prefer manual setup:

```bash
# Run the SQL script manually
mysql -u root -p weather_data < sql_script/database_setup.sql
```
---

## ▶️ Running the Application

### Method 1: Using uv

```bash
# Run with uv (automatically uses virtual environment)
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Method 2: Using the PowerShell Script (Windows Only)

```powershell
# Automated installation and startup
.\install-and-run.ps1
```
---

## ✅ Verify Installation

### Check 1: Server is Running

You should see output like this:

```
================================================================================
🚀 WEATHER DATA PIPELINE API - STARTING UP
================================================================================
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
================================================================================
✨ API SERVER IS READY!
🌐 Access API at: http://0.0.0.0:8000
📖 API docs at: http://localhost:8000/docs
🔄 Auto-fetch interval: Every 10 minutes
================================================================================
```

### Check 2: Access API Documentation

Open in your browser:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Check 3: Test AI Agent

```bash
# PowerShell
$body = @{
    query = "What is the weather in London?"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/agent/query" -Method POST -Body $body -ContentType "application/json"

# curl
curl -X POST "http://localhost:8000/agent/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the weather in London?"}'
```

Expected response:
```json
{
  "query": "What is the weather in London?",
  "response": "The current weather in London is...",
  "weather_data": {
    "temperature": 15.5,
    "condition": "partly cloudy",
    "humidity": 70,
    "wind_speed": 3.5,
    "city": "London"
  },
  "timestamp": "2025-12-23T10:30:00",
  "processing_time_seconds": 1.23
}
```
---

## 📚 Next Steps

Once setup is complete:

1. **Read Documentation**:
   - [README.md](README.md) - Project overview
   - [DATABASE_SCHEMA.md](docs/DATABASE_SCHEMA.md) - Database schemas

2. **Explore API**:
   - Open http://localhost:8000/docs
   - Try different queries
   - Check response formats

3. **Monitor System**:
   - Watch server logs
   - Query database for records
   - Check scheduler is running

4. **Customize**:
   - Add more cities in `cities.py`
   - Adjust fetch interval
   - Modify agent prompts

---

## 🛑 Stopping the Application

### Stop the Server

- **In terminal**: Press `Ctrl+C`
- **Graceful shutdown**: The application will:
  - Stop the scheduler
  - Close database connections
  - Log shutdown completion

### Stop MySQL

```bash
# Windows
net stop MySQL80

# Linux
sudo systemctl stop mysql

# Mac
brew services stop mysql
```
---

## 💡 Tips for Success

1. ✅ **Use `uv run` to avoid manual environment activation**
2. ✅ **Check server logs** if something doesn't work
3. ✅ **Keep API keys secure** - never commit `.env` to Git
4. ✅ **Monitor database size** - clean old data periodically
5. ✅ **Test with simple queries first** before complex ones
6. ✅ **Read error messages carefully** - they usually tell you what's wrong
7. ✅ **Use `uv sync` to keep dependencies updated**

---

**Setup Complete!** 🎊

Your Weather AI Agent is now ready to answer weather queries!

---