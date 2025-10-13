# API Documentation

Complete REST API reference for AI Assistant backend.

**Base URL**: `http://localhost:8000`
**Version**: 0.1.0 (MVP)
**Content-Type**: `application/json`

## Authentication

**Current**: None (single-user local app)
**Future**: OAuth 2.0 / JWT tokens

## Error Responses

All errors return JSON with `detail` field:

```json
{
  "detail": "Human-readable error message"
}
```

**Status Codes**:
- `400`: Invalid request
- `404`: Resource not found
- `500`: Internal server error
- `503`: Service unavailable (Ollama down)

## Endpoints

### GET /

Root endpoint with service information.

**Response**:
```json
{
  "name": "AI Assistant Backend",
  "version": "0.1.0",
  "status": "MVP - Local LLM Only",
  "features": [
    "Local LLM via Ollama",
    "Hardware detection",
    "Basic chat interface",
    "Conversation history"
  ],
  "coming_soon": [
    "MCP tool integration (Gmail, Calendar, Salesforce)",
    "Workflow creation",
    "OAuth authentication"
  ]
}
```

**Reference**: main.py:267-284

---

### GET /health

Health check for backend and dependencies.

**Response**:
```json
{
  "status": "healthy",
  "ollama_available": true,
  "ollama_url": "http://localhost:11434",
  "database_initialized": true,
  "hardware_detected": true,
  "recommended_model": "llama3.1:8b"
}
```

**Field Details**:
- `status`: `"healthy"` | `"degraded"` (Ollama down but DB working)
- `ollama_available`: Whether Ollama is reachable
- `hardware_detected`: Whether Mac hardware specs were detected successfully
- `recommended_model`: Best model for user's hardware (null if detection failed)

**Reference**: main.py:287-306

---

### GET /hardware

Detailed hardware information and all compatible models.

**Response**:
```json
{
  "chip_type": "Apple Silicon",
  "chip_model": "M2 Pro",
  "ram_gb": 16,
  "cpu_cores": 10,
  "compatible_models": [
    {
      "name": "llama3.1:8b",
      "display_name": "Llama 3.1 8B",
      "size_gb": 4.7,
      "expected_performance": "excellent",
      "speed_estimate": "Fast (10-15 tok/s)",
      "quality": "high",
      "recommended": true,
      "ram_required_gb": 10
    },
    {
      "name": "mistral:7b",
      "display_name": "Mistral 7B",
      "size_gb": 4.1,
      "expected_performance": "excellent",
      "speed_estimate": "Fast (10-15 tok/s)",
      "quality": "high",
      "recommended": false,
      "ram_required_gb": 9
    }
  ],
  "recommended_model": { /* same structure as compatible_models */ },
  "detection_successful": true,
  "error_message": null
}
```

**Field Details**:
- `chip_type`: `"Apple Silicon"` | `"Intel"` | `"Unknown"`
- `chip_model`: Specific chip (e.g., "M2 Pro", "Intel Core i7")
- `compatible_models`: All models that fit in RAM (sorted by performance)
- `recommended_model`: Best balance of speed/quality for hardware
- `expected_performance`: `"excellent"` | `"good"` | `"acceptable"` | `"slow"`

**Reference**: main.py:309-352

---

### GET /models

List models downloaded via Ollama.

**Response**:
```json
{
  "models": [
    {
      "name": "llama3.1:8b",
      "size": 4700000000,
      "modified_at": "2024-10-12T15:23:45.123456Z"
    },
    {
      "name": "mistral:7b",
      "size": 4100000000,
      "modified_at": "2024-10-11T10:15:30.654321Z"
    }
  ]
}
```

**Field Details**:
- `size`: Model size in bytes
- `modified_at`: Last modified timestamp (ISO 8601)

**Errors**:
- `503`: Cannot connect to Ollama

**Reference**: main.py:355-376

---

### GET /models/available

List all hardware-compatible models (not just downloaded).

**Response**:
```json
{
  "models": [
    {
      "name": "llama3.1:8b",
      "display_name": "Llama 3.1 8B",
      "size_gb": 4.7,
      "expected_performance": "excellent",
      "speed_estimate": "Fast (10-15 tok/s)",
      "quality": "high",
      "recommended": true,
      "ram_required_gb": 10
    }
  ]
}
```

**Use Case**: Populate model selector in frontend with download buttons

**Reference**: main.py:395-420

---

### GET /models/downloaded

List model names currently available locally.

**Response**:
```json
{
  "models": [
    "llama3.1:8b",
    "mistral:7b",
    "phi3:mini"
  ]
}
```

**Use Case**: Check which models are ready for inference

**Reference**: main.py:423-447

---

### POST /models/download

Initiate model download via Ollama.

**Request**:
```json
{
  "model_name": "llama3.1:8b"
}
```

**Response**:
```json
{
  "status": "download_started",
  "model": "llama3.1:8b",
  "message": "Download of llama3.1:8b has been initiated"
}
```

**Notes**:
- Download happens in background
- No progress tracking in MVP (use polling)
- Large models take 5-15 minutes depending on internet speed

