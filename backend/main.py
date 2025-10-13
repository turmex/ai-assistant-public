"""
FastAPI main application for the AI Assistant backend (compat-preserving, hardened).

- Preserves original response shapes/labels.
- Strictly sanitizes conversation context before sending to Ollama.
- Chat endpoint tries, in order:
    1) /api/chat with sanitized full context (non-streaming)
    2) /api/chat with only the latest user message (non-streaming)
    3) /api/generate with flattened prompt
  If all fail to produce text, returns 502 'Empty response from model' with breadcrumbs in logs.
"""

import logging
from contextlib import asynccontextmanager
from typing import List, Optional, Dict, Any, Tuple

import httpx
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from database import init_db, get_db, settings as db_settings
from hardware_detector import get_hardware_detector, HardwareInfo, ModelInfo as HWModelInfo
from conversation_manager import get_conversation_manager

# ----------------------------------------------------------------------------
# Logging
# ----------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("main")

# Centralized configuration from database module
settings = db_settings

# Global state
hardware_info: Optional[HardwareInfo] = None


# ----------------------------------------------------------------------------
# Lifespan
# ----------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    global hardware_info

    logger.info("🚀 Starting AI Assistant Backend...")

    # DB
    try:
        init_db()
        logger.info("✓ Database initialized")
    except Exception as e:
        logger.error(f"✗ Database initialization failed: {e}")
        raise

    # Hardware detection
    try:
        detector = get_hardware_detector()
        hardware_info = detector.detect()
        if hardware_info.detection_successful:
            logger.info(
                "✓ Hardware detected: %s, %sGB RAM",
                (hardware_info.chip_model or hardware_info.chip_type),
                hardware_info.ram_gb,
            )
            logger.info(
                "✓ Recommended model: %s (%s performance)",
                hardware_info.recommended_model.name,
                hardware_info.recommended_model.expected_performance,
            )
        else:
            logger.warning("⚠ Hardware detection failed: %s", hardware_info.error_message)
            logger.info("Using fallback model: %s", hardware_info.recommended_model.name)
    except Exception as e:
        logger.error("✗ Hardware detection error: %s", e)

    # Ollama availability check (non-fatal)
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.get(f"{settings.ollama_base_url}/api/tags")
            if r.status_code == 200:
                models = r.json().get("models", [])
                logger.info("✓ Ollama is running with %d models available", len(models))
            else:
                logger.warning("⚠ Ollama responded but not OK (%s)", r.status_code)
    except httpx.RequestError:
        logger.warning("⚠ Could not connect to Ollama at %s", settings.ollama_base_url)
    except Exception as e:
        logger.error("✗ Ollama check failed: %s", e)

    logger.info("✓ AI Assistant Backend is ready!")
    yield
    logger.info("Shutting down AI Assistant Backend...")


# ----------------------------------------------------------------------------
# App
# ----------------------------------------------------------------------------
app = FastAPI(
    title="AI Assistant Backend",
    description="Local-first AI assistant with Ollama LLM and MCP integration (future)",
    version="0.1.0 (MVP)",
    lifespan=lifespan,
)

# CORS (keep permissive for MVP; restrict in prod)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ----------------------------------------------------------------------------
# Schemas (preserve original names)
# ----------------------------------------------------------------------------
class ChatRequest(BaseModel):
    message: str = Field(..., description="User message")
    conversation_id: Optional[str] = Field(None, description="Conversation ID")
    model: Optional[str] = Field(None, description="Override model")
    stream: bool = Field(False, description="Streaming (unused in MVP)")


class ChatResponse(BaseModel):
    # ORIGINAL fields kept intact
    response: str = Field(..., description="Assistant response")
    conversation_id: str = Field(..., description="Conversation ID")
    model_used: str = Field(..., description="Model used")
    tokens: Optional[int] = Field(None, description="Token count, if available")


class HealthResponse(BaseModel):
    # ORIGINAL field names
    status: str
    ollama_available: bool
    ollama_url: str
    database_initialized: bool
    hardware_detected: bool
    recommended_model: Optional[str] = None


class ModelInfo(BaseModel):
    name: str
    size: Optional[int] = None
    modified_at: Optional[str] = None


class ModelsResponse(BaseModel):
    models: List[ModelInfo]


class ModelDownloadRequest(BaseModel):
    model_config = {"protected_namespaces": ()}
    model_name: str = Field(..., description="e.g. 'llama3.1:8b'")


# ----------------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------------
async def ollama_ok() -> bool:
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            r = await client.get(f"{settings.ollama_base_url}/api/tags")
            r.raise_for_status()
        return True
    except Exception:
        return False

def pick_model() -> str:
    if hardware_info and hardware_info.recommended_model:
        return hardware_info.recommended_model.name
    return settings.default_local_model

