#!/bin/bash
# AI Assistant - Fix Virtual Environment
# Recreates the Python virtual environment and installs dependencies

set -e

echo "🔧 AI Assistant - Fix Virtual Environment"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/backend"

echo -e "${BLUE}Backend Directory: $BACKEND_DIR${NC}"
echo ""

cd "$BACKEND_DIR"

# Remove old venv if it exists
if [ -d "venv" ]; then
    echo -e "${YELLOW}Removing old virtual environment...${NC}"
    rm -rf venv
    echo -e "${GREEN}✓${NC} Old venv removed"
    echo ""
fi

# Create new venv
echo -e "${YELLOW}Creating new virtual environment...${NC}"
python3 -m venv venv
echo -e "${GREEN}✓${NC} Virtual environment created"
echo ""

# Activate and install
echo -e "${YELLOW}Installing dependencies...${NC}"
source venv/bin/activate

# Upgrade pip
echo "  Upgrading pip..."
pip install --quiet --upgrade pip

# Install requirements
echo "  Installing requirements..."
pip install --quiet -r requirements.txt

echo -e "${GREEN}✓${NC} Dependencies installed"
echo ""

# Initialize database
echo -e "${YELLOW}Initializing database...${NC}"
python -c "from database import init_db; init_db()"
echo -e "${GREEN}✓${NC} Database initialized"
echo ""

# Test hardware detection
echo -e "${YELLOW}Testing hardware detection...${NC}"
python -c "from hardware_detector import get_hardware_detector; print(get_hardware_detector().get_hardware_summary())"
echo ""

deactivate

echo -e "${GREEN}✅ Virtual environment fixed successfully!${NC}"
echo ""
echo "You can now run: ./setup-and-run.sh"
echo ""
