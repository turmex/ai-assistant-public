#!/bin/bash
# Verification script for AI Assistant MVP
# Run this to check if everything is set up correctly

echo "🔍 AI Assistant MVP - System Verification"
echo "=========================================="
echo ""

FAILED=0

# 1. Check Python
echo "1. Checking Python..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "   ✓ Python found: $PYTHON_VERSION"
else
    echo "   ❌ Python 3 not found!"
    FAILED=1
fi
echo ""

# 2. Check Ollama
echo "2. Checking Ollama..."
if command -v ollama &> /dev/null; then
    echo "   ✓ Ollama installed"

    # Check if running
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        MODEL_COUNT=$(curl -s http://localhost:11434/api/tags | python3 -c "import sys, json; print(len(json.load(sys.stdin).get('models', [])))" 2>/dev/null || echo "0")
        echo "   ✓ Ollama is running ($MODEL_COUNT models downloaded)"
    else
        echo "   ⚠️  Ollama not running (run 'ollama serve')"
    fi
else
    echo "   ❌ Ollama not installed (run 'brew install ollama')"
    FAILED=1
fi
echo ""

# 3. Check backend files
echo "3. Checking backend files..."
cd "$(dirname "$0")/backend"

FILES=(
    "main.py"
    "hardware_detector.py"
    "conversation_manager.py"
    "database.py"
    "requirements.txt"
    ".env.example"
)

for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "   ✓ $file"
    else
        echo "   ❌ $file missing!"
        FAILED=1
    fi
done
echo ""

# 4. Check virtual environment
echo "4. Checking virtual environment..."
if [ -d "venv" ]; then
    echo "   ✓ Virtual environment exists"

    # Check if dependencies are installed
    if [ -f "venv/bin/python" ]; then
        if venv/bin/python -c "import fastapi, sqlalchemy, httpx, pydantic" 2>/dev/null; then
            echo "   ✓ Dependencies installed"
        else
            echo "   ⚠️  Dependencies missing (run 'pip install -r requirements.txt')"
        fi
    fi
else
    echo "   ⚠️  Virtual environment not found (run './start.sh' to create)"
fi
echo ""

# 5. Check .env file
echo "5. Checking configuration..."
if [ -f ".env" ]; then
    echo "   ✓ .env file exists"
else
    echo "   ⚠️  .env file missing (copy from .env.example)"
fi
echo ""

# 6. Test hardware detection
echo "6. Testing hardware detection..."
if [ -d "venv" ] && [ -f "venv/bin/python" ]; then
    if venv/bin/python -c "from hardware_detector import get_hardware_detector; d = get_hardware_detector(); print(f'   ✓ Detected: {d.hardware_info.chip_model or d.hardware_info.chip_type}, {d.hardware_info.ram_gb}GB RAM'); print(f'   ✓ Compatible models: {len(d.hardware_info.compatible_models)}'); print(f'   ✓ Recommended: {d.hardware_info.recommended_model.name}')" 2>/dev/null; then
        :
    else
        echo "   ❌ Hardware detection failed"
        FAILED=1
    fi
else
    echo "   ⚠️  Skipped (venv not ready)"
fi
echo ""

# 7. Check frontend
echo "7. Checking frontend..."
cd ..
if [ -f "frontend/index.html" ]; then
    SIZE=$(wc -c < "frontend/index.html")
    echo "   ✓ frontend/index.html exists (${SIZE} bytes)"
else
    echo "   ❌ frontend/index.html missing!"
    FAILED=1
fi
echo ""

# 8. Check documentation
echo "8. Checking documentation..."
if [ -f "README.md" ]; then
    echo "   ✓ README.md"
else
    echo "   ⚠️  README.md missing"
fi

if [ -f "TESTING_GUIDE.md" ]; then
    echo "   ✓ TESTING_GUIDE.md"
else
    echo "   ⚠️  TESTING_GUIDE.md missing"
fi
echo ""

# Summary
echo "=========================================="
if [ $FAILED -eq 0 ]; then
    echo "✅ Verification complete! System is ready."
    echo ""
    echo "Next steps:"
    echo "  1. If Ollama not running: ollama serve"
    echo "  2. Start backend: ./start.sh"
    echo "  3. Open frontend: open frontend/index.html"
else
    echo "❌ Verification failed! Please fix the issues above."
fi
echo ""
