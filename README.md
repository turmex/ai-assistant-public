# AI Assistant MVP - Local LLM Chat with Model Selection

A production-ready local-first AI assistant with hardware-aware model recommendations, intelligent model selection, and conversation management. Built with FastAPI, Ollama, and modern web technologies.

## 🚀 Features

### MVP (Week 1) - ✅ Complete
- **Hardware Detection**: Automatic detection of Mac hardware (Apple Silicon/Intel, RAM, CPU cores)
- **Smart Model Recommendations**: 8+ compatible models with performance indicators
- **Model Selection UI**: Beautiful dropdown with performance badges (🟢 Excellent, 🟡 Good, 🟠 Acceptable, 🔴 Slow)
- **One-Click Downloads**: Download any compatible model directly from the UI
- **Conversation Management**: Full conversation history with database persistence
- **Context-Aware Chat**: Maintains conversation context across messages
- **Modern UI**: Beautiful, responsive Tailwind CSS interface with dark mode

### Coming Soon (Weeks 2-4)
- Gmail integration via MCP
- Google Calendar integration
- Salesforce CRM integration
- Workflow automation builder
- OAuth authentication

## 📋 Prerequisites

1. **macOS** (Hardware detection optimized for Mac)
2. **Python 3.8+**
3. **Ollama** installed and running
   ```bash
   # Install Ollama
   brew install ollama

   # Start Ollama
   ollama serve
   ```

## 🛠️ Setup Instructions

### 1. Backend Setup

```bash
# Navigate to backend directory
cd ai-assistant/backend

# Create virtual environment (if not exists)
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# (Optional) Edit .env to customize settings
nano .env
```

### 2. Initialize Database

```bash
# Still in backend directory with venv activated
python -c "from database import init_db; init_db(); print('✓ Database initialized')"
```

### 3. Test Hardware Detection

```bash
python -c "from hardware_detector import get_hardware_detector; print(get_hardware_detector().get_hardware_summary())"
```

Expected output:
```
Chip: M2 (or your chip model)
RAM: 16GB
CPU Cores: 8
Recommended Model: Llama 3.1 8B
Compatible Models: 5
```

### 4. Start Backend Server

```bash
# Start the FastAPI server
python main.py
```

The server will start on `http://localhost:8000`

You should see:
```
🚀 Starting AI Assistant Backend...
✓ Database initialized
✓ Hardware detected: M2, 16GB RAM
✓ Recommended model: llama3.1:8b (excellent performance)
✓ Ollama is running with 2 models available
✓ AI Assistant Backend is ready!
```

### 5. Open Frontend

Open `frontend/index.html` in your browser:

```bash
# From project root
open frontend/index.html
```

Or use a local web server:
```bash
cd frontend
python3 -m http.server 8080
# Then open http://localhost:8080
```

## 🎯 Testing Checklist

### Manual Testing

1. **✅ Hardware Detection**
   - Open the frontend
   - Check that hardware info displays correctly (Chip, RAM, Cores, Compatible models)

2. **✅ Model Selection**
   - Click the model selector dropdown
   - Verify all compatible models are listed with:
     - ⭐ star on recommended model
     - Performance badges (🟢🟡🟠🔴)
     - Model size in GB
     - "(Not downloaded)" for models not installed locally

3. **✅ Model Download**
   - Select a model that's not downloaded
   - Click the "Download" button
   - Verify the download starts (Ollama will pull the model)
   - Wait for download to complete
   - Refresh and verify "(Not downloaded)" is removed

4. **✅ Chat Functionality**
   - Send a message: "Hello, who are you?"
   - Verify the response appears with model badge
   - Send another message: "What did I just ask you?"
   - Verify the assistant remembers context

5. **✅ Conversation Management**
   - Send a few messages
   - Click "New conversation"
   - Verify chat clears and conversation restarts

### API Testing

Test endpoints with curl:

```bash
# Health check
curl http://localhost:8000/health | jq

# Hardware info
curl http://localhost:8000/hardware | jq

# Available models (compatible with your hardware)
curl http://localhost:8000/models/available | jq

# Downloaded models (installed via Ollama)
curl http://localhost:8000/models/downloaded | jq

# All models (from Ollama)
curl http://localhost:8000/models | jq

# Create conversation
curl -X POST http://localhost:8000/conversations/new | jq

# Send chat message
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, what can you help me with?"}' | jq
```

## 📁 Project Structure

