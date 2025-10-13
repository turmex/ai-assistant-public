# Architecture Decision Records (ADRs)

Important technical decisions made during development, with rationale and trade-offs.

**Format**: Each ADR documents **what** was decided, **why**, **alternatives considered**, and **consequences**.

---

## ADR-001: Local-First Architecture

**Date**: 2024-10-01
**Status**: ✅ Accepted
**Deciders**: Project Lead

### Context

Need to choose between cloud-hosted service vs local-first application for AI assistant.

### Decision

**Build local-first application** where primary LLM inference runs on user's Mac via Ollama.

### Rationale

1. **Privacy**: User data never leaves their machine (unless they choose cloud LLM)
2. **Cost**: No server infrastructure costs, no per-request API fees
3. **Ownership**: Users own their data and models
4. **Offline**: Works without internet (after initial model download)
5. **Control**: Users can inspect, modify, or delete all data

### Alternatives Considered

#### Cloud-Hosted Service
**Pros**: Easier deployment, no hardware requirements, better models
**Cons**: Privacy concerns, ongoing API costs, vendor lock-in, requires internet
**Rejected**: Conflicts with privacy-first principle

#### Hybrid (Cloud Primary, Local Optional)
**Pros**: Best of both worlds
**Cons**: More complex, users still need API keys
**Rejected**: Adds complexity without clear benefit in MVP

### Consequences

**Positive**:
- Clear differentiation from ChatGPT/Claude (privacy angle)
- No usage-based costs
- Works in secure/offline environments

**Negative**:
- Hardware requirements (Mac with 8GB+ RAM)
- User must install Ollama
- Limited to Mac in MVP
- Slower inference than cloud models

**Mitigation**:
- Phase 4: Add optional cloud LLM routing for complex queries
- Detect hardware and recommend appropriate models
- Future: Expand to Linux/Windows

---

## ADR-002: FastAPI Over Flask/Django

**Date**: 2024-10-02
**Status**: ✅ Accepted
**Deciders**: Backend Lead

### Context

Need to choose Python web framework for REST API.

### Decision

**Use FastAPI** for backend framework.

### Rationale

1. **Async/await**: Native support for async operations (Ollama calls, DB queries)
2. **Type Safety**: Pydantic integration for request/response validation
3. **Auto-Documentation**: Swagger/OpenAPI generated automatically
4. **Performance**: Faster than Flask (comparable to Node.js)
5. **Modern**: Built with Python 3.6+ features (type hints)

### Alternatives Considered

#### Flask
**Pros**: Mature, large ecosystem, well-documented
**Cons**: Sync-only (blocking), manual input validation, no auto-docs
**Rejected**: Lack of async support is critical for Ollama calls

#### Django + Django REST Framework
**Pros**: Full-featured, built-in admin, ORM included
**Cons**: Heavy for this use case, opinionated, includes unused features
**Rejected**: Overkill for MVP, less flexibility

### Consequences

**Positive**:
- Fast development with automatic validation
- Type-safe API contracts
- Great developer experience
- Interactive API docs out-of-box

**Negative**:
- Less mature than Flask (but stable since 2018)
- Smaller ecosystem (but growing rapidly)

---

## ADR-003: SQLite for MVP, PostgreSQL for Production

**Date**: 2024-10-03
**Status**: ✅ Accepted
**Deciders**: Backend Lead, Database Architect

### Context

Need to choose database for conversation history, workflows, and user data.

### Decision

**Use SQLite for MVP** (single-user), **migrate to PostgreSQL** for multi-user (Phase 5).

### Rationale (SQLite for MVP)

1. **Zero Config**: No server to install/manage
2. **Single File**: Easy backup (just copy `ai_assistant.db`)
3. **Fast**: Sufficient for single-user local app
4. **Built-in**: Ships with Python
5. **ACID**: Full transaction support

### Rationale (PostgreSQL for Production)

1. **Concurrency**: Multiple users can write simultaneously
2. **Scalability**: Handles thousands of connections
3. **JSON Support**: Better JSON querying than SQLite
4. **Replication**: Built-in master-slave replication
5. **Extensions**: PostGIS, full-text search, etc.

### Alternatives Considered

#### MongoDB (NoSQL)
**Pros**: Flexible schema, JSON-native
**Cons**: Overkill for structured data, no joins, larger footprint
**Rejected**: Relational data model fits our use case better

#### MySQL
**Pros**: Popular, well-supported
**Cons**: Oracle ownership concerns, less feature-rich than PostgreSQL
**Rejected**: PostgreSQL has better JSON support

### Consequences

**Positive**:
- Fast MVP development
- Clear migration path (SQLAlchemy works with both)
- Users can inspect DB with any SQLite client

