# Changelog

All notable changes to AI Assistant will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned for v0.1.1 (2024-10-20)
- Comprehensive documentation (docs/ folder)
- Testing framework (pytest + pytest-asyncio)
- Code quality tools (black, ruff, mypy)

---

## [0.1.0] - 2024-10-13

### Added
- **FastAPI Backend** (650 LOC)
  - 12 REST API endpoints for chat, models, conversations, hardware info
  - Multi-fallback strategy for Ollama calls (/api/chat → /api/generate)
  - Context sanitization for LLM input
  - Health checks with graceful degradation
  - Request/response validation using Pydantic
  - Lifespan management (startup/shutdown hooks)

- **Database Layer** (322 LOC)
  - SQLAlchemy ORM with 5 models (User, ToolConnection, Workflow, WorkflowExecution, Conversation)
  - SQLite for MVP (single-user)
  - Future-ready schema for MCP tools and workflows
  - Session management with dependency injection
  - JSON columns for flexible message storage

- **Hardware Detection** (415 LOC)
  - Mac-specific detection (Apple Silicon vs Intel)
  - Chip model identification (M1/M2/M3 Pro/Max/Ultra)
  - RAM and CPU core count detection
  - 8-model catalog with metadata (size, quality, performance)
  - Smart model recommendations based on hardware
  - Performance estimation (excellent/good/acceptable/slow)
  - Singleton pattern for caching

- **Conversation Management** (390 LOC)
  - Conversation CRUD operations
  - Message persistence with metadata
  - LLM context formatting (last 10 messages)
  - Intent detection (keyword-based placeholder for MCP)
  - User conversation listing with pagination

- **Frontend** (543 LOC)
  - Single-page chat application
  - Tailwind CSS styling (dark theme)
  - Hardware information dashboard
  - Model selector with download capability
  - Chat interface with message history
  - Health status indicator
  - Example prompts sidebar
  - Toast notifications
  - Auto-scrolling chat container

- **API Endpoints**
  - `GET /` - Service information
  - `GET /health` - Health check (Ollama, DB, hardware)
  - `GET /hardware` - Hardware specs and compatible models
  - `GET /models` - List downloaded models
  - `GET /models/available` - List hardware-compatible models
  - `GET /models/downloaded` - List locally available models
  - `POST /models/download` - Download model via Ollama
  - `POST /chat` - Send message, get response
  - `GET /conversations` - List user conversations
  - `POST /conversations/new` - Create conversation
  - `GET /conversations/{id}` - Get conversation history
  - `DELETE /conversations/{id}` - Delete conversation

- **Error Handling**
  - Multi-tier fallback for Ollama communication
  - Graceful degradation (hardware detection, Ollama unavailable)
  - Comprehensive error logging with context
  - User-friendly error messages

- **Configuration**
  - Environment-based settings via .env file
  - Pydantic settings validation
  - OAuth placeholders (Google, Salesforce)

### Technical Details
- **Python**: 3.8+ (3.10+ recommended)
- **Framework**: FastAPI 0.109.0, Uvicorn 0.27.0
- **Database**: SQLAlchemy 2.0.25, SQLite
- **HTTP Client**: httpx 0.26.0 (async)
- **Validation**: Pydantic 2.5.3
- **Frontend**: Vanilla JavaScript, Tailwind CSS (CDN)
- **External Service**: Ollama (localhost:11434)

### Architecture Decisions
- ADR-001: Local-first architecture
- ADR-002: FastAPI over Flask/Django
- ADR-003: SQLite for MVP, PostgreSQL for production
- ADR-004: Single HTML file for frontend
- ADR-005: Hardcoded model catalog (revisit in Phase 1)
- ADR-006: JSON column for messages (migrate in Phase 5)
- ADR-007: Multi-fallback strategy for Ollama
- ADR-008: Tailwind CSS over custom CSS
- ADR-009: No streaming in MVP (add in Phase 2)
- ADR-010: Singleton pattern for hardware detector

### Known Limitations
- Single-user only (no authentication)
- No MCP tool integration
- No streaming responses
- Basic logging (no structured logs)
- Hardcoded model catalog (8 models)
- SQLite only (no multi-user scalability)
- Mac-only (macOS 11.0+ required)

### Installation
1. Install Ollama: `brew install ollama`
2. Download model: `ollama pull llama3.1:8b`
3. Install Python deps: `pip install -r requirements.txt`
4. Start backend: `uvicorn main:app --reload`
5. Open frontend: `open frontend/index.html`

### Repository
- **GitHub**: https://github.com/turmex/ai-assistant-public
- **License**: MIT (assumed, confirm with project)
- **Contributors**: 1 (project lead)

