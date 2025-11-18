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
