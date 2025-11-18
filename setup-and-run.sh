#!/bin/bash
# AI Assistant - Complete Setup and Run Script
# This script handles everything: cleanup, setup, and launch

set -e  # Exit on error

echo "🚀 AI Assistant - Setup and Run"
echo "================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/backend"
FRONTEND_DIR="$SCRIPT_DIR/frontend-v2"

echo -e "${BLUE}📍 Project Directory: $SCRIPT_DIR${NC}"
echo ""

# ============================================================================
# STEP 1: Cleanup - Kill any existing processes
# ============================================================================
echo -e "${YELLOW}🧹 Step 1: Cleaning up existing processes...${NC}"

# Kill Ollama if running
if pgrep -x "ollama" > /dev/null; then
    echo "  ⚠️  Ollama is running. Stopping it..."
    pkill -9 ollama || true
    sleep 2
    echo -e "  ${GREEN}✓${NC} Ollama stopped"
else
    echo "  ✓ Ollama not running"
fi

# Kill any process on port 11434 (Ollama)
if lsof -ti:11434 > /dev/null 2>&1; then
    echo "  ⚠️  Port 11434 is in use. Killing process..."
    kill -9 $(lsof -ti:11434) 2>/dev/null || true
    sleep 1
    echo -e "  ${GREEN}✓${NC} Port 11434 freed"
else
    echo "  ✓ Port 11434 is free"
fi

# Kill any process on port 8000 (Backend)
if lsof -ti:8000 > /dev/null 2>&1; then
    echo "  ⚠️  Port 8000 is in use. Killing process..."
    kill -9 $(lsof -ti:8000) 2>/dev/null || true
    sleep 1
    echo -e "  ${GREEN}✓${NC} Port 8000 freed"
else
    echo "  ✓ Port 8000 is free"
fi

# Kill any process on port 5173 (Frontend)
if lsof -ti:5173 > /dev/null 2>&1; then
    echo "  ⚠️  Port 5173 is in use. Killing process..."
    kill -9 $(lsof -ti:5173) 2>/dev/null || true
    sleep 1
    echo -e "  ${GREEN}✓${NC} Port 5173 freed"
else
    echo "  ✓ Port 5173 is free"
fi

echo ""

# ============================================================================
# STEP 2: Check if Ollama is installed
# ============================================================================
echo -e "${YELLOW}🔍 Step 2: Checking Ollama installation...${NC}"

if ! command -v ollama &> /dev/null; then
    echo -e "  ${RED}✗ Ollama is not installed${NC}"
    echo ""
    echo "  Please install Ollama first:"
    echo "    brew install ollama"
    echo ""
    exit 1
else
    echo -e "  ${GREEN}✓${NC} Ollama is installed"
    ollama --version
fi

echo ""

# ============================================================================
# STEP 3: Setup Python virtual environment
# ============================================================================
echo -e "${YELLOW}🐍 Step 3: Setting up Python environment...${NC}"

cd "$BACKEND_DIR"

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "  Creating virtual environment..."
    python3 -m venv venv
    echo -e "  ${GREEN}✓${NC} Virtual environment created"
else
    echo "  ✓ Virtual environment already exists"
fi

# Activate and install dependencies
echo "  Installing dependencies..."
source venv/bin/activate

# Upgrade pip
pip install --quiet --upgrade pip

# Install requirements
if pip install --quiet -r requirements.txt; then
    echo -e "  ${GREEN}✓${NC} Dependencies installed"
else
    echo -e "  ${RED}✗ Failed to install dependencies${NC}"
    exit 1
fi

# Initialize database
echo "  Initializing database..."
if python -c "from database import init_db; init_db()" 2>/dev/null; then
    echo -e "  ${GREEN}✓${NC} Database initialized"
else
    echo "  ⚠️  Database might already be initialized (this is OK)"
fi

# Test hardware detection
echo "  Testing hardware detection..."
python -c "from hardware_detector import get_hardware_detector; print('  ' + get_hardware_detector().get_hardware_summary().replace('\n', '\n  '))"

deactivate

echo ""

# ============================================================================
# STEP 4: Create tab launch script
# ============================================================================
echo -e "${YELLOW}📝 Step 4: Creating launch script...${NC}"

