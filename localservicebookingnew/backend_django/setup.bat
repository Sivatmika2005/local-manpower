@echo off
REM Setup script for Local Service Booking Django Backend (Windows)

echo Setting up Local Service Booking Backend...

REM Check Python
python --version
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.10+
    pause
    exit /b 1
)

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

REM Check if .env exists
if not exist .env (
    echo Creating .env file...
    (
        echo DEBUG=True
        echo SECRET_KEY=django-insecure-change-this-in-production
        echo ALLOWED_HOSTS=localhost,127.0.0.1
        echo DB_HOST=localhost
        echo DB_PORT=3306
        echo DB_USER=root
        echo DB_PASSWORD=
        echo DB_NAME=service_booking_new
        echo EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
        echo DEFAULT_PROVIDER_PHONE=9360522919
    ) > .env
    echo Please edit .env with your MySQL credentials!
)

REM Run migrations
echo Running database migrations...
python manage.py makemigrations
python manage.py migrate

REM Create superuser prompt
echo.
set /p create_admin="Create admin superuser? (y/n): "
if /i "%create_admin%"=="y" (
    python manage.py createsuperuser
)

echo.
echo Setup complete!
echo.
echo To start the server:
echo   venv\Scripts\activate
echo   python manage.py runserver
echo.
echo Server will run at: http://127.0.0.1:8000/
echo Admin panel: http://127.0.0.1:8000/admin/
pause
