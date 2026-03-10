#!/bin/bash

# Food Donation Backend Setup

echo "🍲 Food Donation Application Setup"
echo "===================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3."
    exit 1
fi

echo "✓ Python 3 found"

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Make manage.py executable
chmod +x manage.py

echo ""
echo "✓ Setup Complete!"
echo ""
echo "Next steps:"
echo "1. Activate the virtual environment: source venv/bin/activate"
echo "2. Run migrations: python manage.py migrate"
echo "3. Create superuser: python manage.py createsuperuser"
echo "4. Start server: python manage.py runserver"
echo ""
echo "Access the application:"
echo "- Home: http://localhost:8000/"
echo "- Admin: http://localhost:8000/admin/"
