# Documentation Index

Complete documentation for AI Assistant. **Start here** to navigate the docs.

## 📋 Quick Navigation

### For AI Assistants (Token-Efficient)
**→ START HERE**: [AI_QUICK_REF.md](AI_QUICK_REF.md) (~480 tokens)
- Ultra-concise project reference
- File structure, endpoints, common tasks
- Designed for AI context windows

### For Developers

#### Getting Started
1. **[DEVELOPMENT.md](DEVELOPMENT.md)** - Setup, testing, contributing
2. **[CODE_STANDARDS.md](CODE_STANDARDS.md)** - Coding conventions
3. **[API.md](API.md)** - REST API reference

#### Understanding the System
4. **[ARCHITECTURE.md](ARCHITECTURE.md)** - System design, data flows, diagrams
5. **[DEPENDENCIES.md](DEPENDENCIES.md)** - Dependency graph and rationale
6. **[DECISIONS.md](DECISIONS.md)** - Architecture Decision Records (ADRs)

#### Operations & Planning
7. **[INFRASTRUCTURE.md](INFRASTRUCTURE.md)** - Logging, monitoring, error handling
8. **[ROADMAP.md](ROADMAP.md)** - Feature timeline and phases
9. **[CHANGELOG.md](CHANGELOG.md)** - Version history

---

## 📚 Documentation by Role

### New Contributor
**Path**: DEVELOPMENT.md → CODE_STANDARDS.md → ARCHITECTURE.md
1. Setup local environment
2. Learn coding conventions
3. Understand system architecture
4. Pick an issue and start coding

### Backend Developer
**Path**: ARCHITECTURE.md → API.md → CODE_STANDARDS.md → DEPENDENCIES.md
- Understand component interactions
- Learn API contracts
- Follow Python conventions
- Know why we chose each dependency

### Frontend Developer
**Path**: API.md → ARCHITECTURE.md (frontend section) → DEVELOPMENT.md
- Learn API endpoints
- Understand frontend architecture
- Setup development environment

### DevOps/SRE
**Path**: INFRASTRUCTURE.md → ARCHITECTURE.md → DEVELOPMENT.md (deployment)
- Setup monitoring and logging
- Understand error handling
- Deploy production environment

### Product Manager
**Path**: ROADMAP.md → DECISIONS.md → CHANGELOG.md
- Understand feature timeline
- Learn why decisions were made
- Track release history

### AI Assistant (Claude, ChatGPT, etc.)
**Path**: AI_QUICK_REF.md → (load specific docs as needed)
- Start with quick reference
- Deep-dive into relevant sections on demand
- All docs are token-efficient and structured

---

## 📖 Document Summaries

### AI_QUICK_REF.md (4.2 KB)
**Token count**: ~480 tokens
**Purpose**: Ultra-concise project reference for AI assistants

**Contents**:
- Project overview and tech stack
- File structure with LOC counts
- API endpoints (table format)
- Common tasks with file references
- Known issues and constraints

**When to read**: First thing every AI assistant should load

---

### ARCHITECTURE.md (22 KB)
**Token count**: ~2,500 tokens
**Purpose**: Comprehensive system design documentation

**Contents**:
- High-level architecture diagrams (mermaid)
- Component breakdown (frontend, backend, data, external)
- Data flow diagrams (chat, hardware detection, model download)
- Design patterns (singleton, factory, repository, multi-fallback)
- Security considerations
- Scalability and performance
- Error handling strategy
- Testing strategy
- Deployment architecture
- Future evolution plans

**When to read**: Understanding how the system works

---

### API.md (9.8 KB)
**Token count**: ~1,200 tokens
**Purpose**: Complete REST API specification

**Contents**:
- 12 endpoint specifications
- Request/response schemas
- Error codes and formats
- curl examples
- OpenAPI/Swagger links

**When to read**: Implementing API calls or adding endpoints

---

### DEVELOPMENT.md (11 KB)
**Token count**: ~1,300 tokens
**Purpose**: Setup, testing, and contributing guide

**Contents**:
- Quick start (7 steps)
- Project structure
- Development workflow
- Adding endpoints/models/hardware detection
- Testing (manual and automated)
- Common tasks
- Troubleshooting
- Deployment

**When to read**: Setting up local environment

---

### CODE_STANDARDS.md (13 KB)
**Token count**: ~1,500 tokens
**Purpose**: Coding conventions and best practices

**Contents**:
- Python style guide (PEP 8 + specifics)
- Naming conventions (table format)
- Type hints requirements
- Docstring templates
- Error handling patterns
- Logging best practices
- JavaScript conventions
- Commit message format (Conventional Commits)
- Security standards

