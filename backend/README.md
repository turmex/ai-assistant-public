# AI Assistant Backend - MVP

Local-first AI assistant powered by Ollama with hardware-optimized model selection.

## Quick Start

### 1. Install Dependencies

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Install Ollama

If you haven't already:
```bash
# Download from https://ollama.ai
# Or use Homebrew
brew install ollama
```

Start Ollama:
```bash
ollama serve
```

### 3. Download Recommended Model

The backend will detect your hardware and recommend a model. To manually download:

```bash
# For M2 16GB or better
ollama pull llama3.1:8b

# For 8GB Macs
ollama pull llama3.2:3b
```

### 4. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` if needed (defaults should work for most setups).

### 5. Run the Server

```bash
python main.py
```

Or with uvicorn directly:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Core Endpoints

- `GET /` - API information
- `GET /health` - Health check (Ollama + database status)
- `GET /hardware` - Detected hardware and model recommendations

### Chat

- `POST /chat` - Send a message to the AI assistant
  ```json
  {
    "message": "Hello, how are you?",
    "conversation_id": "optional-existing-id",
    "model": "optional-override-model"
  }
  ```

### Models

- `GET /models` - List available Ollama models
- `POST /models/download` - Download a new model
  ```json
  {
    "model_name": "llama3.1:8b"
  }
  ```

## Testing the API

### Using curl

```bash
# Health check
curl http://localhost:8000/health

# Hardware info
curl http://localhost:8000/hardware

# Send a chat message
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is the capital of France?"}'
```

### Using the interactive docs

Visit `http://localhost:8000/docs` for the auto-generated Swagger UI.

## Architecture

```
backend/
├── main.py                    # FastAPI application & endpoints
├── database.py                # SQLAlchemy models & session management
├── hardware_detector.py       # Mac hardware detection & model recommendations
├── conversation_manager.py    # Conversation state & intent detection (MVP)
├── logger.py                  # Workflow execution logging
├── requirements.txt           # Python dependencies
└── .env.example              # Environment configuration template
```

## Database Schema

The SQLite database includes:
- **User** - Multi-user support (future-proofing)
- **ToolConnection** - OAuth connections to Gmail/Calendar/Salesforce
- **Workflow** - User-defined automation workflows
- **WorkflowExecution** - Execution history and logs
- **Conversation** - Chat conversation history

Database is auto-created on first run at `./ai_assistant.db`

## Hardware Detection

The backend automatically detects:
- Chip type (Apple Silicon vs Intel)
- Chip model (M1, M2, M3, etc.)
- RAM size
- CPU cores

Based on your hardware, it recommends the optimal Ollama model:
- **M2 16GB+** → llama3.1:8b (excellent performance)
- **Intel 32GB+** → llama3.1:8b (good performance)
- **8GB Macs** → llama3.2:3b (acceptable performance)

## Next Steps (Future Phases)

This is the MVP foundation. Coming in Week 2-3:
- MCP integration for Gmail, Calendar, Salesforce
- Natural language workflow creation
- OAuth authentication flow
- Advanced intent detection
- Desktop app frontend

## Troubleshooting

### Ollama not connecting
- Make sure Ollama is running: `ollama serve`
- Check the URL in `.env` matches your Ollama instance
- Default: `http://localhost:11434`

### Model not found
- Download the recommended model: `ollama pull llama3.1:8b`
- Check available models: `ollama list`

### Database errors
- Delete `ai_assistant.db` to reset
- The database will be recreated on next startup

## Development

Run with auto-reload:
```bash
uvicorn main:app --reload
```

View logs in the console for debugging.
