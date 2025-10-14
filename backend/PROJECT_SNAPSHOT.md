# AI Assistant - Project Snapshot
Generated: 2025-10-14 03:40:51

## Overview
Local-first AI assistant with FastAPI backend, Ollama LLM integration, hardware detection, and conversation management. MVP focuses on chat with local LLM; future phases add MCP tool integration (Gmail, Calendar, Salesforce), workflow automation, and OAuth authentication.

## Architecture
**Stack**: FastAPI + SQLAlchemy + Ollama + httpx
**Database**: SQLite with 5 tables (users, conversations, tool_connections, workflows, workflow_executions)
**LLM**: Local Ollama models with automatic hardware-optimized selection
**Frontend**: Vanilla JS with fetch API (simple SPA at /frontend)

## Core Files

### conversation_manager.py
**Purpose**: Conversation management module for the AI Assistant.
**Lines**: 390
**Classes**: ConversationManager
**Functions**: get_conversation_manager, __init__, create_conversation
**Imports**: database

### database.py
**Purpose**: Database models and connection management for the AI Assistant.
**Lines**: 322
**Classes**: Settings, User, ToolConnection, Workflow, WorkflowExecution
**Functions**: init_db, get_db, get_or_create_user

### hardware_detector.py
**Purpose**: Hardware detection module for optimal Ollama model selection on macOS.
**Lines**: 415
**Classes**: ModelInfo, HardwareInfo, HardwareDetector
**Functions**: get_hardware_detector, __init__, recommended_model

### logger.py
**Purpose**: Workflow execution logging module.
**Lines**: 317
**Classes**: WorkflowLogger
**Functions**: get_workflow_logger, __init__, start_execution
**Imports**: database

### main.py
**Purpose**: FastAPI main application for the AI Assistant backend (compat-preserving, hardened).
**Lines**: 650
**Classes**: ChatRequest, ChatResponse, HealthResponse, ModelInfo, ModelsResponse
**Functions**: async lifespan, async ollama_ok, async ollama_chat, async ollama_generate, async root [endpoint], pick_model, parse_ollama_reply, sanitize_context
**Imports**: conversation_manager, database, hardware_detector

## API Endpoints
- `DELETE /conversations/{conversation_id}`
- `GET /`
- `GET /conversations`
- `GET /conversations/{conversation_id}`
- `GET /hardware`
- `GET /health`
- `GET /models`
- `GET /models/available`
- `GET /models/downloaded`
- `POST /chat`
- `POST /conversations/new`
- `POST /models/download`

## Database Models
- **User**: email, created_at
- **Conversation**: user_id, conversation_id, messages (JSON), timestamps
- **ToolConnection**: user_id, service_name, auth_data, is_connected
- **Workflow**: user_id, name, trigger (JSON), actions (JSON), is_active
- **WorkflowExecution**: workflow_id, status, results (JSON), tokens_used

## Key Dependencies
fastapi, fastapi.middleware.cors, httpx, pydantic, pydantic_settings, sqlalchemy, sqlalchemy.ext.declarative, sqlalchemy.orm, sqlalchemy.orm.attributes

## Dev Notes
- **Startup**: `python main.py` (runs on :8000, auto-reload in debug mode)
- **Config**: Environment vars via .env (ollama_base_url=http://localhost:11434, database_url, host, port)
- **Hardware Detection**: Detects Apple Silicon/Intel, RAM, cores → recommends optimal model from catalog
  - Model catalog: llama3.2 (1B/3B/11B), phi3:mini, mistral:7b, llama3.1:8b, gemma2:9b, codellama:13b
  - Returns ALL compatible models with performance ratings (excellent/good/acceptable/slow)
- **Chat Flow**: User msg → conversation_manager → sanitize context → ollama_chat (full ctx) → fallback to last msg → fallback to generate → store response
- **Robust Fallbacks**: 3-tier strategy ensures responses even when context issues occur
- **Context Sanitization**: Strictly validates messages for Ollama (role+content only, handles list/dict content)

## Stats
**Files**: 6 | **Total Lines**: 2120
