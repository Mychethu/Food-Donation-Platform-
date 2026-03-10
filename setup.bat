@echo off
REM Food Donation Backend Setup for Windows

echo.
echo 🍲 Food Donation Application Setup
echo ====================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed or not in PATH
    exit /b 1
)

echo ✓ Python found

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

echo.
echo ✓ Setup Complete!
echo.
echo Next steps:
echo 1. Activate the virtual environment: venv\Scripts\activate.bat
echo 2. Run migrations: python manage.py migrate
echo 3. Create superuser: python manage.py createsuperuser
echo 4. Start server: python manage.py runserver
echo.
echo Access the application:
echo - Home: http://localhost:8000/
echo - Admin: http://localhost:8000/admin/
echo.
pause