def parse_ollama_reply(payload: Dict[str, Any]) -> str:
    """Extract assistant text from various Ollama response shapes."""
    if not isinstance(payload, dict):
        return ""
    # Modern: { message: { role, content } }
    msg = payload.get("message")
    if isinstance(msg, dict):
        content = msg.get("content")
        if isinstance(content, str) and content.strip():
            return content
    # Older: { response: "..." }
    resp = payload.get("response")
    if isinstance(resp, str) and resp.strip():
        return resp
    # Fallbacks
    for key in ("content", "text", "answer"):
        val = payload.get(key)
        if isinstance(val, str) and val.strip():
            return val
    return ""

def sanitize_context(messages: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    """Return a strictly valid list[{role, content:str}] for Ollama /api/chat."""
    out: List[Dict[str, str]] = []
    for m in messages or []:
        role = str(m.get("role", "user")).lower()
        if role not in {"system", "user", "assistant"}:
            role = "user"
        content = m.get("content", "")
        # normalize content to string
        if isinstance(content, list):
            parts = []
            for c in content:
                if isinstance(c, dict):
                    if "text" in c and isinstance(c["text"], str):
                        parts.append(c["text"])
                    elif "content" in c and isinstance(c["content"], str):
                        parts.append(c["content"])
                    else:
                        parts.append(str(c))
                else:
                    parts.append(str(c))
            content = " ".join([p for p in parts if p]).strip()
        elif not isinstance(content, str):
            content = str(content)
        content = (content or "").strip()
        if not content:
            continue
        out.append({"role": role, "content": content})
    # ensure we have at least the last user message
    if not out:
        out = [{"role": "user", "content": "Hello"}]
    return out

def build_prompt_from_messages(messages: List[Dict[str, Any]], max_chars: int = 6000) -> str:
    """Flatten chat history into a single prompt for /api/generate fallback."""
    chunks = []
    for m in messages[-12:]:  # last 12 messages to keep it short
        role = m.get("role", "user")
        content = m.get("content", "")
        if isinstance(content, list):
            content = " ".join([c.get("text", "") if isinstance(c, dict) else str(c) for c in content])
        chunks.append(f"{role.upper()}: {content}".strip())
    text = "\n\n".join(chunks).strip()
    return text[-max_chars:] if len(text) > max_chars else text


async def ollama_chat(client: httpx.AsyncClient, model: str, messages: List[Dict[str, Any]]) -> Tuple[str, Dict[str, Any]]:
    body = {"model": model, "messages": messages, "stream": False}
    r = await client.post(f"{settings.ollama_base_url}/api/chat", json=body)
    r.raise_for_status()
    data = r.json()
    return parse_ollama_reply(data), data

async def ollama_generate(client: httpx.AsyncClient, model: str, prompt: str) -> Tuple[str, Dict[str, Any]]:
    body = {"model": model, "prompt": prompt, "stream": False}
    r = await client.post(f"{settings.ollama_base_url}/api/generate", json=body)
    r.raise_for_status()
    data = r.json()
    # generate returns {response: "..."}
    text = (data.get("response") or "").strip()
    return text, data


# ----------------------------------------------------------------------------
# Endpoints
# ----------------------------------------------------------------------------
@app.get("/")
async def root():
    return {
        "name": "AI Assistant Backend",
        "version": "0.1.0",
        "status": "MVP - Local LLM Only",
        "features": [
            "Local LLM via Ollama",
            "Hardware detection",
            "Basic chat interface",
            "Conversation history",
        ],
        "coming_soon": [
            "MCP tool integration (Gmail, Calendar, Salesforce)",
            "Workflow creation",
            "OAuth authentication",
        ],
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Return original HealthResponse shape with status='healthy' or 'degraded'."""
    global hardware_info
    ok = await ollama_ok()
    status = "healthy" if ok else "degraded"   # preserve original label

    # Convert ModelInfo to string (model name)
    recommended_model_name = None
    if hardware_info and hardware_info.recommended_model:
        recommended_model_name = hardware_info.recommended_model.name

    return HealthResponse(
        status=status,
        ollama_available=ok,
        ollama_url=settings.ollama_base_url,
        database_initialized=True,
        hardware_detected=bool(hardware_info and hardware_info.detection_successful),
        recommended_model=recommended_model_name,
    )


@app.get("/hardware")
async def get_hardware_info():
    """Get hardware information and ALL compatible models."""
    global hardware_info
    if hardware_info is None:
        detector = get_hardware_detector()
        hardware_info = detector.detect()

    # Convert ModelInfo dataclasses to dicts
    compatible_models_dict = [
        {
            "name": m.name,
            "display_name": m.display_name,
            "size_gb": m.size_gb,
            "expected_performance": m.expected_performance,
            "speed_estimate": m.speed_estimate,
            "quality": m.quality,
            "recommended": m.recommended,
            "ram_required_gb": m.ram_required_gb
        }
        for m in hardware_info.compatible_models
    ]

    recommended_model_dict = {
        "name": hardware_info.recommended_model.name,
        "display_name": hardware_info.recommended_model.display_name,
        "size_gb": hardware_info.recommended_model.size_gb,
        "expected_performance": hardware_info.recommended_model.expected_performance,
        "speed_estimate": hardware_info.recommended_model.speed_estimate,
        "quality": hardware_info.recommended_model.quality,
        "recommended": hardware_info.recommended_model.recommended,
        "ram_required_gb": hardware_info.recommended_model.ram_required_gb
    }

    return {
        "chip_type": hardware_info.chip_type,
        "chip_model": hardware_info.chip_model,
        "ram_gb": hardware_info.ram_gb,
        "cpu_cores": hardware_info.cpu_cores,
        "compatible_models": compatible_models_dict,
        "recommended_model": recommended_model_dict,
        "detection_successful": hardware_info.detection_successful,
        "error_message": hardware_info.error_message,
    }


@app.get("/models", response_model=ModelsResponse)
async def list_models():
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.get(f"{settings.ollama_base_url}/api/tags")
            r.raise_for_status()
            data = r.json()
        models = [
            ModelInfo(
                name=m.get("name"),
                size=m.get("size"),
                modified_at=m.get("modified_at"),
            )
            for m in data.get("models", [])
        ]
        return ModelsResponse(models=models)
    except httpx.RequestError as e:
        logger.error("Failed to connect to Ollama: %s", e)
        raise HTTPException(status_code=503, detail=f"Could not connect to Ollama at {settings.ollama_base_url}")
    except Exception as e:
        logger.error("Failed to list models: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/models/download")
async def download_model(request: ModelDownloadRequest, background_tasks: BackgroundTasks):
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            r = await client.post(f"{settings.ollama_base_url}/api/pull", json={"name": request.model_name})
            r.raise_for_status()
        logger.info("Started downloading model: %s", request.model_name)
        return {"status": "download_started", "model": request.model_name, "message": f"Download of {request.model_name} has been initiated"}
    except httpx.RequestError as e:
        logger.error("Failed to connect to Ollama: %s", e)
        raise HTTPException(status_code=503, detail=f"Could not connect to Ollama at {settings.ollama_base_url}")
    except Exception as e:
        logger.error("Failed to download model: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/models/available")
async def get_available_models():
    """
    Get ALL models that are compatible with the user's hardware.
    This returns models from the hardware detector, not just downloaded ones.
    """
    global hardware_info
    if hardware_info is None:
        detector = get_hardware_detector()
        hardware_info = detector.detect()

    compatible_models = [
        {
            "name": m.name,
            "display_name": m.display_name,
            "size_gb": m.size_gb,
            "expected_performance": m.expected_performance,
            "speed_estimate": m.speed_estimate,
            "quality": m.quality,
            "recommended": m.recommended,
            "ram_required_gb": m.ram_required_gb
        }
        for m in hardware_info.compatible_models
    ]

    return {"models": compatible_models}


@app.get("/models/downloaded")
async def get_downloaded_models():
    """
    Get list of models already downloaded via Ollama.
    Returns model names that are currently available locally.
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.get(f"{settings.ollama_base_url}/api/tags")
            r.raise_for_status()
            data = r.json()

        # Extract just the model names
        downloaded = [m.get("name") for m in data.get("models", []) if m.get("name")]

        return {"models": downloaded}
    except httpx.RequestError as e:
        logger.error("Failed to connect to Ollama: %s", e)
        raise HTTPException(
            status_code=503,
            detail=f"Could not connect to Ollama at {settings.ollama_base_url}"
        )
    except Exception as e:
        logger.error("Failed to list downloaded models: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    """Primary chat endpoint — preserves original response schema w/ multi-fallbacks."""
    global hardware_info
    try:
        # Conversation
        conv_manager = get_conversation_manager(db)

        if request.conversation_id:
            conv = conv_manager.get_conversation(request.conversation_id)
            if not conv:
                raise HTTPException(status_code=404, detail=f"Conversation {request.conversation_id} not found")
            conversation_id = request.conversation_id
        else:
            conv = conv_manager.create_conversation()
            conversation_id = conv.conversation_id

        # Add user message
        conv_manager.add_message(conversation_id=conversation_id, role="user", content=request.message)

        # Build & sanitize context
        raw_context = conv_manager.get_context_for_llm(conversation_id)
        ctx_full = sanitize_context(raw_context)

        # Model
        model_to_use = request.model or pick_model()
        logger.info("Using model: %s for conversation %s with %d messages in context",
                   model_to_use, conversation_id, len(ctx_full))
        logger.debug("Context for LLM: %s", ctx_full)

        # Initialize result variables
        result_text = None
        tokens_used = None

        async with httpx.AsyncClient(timeout=120.0) as client:
            # 1) /api/chat with full context
            try:
                text, raw = await ollama_chat(client, model_to_use, ctx_full)
                if text:
                    result_text = text
                    tokens_used = raw.get("eval_count") or raw.get("eval_count_total")
                    logger.info("Received response from Ollama (full context): %s...", text[:100])
                else:
                    raise ValueError("empty")
            except Exception as e1:
                logger.warning("Chat with full context returned empty (%s). Retrying with last user message only.", e1)
                # 2) /api/chat with only latest user message
                last_user = next((m for m in reversed(ctx_full) if m["role"] == "user"), None) or {"role": "user", "content": request.message}
                try:
                    text2, raw2 = await ollama_chat(client, model_to_use, [last_user])
                    if text2:
                        result_text = text2
                        tokens_used = raw2.get("eval_count") or raw2.get("eval_count_total")
                    else:
                        raise ValueError("empty2")
                except Exception as e2:
                    logger.warning("Chat with last user message returned empty (%s). Falling back to /api/generate.", e2)
                    # 3) /api/generate with flattened prompt
                    prompt = build_prompt_from_messages(ctx_full)
                    text3, raw3 = await ollama_generate(client, model_to_use, prompt)
                    result_text = text3
                    tokens_used = raw3.get("eval_count") or raw3.get("total_tokens")

        if not result_text:
            logger.error("All chat fallbacks returned empty content. Sanitized ctx sample: %s", ctx_full[-2:] if len(ctx_full)>1 else ctx_full)
            raise HTTPException(status_code=502, detail="Empty response from model")

        # Store assistant reply
        conv_manager.add_message(
            conversation_id=conversation_id,
            role="assistant",
            content=result_text,
            metadata={"model": model_to_use, "tokens": tokens_used},
        )

        logger.info("Chat completed for conversation %s using %s", conversation_id, model_to_use)

        # Preserve original response fields
        return ChatResponse(
            response=result_text,
            conversation_id=conversation_id,
            model_used=model_to_use,
            tokens=tokens_used,
        )

    except httpx.RequestError as e:
        logger.error("Failed to connect to Ollama: %s", e)
        raise HTTPException(status_code=503, detail=f"Could not connect to Ollama at {settings.ollama_base_url}. Make sure Ollama is running.")
    except httpx.HTTPStatusError as e:
        logger.error("Ollama returned error: %s", e)
        detail = e.response.text if hasattr(e.response, "text") else str(e)
        raise HTTPException(status_code=e.response.status_code, detail=f"Ollama error: {detail}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Chat endpoint error: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/conversations/new")
async def create_new_conversation(db: Session = Depends(get_db)):
    """Create a new conversation and return its ID."""
    try:
        conv_manager = get_conversation_manager(db)
        conversation = conv_manager.create_conversation()

        return {
            "conversation_id": conversation.conversation_id,
            "created_at": conversation.created_at.isoformat()
        }
    except Exception as e:
        logger.error("Failed to create conversation: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/conversations/{conversation_id}")
async def get_conversation(conversation_id: str, db: Session = Depends(get_db)):
    """Get conversation history by ID."""
    try:
        conv_manager = get_conversation_manager(db)
        conversation = conv_manager.get_conversation(conversation_id)

        if not conversation:
            raise HTTPException(
                status_code=404,
                detail=f"Conversation {conversation_id} not found"
            )

        return {
            "conversation_id": conversation.conversation_id,
            "messages": conversation.messages or [],
            "created_at": conversation.created_at.isoformat(),
            "updated_at": conversation.updated_at.isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get conversation: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str, db: Session = Depends(get_db)):
    """Delete a conversation by ID."""
    try:
        conv_manager = get_conversation_manager(db)
        success = conv_manager.delete_conversation(conversation_id)

        if not success:
            raise HTTPException(
                status_code=404,
                detail=f"Conversation {conversation_id} not found"
            )

        return {
            "status": "deleted",
            "conversation_id": conversation_id
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to delete conversation: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/conversations")
async def list_conversations(limit: int = 20, db: Session = Depends(get_db)):
    """List all conversations for the user."""
    try:
        conv_manager = get_conversation_manager(db)
        conversations = conv_manager.get_user_conversations(limit=limit)

        return {
            "conversations": [
                {
                    "conversation_id": conv.conversation_id,
                    "message_count": len(conv.messages) if conv.messages else 0,
                    "created_at": conv.created_at.isoformat(),
                    "updated_at": conv.updated_at.isoformat()
                }
                for conv in conversations
            ]
        }
    except Exception as e:
        logger.error("Failed to list conversations: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ----------------------------------------------------------------------------
# Entrypoint
# ----------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info",
    )
