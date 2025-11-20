# AI Assistant - WebLLM & Local LLM Chat

A production-ready AI assistant that runs entirely in your browser using WebLLM (WebGPU), with Ollama as an optional backend. Features intelligent model management, hardware-aware recommendations, HuggingFace integration, multi-provider support, and TOON format for optimized token usage.

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
- **40+ Model Catalog**: Comprehensive model catalog with detailed metadata

### HuggingFace Integration
- **Dynamic Catalog**: Fetches 50+ models from HuggingFace API
- **Model Search by URL**: Paste any HuggingFace model URL to search
- **Compatibility Checking**: Automatic hardware compatibility assessment
- **Ollama Mapping**: Detects if HF models are available in Ollama format
- **Cached Results**: 1-hour TTL caching for performance

### Online LLM Providers
- **OpenRouter**: Access 300+ models (GPT-4, Claude, Mistral, etc.)
- **OpenAI**: ChatGPT API integration
- **Anthropic**: Claude API integration
- **API Key Management**: Secure local storage with base64 obfuscation

### Token Optimization (TOON)
- **~40% Token Reduction**: Compress conversation history using TOON format
- **Toggle On/Off**: Enable/disable with one click
- **Automatic**: Works transparently with WebLLM chat
- **Persistent**: Preference saved across sessions

### Multi-Fallback Chat System
- **Robust Chat**: Three-tier fallback ensures responses even with context issues
  1. Full context with `/api/chat`
  2. Latest message only with `/api/chat`
  3. Flattened prompt with `/api/generate`
- **Context Sanitization**: Handles complex message formats automatically
- **Error Recovery**: Detailed logging with breadcrumbs

### Hardware Detection
- **Auto-Detect Mac Hardware**: Chip type (M1/M2/M3/Intel), RAM, CPU cores
- **Smart Recommendations**: Optimal model based on system specs
- **Performance Estimates**: Speed predictions (tokens/second) per model
- **All Compatible Models**: Lists every model you can run with performance indicators
- **Fallback Safety**: Defaults to `llama3.2:1b` if detection fails

### Conversation Management
- **Full History**: SQLite-backed conversation storage
- **Context Window**: Last 10 messages for LLM context
- **Intent Detection**: Keyword-based detection for tools (Gmail, Calendar, Salesforce)
- **Multi-User Framework**: Database supports multiple users (MVP uses single user)

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
- Search by Ollama or HuggingFace URL

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

| Model | Size | Parameters | Performance | Quality |
|-------|------|------------|-------------|---------|
| llama3.2:1b | 1.3GB | 1B | Fastest | Basic |
| llama3.2:3b | 2.0GB | 3B | Fast | Medium |
| phi3:mini | 2.3GB | 3.8B | Fast | Medium |
| mistral:7b | 4.1GB | 7B | Fast | High |
| llama3.1:8b | 4.7GB | 8B | Good | High |
| gemma2:9b | 5.5GB | 9B | Good | High |
| qwen2:7b | 4.4GB | 7B | Good | High |
| codellama:7b | 3.8GB | 7B | Good | High |
| deepseek-r1:7b | 4.7GB | 7B | Good | High |
| mixtral:8x7b | 26.0GB | 8x7B | Slow | High |

**Full catalog includes 30+ models** including Llama 3.1/3.2, Mistral, Phi 3, Gemma 2, Qwen 2, DeepSeek, CodeLlama, and more.

## Project Structure

```
ai-assistant/
├── frontend-v2/
│   └── index.html          # Main UI (WebLLM + Ollama)
├── frontend/
│   └── src/                 # Modular JS components
│       ├── webllm-integration.js
│       ├── provider-toggle.js
│       ├── api-key-manager.js
│       ├── online-llm-client.js
│       └── settings-panel.js
├── backend/
│   ├── main.py              # FastAPI server
│   ├── database.py          # SQLAlchemy ORM & models
│   ├── conversation_manager.py  # Chat history & intent detection
│   ├── hardware_detector.py # Mac hardware detection
│   ├── ollama_integration.py    # Ollama model catalog
│   ├── huggingface_integration.py # HuggingFace API
│   ├── shared_utils.py      # Common utilities
│   ├── logger.py            # Workflow logging
│   └── requirements.txt     # Python dependencies
├── config/
│   └── provider-config.json # Provider configuration
├── tests/
│   └── model_management/    # API tests
├── 🚀 Launch AI Assistant.command  # One-click launcher
├── run.command              # Alternative launcher
└── README.md                # This file
```

## API Endpoints

When running with Ollama backend:

### Health & System Info
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | System health check with hardware info |
| `/hardware` | GET | Detailed hardware info & compatible models |
| `/api` | GET | API information |
| `/` | GET | Serve frontend |

