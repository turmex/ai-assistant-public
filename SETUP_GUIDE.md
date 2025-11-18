# AI Assistant - Setup & Usage Guide

## 🚀 Quick Start

This system provides a **brutally minimal, enterprise-focused** interface for chatting with local LLMs. It:
- ✅ Detects your hardware automatically (Mac-optimized)
- ✅ Fetches ALL compatible models from HuggingFace dynamically
- ✅ Shows performance tiers color-coded (fastest/fast/good/slow)
- ✅ Lets you paste HuggingFace URLs to download any model
- ✅ Auto-downloads Llama 3.2 1B on first run (fastest, most compatible)
- ✅ Loads 1 model at a time
- ✅ Clean, minimal, enterprise UI

---

## 📋 Prerequisites

### 1. Install Ollama
```bash
# Install via Homebrew
brew install ollama
```

### 2. Verify Installation
```bash
# Check Ollama version
ollama --version
```

---

## 🛠️ Installation Steps

### Step 1: Navigate to Project Directory
```bash
cd ~/Desktop/ai-assistant
```

### Step 2: Backend Setup
```bash
# Go to backend directory
cd backend

# Create virtual environment (if not already created)
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

### Step 3: Verify Setup
```bash
# Still in backend directory with venv activated

# Test hardware detection
python -c "from hardware_detector import get_hardware_detector; print(get_hardware_detector().get_hardware_summary())"

# Initialize database
python -c "from database import init_db; init_db(); print('Database initialized')"
```

---

## ▶️ Running the System

### Terminal 1: Start Ollama
```bash
# Start Ollama service
ollama serve
```
**Keep this terminal running**

### Terminal 2: Start Backend Server
```bash
# Navigate to backend
cd ~/Desktop/ai-assistant/backend

# Activate virtual environment
source venv/bin/activate

# Start FastAPI server
python main.py
```

You should see:
```
🚀 Starting AI Assistant Backend...
✓ Database initialized
✓ Hardware detected: M2, 16GB RAM
✓ Recommended model: llama3.2:1b (fastest performance)
No models found. Auto-downloading default model: llama3.2:1b
✓ Successfully downloaded llama3.2:1b
✓ AI Assistant Backend is ready!
```

**Keep this terminal running**

### Terminal 3: Open Frontend
```bash
# Navigate to frontend
cd ~/Desktop/ai-assistant/frontend-v2

# Start local web server
python3 -m http.server 5173
```

**Keep this terminal running**

### Step 4: Open in Browser
Open your browser and go to:
```
http://localhost:5173/index.html
```

---

## 🎯 How to Use

### 1. **Hardware Detection**
The system automatically detects:
- Your chip (M1, M2, M3, or Intel)
- Available RAM
- CPU cores
- Number of compatible models

### 2. **Model Selection**
The dropdown shows ALL models compatible with your hardware from HuggingFace:

**Format:**
```
★ Llama 3.2 1B ● 1.3GB · fastest (Not downloaded)
  Llama 3.1 8B ● 4.7GB · fast
  Mistral 7B ● 4.1GB · fast (Not downloaded)
