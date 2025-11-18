#!/bin/bash
# Quick start script for AI Assistant MVP

set -e

echo "🚀 Starting AI Assistant MVP..."
echo ""

# Check if Ollama is running
echo "1️⃣ Checking Ollama..."
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "❌ Ollama is not running!"
    echo "   Please start Ollama first:"
    echo "   $ ollama serve"
    exit 1
fi
echo "✓ Ollama is running"
echo ""

# Navigate to backend
cd "$(dirname "$0")/backend"

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "2️⃣ Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
    echo ""
fi

# Activate venv
echo "3️⃣ Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"
echo ""

# Install dependencies
echo "4️⃣ Installing dependencies..."
pip install -q -r requirements.txt
echo "✓ Dependencies installed"
echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "5️⃣ Creating .env file..."
    cp .env.example .env
    echo "✓ .env file created (you can customize it later)"
    echo ""
fi

# Initialize database
echo "6️⃣ Initializing database..."
python -c "from database import init_db; init_db()" 2>/dev/null || echo "Database already initialized"
echo "✓ Database ready"
echo ""

# Show hardware info
echo "7️⃣ Detecting hardware..."
python -c "from hardware_detector import get_hardware_detector; print(get_hardware_detector().get_hardware_summary())"
echo ""

# Start backend
echo "8️⃣ Starting backend server..."
echo "   Backend will run on http://localhost:8000"
echo "   Frontend: Open frontend/index.html in your browser"
echo ""
echo "   Press Ctrl+C to stop the server"
echo ""

python main.py
