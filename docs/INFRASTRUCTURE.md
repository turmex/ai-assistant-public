# Infrastructure Documentation

Production-grade logging, monitoring, error handling, and operational guidelines.

## Current State (MVP)

**Logging**: Basic `logging.basicConfig()` with INFO level
**Monitoring**: None (manual checks)
**Error Handling**: Exception catching with HTTP error codes
**Resource Management**: OS-level only (no app-level limits)

**This document** outlines current patterns and future improvements for production readiness.

---

## Logging

### Current Implementation

**Setup** (main.py:30-34):
```python
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("main")
```

**Log Levels Used**:
- `INFO`: Startup events, conversation created, model selected
- `WARNING`: Ollama degraded, fallback strategies triggered
- `ERROR`: Database failures, empty Ollama responses, connection errors

**Example logs**:
```
2024-10-13 12:34:56 - main - INFO - 🚀 Starting AI Assistant Backend...
2024-10-13 12:34:57 - main - INFO - ✓ Database initialized
2024-10-13 12:34:58 - main - INFO - ✓ Hardware detected: M2 Pro, 16GB RAM
2024-10-13 12:35:03 - main - WARNING - ⚠ Ollama responded but not OK (503)
2024-10-13 12:35:10 - main - ERROR - ✗ Chat endpoint error: Empty response
```

### Production Improvements Needed

#### 1. Structured Logging (JSON)

**Why**: Machine-parsable logs for aggregation tools (ELK, Splunk, CloudWatch)

**Implementation**:
```python
import json
import logging

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_data)

handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logger.addHandler(handler)
```

**Output**:
```json
{
  "timestamp": "2024-10-13T12:34:56.789Z",
  "level": "ERROR",
  "logger": "main",
  "message": "Failed to connect to Ollama",
  "module": "main",
  "function": "chat",
  "line": 536,
  "exception": "httpx.ConnectError: Connection refused"
}
```

#### 2. Request ID Tracking

**Why**: Trace requests across multiple log entries

**Implementation**:
```python
import uuid
from contextvars import ContextVar

request_id_var: ContextVar[str] = ContextVar("request_id", default="")

# Middleware
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request_id_var.set(request_id)
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response

# Logger adapter
class RequestIDAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        request_id = request_id_var.get()
        return f"[{request_id}] {msg}", kwargs

logger = RequestIDAdapter(logging.getLogger(__name__), {})
```

**Output**:
```
[a1b2c3d4] User sent message
[a1b2c3d4] Retrieved conversation context (10 messages)
[a1b2c3d4] Called Ollama /api/chat
[a1b2c3d4] Response received (512 tokens)
```

#### 3. Log Rotation

**Why**: Prevent disk space exhaustion

**Implementation** (using `RotatingFileHandler`):
```python
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler(
    "app.log",
    maxBytes=10 * 1024 * 1024,  # 10 MB
    backupCount=5  # Keep 5 old files
)
handler.setFormatter(JSONFormatter())
logger.addHandler(handler)
```

**Result**: Creates `app.log`, `app.log.1`, `app.log.2`, ... `app.log.5`

#### 4. Log Levels by Environment

**Development**: `DEBUG` (verbose)
**Production**: `INFO` (important events only)

```python
log_level = logging.DEBUG if settings.debug else logging.INFO
logging.basicConfig(level=log_level)
```

#### 5. Sensitive Data Redaction

**Never log**:
- OAuth tokens
- User passwords
- API keys
- Full conversation content (only log first 100 chars)

**Implementation**:
```python
def sanitize_for_logging(data: str) -> str:
    if len(data) > 100:
        return data[:100] + "... (truncated)"
    return data

logger.info(f"User message: {sanitize_for_logging(request.message)}")
```

---

## Monitoring

### Current State

**No automated monitoring** - rely on manual checks:
- Health endpoint: `GET /health`
- Ollama status: `curl http://localhost:11434/api/tags`
- Database file existence

