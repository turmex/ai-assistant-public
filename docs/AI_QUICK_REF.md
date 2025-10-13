# AI Quick Reference - ai-assistant-public

## Project
Local-first AI assistant | FastAPI + Ollama | Mac hardware-optimized | ~1500 LOC

## Stack
Backend: FastAPI 0.109, SQLAlchemy 2.0, SQLite | Frontend: HTML, Tailwind CSS, vanilla JS | LLM: Ollama (localhost:11434)

## Files
| File | Purpose | LOC | Key Dependencies |
|------|---------|-----|------------------|
| backend/main.py | REST API, 12 endpoints, chat orchestration | 650 | FastAPI, httpx, database, hardware_detector |
| backend/database.py | 5 SQLAlchemy models, session mgmt | 322 | SQLAlchemy, Pydantic |
| backend/hardware_detector.py | Mac HW detection, model recommendations | 415 | platform, subprocess |
| backend/conversation_manager.py | Chat state, history, intent detection | 390 | database, SQLAlchemy |
| frontend/index.html | Single-page chat UI | 543 | Tailwind CDN |
| backend/requirements.txt | Python deps | 12 | - |

## Architecture
```
User → index.html → FastAPI (main.py) ─→ Ollama (/api/chat, /api/generate)
                         ↓
                    ConversationManager → SQLite (conversations, messages)
                         ↓
                    HardwareDetector → Model recommendations
```

## Database Schema
- **User**: Multi-user ready (MVP: single default user)
- **ToolConnection**: OAuth tokens for MCP tools (future)
- **Workflow**: Automation definitions (future)
- **WorkflowExecution**: Execution logs (future)
- **Conversation**: Chat history (JSON messages column)

## API Endpoints
| Endpoint | Method | Purpose |
|----------|--------|---------|
| /health | GET | Status check (Ollama, DB) |
| /hardware | GET | System specs + compatible models |
| /models | GET | Ollama downloaded models |
| /models/available | GET | Hardware-compatible models |
| /models/downloaded | GET | Locally available models |
| /models/download | POST | Pull model via Ollama |
| /chat | POST | Send message, get response |
| /conversations | GET | List user conversations |
| /conversations/new | POST | Create conversation |
| /conversations/{id} | GET | Get conversation history |
| /conversations/{id} | DELETE | Delete conversation |

## Key Functions
| Task | Location | Function/Pattern |
|------|----------|------------------|
| Add REST endpoint | main.py:267+ | `@app.get/post(path)` |
| Modify DB schema | database.py:79-265 | Update Base models, run init_db() |
| Change HW detection | hardware_detector.py:128-198 | `HardwareDetector.detect()` |
| Update model catalog | hardware_detector.py:44-101 | Modify MODEL_CATALOG list |
| Add conversation logic | conversation_manager.py | ConversationManager methods |
| UI changes | frontend/index.html | Direct HTML/JS/CSS edits |

## Design Patterns
- **Singleton**: HardwareDetector (hardware_detector.py:409-414)
- **Factory**: get_conversation_manager(db) (conversation_manager.py:379)
- **Dependency Injection**: FastAPI Depends(get_db) for sessions
- **Multi-fallback**: Chat tries /api/chat → last msg only → /api/generate (main.py:486-512)
- **Repository**: ConversationManager abstracts DB operations

## Model Recommendations
Algorithm: Filter by RAM (2x model size) → Sort by performance/quality/size → Mark best as recommended
8 models in catalog: llama3.2:1b (1.3GB) → codellama:13b (7.4GB)

## Common Operations
**Start server**: `cd backend && uvicorn main:app --reload`
**Add model**: Update MODEL_CATALOG in hardware_detector.py
**New endpoint**: Add to main.py, update docs/API.md
**Schema change**: Edit database.py models, consider migration

## Environment Config
`.env` variables: OLLAMA_BASE_URL, DATABASE_URL, HOST, PORT, DEBUG, OAuth credentials (unused in MVP)

## Future Roadmap
- MCP tool integration (Gmail, Calendar, Salesforce)
- Multi-agent collaboration
- Cloud LLM routing (Claude/GPT via user API keys)
- Workflow automation
- WebSocket for streaming responses

## Constraints
- Single-user local app (no auth in MVP)
- Mac-focused (Apple Silicon/Intel detection)
- Privacy-first (local Ollama models)
- SQLite (no scaling needed for local use)
- No rate limiting (local inference)

## Known Issues
- Model catalog hardcoded (need dynamic Ollama registry fetch)
- No Alembic migrations configured
- logger.py exists but unused
- Model downloads poll instead of WebSocket progress
- No token/context size limits enforced