**When to read**: Before writing code

---

### DEPENDENCIES.md (14 KB)
**Token count**: ~1,600 tokens
**Purpose**: Dependency graph and rationale

**Contents**:
- Dependency diagram (mermaid)
- Backend dependencies (FastAPI, SQLAlchemy, httpx, etc.)
- Frontend dependencies (Tailwind CSS)
- External services (Ollama, SQLite)
- Why each dependency was chosen
- Alternatives considered
- Dependency size analysis
- Update policy

**When to read**: Understanding why we use certain libraries

---

### INFRASTRUCTURE.md (17 KB)
**Token count**: ~2,000 tokens
**Purpose**: Production-grade infrastructure patterns

**Contents**:
- Current logging setup
- Production improvements (JSON logs, request IDs, rotation)
- Monitoring (Prometheus, Grafana)
- Error handling categories
- Resource management
- Observability best practices
- Runbooks (Ollama down, DB locked, high memory)
- Future infrastructure (Docker, Kubernetes)

**When to read**: Setting up production environment

---

### ROADMAP.md (12 KB)
**Token count**: ~1,400 tokens
**Purpose**: Feature timeline and development phases

**Contents**:
- Vision and core principles
- Current state (v0.1.0 MVP)
- 5 phases over 14 weeks:
  - Phase 1: Infrastructure (testing, logging)
  - Phase 2: MCP tool integration
  - Phase 3: Workflow automation
  - Phase 4: Cloud LLM routing
  - Phase 5: Multi-agent collaboration
- Release schedule (weekly releases)
- Success metrics
- Non-goals

**When to read**: Understanding project direction

---

### DECISIONS.md (18 KB)
**Token count**: ~2,100 tokens
**Purpose**: Architecture Decision Records (ADRs)

**Contents**:
- 10 major decisions documented:
  - ADR-001: Local-first architecture
  - ADR-002: FastAPI over Flask/Django
  - ADR-003: SQLite → PostgreSQL migration
  - ADR-004: Single HTML file frontend
  - ADR-005: Hardcoded model catalog
  - ADR-006: JSON messages column
  - ADR-007: Multi-fallback strategy
  - ADR-008: Tailwind CSS
  - ADR-009: No streaming in MVP
  - ADR-010: Singleton hardware detector
- Each ADR: context, decision, rationale, alternatives, consequences

**When to read**: Understanding why decisions were made

---

### CHANGELOG.md (8.5 KB)
**Token count**: ~1,000 tokens
**Purpose**: Version history and release notes

**Contents**:
- Semantic versioning guide
- v0.1.0 release notes (current)
- Planned releases (v0.1.1 - v2.0.0)
- Migration guides
- Deprecation warnings
- Release notes template

**When to read**: Before upgrading versions

---

## 📊 Token Budget Summary

| Document | Tokens | Use Case |
|----------|--------|----------|
| AI_QUICK_REF.md | ~480 | Always load first |
| API.md | ~1,200 | When calling endpoints |
| CHANGELOG.md | ~1,000 | Version upgrades |
| DEVELOPMENT.md | ~1,300 | Local setup |
| ROADMAP.md | ~1,400 | Feature planning |
| CODE_STANDARDS.md | ~1,500 | Writing code |
| DEPENDENCIES.md | ~1,600 | Understanding libs |
| INFRASTRUCTURE.md | ~2,000 | Production ops |
| DECISIONS.md | ~2,100 | Understanding rationale |
| ARCHITECTURE.md | ~2,500 | System design |
| **TOTAL** | **~15,080** | Complete docs |

**AI Context Window Strategy**:
- Load AI_QUICK_REF.md (480 tokens) always
- Load 2-3 additional docs as needed (~4,000 tokens)
- Total context: ~4,500 tokens (fits in most AI context windows)

---

## 🔍 How to Find Information

### "How do I...?"
| Question | Document |
|----------|----------|
| Setup the project | DEVELOPMENT.md |
| Add a new endpoint | DEVELOPMENT.md → API.md |
| Understand a design choice | DECISIONS.md |
| See what's coming next | ROADMAP.md |
| Check API specs | API.md |
| Learn coding standards | CODE_STANDARDS.md |
| Setup monitoring | INFRASTRUCTURE.md |
| Understand architecture | ARCHITECTURE.md |

### "Why did we...?"
| Question | Document |
|----------|----------|
| Choose FastAPI | DECISIONS.md (ADR-002) |
| Use SQLite instead of Postgres | DECISIONS.md (ADR-003) |
| Not implement streaming | DECISIONS.md (ADR-009) |
| Pick local-first approach | DECISIONS.md (ADR-001) |

