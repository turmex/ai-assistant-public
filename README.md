# AI Assistant - WebLLM & Local LLM Chat

A production-ready AI assistant that runs entirely in your browser using WebLLM (WebGPU), with Ollama as an optional backend. Features intelligent model management, hardware-aware recommendations, and TOON format for optimized token usage.

## Features

### Browser-First AI (WebLLM)
- **Zero Server Required**: Run LLMs directly in your browser using WebGPU
- **Privacy-First**: All inference happens locally, no data leaves your device
- **Multiple Models**: Qwen2.5, Llama 3.2, Phi 3.5, Gemma 2, SmolLM2
- **Model Caching**: Downloaded models persist in browser storage
- **One-Click Loading**: Load, unload, and clear models with simple buttons

### Ollama Integration (Optional)
- **Local Server**: Use Ollama for larger models and faster inference
- **Smart Detection**: Hardware-aware model recommendations
- **Auto-Download**: One-click model downloads from Ollama library
- **URL Search**: Find and download any model from Ollama Hub

### Token Optimization (TOON)
- **~40% Token Reduction**: Compress conversation history using TOON format
- **Toggle On/Off**: Enable/disable with one click
- **Automatic**: Works transparently with WebLLM chat
- **Persistent**: Preference saved across sessions

### One-Click Launch
- **Single File**: Double-click `🚀 Launch AI Assistant.command`
- **Auto Setup**: Installs dependencies, starts services, opens browser
- **WebGPU Enabled**: Launches Chrome with optimal WebGPU flags
- **Cross-Platform**: Works on macOS and Linux

## Quick Start

### Option 1: One-Click Launch (Recommended)

1. Double-click `🚀 Launch AI Assistant.command`
2. Wait for setup to complete
3. Browser opens automatically with WebGPU enabled
4. Start chatting with WebLLM (no server needed!)

### Option 2: Manual Setup

```bash
# Navigate to project
cd ai-assistant

# Backend setup
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Start server
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Open in browser
open http://localhost:8000
```

### Option 3: WebLLM Only (No Server)

Simply open `frontend-v2/index.html` in Chrome with WebGPU support:

```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
    --enable-unsafe-webgpu \
    --enable-features=Vulkan,UseSkiaRenderer \
    --ignore-gpu-blocklist \
    "file:///path/to/ai-assistant/frontend-v2/index.html"
```

## Requirements

### For WebLLM (Browser-Based)
- **Chrome 113+** or Edge 113+ with WebGPU support
- **8GB+ RAM** recommended
- **GPU** with WebGPU support (most modern GPUs)

### For Ollama (Optional)
- **macOS** or Linux
- **Python 3.8+**
- **Ollama** installed (`brew install ollama`)

## Usage Guide

### Switching Providers

Toggle between WebLLM and Ollama using the buttons in the header:
- **WebLLM**: Browser-based inference, no server needed
- **Ollama**: Local server, larger models available

### Managing Models

Click the **Models** button to:
- View downloaded models
- Download new models
- Load/Unload models
- Clear model cache
- Check model sizes and performance ratings

### Using TOON Format

Click the **TOON** button (lightning bolt) to enable token optimization:
- Button turns green when active
- Compresses conversation history by ~40%
- Ideal for longer conversations
- Toggle off anytime for standard format

### WebGPU Troubleshooting

If WebLLM fails to load:

1. **Enable Hardware Acceleration**:
   - Chrome → Settings → Search "hardware"
   - Enable "Use graphics acceleration when available"
   - Restart Chrome completely

2. **Check WebGPU Support**:
   - Visit `chrome://gpu`
   - Look for "WebGPU: Hardware accelerated"

3. **Use Launch Script**:
   - The `🚀 Launch AI Assistant.command` launches Chrome with correct flags

## Available Models

### WebLLM Models (Browser)