### Model Management
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/models` | GET | List downloaded Ollama models |
| `/models/available` | GET | Get ALL models (Ollama + HuggingFace) |
| `/models/downloaded` | GET | Get locally installed models |
| `/models/download` | POST | Download model from Ollama |
| `/models/download-from-hf` | POST | Download from HuggingFace URL |
| `/models/search-hf` | POST | Search HuggingFace for model info |
| `/models/search-url` | POST | Unified search (Ollama or HF URL) |
| `/models/{name}` | DELETE | Delete/unload a model |

### Chat & Conversations
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/chat` | POST | Send message with multi-fallback |
| `/conversations/new` | POST | Create new conversation |
| `/conversations/{id}` | GET | Get conversation history |
| `/conversations/{id}` | DELETE | Delete conversation |
| `/conversations` | GET | List all conversations (limit: 20) |

## Technical Details

### WebLLM Architecture
- Uses `@mlc-ai/web-llm` for browser inference
- WebGPU for GPU acceleration
- IndexedDB/Cache API for model storage
- Web Workers for non-blocking inference

### Backend Architecture
- **FastAPI 0.109.0**: Async web framework
- **SQLAlchemy 2.0.25**: ORM with SQLite/PostgreSQL
- **httpx 0.26.0**: Async HTTP client
- **Pydantic 2.5.3**: Data validation

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

### Database Schema

The backend uses SQLite with the following tables:

- **users**: Multi-user support (id, email, created_at)
- **conversations**: Chat history with JSON messages
- **tool_connections**: OAuth connections (Gmail, Calendar, Salesforce)
- **workflows**: User-defined automation workflows
- **workflow_executions**: Workflow run history & logs

## Configuration

### Environment Variables (.env)

```bash
# Ollama
OLLAMA_BASE_URL=http://localhost:11434
DEFAULT_LOCAL_MODEL=llama3.1

# Database
DATABASE_URL=sqlite:///./ai_assistant.db

# Server
HOST=0.0.0.0
PORT=8000
DEBUG=true

# OAuth (Future)
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
SALESFORCE_CLIENT_ID=
SALESFORCE_CLIENT_SECRET=

# Security
SECRET_KEY=<your-secret-key>
```

### Provider Configuration (provider-config.json)

```json
{
  "default_provider": "webllm",
  "providers": {
    "webllm": {
      "enabled": true,
      "default_model": "Llama-3.2-1B-Instruct-q4f16_1-MLC",
      "features": {
        "streaming": true,
        "offline_support": true,
        "privacy_focused": true
      }
    },
    "ollama": {
      "enabled": true,
      "base_url": "http://localhost:11434",
      "default_model": "llama3.2:1b",
      "features": {
        "streaming": true,
        "large_models": true,
        "higher_quality": true
      }
    }
  },
  "fallback_strategy": {
    "enabled": true,
    "order": ["webllm", "ollama"]
  },
  "toon_optimization": {
    "enabled": false,
    "auto_enable_threshold": 500
  }
}
```

### LocalStorage Keys

- `ai-assistant-provider` - Current provider (webllm/ollama)
- `ai-assistant-toon` - TOON enabled state
- `ai-assistant-api-keys` - Encrypted API keys
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

### Chat Returns Empty Response
The multi-fallback system will try three different approaches. If all fail:
- Check Ollama is running and responsive
- Verify model is fully downloaded
- Check server logs for specific error

## Performance Tips

1. **Use TOON** for long conversations
2. **Start with smaller models** (0.5B-1B) for testing
3. **Enable GPU** in Chrome settings
4. **Close other GPU apps** when using WebLLM
5. **Use Ollama** for models >3B parameters
6. **Apple Silicon users** get 2-3x speed improvement

### Performance Estimates

| RAM | Apple Silicon | Intel |
|-----|--------------|-------|
| 8GB | 1-3B models | 1-2B models |
| 16GB | 1-8B models | 1-5B models |
| 32GB | 1-13B models | 1-8B models |
| 64GB+ | All models | Most models |

## Security Notes

- **API Keys**: Stored in localStorage with base64 obfuscation (not encryption)
- **CORS**: Permissive for MVP - restrict in production
- **Authentication**: Single-user MVP - OAuth framework ready
- **Input Sanitization**: All chat context sanitized before LLM
- **No Server Secrets**: No sensitive data on backend

## Upcoming Features

Based on database schema and code structure:

- **MCP Tool Integration**: Gmail, Calendar, Salesforce
- **OAuth Authentication**: Google, Salesforce
- **Workflow Automation**: Create and schedule workflows
- **Multi-user Support**: Activate existing framework
- **Advanced Intent Detection**: ML-based (currently keyword-based)
- **Streaming Responses**: Real-time token streaming
- **Token Analytics**: Usage tracking and optimization

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `cd tests && python -m pytest`
5. Submit a pull request

## License

MIT License - Use freely for personal or commercial projects.

---

**Built with**: WebLLM, FastAPI, Ollama, HuggingFace, Tailwind CSS, SQLAlchemy, WebGPU

**Token Optimization**: TOON Format for ~40% reduction

**Privacy**: All inference runs locally on your device

**Model Sources**: Ollama Library (30+ models) + HuggingFace Hub (50+ models)
