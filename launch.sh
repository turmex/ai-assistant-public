#!/bin/bash

# AI Assistant - Single Command Launcher
# Terminates existing instances, launches backend/frontend, opens browser

echo "🚀 AI Assistant - One-Command Launcher"
echo "========================================"
echo ""

# Step 1: Terminate existing processes
echo "🧹 Step 1: Terminating existing processes..."
lsof -ti:8000,11434,5173 | xargs kill -9 2>/dev/null
pkill -f "uvicorn main:app" 2>/dev/null
pkill -f "ollama serve" 2>/dev/null
pkill -f "npx http-server" 2>/dev/null
echo "  ✓ All AI Assistant processes terminated"
echo ""

# Step 2: Start Ollama in background
echo "🔧 Step 2: Starting Ollama..."
ollama serve > /dev/null 2>&1 &
sleep 2
echo "  ✓ Ollama started on port 11434"
echo ""

# Step 3: Start Backend in new Terminal tab
echo "🐍 Step 3: Launching Backend..."
osascript -e 'tell application "Terminal"
    do script "cd ~/Desktop/ai-assistant/backend && source .venv/bin/activate && echo \"🚀 Backend Server Starting...\" && python main.py"
    activate
end tell' > /dev/null 2>&1
sleep 3
echo "  ✓ Backend launched in new Terminal tab (port 8000)"
echo ""

# Step 4: Start Frontend in new Terminal tab
echo "🌐 Step 4: Launching Frontend..."
osascript -e 'tell application "Terminal"
    do script "cd ~/Desktop/ai-assistant/frontend-v2 && echo \"🌐 Frontend Server Starting...\" && npx http-server -p 5173 -c-1"
end tell' > /dev/null 2>&1
sleep 2
echo "  ✓ Frontend launched in new Terminal tab (port 5173)"
echo ""

# Step 5: Open browser
echo "🌍 Step 5: Opening browser..."
sleep 3
open "http://localhost:8000"
echo "  ✓ Browser opened to http://localhost:8000"
echo ""

echo "══════════════════════════════════════════════════════"
echo "  ✅ AI Assistant is now running!"
echo "══════════════════════════════════════════════════════"
echo ""
echo "📋 Services:"
echo "  • Ollama:   http://localhost:11434"
echo "  • Backend:  http://localhost:8000"
echo "  • Frontend: http://localhost:8000 (served by backend)"
echo ""
echo "🛑 To stop: Close the Terminal tabs or run:"
echo "   lsof -ti:8000,11434,5173 | xargs kill -9"
echo ""