| Model | Size | Best For |
|-------|------|----------|
| Qwen2.5-0.5B | ~300MB | Fast responses, basic tasks |
| Qwen2.5-1.5B | ~900MB | Good balance of speed/quality |
| Llama-3.2-1B | ~700MB | General conversation |
| Llama-3.2-3B | ~2GB | Higher quality responses |
| Phi-3.5-mini | ~2.4GB | Code and reasoning |
| SmolLM2-1.7B | ~1GB | Efficient, fast |
| Gemma-2-2B | ~1.5GB | Google's efficient model |

### Ollama Models (Server)

| Model | Size | Performance |
|-------|------|-------------|
| llama3.2:1b | 1.3GB | 🟢 Excellent |
| llama3.2:3b | 2.0GB | 🟢 Excellent |
| phi3:mini | 2.3GB | 🟢 Excellent |
| mistral:7b | 4.1GB | 🟡 Good |
| llama3.1:8b | 4.7GB | 🟡 Good |
| gemma2:9b | 5.5GB | 🟠 Acceptable |

## Project Structure

```
ai-assistant/
├── frontend-v2/
│   └── index.html          # Main UI (WebLLM + Ollama)
├── backend/
│   ├── main.py             # FastAPI server
│   ├── requirements.txt    # Python dependencies
│   └── src/                # Source modules
├── 🚀 Launch AI Assistant.command  # One-click launcher
├── run.command             # Alternative launcher
└── README.md               # This file
```

## API Endpoints

When running with Ollama backend:

### Health & Info
- `GET /health` - System health check
- `GET /hardware` - Hardware detection

### Models
- `GET /models` - List all Ollama models
- `GET /models/available` - Compatible models
- `GET /models/downloaded` - Installed models
- `POST /models/download` - Download a model
- `DELETE /models/{name}` - Delete a model

### Chat
- `POST /chat` - Send message (Ollama)
- `POST /conversations/new` - New conversation
- `GET /conversations/{id}` - Get history

## Technical Details

### WebLLM Architecture
- Uses `@mlc-ai/web-llm` for browser inference
- WebGPU for GPU acceleration
- IndexedDB/Cache API for model storage
- Web Workers for non-blocking inference

### TOON Format
Based on [toon-format/toon](https://github.com/toon-format/toon):
- Tabular notation reduces JSON overhead
- Field names in header, data in rows
- ~40% token reduction for conversations
- Automatic encoding/decoding

### Dark Mode
- Full dark theme by default
- Optimized for reduced eye strain
- Consistent styling across all components

## Configuration

### Environment Variables (.env)

```bash
# Ollama
OLLAMA_BASE_URL=http://localhost:11434

# Database
DATABASE_URL=sqlite:///./ai_assistant.db

# Server
HOST=0.0.0.0
PORT=8000
DEBUG=true
```

### LocalStorage Keys

- `ai-assistant-provider` - Current provider (webllm/ollama)
- `ai-assistant-toon` - TOON enabled state
- `webllm-cached-{model}` - Model cache status

## Troubleshooting

### WebLLM Not Loading
1. Check Chrome version (113+ required)
2. Enable hardware acceleration in Chrome settings
3. Verify WebGPU at `chrome://gpu`
4. Use the launch script for correct flags

### Ollama Connection Failed
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Start Ollama
ollama serve
```

### Model Download Stuck
```bash
# Check Ollama logs
tail -f ~/.ollama/logs/server.log

# Restart Ollama
pkill ollama && ollama serve
```

### 404 Model Not Found
- Model auto-removed from list
- Re-download from Available Models
- Check Ollama storage: `~/.ollama/models`

## Performance Tips

1. **Use TOON** for long conversations
2. **Start with smaller models** (0.5B-1B) for testing
3. **Enable GPU** in Chrome settings
4. **Close other GPU apps** when using WebLLM
5. **Use Ollama** for models >3B parameters

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - Use freely for personal or commercial projects.

---

**Built with**: WebLLM, FastAPI, Ollama, Tailwind CSS, and WebGPU

**Token Optimization**: TOON Format for ~40% reduction

**Privacy**: All inference runs locally on your device
