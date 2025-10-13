# Code Standards

Coding conventions, style guide, and best practices for AI Assistant.

## Python (Backend)

### Style Guide

Follow **PEP 8** with these specifics:

- **Line length**: 100 characters (not 79)
- **Indentation**: 4 spaces (no tabs)
- **Quotes**: Double quotes `"` for strings
- **Imports**: Grouped and sorted (stdlib → third-party → local)

### Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Variables | snake_case | `conversation_id`, `model_name` |
| Functions | snake_case | `get_hardware_info()`, `sanitize_context()` |
| Classes | PascalCase | `HardwareDetector`, `ConversationManager` |
| Constants | UPPER_SNAKE_CASE | `MODEL_CATALOG`, `DEFAULT_MODEL` |
| Private vars | _leading_underscore | `_detector_instance`, `_calculate_performance()` |
| Database tables | snake_case (plural) | `users`, `conversations`, `tool_connections` |
| Pydantic models | PascalCase | `ChatRequest`, `HealthResponse` |

### Type Hints

**Required** for all function signatures:

```python
# Good
def get_conversation(conversation_id: str) -> Optional[Conversation]:
    pass

def add_message(
    conversation_id: str,
    role: str,
    content: str,
    metadata: Optional[Dict[str, Any]] = None
) -> None:
    pass

# Bad (missing type hints)
def get_conversation(conversation_id):
    pass
```