```

- **★** = Recommended model for your hardware
- **●** = Performance tier color (green=fastest, blue=fast, amber=good, red=slow)
- **(Not downloaded)** = Model needs to be downloaded

### 3. **Download Models**

**Option A: Select from dropdown**
1. Choose a model from the dropdown
2. If it shows "(Not downloaded)", click the "Download Selected Model" button
3. Wait for download to complete (progress shown)

**Option B: Paste HuggingFace URL**
1. Go to https://huggingface.co
2. Find any compatible model (e.g., https://huggingface.co/meta-llama/Llama-3.2-1B-Instruct)
3. Copy the URL
4. Paste into "Or Paste HuggingFace URL" field
5. Click "Download" or press Enter
6. System finds the Ollama-compatible name and downloads it

### 4. **Chat**
1. Select a downloaded model (one without "(Not downloaded)")
2. Type your message in the input box
3. Press Enter or click "Send"
4. The assistant responds using the selected model

### 5. **New Conversation**
Click "New conversation" to start fresh (clears chat history)

---

## 📊 Performance Tiers Explained

| Tier | Speed | When to Use |
|------|-------|-------------|
| **Fastest** | 15-20 tok/s | Quick responses, basic tasks |
| **Fast** | 10-15 tok/s | Good balance of speed & quality |
| **Good** | 5-10 tok/s | High quality, acceptable speed |
| **Slow** | 2-5 tok/s | Best quality, slower responses |

The system automatically calculates performance based on:
- Your chip type (Apple Silicon is 2-3x faster than Intel)
- Available RAM
- Model size
- RAM headroom (available after loading model)

---

## 🔧 Troubleshooting

### "Could not connect to Ollama"
```bash
# Terminal 1: Restart Ollama
killall ollama
ollama serve
```

### "Hardware detection failed"
```bash
# Test hardware detection
cd ~/Desktop/ai-assistant/backend
source venv/bin/activate
python -c "from hardware_detector import get_hardware_detector; print(get_hardware_detector().get_hardware_summary())"
```

### "Failed to load models from HuggingFace"
The system will fallback to a hardcoded catalog of 20+ popular models. This is normal if:
- No internet connection
- HuggingFace API is slow/down
- Rate limiting

The fallback catalog includes:
- Llama 3.2 (1B, 3B)
- Llama 3.1 (8B)
- Mistral 7B
- Phi 3 Mini
- Gemma 2 (9B)
- And more...

### Backend won't start
```bash
# Reinstall dependencies
cd ~/Desktop/ai-assistant/backend
source venv/bin/activate
pip install --upgrade -r requirements.txt
```

### Database errors
```bash
# Reset database
cd ~/Desktop/ai-assistant/backend
source venv/bin/activate
rm ai_assistant.db
python -c "from database import init_db; init_db()"
```

---

## 🎨 UI Features

### Minimal Enterprise Design
- **Clean Layout**: No clutter, only essentials
- **Professional Colors**: Grays, blues, subtle accents
- **Clear Typography**: Easy to read, well-spaced
- **Responsive**: Works on different screen sizes

### Smart Features
- **Auto Status**: Green = online, Amber = degraded, Red = offline
- **Download Progress**: Real-time feedback
- **Model Info**: Shows current model in chat
- **Toast Notifications**: Non-intrusive alerts

---

## 🔬 Technical Details

### Architecture
```
Frontend (frontend-v2/index.html)
    ↓ HTTP
Backend (FastAPI on port 8000)
    ↓ API calls
Ollama (Local LLM server on port 11434)
    ↓ Model inference
Local Models (downloaded to ~/.ollama)
```

### API Endpoints
- `GET /health` - System health check
- `GET /hardware` - Hardware detection results
- `GET /models/available` - Compatible models from HuggingFace
- `GET /models/downloaded` - Already downloaded models
- `POST /models/download` - Download model by name
- `POST /models/download-from-hf` - Download from HuggingFace URL
- `POST /chat` - Send chat message
- `POST /conversations/new` - Start new conversation

### HuggingFace Integration
The system fetches 20+ popular open-source models from HuggingFace:
- Llama family (Meta)
- Mistral (Mistral AI)
- Phi (Microsoft)
- Gemma (Google)
- Qwen (Alibaba)
- CodeLlama (Meta)
- Vicuna (LMSYS)
- And more...

Each model includes:
- Download count
- Likes
- Size
- Ollama compatibility mapping
- Performance estimation

---

## 📝 Configuration

### Environment Variables (backend/.env)
```bash
# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434

# Database
DATABASE_URL=sqlite:///./ai_assistant.db

# Server
HOST=0.0.0.0
PORT=8000
DEBUG=true

# Default Model (if HuggingFace fails)
DEFAULT_LOCAL_MODEL=llama3.2:1b
```

### Customization
To add more models, edit:
`backend/huggingface_integration.py`

Look for `OLLAMA_COMPATIBLE_MODELS` dictionary and add new entries:
```python
"huggingface/model-id": {
    "ollama": "model:tag",
    "size_gb": 4.0,
    "quality": "high"
}
```

---

## 🚀 Advanced Usage

### Command Line Model Download
```bash
# Download a specific model
ollama pull llama3.2:1b

# List downloaded models
ollama list

# Remove a model
ollama rm llama3.2:1b
```

### Test Backend Directly
```bash
# Health check
curl http://localhost:8000/health | jq

# Hardware info
curl http://localhost:8000/hardware | jq

# Available models
curl http://localhost:8000/models/available | jq

# Send a chat message
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello!"}' | jq
```

---

## 🎓 Next Steps

Once the basic system is working:
1. Explore different models and their strengths
2. Try different performance tiers
3. Download specialized models (code, math, reasoning)
4. Experiment with conversation contexts

---

## 📄 License

MIT License - Use freely for personal or commercial projects.

---

## 🆘 Support

If issues persist:
1. Check all 3 terminals are running
2. Verify Ollama is accessible: `curl http://localhost:11434/api/tags`
3. Check backend logs for errors
4. Try restarting everything from scratch

---

**Built with:** FastAPI, Ollama, HuggingFace API, Tailwind CSS, and minimal dependencies.