### Metrics to Track

#### Application Metrics

| Metric | Purpose | Implementation |
|--------|---------|----------------|
| **Request rate** | Requests/second | Middleware counter |
| **Response time** | Latency percentiles (p50, p95, p99) | Middleware timer |
| **Error rate** | 5xx responses/total | Counter by status code |
| **Conversation length** | Avg messages per conversation | Database query |
| **Token usage** | Tokens/request | Parse from Ollama response |
| **Model usage** | Most popular models | Counter by model name |

#### System Metrics

| Metric | Purpose | Tool |
|--------|---------|------|
| **CPU usage** | Detect resource exhaustion | `psutil` |
| **Memory usage** | Detect memory leaks | `psutil` |
| **Disk usage** | Database growth | `psutil.disk_usage()` |
| **Ollama latency** | External service health | Request timer |

### Implementation: Prometheus + Grafana

**1. Add Prometheus exporter**:
```bash
pip install prometheus-fastapi-instrumentator
```

**2. Instrument FastAPI** (main.py):
```python
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI()
Instrumentator().instrument(app).expose(app)
```

**3. Access metrics**: `GET /metrics` (Prometheus format)

**4. Setup Grafana dashboard**:
- Import FastAPI dashboard template
- Add custom panels for conversation metrics

### Health Checks

**Current** (main.py:287-306):
- Checks Ollama reachability
- Verifies database initialized
- Reports hardware detection status

**Production improvements**:
```python
@app.get("/health/live")
async def liveness():
    """Kubernetes liveness probe - is the app alive?"""
    return {"status": "alive"}

@app.get("/health/ready")
async def readiness():
    """Kubernetes readiness probe - can accept traffic?"""
    ollama_ok = await check_ollama()
    db_ok = await check_database()

    if not (ollama_ok and db_ok):
        raise HTTPException(status_code=503, detail="Not ready")

    return {"status": "ready", "checks": {
        "ollama": ollama_ok,
        "database": db_ok
    }}
```

---

## Error Handling

### Current Pattern

**HTTP Exceptions** (main.py:450-546):
```python
try:
    # Business logic
    result = await process_chat(request)
    return ChatResponse(...)
except httpx.RequestError as e:
    logger.error(f"Failed to connect: {e}")
    raise HTTPException(status_code=503, detail="Ollama unavailable")
except HTTPException:
    raise  # Re-raise HTTP exceptions
except Exception as e:
    logger.error(f"Unexpected error: {e}", exc_info=True)
    raise HTTPException(status_code=500, detail=str(e))
```

**Response format**:
```json
{
  "detail": "Human-readable error message"
}
```

### Error Categories

#### 1. User Errors (4xx)

**400 Bad Request**: Invalid input
```python
if not request.message.strip():
    raise HTTPException(status_code=400, detail="Message cannot be empty")
```

**404 Not Found**: Resource doesn't exist
```python
conversation = conv_manager.get_conversation(id)
if not conversation:
    raise HTTPException(status_code=404, detail=f"Conversation {id} not found")
```

#### 2. Service Errors (5xx)

**500 Internal Server Error**: Unexpected exceptions
```python
except Exception as e:
    logger.error(f"Unexpected: {e}", exc_info=True)
    raise HTTPException(status_code=500, detail="Internal error")
```

**502 Bad Gateway**: Ollama returned invalid response
```python
if not result_text:
    logger.error("All fallbacks returned empty")
    raise HTTPException(status_code=502, detail="Empty response from model")
```

**503 Service Unavailable**: Ollama down
```python
except httpx.RequestError:
    raise HTTPException(status_code=503, detail="Could not connect to Ollama")
```

**504 Gateway Timeout**: Request timeout
```python
async with httpx.AsyncClient(timeout=120.0) as client:
    # If exceeds 120s, httpx raises TimeoutException
```

### Error Recovery Strategies

#### 1. Multi-Fallback (main.py:486-512)

