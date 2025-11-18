#!/bin/bash
# AI Assistant - Diagnostic Script
# Checks if all services are running correctly

echo "🔍 AI Assistant - Diagnostics"
echo "=============================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Check Ollama
echo -e "${YELLOW}1. Checking Ollama (port 11434)...${NC}"
if lsof -ti:11434 > /dev/null 2>&1; then
    echo -e "  ${GREEN}✓${NC} Ollama is running on port 11434"
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo -e "  ${GREEN}✓${NC} Ollama API is responding"
    else
        echo -e "  ${RED}✗${NC} Ollama port is open but API not responding"
    fi
else
    echo -e "  ${RED}✗${NC} Ollama is NOT running"
    echo "    Run: ollama serve"
fi
echo ""

# Check Backend
echo -e "${YELLOW}2. Checking Backend (port 8000)...${NC}"
if lsof -ti:8000 > /dev/null 2>&1; then
    echo -e "  ${GREEN}✓${NC} Backend is running on port 8000"

    # Test health endpoint
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "  ${GREEN}✓${NC} Backend API is responding"

        # Show health status
        HEALTH=$(curl -s http://localhost:8000/health | python3 -m json.tool 2>/dev/null || echo "{}")
        echo "  Health check response:"
        echo "$HEALTH" | sed 's/^/    /'
    else
        echo -e "  ${RED}✗${NC} Backend port is open but API not responding"
    fi
else
    echo -e "  ${RED}✗${NC} Backend is NOT running"
    echo "    Run: cd backend && source venv/bin/activate && python main.py"
fi
echo ""

# Check Frontend
echo -e "${YELLOW}3. Checking Frontend (port 5173)...${NC}"
if lsof -ti:5173 > /dev/null 2>&1; then
    echo -e "  ${GREEN}✓${NC} Frontend is running on port 5173"

    # Get the actual listening address
    LISTEN_ADDR=$(lsof -ti:5173 | xargs lsof -Pan -p | grep LISTEN | grep 5173 | awk '{print $9}' | head -1)
    echo "  Listening on: $LISTEN_ADDR"

    # Test if we can reach it
    if curl -s http://localhost:5173 > /dev/null 2>&1; then
        echo -e "  ${GREEN}✓${NC} Frontend is accessible via http://localhost:5173"
    elif curl -s http://127.0.0.1:5173 > /dev/null 2>&1; then
        echo -e "  ${GREEN}✓${NC} Frontend is accessible via http://127.0.0.1:5173"
    else
        echo -e "  ${RED}✗${NC} Frontend port is open but HTTP not responding"
        echo "    This might be an IPv6 issue"
    fi
else
    echo -e "  ${RED}✗${NC} Frontend is NOT running"
    echo "    Run: cd frontend-v2 && python3 -m http.server 5173"
fi
echo ""

# Show all processes using our ports
echo -e "${YELLOW}4. Processes on our ports:${NC}"
for PORT in 11434 8000 5173; do
    if lsof -ti:$PORT > /dev/null 2>&1; then
        echo -e "  Port $PORT:"
        lsof -Pan -i:$PORT | grep LISTEN | sed 's/^/    /'
    fi
done
echo ""

# Test URLs
echo -e "${YELLOW}5. Testing URLs:${NC}"

# Test Ollama
echo -n "  http://localhost:11434/api/tags ... "
if curl -s -o /dev/null -w "%{http_code}" http://localhost:11434/api/tags | grep -q 200; then
    echo -e "${GREEN}OK${NC}"
else
    echo -e "${RED}FAILED${NC}"
fi

# Test Backend Health
echo -n "  http://localhost:8000/health ... "
if curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health | grep -q 200; then
    echo -e "${GREEN}OK${NC}"
else
    echo -e "${RED}FAILED${NC}"
fi

# Test Backend Hardware
echo -n "  http://localhost:8000/hardware ... "
if curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/hardware | grep -q 200; then
    echo -e "${GREEN}OK${NC}"
else
    echo -e "${RED}FAILED${NC}"
fi

# Test Frontend (both localhost and 127.0.0.1)
echo -n "  http://localhost:5173/index.html ... "
if curl -s -o /dev/null -w "%{http_code}" http://localhost:5173/index.html | grep -q 200; then
    echo -e "${GREEN}OK${NC}"
elif curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:5173/index.html | grep -q 200; then
    echo -e "${GREEN}OK (via 127.0.0.1)${NC}"
else
    echo -e "${RED}FAILED${NC}"
fi

echo ""

# Network configuration check
echo -e "${YELLOW}6. Network Configuration:${NC}"
echo "  Hostname: $(hostname)"
echo "  Localhost resolves to:"
if command -v dscacheutil &> /dev/null; then
    dscacheutil -q host -a name localhost | grep "ip_address:" | sed 's/^/    /'
else
    getent hosts localhost | sed 's/^/    /'
fi
echo ""

# Recommendations
echo -e "${BLUE}📋 Recommendations:${NC}"
echo ""

if ! lsof -ti:11434 > /dev/null 2>&1; then
    echo -e "  ${RED}⚠${NC}  Start Ollama: ollama serve"
fi

if ! lsof -ti:8000 > /dev/null 2>&1; then
    echo -e "  ${RED}⚠${NC}  Start Backend: cd backend && source venv/bin/activate && python main.py"
fi

if ! lsof -ti:5173 > /dev/null 2>&1; then
    echo -e "  ${RED}⚠${NC}  Start Frontend: cd frontend-v2 && python3 -m http.server 5173 --bind 127.0.0.1"
fi

# If frontend is running but not accessible
if lsof -ti:5173 > /dev/null 2>&1; then
    if ! curl -s http://localhost:5173 > /dev/null 2>&1; then
        echo -e "  ${YELLOW}⚠${NC}  Frontend IPv6 issue detected. Try accessing via:"
        echo "      http://127.0.0.1:5173/index.html"
        echo ""
        echo "  Or restart frontend with IPv4 binding:"
        echo "      cd frontend-v2 && python3 -m http.server 5173 --bind 127.0.0.1"
    fi
fi

echo ""
echo -e "${GREEN}✅ Diagnostics complete!${NC}"
echo ""
echo "If all services are running but browser can't connect, try:"
echo "  1. http://127.0.0.1:5173/index.html (IPv4 instead of localhost)"
echo "  2. Clear browser cache"
echo "  3. Try a different browser"
echo "  4. Run ./cleanup.sh then ./setup-and-run.sh"
echo ""
