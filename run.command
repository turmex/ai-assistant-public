#!/bin/bash
# ============================================================================
# AI Assistant - One-Click Launcher
# ============================================================================
# This script will:
# 1. Install all dependencies
# 2. Kill any previous server instances
# 3. Start Ollama (if not running)
# 4. Start the backend server
# 5. Open the browser interface
# ============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BACKEND_DIR="$SCRIPT_DIR/backend"
FRONTEND_DIR="$SCRIPT_DIR/frontend-v2"

echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}   AI Assistant - One-Click Launcher${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""

# Function to print status
print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[i]${NC} $1"
}

# ============================================================================
# Step 1: Kill Previous Instances
# ============================================================================
echo -e "${YELLOW}Step 1: Cleaning up previous instances...${NC}"

# Kill any existing uvicorn/python servers on port 8000
if lsof -ti:8000 > /dev/null 2>&1; then
    print_info "Killing processes on port 8000..."
    lsof -ti:8000 | xargs kill -9 2>/dev/null || true
    sleep 1
fi

# Kill any Python processes running main.py
pkill -f "uvicorn main:app" 2>/dev/null || true
pkill -f "python.*main.py" 2>/dev/null || true

print_status "Previous server instances cleaned up"

# ============================================================================
# Step 2: Check and Start Ollama
# ============================================================================
echo ""
echo -e "${YELLOW}Step 2: Checking Ollama...${NC}"

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    print_error "Ollama is not installed!"
    echo ""
    echo "Please install Ollama first:"
    echo "  brew install ollama"
    echo "  OR"
    echo "  Visit: https://ollama.ai/download"
    echo ""
    exit 1
fi

# Check if Ollama is running
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    print_info "Starting Ollama service..."

    # Start Ollama in background
    ollama serve > /dev/null 2>&1 &

    # Wait for Ollama to be ready
    for i in {1..30}; do
        if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
            break
        fi
        sleep 1
    done

    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        print_status "Ollama service started"
    else
        print_error "Failed to start Ollama service"
        exit 1
    fi
else
    print_status "Ollama is already running"
fi

# Check for models
MODELS=$(curl -s http://localhost:11434/api/tags | python3 -c "import sys, json; models = json.load(sys.stdin).get('models', []); print(len(models))" 2>/dev/null || echo "0")

if [ "$MODELS" = "0" ]; then
    print_warning "No models downloaded yet"
    print_info "Downloading default model (llama3.2:1b)..."
    ollama pull llama3.2:1b &
    print_info "Model download started in background"
else
    print_status "Found $MODELS model(s) available"
fi

# ============================================================================
# Step 3: Install Dependencies
# ============================================================================
echo ""
echo -e "${YELLOW}Step 3: Installing dependencies...${NC}"

cd "$BACKEND_DIR"

# Check if virtual environment exists
if [ ! -d ".venv" ] && [ ! -d "venv" ]; then
    print_info "Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
if [ -d ".venv" ]; then
    source .venv/bin/activate
elif [ -d "venv" ]; then
    source venv/bin/activate
fi

# Install/upgrade pip
pip install --upgrade pip -q

# Install requirements
if [ -f "requirements.txt" ]; then
    print_info "Installing Python dependencies..."
    pip install -r requirements.txt -q
    print_status "Dependencies installed"
else
    print_warning "requirements.txt not found, skipping dependency installation"
fi

# ============================================================================
# Step 4: Start Backend Server
# ============================================================================
echo ""
echo -e "${YELLOW}Step 4: Starting backend server...${NC}"

cd "$BACKEND_DIR"

# Start uvicorn in background
print_info "Starting FastAPI server on http://localhost:8000..."
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload > /tmp/ai-assistant-backend.log 2>&1 &
BACKEND_PID=$!

# Wait for server to be ready
for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        break
    fi
    sleep 1
done

if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    print_status "Backend server started (PID: $BACKEND_PID)"
else
    print_error "Backend server failed to start"
    echo "Check logs at: /tmp/ai-assistant-backend.log"
    cat /tmp/ai-assistant-backend.log
    exit 1
fi

# ============================================================================
# Step 5: Open Browser with WebGPU Support
# ============================================================================
echo ""
echo -e "${YELLOW}Step 5: Opening browser with WebGPU enabled...${NC}"

sleep 2

# Open Chrome with WebGPU flags enabled
if [[ "$OSTYPE" == "darwin"* ]]; then
    # Check if Chrome is installed
    if [ -d "/Applications/Google Chrome.app" ]; then
        print_info "Launching Chrome with WebGPU flags..."

        # Launch Chrome with WebGPU-enabling flags
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
            --enable-unsafe-webgpu \
            --enable-features=Vulkan,UseSkiaRenderer \
            --disable-dawn-features=disallow_unsafe_apis \
            --ignore-gpu-blocklist \
            "http://localhost:8000" &

        print_status "Chrome launched with WebGPU support"
    else
        # Fallback to default browser
        print_warning "Chrome not found, using default browser"
        print_info "For WebGPU support, install Chrome and re-run this script"
        open "http://localhost:8000"
    fi
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Try Chrome first with flags
    if command -v google-chrome &> /dev/null; then
        google-chrome \
            --enable-unsafe-webgpu \
            --enable-features=Vulkan \
            --ignore-gpu-blocklist \
            "http://localhost:8000" &
    else
        xdg-open "http://localhost:8000" 2>/dev/null || sensible-browser "http://localhost:8000"
    fi
else
    print_info "Please open http://localhost:8000 in Chrome with WebGPU enabled"
fi

print_status "Browser opened"

echo ""
echo -e "${BLUE}WebGPU Troubleshooting:${NC}"
echo "  If WebLLM fails, ensure Hardware Acceleration is enabled:"
echo "  Chrome → Settings → search 'hardware' → 'Use graphics acceleration' ON"
echo "  Then restart Chrome completely (quit and reopen)"

# ============================================================================
# Complete
# ============================================================================
echo ""
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}   AI Assistant is now running!${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""
echo -e "  ${BLUE}Interface:${NC} http://localhost:8000"
echo -e "  ${BLUE}API Docs:${NC}  http://localhost:8000/docs"
echo -e "  ${BLUE}Health:${NC}    http://localhost:8000/health"
echo ""
echo -e "  ${YELLOW}To stop:${NC} Press Ctrl+C or close this terminal"
echo ""

# Keep script running to show logs
print_info "Server logs (press Ctrl+C to stop):"
echo ""
tail -f /tmp/ai-assistant-backend.log