**Strategy**: Try multiple approaches before failing
```
Try /api/chat with full context
  ↓ (fails)
Try /api/chat with last message
  ↓ (fails)
Try /api/generate with flattened prompt
  ↓ (fails)
Return 502 error
```

#### 2. Graceful Degradation

**Hardware detection failure**: Use safe default model
```python
if not hardware_info.detection_successful:
    logger.warning("Hardware detection failed, using fallback")
    # Returns llama3.2:3b (safe default)
```

**Ollama unavailable**: Return "degraded" status (not "down")
```python
status = "healthy" if ollama_ok else "degraded"
```

#### 3. Retry Logic (Future)

**Transient errors**: Retry with exponential backoff
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
async def call_ollama_with_retry(model: str, messages: List[Dict]):
    return await ollama_chat(client, model, messages)
```

### Error Monitoring

**Track error rates** by:
- Endpoint (e.g., `/chat` has more 503s than `/health`)
- Error type (connection errors vs timeout vs validation)
- Time of day (spikes during peak usage)

**Alerting** (future):
- >5% error rate: Warning
- >10% error rate: Critical
- Ollama down: Page on-call

---

## Resource Management

### Current State

**No app-level limits** - relies on OS limits:
- Memory: Limited by system RAM
- CPU: Limited by macOS scheduler
- Disk: Limited by filesystem

### Production Improvements

#### 1. Request Concurrency Limits

**Problem**: Too many concurrent Ollama requests → OOM

**Solution**: Semaphore to limit concurrent inferences
```python
from asyncio import Semaphore

ollama_semaphore = Semaphore(2)  # Max 2 concurrent requests

@app.post("/chat")
async def chat(request: ChatRequest):
    async with ollama_semaphore:
        # Only 2 requests can be here simultaneously
        result = await call_ollama(request)
    return result
```

#### 2. Context Size Limits

**Problem**: Very long conversations → slow inference, high memory

**Solution**: Limit context to last N messages
```python
MAX_CONTEXT_MESSAGES = 10  # Already implemented

context = conv_manager.get_context_for_llm(conversation_id, max_messages=MAX_CONTEXT_MESSAGES)
```

#### 3. Request Timeouts

**Current**: 120s for chat endpoint
**Production**: Dynamic based on model size

```python
timeout_map = {
    "llama3.2:1b": 30,   # Fast model
    "llama3.1:8b": 120,  # Medium model
    "codellama:13b": 300  # Slow model
}

timeout = timeout_map.get(model, 120)
async with httpx.AsyncClient(timeout=timeout) as client:
    ...
```

#### 4. Database Connection Pooling

**Current**: Single connection per request
**Production**: Connection pool

```python
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=5,       # 5 connections
    max_overflow=10,   # +10 if needed
    pool_timeout=30    # Wait 30s for connection
)
```

#### 5. Rate Limiting (Future)

**Per-user limits**: 60 requests/minute
**Per-IP limits**: 100 requests/minute

**Implementation**:
```bash
pip install slowapi
```

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/chat")
@limiter.limit("60/minute")
async def chat(request: Request):
    ...
```

---

## Observability

### Logging Best Practices

**Do**:
- Log at appropriate levels (DEBUG < INFO < WARNING < ERROR)
- Include context (user ID, conversation ID, model used)
- Log entry/exit of critical functions
- Log external service calls with latency

**Don't**:
- Log sensitive data (passwords, tokens, full messages)
- Log inside tight loops (creates log spam)
- Use `print()` statements (use logger)
- Log without context (e.g., just "Error")

### Example: Well-Instrumented Function

