# Weather Data Pipeline API - Installation & Startup Script

Write-Host "=" -ForegroundColor Cyan -NoNewline; Write-Host ("=" * 78) -ForegroundColor Cyan
Write-Host "  WEATHER DATA PIPELINE REST API - INSTALLATION & STARTUP" -ForegroundColor Yellow
Write-Host "=" -ForegroundColor Cyan -NoNewline; Write-Host ("=" * 78) -ForegroundColor Cyan
Write-Host ""

# Step 1: Check Python
Write-Host "[1/4] Checking Python installation..." -ForegroundColor Cyan
try {
    $pythonVersion = python --version 2>&1
    Write-Host "  $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "  ERROR: Python not found. Please install Python 3.8+ first." -ForegroundColor Red
    exit 1
}

# Step 2: Check MySQL
Write-Host "`n[2/4] Checking MySQL connection..." -ForegroundColor Cyan
try {
    $mysqlTest = mysql -u root -pKeiri@1511 -e "SELECT 1;" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  MySQL connection successful" -ForegroundColor Green
    } else {
        Write-Host "  WARNING: MySQL connection failed. Check your credentials in .env" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  WARNING: MySQL not found or not running" -ForegroundColor Yellow
}

# Step 3: Install dependencies
Write-Host "`n[3/4] Installing Python dependencies..." -ForegroundColor Cyan
Write-Host "  This may take a few minutes..." -ForegroundColor Gray

pip install -r requirements.txt

if ($LASTEXITCODE -eq 0) {
    Write-Host "  Dependencies installed successfully" -ForegroundColor Green
} else {
    Write-Host "  ERROR: Failed to install dependencies" -ForegroundColor Red
    exit 1
}

# Step 4: Check .env file
Write-Host "`n[4/4] Checking configuration..." -ForegroundColor Cyan
if (Test-Path ".env") {
    Write-Host "  .env file found" -ForegroundColor Green
    
    # Check for required keys
    $envContent = Get-Content ".env" -Raw
    
    $hasOpenAI = $envContent -match "OPENAI_API_KEY\s*=\s*.+"
    $hasWeather = $envContent -match "OpenWeatherMapAPI\s*=\s*.+"
    
    if ($hasOpenAI) {
        Write-Host "  OpenAI API key configured" -ForegroundColor Green
    } else {
        Write-Host "  WARNING: OpenAI API key not found in .env" -ForegroundColor Yellow
    }
    
    if ($hasWeather) {
        Write-Host "  OpenWeatherMap API key configured" -ForegroundColor Green
    } else {
        Write-Host "  WARNING: OpenWeatherMap API key not found in .env" -ForegroundColor Yellow
    }
} else {
    Write-Host "  ERROR: .env file not found" -ForegroundColor Red
    exit 1
}

# Ready to start
Write-Host "`n" -NoNewline
Write-Host "=" -ForegroundColor Cyan -NoNewline; Write-Host ("=" * 78) -ForegroundColor Cyan
Write-Host "  INSTALLATION COMPLETE - READY TO START!" -ForegroundColor Green
Write-Host "=" -ForegroundColor Cyan -NoNewline; Write-Host ("=" * 78) -ForegroundColor Cyan
Write-Host ""

Write-Host "To start the server, run:" -ForegroundColor Yellow
Write-Host "  uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload`n" -ForegroundColor White

Write-Host "Once started, access:" -ForegroundColor Yellow
Write-Host "  API Docs:     " -NoNewline -ForegroundColor Gray
Write-Host "http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "  Health Check: " -NoNewline -ForegroundColor Gray
Write-Host "http://localhost:8000/health" -ForegroundColor Cyan
Write-Host "  Status:       " -NoNewline -ForegroundColor Gray
Write-Host "http://localhost:8000/status`n" -ForegroundColor Cyan

# Ask if user wants to start now
Write-Host "Would you like to start the server now? (Y/N): " -NoNewline -ForegroundColor Yellow
$response = Read-Host

if ($response -eq "Y" -or $response -eq "y") {
    Write-Host "`nStarting server..." -ForegroundColor Green
    Write-Host "Press Ctrl+C to stop the server`n" -ForegroundColor Gray
    
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
} else {
    Write-Host "`nServer not started. Run manually when ready:" -ForegroundColor Gray
    Write-Host "  uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload`n" -ForegroundColor White
}