**Negative**:
- Migration work required in Phase 5
- Need to test migration scripts carefully
- Single-writer limitation (not an issue for single-user)

**Migration Plan**:
1. Setup Alembic for schema versioning
2. Write migration script (SQLite → PostgreSQL)
3. Test with sample data
4. Document migration process

---

## ADR-004: Single HTML File for Frontend

**Date**: 2024-10-04
**Status**: ✅ Accepted
**Deciders**: Frontend Lead

### Context

Need to choose frontend architecture for chat UI.

### Decision

**Build single-page app in one HTML file** with Tailwind CSS (CDN) and vanilla JavaScript.

### Rationale

1. **Simplicity**: No build step, no bundler, no dependencies
2. **Fast Iteration**: Edit and refresh (no npm install, webpack, etc.)
3. **Portability**: Single file is easy to serve, share, or embed
4. **Lightweight**: No React/Vue overhead for simple UI

### Alternatives Considered

#### React + Create React App
**Pros**: Component reusability, rich ecosystem, familiar to devs
**Cons**: Complex setup, slow build times, overkill for MVP
**Rejected**: Too much overhead for 500-line UI

#### Vue.js + Vite
**Pros**: Simpler than React, fast builds
**Cons**: Still requires build step and npm
**Rejected**: Still more complex than needed

#### Svelte
**Pros**: Compiles to vanilla JS, fast, elegant
**Cons**: Less familiar, requires build step
**Rejected**: Team unfamiliar with Svelte

### Consequences

**Positive**:
- Instant feedback loop (edit → refresh)
- No node_modules (no dependency hell)
- Easy for contributors (just HTML/CSS/JS)

**Negative**:
- Hard to scale beyond ~1000 lines
- No component reusability
- Manual DOM manipulation (no Virtual DOM)

**Future Migration**:
- Phase 6: Migrate to React when UI complexity warrants it
- Keep API separate (no tight coupling)

---

## ADR-005: Hardcoded Model Catalog vs Dynamic Fetching

**Date**: 2024-10-05
**Status**: ⚠️ Revisit in Phase 1
**Deciders**: Backend Lead

### Context

Hardware detector needs list of available Ollama models with metadata (size, quality, etc.).

### Decision (MVP)

**Hardcode model catalog** in `hardware_detector.py:MODEL_CATALOG` (8 models).

### Rationale

1. **Simplicity**: No API calls to Ollama registry on startup
2. **Metadata**: Ollama API doesn't provide quality/performance estimates
3. **Fast Startup**: No network dependency during hardware detection
4. **Curated**: Only include tested, high-quality models

### Alternatives Considered

#### Fetch from Ollama Library API
**Pros**: Always up-to-date, includes new models
**Cons**: Ollama library API doesn't have size/metadata, requires internet
**Rejected**: Missing critical metadata

#### Hybrid: Fetch + Local Metadata
**Pros**: Best of both worlds
**Cons**: More complex, requires metadata database
**Deferred to Phase 1**: Will implement when model catalog grows

### Consequences

**Positive**:
- Reliable startup (no network calls)
- Curated model list (only tested models)
- Clear performance expectations

**Negative**:
- Manual updates needed for new models
- Users can't discover models we haven't added
- Becomes stale over time

**Revisit Plan**:
1. Phase 1: Create `models.json` with metadata
2. Fetch Ollama library list on startup
3. Merge with local metadata (local overrides if conflict)
4. Cache for 24 hours

---

## ADR-006: JSON Column for Messages vs Separate Messages Table

**Date**: 2024-10-06
**Status**: ✅ Accepted (with migration plan)
**Deciders**: Database Architect

### Context

Store conversation messages: single JSON column or separate `messages` table?

### Decision (MVP)

**Store messages in JSON column** (`Conversation.messages: JSON`).

### Rationale

1. **Simplicity**: One query to get entire conversation
2. **Atomic Updates**: Whole conversation updates atomically
3. **Schema Flexibility**: Easy to add metadata fields
4. **MVP Speed**: Faster to implement

### Alternatives Considered

#### Separate Messages Table
**Pros**: Easier to query individual messages, better normalization, scalable
**Cons**: More complex queries (JOINs), need separate CRUD
**Deferred**: Will migrate in Phase 5 (multi-user)

### Consequences

**Positive**:
- Simple queries: `SELECT * FROM conversations WHERE id=?`
- Fast development
- Easy to serialize entire conversation

**Negative**:
- Can't query individual messages easily
- Can't add indexes on message fields
- JSON parsing overhead (small for <100 messages)
- Hard to do analytics ("most common user questions")

