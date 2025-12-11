@echo off
REM ===================================
REM Quick Start: Populate Database
REM ===================================

echo.
echo ========================================
echo   NEXUS IGNIS - Database Populator
echo ========================================
echo.

REM Check if .env exists
if not exist .env (
    echo [ERROR] File .env tidak ditemukan!
    echo.
    echo Cara membuat .env:
    echo 1. Buka Railway Dashboard
    echo 2. Postgres service -^> Variables -^> Copy DATABASE_URL
    echo 3. Buat file .env dengan isi:
    echo    DATABASE_URL=postgresql://postgres:password@host:port/railway
    echo.
    pause
    exit /b 1
)

echo [OK] File .env found
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python tidak terinstall!
    echo Install Python dari: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo [OK] Python installed
echo.

REM Install dependencies
echo [STEP 1/3] Installing dependencies...
pip install -r requirements.txt -q
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)
echo [OK] Dependencies installed
echo.

REM Run the pipeline
echo [STEP 2/3] Running archive pipeline...
echo This will take 5-10 minutes. Please wait...
echo.
python main.py
if errorlevel 1 (
    echo.
    echo [ERROR] Pipeline failed!
    echo Check error messages above.
    pause
    exit /b 1
)

echo.
echo [STEP 3/3] Verify database...
echo.
echo ========================================
echo   SUCCESS! Database populated!
echo ========================================
echo.
echo Next steps:
echo 1. Open your web app
echo 2. Search for "kaskus"
echo 3. Should see results now!
echo.
echo GitHub Actions will auto-run daily at 2 AM
echo to keep database updated.
echo.
pause
