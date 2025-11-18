#!/bin/bash
# AI Assistant - Cleanup Script
# Kills all running services and frees up ports

echo "🛑 AI Assistant - Cleanup"
echo "========================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}Stopping all AI Assistant services...${NC}"
echo ""

# Kill Ollama
if pgrep -x "ollama" > /dev/null; then
    echo "  Stopping Ollama..."
    pkill -9 ollama
    sleep 1
    echo -e "  ${GREEN}✓${NC} Ollama stopped"
else
    echo "  ✓ Ollama was not running"
fi

# Kill port 11434 (Ollama)
if lsof -ti:11434 > /dev/null 2>&1; then
    echo "  Freeing port 11434..."
    kill -9 $(lsof -ti:11434) 2>/dev/null || true
    echo -e "  ${GREEN}✓${NC} Port 11434 freed"
else
    echo "  ✓ Port 11434 was free"
fi

# Kill port 8000 (Backend)
if lsof -ti:8000 > /dev/null 2>&1; then
    echo "  Freeing port 8000..."
    kill -9 $(lsof -ti:8000) 2>/dev/null || true
    echo -e "  ${GREEN}✓${NC} Port 8000 freed"
else
    echo "  ✓ Port 8000 was free"
fi

# Kill port 5173 (Frontend)
if lsof -ti:5173 > /dev/null 2>&1; then
    echo "  Freeing port 5173..."
    kill -9 $(lsof -ti:5173) 2>/dev/null || true
    echo -e "  ${GREEN}✓${NC} Port 5173 freed"
else
    echo "  ✓ Port 5173 was free"
fi

# Kill any Python processes in the backend directory
if pgrep -f "python.*main.py" > /dev/null; then
    echo "  Stopping Python backend processes..."
    pkill -9 -f "python.*main.py" || true
    echo -e "  ${GREEN}✓${NC} Backend processes stopped"
fi

# Kill any Python HTTP servers on port 5173
if pgrep -f "python.*http.server.*5173" > /dev/null; then
    echo "  Stopping Python HTTP server..."
    pkill -9 -f "python.*http.server.*5173" || true
    echo -e "  ${GREEN}✓${NC} HTTP server stopped"
fi

echo ""
echo -e "${GREEN}✅ All services stopped successfully!${NC}"
echo ""
echo "You can now run ./setup-and-run.sh to start again"
echo ""
