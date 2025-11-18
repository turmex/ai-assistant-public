# Project Structure Analysis

**Project:** `/Users/davidcelekli/Desktop/ai-assistant`
**Architecture:** FastAPI backend + Single-page HTML/JS frontend
**Type:** Local-first AI chat application using Ollama for LLM inference

## Directory Structure

### Backend (`/backend/`)
Python FastAPI application with the following components:

- **main.py** (1108 lines) - Main server with all API endpoints
- **ollama_integration.py** (811 lines) - Ollama model catalog and compatibility checking
- **hardware_detector.py** (416 lines) - Mac hardware detection (Apple Silicon/Intel)
- **huggingface_integration.py** - HuggingFace model search integration
- **database.py** - SQLAlchemy models and database setup
- **conversation_manager.py** - Chat history and conversation management
- **requirements.txt** - Python dependencies

### Frontend
- **frontend/index.html** (543 lines) - Complete SPA with Tailwind CSS
- **frontend-v2/** - Alternative frontend (referenced in main.py line 299)

## Technology Stack

### Backend
- **FastAPI** - Modern async web framework
- **SQLAlchemy** - Database ORM
- **httpx** - Async HTTP client (for Ollama API communication)
- **Pydantic** - Data validation and settings management
- **SQLite** - Local database for conversation history

### Frontend
- **Vanilla JavaScript** - No framework dependencies
- **Tailwind CSS** - Utility-first CSS via CDN
- **Fetch API** - HTTP requests to backend

### LLM Integration
- **Ollama** - Local LLM inference server (http://localhost:11434)
- Supports 25+ models across multiple families
- GGUF model format

### Hardware Support
- Mac-optimized (Apple Silicon M1/M2/M3 and Intel)
- Hardware detection for optimal model recommendations
- Performance estimates based on available RAM and chip type

## Key Features

1. **Hardware-aware model recommendations** - Automatically detects Mac specs
2. **Model catalog with 25+ models** - Llama, Mistral, Phi, Gemma, Qwen, DeepSeek families
3. **Compatibility checking** - Shows only models that will run well
4. **One-click model downloads** - Direct integration with Ollama
5. **Performance indicators** - Color-coded badges (🟢🟡🟠🔴)
6. **Conversation persistence** - SQLite database for chat history
7. **Context-aware chat** - Maintains conversation context across messages
