#!/bin/bash
# Quick fix script to start frontend with IPv4 binding

cd "$(dirname "$0")/frontend-v2"

echo "🌐 Starting Frontend on IPv4 (127.0.0.1)..."
echo ""
echo "Open your browser to:"
echo "  http://127.0.0.1:5173/index.html"
echo ""
echo "Press Ctrl+C to stop"
echo ""

python3 -m http.server 5173 --bind 127.0.0.1
