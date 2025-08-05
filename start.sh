#!/bin/bash

echo "🔥 Face Morphing Web App Startup Script"
echo "====================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo ""
echo "📋 Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed or not in PATH${NC}"
    echo "Please install Python 3.8+ and try again"
    exit 1
fi

echo -e "${GREEN}✅ Python found${NC}"
python3 --version

echo ""
echo "📦 Installing dependencies..."
echo "Trying exact versions first..."
if ! python3 -m pip install -r requirements.txt; then
    echo -e "${YELLOW}⚠️  Exact versions failed, trying flexible versions...${NC}"
    if ! python3 -m pip install -r requirements-flexible.txt; then
        echo -e "${YELLOW}⚠️  Flexible versions failed, trying individual packages...${NC}"
        if ! python3 -m pip install Flask Pillow requests Werkzeug; then
            echo -e "${RED}❌ All dependency installation methods failed${NC}"
            echo "Please try manually: python3 -m pip install Flask Pillow requests Werkzeug"
            exit 1
        fi
    fi
fi

echo -e "${GREEN}✅ Dependencies installed${NC}"

echo ""
echo "📁 Creating directories..."
mkdir -p uploads outputs
echo -e "${GREEN}✅ Directories created${NC}"

echo ""
echo "🔍 Checking ComfyUI connection..."
if ! python3 -c "import requests; requests.get('http://127.0.0.1:8188/system_stats', timeout=5)" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  WARNING: Cannot connect to ComfyUI at http://127.0.0.1:8188${NC}"
    echo "Please make sure ComfyUI is running with API enabled:"
    echo "  python main.py --listen 127.0.0.1 --port 8188"
    echo ""
    echo "Press Enter to continue anyway, or Ctrl+C to exit..."
    read
else
    echo -e "${GREEN}✅ ComfyUI connection successful${NC}"
fi

echo ""
echo "🚀 Starting Face Morphing Web App..."
echo "🌐 Open http://localhost:5000 in your browser"
echo "🛑 Press Ctrl+C to stop the server"
echo ""

python3 app.py

echo ""
echo "👋 Face Morphing Web App stopped"