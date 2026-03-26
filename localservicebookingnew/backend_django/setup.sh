#!/bin/bash
# Setup script for Local Service Booking Django Backend

echo "🚀 Setting up Local Service Booking Backend..."

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $python_version"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚙️  Creating .env file..."
    cp .env.example .env 2>/dev/null || cat > .env << 'EOF'
DEBUG=True
SECRET_KEY=django-insecure-change-this-in-production
ALLOWED_HOSTS=localhost,127.0.0.1
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=
DB_NAME=service_booking_new
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
DEFAULT_PROVIDER_PHONE=9360522919
EOF
    echo "⚠️  Please edit .env with your MySQL credentials!"
fi

# Run migrations
echo "🗄️  Running database migrations..."
python manage.py makemigrations
python manage.py migrate

# Create superuser prompt
echo ""
read -p "📝 Create admin superuser? (y/n): " create_admin
if [ "$create_admin" = "y" ]; then
    python manage.py createsuperuser
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "To start the server:"
echo "  source venv/bin/activate"
echo "  python manage.py runserver"
echo ""
echo "Server will run at: http://127.0.0.1:8000/"
echo "Admin panel: http://127.0.0.1:8000/admin/"