**Migration Plan (Phase 5)**:
1. Create `messages` table:
   ```sql
   CREATE TABLE messages (
     id SERIAL PRIMARY KEY,
     conversation_id UUID REFERENCES conversations(id),
     role VARCHAR(20),
     content TEXT,
     metadata JSONB,
     created_at TIMESTAMP
   );
   ```
2. Migrate existing JSON data:
   ```python
   for conv in conversations:
       for msg in conv.messages:
           Message.create(conversation_id=conv.id, **msg)
   ```
3. Drop `messages` column from `conversations`

---

## ADR-007: Multi-Fallback Strategy for Ollama Calls

**Date**: 2024-10-07
**Status**: ✅ Accepted
**Deciders**: Backend Lead, ML Engineer

### Context

Ollama's `/api/chat` endpoint sometimes returns empty responses or errors with long context.

### Decision

**Implement 3-tier fallback strategy**:
1. Try `/api/chat` with full conversation context (10 messages)
2. If empty, try `/api/chat` with only last user message
3. If still empty, try `/api/generate` with flattened prompt

### Rationale

1. **Reliability**: Users always get a response (even if degraded)
2. **Graceful Degradation**: Prefer full context, fall back to less context
3. **Breadcrumb Logging**: Debug why fallbacks are needed
4. **User Experience**: Better than "Empty response" error

### Alternatives Considered

#### Fail Fast (No Fallbacks)
**Pros**: Simpler code, clearer errors
**Cons**: Poor user experience, users see errors often
**Rejected**: Unacceptable UX

#### Retry Same Endpoint
**Pros**: Simpler than multi-strategy
**Cons**: Same error likely repeats
**Rejected**: Doesn't solve root cause

#### Increase Timeout
**Pros**: Gives Ollama more time
**Cons**: Slow UX, doesn't fix empty response issue
**Rejected**: Doesn't address the problem

### Consequences

**Positive**:
- Extremely reliable (3 chances to succeed)
- Users rarely see errors
- Logging helps debug Ollama issues

**Negative**:
- Complex code (3 code paths)
- Slower on failures (each fallback takes time)
- May mask underlying Ollama issues

**Future Improvements**:
- Track fallback usage (metrics)
- If fallback rate >10%, investigate Ollama
- Consider context size limits

---

## ADR-008: Tailwind CSS Over Custom CSS

**Date**: 2024-10-08
**Status**: ✅ Accepted
**Deciders**: Frontend Lead, Designer

### Context

Style frontend: write custom CSS or use utility framework?

### Decision

**Use Tailwind CSS** via CDN.

### Rationale

1. **Speed**: Prototype quickly without writing CSS
2. **Consistency**: Built-in design system (spacing, colors)
3. **Responsive**: Mobile-first utilities out-of-box
4. **JIT**: Only includes used classes (small bundle)
5. **Customizable**: Can extend with custom config

### Alternatives Considered

#### Custom CSS
**Pros**: Full control, no dependencies, smaller file
**Cons**: Slow development, hard to maintain consistency
**Rejected**: Too slow for MVP

#### Bootstrap
**Pros**: Component library, well-documented
**Cons**: Opinionated design, harder to customize
**Rejected**: Want custom design, not Bootstrap look

#### No Framework (Inline Styles)
**Pros**: Maximum simplicity
**Cons**: Unmaintainable, no consistency
**Rejected**: Unprofessional

### Consequences

**Positive**:
- Beautiful UI in hours, not days
- Easy to iterate on design
- Responsive by default

**Negative**:
- CDN dependency (37KB gzipped)
- HTML gets verbose with utility classes
- Harder to reuse styles (no CSS classes)

**Production Optimization**:
- Switch to Tailwind CLI (generate CSS file)
- Purge unused classes (reduce to ~5KB)
- Self-host instead of CDN

---

## ADR-009: No Streaming in MVP

**Date**: 2024-10-09
**Status**: ⚠️ Revisit in Phase 2
**Deciders**: Backend Lead

### Context

Should chat responses stream token-by-token like ChatGPT?

### Decision (MVP)

**No streaming** - wait for complete response, then show all at once.

### Rationale

1. **Simplicity**: No WebSocket/SSE setup needed
2. **MVP Speed**: Streaming adds significant complexity
3. **Reliability**: Easier error handling with complete responses
4. **Testing**: Simpler to test without streaming

### Alternatives Considered

#### Server-Sent Events (SSE)
**Pros**: Native browser support, simpler than WebSocket
**Cons**: One-way only, less browser support
**Deferred to Phase 2**

#### WebSocket
**Pros**: Bidirectional, real-time updates
**Cons**: More complex, requires ws:// upgrade
**Deferred to Phase 3** (for workflow updates)

### Consequences

**Positive**:
- Simple request/response model
- Easy to cache responses
- Straightforward error handling