---

## Version History

| Version | Date | Status | Key Features |
|---------|------|--------|--------------|
| 0.1.0 | 2024-10-13 | ✅ Released | MVP - Local LLM chat with hardware detection |
| 0.1.1 | 2024-10-20 | 🔄 Planned | Documentation + Testing framework |
| 0.2.0 | 2024-10-27 | 📅 Planned | Logging + Monitoring infrastructure |
| 0.3.0 | 2024-11-10 | 📅 Planned | MCP Foundation + OAuth |
| 0.4.0 | 2024-11-17 | 📅 Planned | Gmail + Calendar integration |
| 0.5.0 | 2024-11-24 | 📅 Planned | Salesforce + Multi-tool workflows |
| 1.0.0 | 2025-01-05 | 📅 Planned | Production-ready hybrid local/cloud |
| 2.0.0 | 2025-02-09 | 📅 Planned | Multi-agent collaboration GA |

---

## Semantic Versioning Guide

**Format**: MAJOR.MINOR.PATCH

- **MAJOR**: Breaking changes (API contract changes, database schema changes)
- **MINOR**: New features (backward-compatible)
- **PATCH**: Bug fixes (backward-compatible)

**Examples**:
- `0.1.0 → 0.1.1`: Documentation added (patch: no code change)
- `0.1.1 → 0.2.0`: Logging infrastructure (minor: new feature)
- `0.5.0 → 1.0.0`: Production-ready, stable API (major: commitment)
- `1.0.0 → 2.0.0`: Multi-user, breaking auth changes (major)

---

## Release Notes Template

For future releases, use this template:

```markdown
## [X.Y.Z] - YYYY-MM-DD

### Added
- New features or capabilities

### Changed
- Changes to existing functionality

### Deprecated
- Features that will be removed in future

### Removed
- Features removed in this release

### Fixed
- Bug fixes

### Security
- Security fixes or improvements

### Breaking Changes
- Changes that break backward compatibility
- Migration guide

### Performance
- Performance improvements

### Documentation
- Documentation updates

### Internal
- Internal refactoring or tooling
```

---

## Migration Guides

### Upgrading to v0.1.1 (from v0.1.0)

No migration needed - documentation and testing only.

### Future: Upgrading to v0.3.0 (SQLite → PostgreSQL)

**Will be provided when released**. Expected migration:

1. Export SQLite data: `sqlite3 ai_assistant.db .dump > backup.sql`
2. Install PostgreSQL: `brew install postgresql`
3. Create database: `createdb ai_assistant`
4. Update .env: `DATABASE_URL=postgresql://localhost/ai_assistant`
5. Run migration script: `python migrate_to_postgres.py`
6. Verify data: Check conversation count matches

### Future: Upgrading to v2.0.0 (Multi-User)

**Will be provided when released**. Expected changes:

- Authentication required (OAuth or local accounts)
- All conversations scoped to user_id
- Shared conversations require permissions
- API requires Authorization header

---

## Deprecation Warnings

### v0.1.0
No deprecations (first release).

### Planned Deprecations
- **v0.3.0**: SQLite support (deprecated, removed in v0.5.0)
- **v0.5.0**: Single HTML frontend (deprecated, migrate to React in v1.0.0)
- **v1.0.0**: Keyword-based intent detection (removed, replaced with LLM classification)

---

## Support

**Bug Reports**: https://github.com/turmex/ai-assistant-public/issues
**Feature Requests**: https://github.com/turmex/ai-assistant-public/issues
**Security Issues**: security@[project-domain].com (or private GitHub issue)
**Discussions**: https://github.com/turmex/ai-assistant-public/discussions

---

## Links

- [ROADMAP.md](ROADMAP.md) - Planned features and timeline
- [ARCHITECTURE.md](ARCHITECTURE.md) - System design documentation
- [API.md](API.md) - API endpoint specifications
- [DECISIONS.md](DECISIONS.md) - Architecture Decision Records
- [DEVELOPMENT.md](DEVELOPMENT.md) - Setup and contributing guide

---

## Acknowledgments

- **Ollama**: Local LLM inference engine (https://ollama.ai)
- **FastAPI**: Modern async web framework (https://fastapi.tiangolo.com)
- **Tailwind CSS**: Utility-first CSS framework (https://tailwindcss.com)
- **SQLAlchemy**: Python SQL toolkit and ORM (https://www.sqlalchemy.org)
- **Contributors**: Thank you to all contributors (list will grow)

---

**Note**: This changelog started with v0.1.0 (MVP release). Pre-release development history was not tracked.