```
ai-assistant/
├── backend/
│   ├── main.py                    # FastAPI application with all endpoints
│   ├── hardware_detector.py       # Hardware detection & model recommendations
│   ├── conversation_manager.py    # Conversation state management
│   ├── database.py               # SQLAlchemy models & database setup
│   ├── requirements.txt          # Python dependencies
│   ├── .env.example             # Environment template
│   ├── .env                     # Your environment config (gitignored)
│   └── ai_assistant.db          # SQLite database (auto-created)
│
├── frontend/
│   └── index.html               # Complete single-page app (Tailwind CSS)
│
└── README.md                    # This file
```

## 🔧 Configuration

### Environment Variables (.env)

```bash
# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434

# Database
DATABASE_URL=sqlite:///./ai_assistant.db

# Server
HOST=0.0.0.0
PORT=8000
DEBUG=true

# Security (generate a random 32-character string)
SECRET_KEY=your-secret-key-here

# OAuth (for future weeks)
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
SALESFORCE_CLIENT_ID=
SALESFORCE_CLIENT_SECRET=
```

## 🎨 Model Catalog

The system supports 8 models with hardware-aware recommendations:

| Model | Size | Quality | Best For |
|-------|------|---------|----------|
| **Llama 3.2 1B** | 1.3GB | Basic | Fastest responses, basic tasks |
| **Llama 3.2 3B** | 2.0GB | Medium | Good balance, recommended for 8GB RAM |
| **Phi 3 Mini** | 2.3GB | Medium | Code-focused tasks |
| **Mistral 7B** | 4.1GB | High | Fast, high-quality responses |
| **Llama 3.1 8B** | 4.7GB | High | ⭐ Recommended for 16GB+ RAM |
| **Gemma 2 9B** | 5.5GB | High | Slower but excellent quality |
| **Llama 3.2 11B** | 6.5GB | High | Excellent quality, requires 16GB+ |
| **CodeLlama 13B** | 7.4GB | High | Best for code, requires 32GB+ |

### Performance Indicators

- 🟢 **Excellent**: Fast (10-15 tok/s) on your hardware
- 🟡 **Good**: Good speed (5-10 tok/s)
- 🟠 **Acceptable**: Acceptable (2-5 tok/s)
- 🔴 **Slow**: Slow (1-3 tok/s)

## 🐛 Troubleshooting

### "Could not connect to Ollama"
```bash
# Check if Ollama is running
ps aux | grep ollama

# Start Ollama
ollama serve

# Verify it's accessible
curl http://localhost:11434/api/tags
```

### "Hardware detection failed"
```bash
# Test hardware detection
cd backend
source venv/bin/activate
python -c "from hardware_detector import get_hardware_detector; print(get_hardware_detector().get_hardware_summary())"
```

### Database errors
```bash
# Reinitialize database
cd backend
source venv/bin/activate
rm ai_assistant.db
python -c "from database import init_db; init_db()"
```

### Frontend not loading hardware info
- Check browser console for errors (F12)
- Verify backend is running on port 8000
- Check CORS headers in browser Network tab

## 📊 API Endpoints

### Health & Info
- `GET /` - API info
- `GET /health` - Health check with Ollama status
- `GET /hardware` - Hardware detection results

### Models
- `GET /models` - All downloaded models from Ollama
- `GET /models/available` - Compatible models for your hardware
- `GET /models/downloaded` - Models already downloaded
- `POST /models/download` - Download a model

### Chat
- `POST /chat` - Send a message
- `POST /conversations/new` - Create new conversation
- `GET /conversations/{id}` - Get conversation history
- `DELETE /conversations/{id}` - Delete conversation
- `GET /conversations` - List all conversations

## 🚀 Next Steps (Weeks 2-4)

1. **Week 2**: Gmail Integration
   - OAuth setup
   - MCP Gmail connector
   - Email reading/sending

2. **Week 3**: Calendar & Salesforce
   - Google Calendar integration
   - Salesforce CRM connector
   - Unified tool interface

3. **Week 4**: Workflows
   - Workflow builder UI
   - Scheduled automation
   - Tool chaining

## 📝 Code Quality

All code follows best practices:
- ✅ Type hints on all functions
- ✅ Comprehensive docstrings
- ✅ Error handling with helpful messages
- ✅ Logging at INFO level
- ✅ Clean, readable structure
- ✅ Async/await throughout
- ✅ Proper HTTP status codes
- ✅ Pydantic validation
- ✅ Security best practices

## 🤝 Contributing

This is a personal project for local AI assistance. Feel free to fork and customize!

## 📄 License

MIT License - Use freely for personal or commercial projects.

---

**Built with**: FastAPI, SQLAlchemy, Ollama, Tailwind CSS, and lots of ☕
