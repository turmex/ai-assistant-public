# Product Roadmap

Feature timeline and development phases for AI Assistant.

## Vision

Build a **local-first, privacy-focused AI assistant** that runs on your Mac, integrates with your tools (Gmail, Calendar, Salesforce), and enables **multi-agent collaboration** within organizations—all while keeping your data on your hardware and your API keys in your control.

**Core Principles**:
1. **Local-First**: Primary inference runs on user's Mac (Ollama)
2. **Privacy**: No data sent to third parties without explicit user control
3. **Hardware-Aware**: Intelligent model selection based on Mac specs
4. **Extensible**: Easy integration of new MCP tools
5. **Multi-Agent Ready**: Foundation for organizational collaboration

---

## Current State (v0.1.0 - MVP)

**Status**: ✅ Production-ready for single-user local deployment

**Features**:
- ✅ Local LLM inference via Ollama
- ✅ Mac hardware detection (Apple Silicon/Intel)
- ✅ Smart model recommendations (8 models)
- ✅ Model download management
- ✅ Chat interface with conversation history
- ✅ SQLite persistence
- ✅ REST API (12 endpoints)
- ✅ Single-page frontend (Tailwind CSS)

**Lines of Code**: ~1,500
**Files**: 6 backend, 1 frontend

**Known Limitations**:
- Single-user only (no authentication)
- No MCP tool integration
- Hardcoded model catalog
- No streaming responses
- Basic logging (no structured logs)
- SQLite only (no multi-user scalability)

---

## Phase 1: Infrastructure Foundation (Week 1-2)

**Goal**: Establish production-grade infrastructure patterns before adding features

**Rationale**: Every future feature will use these systems. Build them correctly once.

### Week 1: Documentation & Testing

**Documentation** (COMPLETED ✅):
- [x] AI_QUICK_REF.md - Token-efficient reference
- [x] ARCHITECTURE.md - System design with diagrams
- [x] API.md - Endpoint specifications
- [x] DEVELOPMENT.md - Setup and contributing guide
- [x] CODE_STANDARDS.md - Coding conventions
- [x] DEPENDENCIES.md - Dependency graph and rationale
- [x] INFRASTRUCTURE.md - Logging, monitoring, error handling
- [x] ROADMAP.md - This document
- [x] DECISIONS.md - Architecture Decision Records
- [x] CHANGELOG.md - Version history

**Testing Framework**:
- [ ] Setup pytest + pytest-asyncio
- [ ] Unit tests for conversation_manager.py (80% coverage)
- [ ] Unit tests for hardware_detector.py (80% coverage)
- [ ] Integration tests for API endpoints
- [ ] Mock Ollama for testing
- [ ] CI/CD pipeline (GitHub Actions)

**Code Quality**:
- [ ] Add `black` (code formatting)
- [ ] Add `ruff` (linting)
- [ ] Add `mypy` (type checking)
- [ ] Pre-commit hooks

**Deliverable**: v0.1.1 - Fully documented and tested MVP

### Week 2: Logging & Monitoring

**Structured Logging**:
- [ ] JSON log format
- [ ] Request ID tracking (middleware)
- [ ] Log rotation (RotatingFileHandler)
- [ ] Sensitive data redaction
- [ ] Environment-based log levels

**Monitoring**:
- [ ] Prometheus exporter (prometheus-fastapi-instrumentator)
- [ ] Metrics: request rate, latency, error rate, token usage
- [ ] Grafana dashboard templates
- [ ] Health check improvements (liveness/readiness)

**Error Handling**:
- [ ] Retry logic with exponential backoff (tenacity)
- [ ] Circuit breaker for Ollama calls
- [ ] Better error messages (user-friendly)

**Resource Management**:
- [ ] Request concurrency limits (Semaphore)
- [ ] Database connection pooling
- [ ] Dynamic timeouts based on model size

**Deliverable**: v0.2.0 - Production-ready infrastructure

---

## Phase 2: MCP Tool Integration (Week 3-5)

**Goal**: Enable assistant to interact with user's tools (Gmail, Calendar, Salesforce)

### Week 3: MCP Foundation

**OAuth Framework**:
- [ ] Google OAuth 2.0 flow (Gmail + Calendar)
- [ ] Salesforce OAuth flow
- [ ] Token encryption using cryptography (Fernet)
- [ ] Token refresh logic
- [ ] ToolConnection CRUD endpoints

**MCP Client**:
- [ ] Install MCP Python SDK
- [ ] Spawn MCP server processes
- [ ] Standardized tool call interface
- [ ] Tool response parsing

**Database**:
- [ ] Migrate to PostgreSQL (multi-user ready)
- [ ] Setup Alembic migrations
- [ ] Migrate existing SQLite data

**Deliverable**: v0.3.0 - OAuth + MCP foundation

### Week 4: Gmail & Calendar Integration

