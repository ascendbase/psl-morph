@echo off
echo Testing Brevo Email Functionality...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python and try again
    pause
    exit /b 1
)

REM Check if .env file exists
if not exist ".env" (
    echo Error: .env file not found
    echo Please create .env file with your Brevo credentials
    echo See BREVO_EMAIL_SETUP_GUIDE.md for instructions
    pause
    exit /b 1
)

REM Run the test
python test_brevo_email.py

echo.
echo Test completed. Press any key to exit...
pause >nul