**Use**:
- `Optional[T]` instead of `T | None` (for Python 3.8 compatibility)
- `List`, `Dict`, `Tuple` from `typing` module
- `Any` sparingly (document why it's needed)

### Docstrings

**Required** for:
- All public functions/methods
- All classes
- Complex private functions

**Format**: Google-style docstrings

```python
def create_conversation(user_id: Optional[int] = None) -> Conversation:
    """
    Create a new conversation.

    Args:
        user_id: User ID (optional, will create/fetch default user if not provided)

    Returns:
        Conversation: The created conversation record

    Raises:
        DatabaseError: If database operation fails
    """
    pass
```

**Module-level docstring** (file header):

```python
"""
Conversation management module for the AI Assistant.

This module manages conversation state, detects user intent, stores conversation
history in the database, and provides context to the LLM. This is the MVP
implementation that will be expanded in Week 2-3 to include MCP tool detection
and advanced intent recognition.
"""
```

### Function Structure

**Order**:
1. Docstring
2. Input validation
3. Business logic
4. Error handling
5. Return value

**Example**:

```python
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    """Send message and get AI response."""
    # Validation
    if not request.message or not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    # Business logic
    try:
        conv_manager = get_conversation_manager(db)
        conversation_id = request.conversation_id or conv_manager.create_conversation().conversation_id
        # ... more logic ...
        return ChatResponse(response=result_text, conversation_id=conversation_id, ...)

    # Error handling
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat endpoint error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
```

### Error Handling

**Principles**:
1. **Catch specific exceptions** first, then broader ones
2. **Log errors** with context (user ID, conversation ID, etc.)
3. **Re-raise as HTTPException** for user-facing errors
4. **Never swallow exceptions** silently

```python
# Good
try:
    result = await ollama_chat(client, model, messages)
except httpx.TimeoutException as e:
    logger.error(f"Ollama timeout: {e}")
    raise HTTPException(status_code=504, detail="Request timed out")
except httpx.RequestError as e:
    logger.error(f"Ollama connection failed: {e}")
    raise HTTPException(status_code=503, detail="Service unavailable")
except Exception as e:
    logger.error(f"Unexpected error: {e}", exc_info=True)
    raise HTTPException(status_code=500, detail="Internal server error")

# Bad (too broad)
try:
    result = do_something()
except:
    pass  # Silently fails!
```

### Logging

**Levels**:
- `logger.debug()`: Verbose debugging (sanitized context, intermediate values)
- `logger.info()`: Important events (startup, conversation created, model selected)
- `logger.warning()`: Recoverable issues (Ollama degraded, fallback used)
- `logger.error()`: Errors requiring attention (database failure, empty response)

**Format**:

```python
# Good
logger.info(f"Created conversation {conversation_id} for user {user_id}")
logger.error(f"Failed to connect to Ollama: {e}", exc_info=True)

# Bad (not enough context)
logger.info("Conversation created")
logger.error("Error")
```

### Async/Await

**Rules**:
1. **Use `async def`** for all I/O-bound operations (HTTP, database)
2. **Use `await`** for async calls (don't forget!)
3. **Use `asyncio.gather()`** for concurrent operations

```python
# Good (concurrent)
async def load_data():
    hardware_info, models = await asyncio.gather(
        fetch_hardware(),
        fetch_models()
    )
    return hardware_info, models

# Bad (sequential when could be concurrent)
async def load_data():
    hardware_info = await fetch_hardware()
    models = await fetch_models()  # Waits for hardware first
    return hardware_info, models
```

### Database Operations

**Principles**:
1. **Always use sessions properly** (via `Depends(get_db)`)
2. **Commit after writes**, rollback on errors
3. **Use `flag_modified()`** for JSON column updates
4. **Close/cleanup automatically** (handled by dependency injection)

```python
# Good
def add_message(conversation_id: str, role: str, content: str):
    try:
        conversation = self.get_conversation(conversation_id)
        conversation.messages.append({"role": role, "content": content})
        flag_modified(conversation, "messages")  # Essential for JSON columns!
        self.db.commit()
    except Exception as e:
        self.db.rollback()
        raise

# Bad (missing flag_modified)
def add_message(conversation_id: str, role: str, content: str):
    conversation = self.get_conversation(conversation_id)
    conversation.messages.append({"role": role, "content": content})
    self.db.commit()  # Won't update JSON column!
```

---

## JavaScript (Frontend)

### Style Guide

- **Indentation**: 2 spaces
- **Quotes**: Single quotes `'` for strings
- **Semicolons**: Required
- **Line length**: 100 characters

### Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Variables | camelCase | `conversationId`, `modelName` |
| Functions | camelCase | `sendMessage()`, `updateModelInfo()` |
| Constants | UPPER_SNAKE_CASE | `API_URL`, `DEFAULT_TIMEOUT` |
| DOM IDs | camelCase | `messageInput`, `chatContainer` |
| CSS classes | kebab-case | `chat-bubble`, `model-selector` |

### Modern JavaScript

**Use ES6+**:
- Arrow functions: `const add = (a, b) => a + b`
- Template literals: `` `Hello ${name}` ``
- Destructuring: `const {response, model_used} = data`
- Async/await: `async function fetchData() { await ... }`
- Const/let (no var): `const API = '...'`, `let counter = 0`

### Async Operations

```javascript
// Good (async/await with error handling)
async function sendMessage(text) {
  try {
    const data = await fetchJSON(`${API}/chat`, {
      method: 'POST',
      body: JSON.stringify({message: text})
    });
    return data;
  } catch (e) {
    toast('Failed to send message: ' + e.message, 'error');
    throw e;
  }
}

// Bad (promise chains)
function sendMessage(text) {
  return fetch(`${API}/chat`, {...})
    .then(r => r.json())
    .then(data => data)
    .catch(e => console.error(e));
}
```

### DOM Manipulation

**Prefer**:
- `document.getElementById()` or `$('id')` helper
- `element.classList.add/remove()` over `element.className`
- `element.textContent` over `element.innerHTML` (XSS prevention)

```javascript
// Good
const btn = document.getElementById('sendBtn');
btn.classList.add('disabled');
btn.textContent = 'Sending...';

// Bad (XSS risk)
const btn = document.getElementById('sendBtn');
btn.className = 'btn disabled';
btn.innerHTML = userInput;  // Dangerous if userInput is untrusted!
```

### Comments

**Use sparingly** - code should be self-documenting

```javascript
// Good (necessary comment)
// Delay typing bubble removal for smooth UX (min 250ms)
const delay = Math.max(0, 250 - (Date.now() - shownAt));

// Bad (obvious comment)
// Set the text content
element.textContent = 'Hello';
```

---

## Commit Messages

### Format

Follow **Conventional Commits**:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Formatting (no code change)
- `refactor`: Code restructuring (no behavior change)
- `test`: Add/update tests
- `chore`: Maintenance (deps, build, etc.)

**Examples**:

```bash
feat(chat): add streaming response support

Implement WebSocket endpoint for streaming chat responses.
Backend uses SSE to stream from Ollama, frontend updates UI
in real-time.

Closes #123

---

fix(hardware): handle M3 chip detection

M3 chip model wasn't being parsed correctly from sysctl output.
Updated regex to match "M3", "M3 Pro", "M3 Max".

Fixes #456

---

docs: add API endpoint examples

Added curl examples for all endpoints in API.md

---

refactor(db): extract session management

Moved database session logic to separate module for reusability.
No functional changes.
```

### Rules

- **Subject line**: Max 72 characters, imperative mood ("add" not "added")
- **Body**: Wrap at 100 characters, explain "why" not "what"
- **Breaking changes**: Use `BREAKING CHANGE:` in footer

---

## File Organization

### Backend Module Structure

```python
# Imports (grouped and sorted)
import logging                          # Stdlib
from datetime import datetime
from typing import List, Optional

from fastapi import FastAPI, HTTPException  # Third-party
from sqlalchemy.orm import Session

from database import Conversation, get_db    # Local
from hardware_detector import get_hardware_detector

# Constants
DEFAULT_MODEL = "llama3.1:8b"
MAX_CONTEXT_MESSAGES = 10

# Module-level variables
logger = logging.getLogger(__name__)
_cache = {}

# Classes
class ConversationManager:
    pass

# Functions
def helper_function():
    pass

# Main execution
if __name__ == "__main__":
    main()
```

### Frontend Structure

```javascript
// Constants
const API = 'http://localhost:8000';
const DEFAULT_TIMEOUT = 20000;

// State
let conversationId = null;
let selectedModel = null;

// Utility functions
function toast(msg, type) { ... }
function scrollToBottom() { ... }

// API functions
async function fetchJSON(url, opts) { ... }
async function sendMessage(text) { ... }

// UI functions
function renderMessage(msg) { ... }
function updateModelInfo(model) { ... }

// Event handlers
function bind() {
  document.getElementById('sendBtn').addEventListener('click', ...);
}

// Initialization
(async function init() {
  await loadHardware();
  bind();
})();
```

---

## Testing Standards

### Unit Tests (when implemented)

**Naming**: `test_<function_name>_<scenario>.py`

```python
# tests/test_conversation_manager.py

def test_create_conversation_success(db_session):
    """Test successful conversation creation."""
    manager = ConversationManager(db_session)
    conv = manager.create_conversation()
    assert conv.conversation_id is not None
    assert len(conv.messages) == 0

def test_add_message_to_nonexistent_conversation(db_session):
    """Test adding message to nonexistent conversation fails gracefully."""
    manager = ConversationManager(db_session)
    # Should not raise, but log error
    manager.add_message("fake-uuid", "user", "Hello")
```

**Structure**:
- Arrange: Setup test data
- Act: Execute function
- Assert: Verify results

---

## Security Standards

### Input Validation

**Always validate**:
- String lengths (max 10,000 chars for messages)
- JSON structure (use Pydantic models)
- File uploads (size, type)
- SQL injection (use ORM, never raw SQL)

```python
# Good
class ChatRequest(BaseModel):
    message: str = Field(..., max_length=10000)
    conversation_id: Optional[str] = Field(None, regex=r'^[a-f0-9-]{36}$')

# Bad (no validation)
@app.post("/chat")
async def chat(message: str):
    # Accepts any length, any content!
    pass
```

### Secrets Management

**Never commit**:
- API keys
- OAuth secrets
- Database passwords
- Encryption keys

**Use**:
- `.env` file (gitignored)
- Environment variables
- Secrets manager (AWS Secrets Manager, etc.)

```python
# Good
settings = Settings()  # Loads from .env
client_secret = settings.google_client_secret

# Bad
client_secret = "abc123secret"  # Hardcoded!
```

---

## Documentation Standards

**Every PR should update**:
- **docs/API.md** if endpoints changed
- **docs/ARCHITECTURE.md** if design changed
- **README.md** if setup changed
- **docs/CHANGELOG.md** with version bump

**Docstrings required**:
- All public functions
- All classes
- Complex logic blocks

---

## Performance Guidelines

### Backend

- **Use async** for I/O operations
- **Limit context size** to 10 messages
- **Index database queries** (already done)
- **Cache static data** (hardware info, model catalog)

### Frontend

- **Debounce input** (e.g., search)
- **Throttle scroll events**
- **Lazy load** conversation history
- **Cache API responses** when possible

---

## Related Documentation

- **ARCHITECTURE.md**: System design patterns
- **API.md**: Endpoint specifications
- **DEVELOPMENT.md**: Setup and workflow
- **INFRASTRUCTURE.md**: Logging and monitoring best practices