**Gmail MCP Server**:
- [ ] Read emails (list, search, get)
- [ ] Send emails (compose, reply)
- [ ] Draft management
- [ ] Label/filter operations

**Calendar MCP Server**:
- [ ] List events
- [ ] Create events
- [ ] Update/delete events
- [ ] Find available time slots

**Intent Detection**:
- [ ] Replace keyword-based detection with LLM classification
- [ ] Train on examples ("send email to..." → gmail.send)
- [ ] Confidence thresholds
- [ ] Ambiguity handling ("Did you mean...?")

**Frontend**:
- [ ] Tool connection UI (OAuth buttons)
- [ ] Tool status indicators
- [ ] Tool response formatting

**Deliverable**: v0.4.0 - Gmail + Calendar working

### Week 5: Salesforce Integration

**Salesforce MCP Server**:
- [ ] Query records (SOQL)
- [ ] Create/update records (Leads, Opportunities, Accounts)
- [ ] Custom object support
- [ ] Report generation

**Multi-Tool Workflows**:
- [ ] Chain tool calls ("Check calendar, then schedule meeting")
- [ ] Error handling across tools
- [ ] Transaction rollback (if one tool fails, undo others)

**Testing**:
- [ ] Integration tests with mock MCP servers
- [ ] E2E tests with real tool accounts (test environment)

**Deliverable**: v0.5.0 - Full MCP tool suite

---

## Phase 3: Workflow Automation (Week 6-8)

**Goal**: Let users create automated workflows combining LLM + tools

### Week 6: Workflow Engine

**Workflow Model** (database.py already has schema):
- [ ] Workflow CRUD API endpoints
- [ ] Trigger types: schedule, manual, event
- [ ] Action execution engine
- [ ] Variable substitution ("Use email from step 1")

**Workflow Execution**:
- [ ] Background task queue (use `schedule` for MVP)
- [ ] Execution history (WorkflowExecution table)
- [ ] Error handling and retries
- [ ] Partial execution recovery

**Deliverable**: v0.6.0 - Basic workflow engine

### Week 7: Workflow Builder UI

**Frontend**:
- [ ] Drag-and-drop workflow builder
- [ ] Node types: trigger, action, condition, LLM
- [ ] Visual flow editor (react-flow or similar)
- [ ] Test workflow feature

**Pre-built Templates**:
- [ ] "Daily email digest"
- [ ] "Meeting scheduler"
- [ ] "Lead follow-up automation"
- [ ] "Weekly report generation"

**Deliverable**: v0.7.0 - Workflow builder UI

### Week 8: Advanced Workflows

**Features**:
- [ ] Conditional logic (if/else)
- [ ] Loops (for each email...)
- [ ] Approval steps (require human confirmation)
- [ ] Error notifications (Slack, email)

**Workflow Marketplace** (stretch goal):
- [ ] Share workflows with community
- [ ] Import/export workflow JSON
- [ ] Workflow versioning

**Deliverable**: v0.8.0 - Advanced workflows

---

## Phase 4: Cloud LLM Routing (Week 9-10)

**Goal**: Route complex queries to cloud LLMs (Claude, GPT) using user's API keys

### Week 9: Cloud LLM Integration

**Supported Providers**:
- [ ] Anthropic (Claude 3.5 Sonnet, Opus)
- [ ] OpenAI (GPT-4, GPT-4 Turbo)
- [ ] Future: Google (Gemini), Cohere

**Smart Routing**:
- [ ] Query complexity analysis
- [ ] Route simple → local Ollama (free, fast, private)
- [ ] Route complex → cloud (paid, slow, more capable)
- [ ] User preferences (always local / always cloud / auto)

**Cost Tracking**:
- [ ] Track tokens used per provider
- [ ] Estimate costs ($ per request)
- [ ] Monthly spending dashboard
- [ ] Budget alerts

**Deliverable**: v0.9.0 - Hybrid local/cloud LLM

### Week 10: Model Selection UI

**Frontend**:
- [ ] Model selector: local vs cloud
- [ ] Cost calculator
- [ ] Model comparison table (speed, cost, quality)
- [ ] API key management UI

**Backend**:
- [ ] Secure API key storage (encrypted)
- [ ] Provider health checks
- [ ] Failover logic (if Claude down, use GPT)

**Deliverable**: v1.0.0 - Production-ready hybrid system

---

## Phase 5: Multi-Agent Collaboration (Week 11-14)

**Goal**: Enable multiple users in an organization to have agents that collaborate

### Week 11: Multi-User Foundation

**Authentication**:
- [ ] User registration and login
- [ ] JWT token-based auth
- [ ] Row-level security (users see only their data)
- [ ] Organization model (users belong to orgs)

**Authorization**:
- [ ] Permissions system (admin, member, guest)
- [ ] Shared conversations (within org)
- [ ] Private vs public workflows

**Deliverable**: v1.1.0 - Multi-user support