### "What changed in...?"
| Question | Document |
|----------|----------|
| Latest version | CHANGELOG.md |
| Past 3 months | CHANGELOG.md + git log |
| Next 3 months | ROADMAP.md |

---

## 📝 Updating Documentation

### When to Update

**After every PR** that:
- Adds/modifies API endpoints → Update API.md
- Changes architecture → Update ARCHITECTURE.md
- Adds dependencies → Update DEPENDENCIES.md
- Makes significant decisions → Add ADR to DECISIONS.md
- Ships a release → Update CHANGELOG.md
- Changes setup process → Update DEVELOPMENT.md
- Modifies roadmap → Update ROADMAP.md

### Documentation Standards

1. **Keep token counts low**: AI assistants are frequent readers
2. **Use tables** instead of prose where possible
3. **Include mermaid diagrams** for architecture/flows
4. **Cross-reference** related docs
5. **Update AI_QUICK_REF.md** if structure changes
6. **Mark outdated sections** with ⚠️ and create GitHub issue

### How to Update

1. Edit relevant markdown file(s)
2. Update "Last Updated" date (if file has one)
3. Run doc linter: `markdownlint docs/` (future)
4. Commit with clear message: `docs: update API.md with new /workflow endpoint`
5. Include doc updates in same PR as code changes

---

## 🤖 AI Assistant Guidelines

### Optimal Usage

**Phase 1: Context Loading**
```
1. Load AI_QUICK_REF.md (always)
2. Ask user: "What are you trying to do?"
3. Load 1-2 relevant docs based on task:
   - Writing code → CODE_STANDARDS.md + ARCHITECTURE.md
   - API questions → API.md
   - Setup issues → DEVELOPMENT.md
   - Design questions → DECISIONS.md
```

**Phase 2: Task Execution**
```
1. Reference specific file:line numbers
2. Quote relevant sections from docs
3. Suggest doc updates if information is missing
```

**Phase 3: Follow-up**
```
1. If new pattern introduced, suggest ADR
2. If bug found, check CHANGELOG.md for known issues
3. If feature requested, check ROADMAP.md for plans
```

### Token Optimization Tips

- **Don't load everything**: Pick 2-3 relevant docs max
- **Use AI_QUICK_REF.md first**: Answers 80% of questions
- **Search before loading**: grep for keywords to find right doc
- **Summarize findings**: Don't echo entire docs back to user
- **Cache common patterns**: Remember file:line refs for frequent operations

---

## 📂 Documentation Structure

```
docs/
├── README.md              # This file (navigation guide)
├── AI_QUICK_REF.md       # Token-efficient reference (START HERE for AI)
├── ARCHITECTURE.md        # System design and diagrams
├── API.md                # REST API specifications
├── CHANGELOG.md          # Version history
├── CODE_STANDARDS.md     # Coding conventions
├── DECISIONS.md          # Architecture Decision Records
├── DEPENDENCIES.md       # Dependency graph and rationale
├── DEVELOPMENT.md        # Setup and contributing guide
├── INFRASTRUCTURE.md     # Logging, monitoring, ops
└── ROADMAP.md            # Feature timeline
```

**Total Size**: 140 KB (10 files)
**Total Tokens**: ~15,000 (optimized for AI consumption)

---

## 🔗 External Resources

- **Main README**: ../README.md (project overview)
- **GitHub Repo**: https://github.com/turmex/ai-assistant-public
- **Ollama Docs**: https://ollama.ai/docs
- **FastAPI Docs**: https://fastapi.tiangolo.com
- **SQLAlchemy Docs**: https://docs.sqlalchemy.org

---

## ✅ Documentation Completeness Checklist

- [x] AI_QUICK_REF.md - Ultra-concise reference
- [x] ARCHITECTURE.md - System design
- [x] API.md - Endpoint specs
- [x] CHANGELOG.md - Version history
- [x] CODE_STANDARDS.md - Coding conventions
- [x] DECISIONS.md - ADRs
- [x] DEPENDENCIES.md - Dependency graph
- [x] DEVELOPMENT.md - Setup guide
- [x] INFRASTRUCTURE.md - Ops guide
- [x] ROADMAP.md - Feature timeline
- [x] README.md (this file) - Navigation

**Status**: ✅ Documentation complete (v0.1.1)

---

## 📧 Feedback

Found outdated info? Missing documentation? Suggestions?

- **GitHub Issues**: https://github.com/turmex/ai-assistant-public/issues
- **Label**: `documentation`
- **PR Welcome**: Submit fixes directly

---

**Last Updated**: 2024-10-13
**Documentation Version**: 0.1.1
**Project Version**: 0.1.0