# Create the AppleScript to open tabs
LAUNCH_SCRIPT="$SCRIPT_DIR/launch-tabs.scpt"

cat > "$LAUNCH_SCRIPT" << 'APPLESCRIPT_EOF'
tell application "Terminal"
    -- Activate Terminal
    activate

    -- Get the script directory (passed as argument)
    set scriptDir to system attribute "SCRIPT_DIR"

    -- Create new window for Ollama
    do script "cd " & quoted form of scriptDir & " && echo '🚀 Starting Ollama...' && ollama serve"
    set ollamaWindow to front window

    -- Wait a moment for Ollama to start
    delay 2

    -- Create new tab for Backend
    tell ollamaWindow
        set currentTab to do script "cd " & quoted form of (scriptDir & "/backend") & " && echo '🐍 Starting Backend...' && source venv/bin/activate && python main.py" in ollamaWindow
    end tell

    -- Wait a moment for backend to initialize
    delay 3

    -- Create new tab for Frontend
    tell ollamaWindow
        set frontendTab to do script "cd " & quoted form of (scriptDir & "/frontend-v2") & " && echo '🌐 Starting Frontend...' && echo '' && echo 'Open your browser to:' && echo 'http://127.0.0.1:5173/index.html' && echo 'or http://localhost:5173/index.html' && echo '' && python3 -m http.server 5173 --bind 127.0.0.1" in ollamaWindow
    end tell

    -- Focus on the frontend tab
    set selected tab of ollamaWindow to frontendTab

end tell
APPLESCRIPT_EOF

echo -e "  ${GREEN}✓${NC} Launch script created"
echo ""

# ============================================================================
# STEP 5: Launch in separate tabs
# ============================================================================
echo -e "${YELLOW}🚀 Step 5: Launching AI Assistant...${NC}"
echo ""
echo "  Opening 3 tabs in Terminal:"
echo "    Tab 1: Ollama server (port 11434)"
echo "    Tab 2: Backend server (port 8000)"
echo "    Tab 3: Frontend server (port 5173)"
echo ""
echo -e "${BLUE}  ⏳ Please wait 5-10 seconds for all services to start...${NC}"
echo ""

# Export script directory as environment variable for AppleScript
export SCRIPT_DIR

# Run the AppleScript
osascript "$LAUNCH_SCRIPT"

# Wait for services to be ready
echo "  Waiting for services to start..."
sleep 5

# Check if services are running
echo ""
echo -e "${YELLOW}🔍 Checking services...${NC}"

# Check Ollama
if lsof -ti:11434 > /dev/null 2>&1; then
    echo -e "  ${GREEN}✓${NC} Ollama is running on port 11434"
else
    echo -e "  ${YELLOW}⚠${NC}  Ollama might still be starting..."
fi

# Check Backend
if lsof -ti:8000 > /dev/null 2>&1; then
    echo -e "  ${GREEN}✓${NC} Backend is running on port 8000"
else
    echo -e "  ${YELLOW}⚠${NC}  Backend might still be starting..."
fi

# Check Frontend
if lsof -ti:5173 > /dev/null 2>&1; then
    echo -e "  ${GREEN}✓${NC} Frontend is running on port 5173"
else
    echo -e "  ${YELLOW}⚠${NC}  Frontend might still be starting..."
fi

echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  ✅ AI Assistant is launching!${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${BLUE}📱 Next Steps:${NC}"
echo ""
echo "  1. Check the 3 Terminal tabs that just opened"
echo "  2. Wait for all services to finish starting (~10 seconds)"
echo "  3. Open your browser to:"
echo ""
echo -e "     ${GREEN}http://127.0.0.1:5173/index.html${NC}"
echo -e "     or ${GREEN}http://localhost:5173/index.html${NC}"
echo ""
echo -e "${YELLOW}💡 Tips:${NC}"
echo "  - Keep all 3 tabs running"
echo "  - Check each tab for errors"
echo "  - Backend should show: ✓ AI Assistant Backend is ready!"
echo "  - If no models, it will auto-download llama3.2:1b"
echo ""
echo -e "${BLUE}🛑 To Stop:${NC}"
echo "  - Press Ctrl+C in each tab"
echo "  - Or run: ./cleanup.sh"
echo ""
echo "Enjoy your AI Assistant! 🎉"
echo ""