```python
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    """Send message and get AI response."""
    logger.info(
        f"Chat request received",
        extra={
            "conversation_id": request.conversation_id,
            "model": request.model,
            "message_length": len(request.message)
        }
    )

    start_time = time.time()

    try:
        # Business logic
        result = await process_chat(request, db)

        elapsed = time.time() - start_time
        logger.info(
            f"Chat completed successfully",
            extra={
                "conversation_id": result.conversation_id,
                "model_used": result.model_used,
                "tokens": result.tokens,
                "latency_ms": int(elapsed * 1000)
            }
        )

        return result

    except Exception as e:
        elapsed = time.time() - start_time
        logger.error(
            f"Chat failed: {e}",
            exc_info=True,
            extra={
                "conversation_id": request.conversation_id,
                "latency_ms": int(elapsed * 1000)
            }
        )
        raise
```

---

## Deployment Checklist

### Pre-Production

- [ ] Switch to JSON logging
- [ ] Add request ID tracking
- [ ] Setup log rotation
- [ ] Configure structured error responses
- [ ] Add Prometheus metrics
- [ ] Setup Grafana dashboards
- [ ] Configure alerting rules
- [ ] Add rate limiting
- [ ] Implement retry logic
- [ ] Add circuit breakers for Ollama
- [ ] Setup health check endpoints
- [ ] Test failure scenarios
- [ ] Document runbooks for common issues

### Production Monitoring

**Daily**:
- Check error rate dashboard
- Review critical log entries
- Verify Ollama uptime

**Weekly**:
- Review performance trends
- Check disk space growth
- Analyze popular models/features

**Monthly**:
- Review and rotate logs
- Update dependencies (security patches)
- Capacity planning

---

## Runbooks

### Issue: Ollama Not Responding

**Symptoms**: 503 errors, `/health` shows `ollama_available: false`

**Diagnosis**:
```bash
# Check if Ollama is running
ps aux | grep ollama

# Check Ollama logs
tail -f ~/Library/Logs/ollama.log

# Test API directly
curl http://localhost:11434/api/tags
```

**Resolution**:
```bash
# Restart Ollama
pkill ollama && ollama serve

# Verify fixed
curl http://localhost:8000/health
```

### Issue: Database Locked

**Symptoms**: `database is locked` errors in logs

**Diagnosis**:
```bash
# Check for multiple backend processes
ps aux | grep uvicorn

# Check database file
ls -lh backend/ai_assistant.db
lsof backend/ai_assistant.db  # Who has it open?
```

**Resolution**:
```bash
# Kill all backend processes
pkill -f "uvicorn main:app"

# Restart single instance
cd backend && uvicorn main:app --reload
```

### Issue: High Memory Usage

**Symptoms**: Slow responses, system lag

**Diagnosis**:
```bash
# Check memory usage
ps aux | grep python
top -pid <PID>

# Check active conversations
sqlite3 backend/ai_assistant.db "SELECT COUNT(*) FROM conversations;"
```

**Resolution**:
```bash
# Reduce context size (main.py)
MAX_CONTEXT_MESSAGES = 5  # Down from 10

# Clear old conversations
sqlite3 backend/ai_assistant.db "DELETE FROM conversations WHERE updated_at < datetime('now', '-30 days');"

# Restart backend
```

---

## Future Infrastructure

### Containerization (Docker)

**Dockerfile**:
```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**docker-compose.yml**:
```yaml
version: '3.8'
services:
  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/aiassistant
    depends_on:
      - db
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: aiassistant
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
```

### Kubernetes Deployment

**Features**:
- Auto-scaling based on CPU/memory
- Rolling updates with zero downtime
- Health checks (liveness/readiness probes)
- Config management (ConfigMaps, Secrets)

**Manifest** (simplified):
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ai-assistant
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: backend
        image: ai-assistant:latest
        ports:
        - containerPort: 8000
        livenessProbe:
          httpGet:
            path: /health/live
            port: 8000
        readinessProbe:
          httpGet:
            path: /health/ready
            port: 8000
```

---

## Related Documentation

- **ARCHITECTURE.md**: Error handling patterns in data flows
- **API.md**: Error response formats
- **DEVELOPMENT.md**: Troubleshooting common issues
- **CODE_STANDARDS.md**: Logging best practices
