# Development Guide

Setup, testing, and contributing guide for AI Assistant.

## Prerequisites

**Operating System**: macOS (Apple Silicon or Intel)

**Required Software**:
- Python 3.8+ (3.10+ recommended)
- [Ollama](https://ollama.ai) installed and running
- Git

**Optional**:
- VS Code or PyCharm
- Postman or curl for API testing

## Quick Start

### 1. Clone Repository

```bash
git clone https://github.com/turmex/ai-assistant-public.git
cd ai-assistant-public
```

### 2. Install Ollama

```bash
# Visit https://ollama.ai and download installer
# Or use Homebrew:
brew install ollama

# Start Ollama service
ollama serve
```

### 3. Download a Model

```bash
# Recommended starter model (4.7GB)
ollama pull llama3.1:8b

# Or lightweight alternative (2GB)
ollama pull llama3.2:3b
```

### 4. Setup Backend

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit .env if needed (defaults work for local development)
```

### 5. Initialize Database

```bash
# Database is auto-created on first run
python3 -c "from database import init_db; init_db()"
```

### 6. Start Backend Server

```bash
# Development mode (auto-reload on code changes)
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Or use the convenience script
python3 main.py
```

**Verify**: http://localhost:8000/health should return `{"status": "healthy"}`

### 7. Open Frontend

**Option A: Direct File**
```bash
cd ../frontend
open index.html  # macOS
```

**Option B: Local Server** (avoids CORS issues)
```bash
cd frontend
python3 -m http.server 8080
# Open http://localhost:8080
```

## Project Structure

```
ai-assistant/
├── backend/
│   ├── main.py                      # FastAPI app
│   ├── database.py                  # SQLAlchemy models
│   ├── hardware_detector.py         # Mac hardware detection
│   ├── conversation_manager.py      # Chat state management
│   ├── requirements.txt             # Python dependencies
│   ├── .env.example                 # Environment template
│   ├── .env                         # Your local config (gitignored)
│   ├── venv/                        # Virtual environment (gitignored)
│   └── ai_assistant.db              # SQLite database (gitignored)
├── frontend/
│   └── index.html                   # Single-page app
├── docs/
│   ├── AI_QUICK_REF.md             # Token-efficient reference
│   ├── ARCHITECTURE.md             # System design
│   ├── API.md                      # Endpoint documentation
│   └── ...
├── README.md
├── TESTING_GUIDE.md
└── start.sh                        # Launch script
```

## Development Workflow

### Making Code Changes

1. **Create feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make changes** (see CODE_STANDARDS.md)

3. **Test locally**:
   ```bash
   # Run backend tests (when implemented)
   pytest backend/tests/

   # Manual testing via frontend
   ```

4. **Commit**:
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```

5. **Push and create PR**:
   ```bash
   git push origin feature/your-feature-name
   ```

### Adding a New Endpoint

**Example**: Add `GET /models/stats` to show model statistics

1. **Define request/response models** (main.py):
   ```python
   class ModelStats(BaseModel):
       total_models: int
       total_size_gb: float
       most_used: str
   ```

2. **Implement endpoint** (main.py):
   ```python
   @app.get("/models/stats", response_model=ModelStats)
   async def get_model_stats():
       # Implementation
       return ModelStats(
           total_models=5,
           total_size_gb=23.5,
           most_used="llama3.1:8b"
       )
   ```

3. **Update documentation** (docs/API.md)

4. **Test**:
   ```bash
   curl http://localhost:8000/models/stats
   ```

### Adding a Database Model

**Example**: Add `Agent` model for multi-agent feature

1. **Define model** (database.py):
   ```python
   class Agent(Base):
       __tablename__ = "agents"

       id = Column(Integer, primary_key=True, index=True)
       user_id = Column(Integer, ForeignKey("users.id"))
       name = Column(String, nullable=False)
       role = Column(String)  # coordinator, specialist, etc.
       created_at = Column(DateTime, default=datetime.utcnow)

       user = relationship("User", back_populates="agents")
   ```

2. **Add relationship to User** (database.py):
   ```python
   class User(Base):
       # Existing code...
       agents = relationship("Agent", back_populates="user")
   ```

3. **Recreate database** (or use Alembic migration):
   ```bash
   rm backend/ai_assistant.db
   python3 -c "from database import init_db; init_db()"
   ```

### Adding Hardware Detection for New Models

**Example**: Add GPT-4 model recommendation

1. **Update MODEL_CATALOG** (hardware_detector.py:44-101):
   ```python
   MODEL_CATALOG = [
       # Existing models...
       {
           "name": "gpt4all:7b",
           "display_name": "GPT4All 7B",
           "size_gb": 3.8,
           "quality": "high",
           "description": "Fast, good for general use"
       }
   ]
   ```

2. **Algorithm automatically handles** compatibility checking and performance scoring

3. **Test**:
   ```bash
   curl http://localhost:8000/hardware
   ```

## Testing

### Manual Testing

**Backend API**:
```bash
# Health check
curl http://localhost:8000/health

# List models
curl http://localhost:8000/models

# Send chat message
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello world"}'

# Get hardware info
curl http://localhost:8000/hardware
```

**Frontend**: Open in browser and click through UI

### Automated Testing (Future)

**Unit Tests** (backend/tests/):
```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run all tests
pytest

# Run specific test
pytest tests/test_conversation_manager.py

# With coverage
pytest --cov=backend --cov-report=html
```

**Integration Tests**:
```bash
# Test with real database
pytest tests/integration/

# Test with mock Ollama
pytest tests/integration/ --mock-ollama
```

**E2E Tests** (future):
```bash
# Install Playwright
npm install -D @playwright/test

# Run E2E tests
npx playwright test
```

See: TESTING_GUIDE.md for detailed test plan

## Common Tasks

### Reset Database

```bash
cd backend
rm ai_assistant.db
python3 -c "from database import init_db; init_db()"
```

### View Database Contents

```bash
cd backend
sqlite3 ai_assistant.db

# List tables
.tables

# Query conversations
SELECT * FROM conversations;

# Exit
.quit
```

### Check Ollama Status

```bash
# List downloaded models
ollama list

# Check if running
curl http://localhost:11434/api/tags

# Pull new model
ollama pull mistral:7b
```

### View Logs

**Backend**:
```bash
# Logs print to stdout (terminal)
# For production, redirect to file:
uvicorn main:app --log-config logging_config.yaml > app.log 2>&1
```

**Ollama**:
```bash
# macOS logs
tail -f ~/Library/Logs/ollama.log
```

### Environment Variables

Edit `backend/.env`:

```bash
# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
DEFAULT_LOCAL_MODEL=llama3.1

# Database
DATABASE_URL=sqlite:///./ai_assistant.db

# Server
HOST=0.0.0.0
PORT=8000
DEBUG=true

# OAuth (future)
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
SALESFORCE_CLIENT_ID=
SALESFORCE_CLIENT_SECRET=
```

## Troubleshooting

### Ollama Not Running

**Symptom**: `503 Could not connect to Ollama`

**Fix**:
```bash
# Check if running
curl http://localhost:11434/api/tags

# Start Ollama
ollama serve

# Or restart
pkill ollama && ollama serve
```

### Model Not Downloaded

**Symptom**: `Model not found` error

**Fix**:
```bash
# List available models
ollama list

# Pull missing model
ollama pull llama3.1:8b
```

### Database Locked

**Symptom**: `database is locked` error

**Fix**:
```bash
# Stop all backend processes
pkill -f "uvicorn main:app"

# Restart server
cd backend
uvicorn main:app --reload
```

### Frontend Not Connecting

**Symptom**: CORS errors or network failures

**Fix**:
1. Check backend is running: `curl http://localhost:8000/health`
2. Check frontend URL matches backend: `http://localhost:8000`
3. Clear browser cache and reload
4. Serve frontend via HTTP server (not `file://`)

### Import Errors

**Symptom**: `ModuleNotFoundError`

**Fix**:
```bash
# Ensure virtual environment is activated
source backend/venv/bin/activate

# Reinstall dependencies
pip install -r backend/requirements.txt
```

### Port Already in Use

**Symptom**: `Address already in use` on port 8000

**Fix**:
```bash
# Find process using port 8000
lsof -i :8000

# Kill process (use PID from above)
kill -9 <PID>

# Or use different port
uvicorn main:app --reload --port 8001
```

## Performance Optimization

### Backend

1. **Database Indexing**: Already optimized (see database.py)
2. **Connection Pooling**: Use PostgreSQL for production
3. **Caching**: Add Redis for conversation context
4. **Async Operations**: Already using async/await

### Frontend

1. **Minimize API Calls**: Cache hardware info, model list
2. **Lazy Loading**: Load conversation history on demand
3. **Debounce**: Throttle input events
4. **Virtual Scrolling**: For long chat histories

### Ollama

1. **GPU Acceleration**: Ensure Metal (Apple Silicon) or CUDA (NVIDIA) enabled
2. **Model Quantization**: Use smaller quantized models (q4, q5)
3. **Context Size**: Limit to 2048 tokens for faster inference
4. **Concurrent Requests**: Ollama handles 1 request at a time (queue others)

## Code Style

See: CODE_STANDARDS.md

**Quick Reference**:
- **Python**: PEP 8, type hints, docstrings
- **JavaScript**: camelCase, async/await, ES6+
- **Commits**: Conventional commits (`feat:`, `fix:`, `docs:`)

## Contributing

1. **Fork repository**
2. **Create feature branch**: `git checkout -b feature/amazing-feature`
3. **Follow CODE_STANDARDS.md**
4. **Add tests** (when test framework is set up)
5. **Update documentation**
6. **Commit**: `git commit -m "feat: add amazing feature"`
7. **Push**: `git push origin feature/amazing-feature`
8. **Open Pull Request**

### PR Checklist

- [ ] Code follows style guidelines (CODE_STANDARDS.md)
- [ ] Self-review completed
- [ ] Documentation updated (docs/)
- [ ] No breaking changes (or documented)
- [ ] Tested locally
- [ ] Commit messages are clear

## Deployment

### Local Production

1. **Use production-ready ASGI server**:
   ```bash
   pip install gunicorn
   gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
   ```

2. **Set production environment**:
   ```bash
   # .env
   DEBUG=false
   ```

3. **Setup as system service** (macOS launchd):
   ```bash
   # Create ~/Library/LaunchAgents/com.aiassistant.backend.plist
   # See deployment docs for details
   ```

### Cloud Deployment (Future)

- Docker containerization
- PostgreSQL database
- OAuth configuration
- Load balancing
- Monitoring (Prometheus, Grafana)

## Related Documentation

- **API.md**: Complete API reference
- **ARCHITECTURE.md**: System design
- **CODE_STANDARDS.md**: Coding conventions
- **TESTING_GUIDE.md**: Comprehensive test plan
- **INFRASTRUCTURE.md**: Logging, monitoring, error handling
