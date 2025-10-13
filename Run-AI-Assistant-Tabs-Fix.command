#!/bin/bash
# Terminal Tabs Launcher (explicit per-tab execution)
# Save as: ~/Desktop/Run-AI-Assistant-Tabs-Fix.command
# chmod +x ~/Desktop/Run-AI-Assistant-Tabs-Fix.command
# Double-click (Right-click → Open the first time)

set -e

PROJECT_DIR="$HOME/Desktop/ai-assistant"
BACKEND_DIR="$PROJECT_DIR/backend"
FRONTEND_DIR="$PROJECT_DIR/frontend"
VENV_BIN="$BACKEND_DIR/venv/bin"
FRONTEND_PORT="5173"

# Checks
[ -d "$BACKEND_DIR" ] || { echo "❌ Missing $BACKEND_DIR"; exit 1; }
[ -d "$FRONTEND_DIR" ] || { echo "❌ Missing $FRONTEND_DIR"; exit 1; }
[ -d "$VENV_BIN" ] || { echo "❌ Missing Python venv at $VENV_BIN"; exit 1; }

# from project root: ~/Desktop/ai-assistant
pkill -f "python main.py" 2>/dev/null || true
pkill -f "http.server 5173" 2>/dev/null || true

# Simple command strings (no quotes inside); bash -lc will interpret them in the shell
CMD1="cd $BACKEND_DIR; source $VENV_BIN/activate; echo '⏳ Checking Ollama...'; if curl -sSf http://localhost:11434/api/tags >/dev/null 2>&1; then echo '✅ Ollama already running on 11434'; else echo '🚀 Starting Ollama on 11434...'; ollama serve; fi"
CMD2="cd $BACKEND_DIR; source $VENV_BIN/activate; echo '🚀 Launching backend on http://localhost:8000'; python main.py"
CMD3="cd $FRONTEND_DIR; echo '🌐 Serving frontend on http://localhost:$FRONTEND_PORT'; python -m http.server $FRONTEND_PORT"

/usr/bin/osascript <<OSA
tell application "Terminal"
  activate
  -- Ensure there's a window
  set win to do script "" -- opens a new window with a shell
  delay 0.2

  -- Tab 1: Ollama
  set cmd1 to "bash -lc " & quoted form of "$CMD1"
  do script cmd1 in selected tab of front window
  delay 0.4

  -- Tab 2: Backend
  tell application "System Events" to tell process "Terminal" to keystroke "t" using command down
  delay 0.2
  set cmd2 to "bash -lc " & quoted form of "$CMD2"
  do script cmd2 in selected tab of front window
  delay 0.4

  -- Tab 3: Frontend
  tell application "System Events" to tell process "Terminal" to keystroke "t" using command down
  delay 0.2
  set cmd3 to "bash -lc " & quoted form of "$CMD3"
  do script cmd3 in selected tab of front window
end tell
OSA

#sleep 2
#open "http://localhost:${FRONTEND_PORT}/index.html"

sleep 4
open "/Users/davidcelekli/Desktop/ai-assistant/frontend/index.html"