**Errors**:
- `503`: Cannot connect to Ollama
- `500`: Ollama error (e.g., invalid model name)

**Reference**: main.py:379-392

---

### POST /chat

Send message and get AI response.

**Request**:
```json
{
  "message": "Explain quantum computing",
  "conversation_id": "uuid-string-optional",
  "model": "llama3.1:8b",
  "stream": false
}
```

**Field Details**:
- `message` (required): User's message text
- `conversation_id` (optional): UUID for continuing conversation (omit to start new)
- `model` (optional): Override recommended model
- `stream` (optional): Reserved for future streaming support (unused in MVP)

**Response**:
```json
{
  "response": "Quantum computing is a revolutionary approach...",
  "conversation_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "model_used": "llama3.1:8b",
  "tokens": 512
}
```

**Field Details**:
- `response`: Assistant's text response
- `conversation_id`: UUID for this conversation (use in subsequent requests)
- `model_used`: Actual model that generated response
- `tokens`: Token count (null if unavailable)

**Behavior**:
1. Create/retrieve conversation
2. Add user message to history
3. Get last 10 messages as context
4. Sanitize context for Ollama
5. Try 3 strategies (see ARCHITECTURE.md):
   - `/api/chat` with full context
   - `/api/chat` with last message only
   - `/api/generate` with flattened prompt
6. Store assistant response
7. Return to user

**Errors**:
- `404`: Conversation not found (if invalid conversation_id)
- `503`: Cannot connect to Ollama
- `502`: Empty response from model (all fallbacks failed)
- `500`: Internal error

**Reference**: main.py:450-546

---

### POST /conversations/new

Create a new conversation.

**Response**:
```json
{
  "conversation_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "created_at": "2024-10-13T12:34:56.789012"
}
```

**Reference**: main.py:549-562

---

### GET /conversations/{conversation_id}

Retrieve conversation history.

**Response**:
```json
{
  "conversation_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "messages": [
    {
      "role": "user",
      "content": "What is Python?",
      "timestamp": "2024-10-13T12:35:00.123456",
      "metadata": {}
    },
    {
      "role": "assistant",
      "content": "Python is a high-level programming language...",
      "timestamp": "2024-10-13T12:35:03.456789",
      "metadata": {
        "model": "llama3.1:8b",
        "tokens": 256
      }
    }
  ],
  "created_at": "2024-10-13T12:34:56.789012",
  "updated_at": "2024-10-13T12:35:03.456789"
}
```

**Errors**:
- `404`: Conversation not found

**Reference**: main.py:565-588

---

### DELETE /conversations/{conversation_id}

Delete a conversation.

**Response**:
```json
{
  "status": "deleted",
  "conversation_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

**Errors**:
- `404`: Conversation not found

**Reference**: main.py:591-612

---

### GET /conversations

List user's conversations (most recent first).

**Query Parameters**:
- `limit` (optional): Max conversations to return (default: 20)

**Example**: `GET /conversations?limit=10`

**Response**:
```json
{
  "conversations": [
    {
      "conversation_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "message_count": 8,
      "created_at": "2024-10-13T12:34:56.789012",
      "updated_at": "2024-10-13T15:23:45.123456"
    },
    {
      "conversation_id": "b2c3d4e5-f6g7-8901-bcde-f12345678901",
      "message_count": 3,
      "created_at": "2024-10-12T10:15:30.654321",
      "updated_at": "2024-10-12T10:18:42.987654"
    }
  ]
}
```

**Reference**: main.py:615-635

---

## Request Examples

### Starting a New Chat

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Write a Python function to calculate factorial"
  }'
```

Response:
```json
{
  "response": "Here's a recursive factorial function:\n\ndef factorial(n):\n    if n == 0 or n == 1:\n        return 1\n    return n * factorial(n - 1)",
  "conversation_id": "abc123...",
  "model_used": "llama3.1:8b",
  "tokens": 128
}
```

### Continuing a Conversation

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Now add error handling",
    "conversation_id": "abc123..."
  }'
```

### Downloading a Model

```bash
curl -X POST http://localhost:8000/models/download \
  -H "Content-Type: application/json" \
  -d '{"model_name": "mistral:7b"}'
```

### Checking Health

```bash
curl http://localhost:8000/health
```

---

## Rate Limiting

**Current**: None (local deployment)

**Future**:
- Per-user limits: 60 requests/minute
- Per-IP limits: 100 requests/minute
- Token-based throttling for expensive operations

---

## WebSocket Support

**Current**: Not implemented

**Future** (Phase 2):
- `/ws/chat`: Streaming chat responses
- `/ws/download`: Real-time download progress
- `/ws/workflow`: Workflow execution updates

---

## OpenAPI / Swagger

FastAPI automatically generates interactive documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

---

## Related Documentation

- **ARCHITECTURE.md**: System design and data flows
- **AI_QUICK_REF.md**: Quick reference for AI assistants
- **DEVELOPMENT.md**: Setup and testing guide