**Negative**:
- Slower perceived UX (wait for full response)
- Can't cancel in-progress requests easily
- Users see "typing" animation, then wait 5-30s

**Phase 2 Migration Plan**:
1. Add SSE endpoint: `GET /chat/stream`
2. Modify Ollama call: `stream=true`
3. Yield tokens as they arrive
4. Frontend: Use EventSource API
5. Keep non-streaming endpoint for backwards compat

---

## ADR-010: Singleton Pattern for Hardware Detector

**Date**: 2024-10-10
**Status**: ✅ Accepted
**Deciders**: Backend Lead

### Context

Hardware detection is expensive (subprocess calls). How often to run?

### Decision

**Use Singleton pattern** - detect hardware once at startup, cache globally.

### Rationale

1. **Immutable**: Hardware doesn't change during runtime
2. **Expensive**: `sysctl` subprocess calls take 50-100ms
3. **Frequent**: Hardware info requested on every `/hardware` and `/health` call
4. **Predictable**: No race conditions (detected before server starts)

### Alternatives Considered

#### Detect Per-Request
**Pros**: Always fresh data
**Cons**: 50-100ms overhead per request
**Rejected**: Unnecessary (hardware is static)

#### Time-Based Cache (TTL)
**Pros**: Handles edge cases (RAM upgrade during runtime)
**Cons**: More complex, unnecessary
**Rejected**: Hardware won't change during app lifetime

#### Lazy Initialization
**Pros**: Only detect if endpoint is called
**Cons**: First request is slow
**Rejected**: Want fast first request

### Consequences

**Positive**:
- Fast responses (<1ms for cached data)
- Simple implementation (global variable)
- Predictable startup

**Negative**:
- Won't detect hardware changes during runtime
- Slight startup delay (50-100ms)

**Edge Case**: User upgrades RAM while app running
**Resolution**: Restart app (acceptable for local app)

---

## Decision Log Summary

| ADR | Decision | Status | Impact |
|-----|----------|--------|--------|
| 001 | Local-first architecture | ✅ Accepted | High - defines entire project |
| 002 | FastAPI over Flask/Django | ✅ Accepted | High - all API code |
| 003 | SQLite → PostgreSQL | ✅ Accepted | Medium - migration in Phase 5 |
| 004 | Single HTML file | ✅ Accepted | Medium - migrate in Phase 6 |
| 005 | Hardcoded model catalog | ⚠️ Revisit Phase 1 | Low - easy to change |
| 006 | JSON messages column | ✅ Accepted | Medium - migrate in Phase 5 |
| 007 | Multi-fallback strategy | ✅ Accepted | High - reliability |
| 008 | Tailwind CSS | ✅ Accepted | Low - UI only |
| 009 | No streaming (MVP) | ⚠️ Revisit Phase 2 | Medium - UX improvement |
| 010 | Singleton hardware detector | ✅ Accepted | Low - performance |

---

## Future ADRs (Placeholder)

Topics to document as decisions are made:

- **ADR-011**: MCP protocol vs custom tool integration
- **ADR-012**: Workflow engine (schedule vs Celery vs custom)
- **ADR-013**: Multi-agent communication protocol
- **ADR-014**: Cloud LLM provider selection strategy
- **ADR-015**: Testing framework (pytest vs unittest)
- **ADR-016**: Monitoring solution (Prometheus vs DataDog)
- **ADR-017**: Deployment strategy (Docker vs native)

---

## How to Use This Document

**When making a significant decision**:
1. Copy ADR template
2. Fill in context, alternatives, rationale
3. Get review from relevant stakeholders
4. Update status (✅ Accepted / ❌ Rejected / ⚠️ Revisit)
5. Implement decision
6. Update CHANGELOG.md with reference to ADR

**Template**:
```markdown
## ADR-XXX: [Decision Title]

**Date**: YYYY-MM-DD
**Status**: 🔄 Proposed / ✅ Accepted / ❌ Rejected / ⚠️ Revisit
**Deciders**: [Names/Roles]

### Context
[What problem are we solving?]

### Decision
[What did we decide?]

### Rationale
[Why this decision? List key factors]

### Alternatives Considered
[What else did we evaluate?]
#### Option A
**Pros**: ...
**Cons**: ...
**Rejected**: ...

### Consequences
**Positive**: [Good outcomes]
**Negative**: [Trade-offs]
**Mitigation**: [How to address negatives]
```

---

## Related Documentation

- **ARCHITECTURE.md**: Architectural patterns implemented from these decisions
- **ROADMAP.md**: How decisions affect future phases
- **CODE_STANDARDS.md**: Coding conventions derived from framework choices
- **DEPENDENCIES.md**: Dependencies chosen based on these decisions