### Week 12: Agent System

**Agent Model**:
- [ ] Agent table (name, role, capabilities)
- [ ] Agent types: coordinator, specialist, researcher
- [ ] Agent-to-agent communication protocol

**Coordination Layer**:
- [ ] Task delegation (coordinator → specialists)
- [ ] Shared knowledge base (Redis cache)
- [ ] Agent discovery (who can help with X?)

**Deliverable**: v1.2.0 - Basic multi-agent system

### Week 13: Advanced Collaboration

**Features**:
- [ ] Conversation hand-offs (agent A → agent B)
- [ ] Parallel task execution (multiple agents work simultaneously)
- [ ] Consensus building (agents vote on decisions)
- [ ] Agent performance tracking (success rates)

**UI**:
- [ ] Agent directory
- [ ] Multi-agent conversation view
- [ ] Task assignment dashboard

**Deliverable**: v1.3.0 - Advanced collaboration

### Week 14: Polish & Launch

**Testing**:
- [ ] Multi-agent integration tests
- [ ] Load testing (100 concurrent users)
- [ ] Security audit

**Documentation**:
- [ ] Multi-agent guide
- [ ] Organization setup guide
- [ ] Admin documentation

**Deliverable**: v2.0.0 - Multi-agent collaboration GA

---

## Future Phases (Beyond 3 Months)

### Phase 6: Mobile & Web

- Native iOS/iPadOS app
- Web-based frontend (replace single HTML file)
- Cross-device sync
- Mobile push notifications

### Phase 7: Advanced Features

- Voice interface (Whisper for transcription)
- Document understanding (PDF, DOCX parsing)
- Image analysis (vision models)
- Code execution sandbox (for data analysis)

### Phase 8: Enterprise

- Self-hosted deployment guides
- SSO integration (SAML, Okta)
- Audit logging
- Compliance certifications (SOC 2, GDPR)

---

## Non-Goals

**Will NOT build**:
- Cloud-hosted service (always local-first)
- Proprietary LLM training (use existing models)
- Windows/Linux support in Phase 1 (Mac-first, then expand)
- Mobile-first design (desktop-first, then mobile)
- Consumer social features (not targeting consumer market)

---

## Success Metrics

### Phase 1-2 (Infrastructure + MCP)
- [ ] 100% test coverage for critical paths
- [ ] <500ms p95 API latency
- [ ] <1% error rate
- [ ] 10+ MCP tools integrated

### Phase 3-4 (Workflows + Cloud LLM)
- [ ] 50+ workflow templates
- [ ] <$0.10 average cost per complex query
- [ ] 90% user preference for hybrid routing

### Phase 5 (Multi-Agent)
- [ ] 5+ users per organization average
- [ ] 3+ agents per organization
- [ ] 50% of tasks completed via agent collaboration

---

## Release Schedule

| Version | Target Date | Status | Key Features |
|---------|-------------|--------|--------------|
| v0.1.0 | 2024-10-13 | ✅ Released | MVP - Local LLM chat |
| v0.1.1 | 2024-10-20 | 🔄 In Progress | Documentation + Testing |
| v0.2.0 | 2024-10-27 | 📅 Planned | Logging + Monitoring |
| v0.3.0 | 2024-11-10 | 📅 Planned | MCP Foundation + OAuth |
| v0.4.0 | 2024-11-17 | 📅 Planned | Gmail + Calendar |
| v0.5.0 | 2024-11-24 | 📅 Planned | Salesforce + Multi-tool |
| v0.6.0 | 2024-12-08 | 📅 Planned | Workflow Engine |
| v0.7.0 | 2024-12-15 | 📅 Planned | Workflow Builder UI |
| v0.8.0 | 2024-12-22 | 📅 Planned | Advanced Workflows |
| v0.9.0 | 2024-12-29 | 📅 Planned | Cloud LLM Routing |
| v1.0.0 | 2025-01-05 | 📅 Planned | Production-ready hybrid |
| v1.1.0 | 2025-01-19 | 📅 Planned | Multi-user |
| v1.2.0 | 2025-01-26 | 📅 Planned | Basic multi-agent |
| v1.3.0 | 2025-02-02 | 📅 Planned | Advanced collaboration |
| v2.0.0 | 2025-02-09 | 📅 Planned | Multi-agent GA |

**Release Cadence**: Weekly releases (Fridays)

---

## Contributing to Roadmap

**Suggest features**: Open GitHub issue with label `enhancement`

**Vote on features**: 👍 issues you want to see prioritized

**Propose changes**: Submit PR updating this roadmap

**Join discussions**: GitHub Discussions (coming soon)

---

## Related Documentation

- **ARCHITECTURE.md**: How each phase fits into system design
- **DECISIONS.md**: Why we chose this roadmap order
- **CHANGELOG.md**: Actual release notes (vs planned roadmap)
- **API.md**: Endpoint specs for upcoming features
