# Architecture Decision Records (ADRs)

## Overview

This document captures key architectural decisions made for the WebLLM/Ollama dual-mode system, including context, options considered, and rationale.

---

## ADR-001: Provider Selection Strategy

### Status
**Accepted** - 2025-11-18

### Context
We need to support both WebLLM (browser-based) and Ollama (server-based) LLM providers. We must decide:
1. Which provider to prioritize by default
2. How to handle fallback scenarios
3. Whether to allow user override

### Options Considered

#### Option A: Ollama-First
- **Pros**: Existing codebase uses Ollama, minimal refactoring, reliable server-based inference
- **Cons**: Requires local server, less privacy (server sees all data), no offline browser support

#### Option B: WebLLM-First (Selected)
- **Pros**: Browser-native, maximum privacy, no server required, offline capable, cutting-edge tech
- **Cons**: Browser compatibility requirements, WebGPU support needed, newer technology

#### Option C: User Choice at Startup
- **Pros**: Maximum flexibility, user controls their experience
- **Cons**: Decision fatigue, requires technical knowledge, complicates setup

### Decision
**WebLLM-First with Automatic Ollama Fallback**

### Rationale
1. **Privacy-First**: WebLLM keeps all data in browser, aligning with privacy best practices
2. **Future-Proof**: WebGPU is the future of browser ML, early adoption positions us well
3. **Offline Support**: Browser-based inference works without network connectivity
4. **Graceful Degradation**: Automatic fallback to Ollama ensures reliability
5. **Best of Both**: Users get cutting-edge tech with battle-tested fallback

### Implications
- Frontend must detect WebGPU support
- Backend provides fallback coordination
- Clear UI indication of active provider
- Manual override option for user preference

---

## ADR-002: Provider Abstraction Pattern

### Status
**Accepted** - 2025-11-18

### Context
Need to design abstraction layer that:
1. Supports multiple provider implementations
2. Allows runtime provider switching
3. Maintains clean separation of concerns
4. Enables easy testing and extension

### Options Considered

#### Option A: Simple Adapter Pattern
```python
class OllamaAdapter:
    def generate(prompt): ...

class WebLLMAdapter:
    def generate(prompt): ...
```
- **Pros**: Simple, straightforward
- **Cons**: No unified interface, hard to add new providers, testing difficult

#### Option B: Strategy + Factory Pattern (Selected)
```python
class LLMProvider(ABC):
    @abstractmethod
    def generate(prompt): ...

class LLMProviderFactory:
    def get_provider() -> LLMProvider: ...
```
- **Pros**: Clean interface, runtime selection, testable, extensible
- **Cons**: More initial code, requires interface design

#### Option C: Plugin Architecture
- **Pros**: Maximum flexibility, dynamic loading
- **Cons**: Overkill for 2-3 providers, complex configuration

### Decision
**Strategy + Factory Pattern with Base Interface**

### Rationale
1. **Separation of Concerns**: Business logic decoupled from provider specifics
2. **Testability**: Easy to mock providers for unit tests
3. **Extensibility**: New providers (OpenAI, Anthropic) can be added easily
4. **Type Safety**: Abstract base class ensures consistent interface
5. **Runtime Flexibility**: Factory enables dynamic provider selection

### Implications
- All providers must implement `LLMProvider` interface
- Factory manages provider lifecycle and selection
- Application code only depends on interface
- Existing Ollama code wrapped in adapter

---

## ADR-003: Model Catalog Architecture

### Status
**Accepted** - 2025-11-18

### Context
Users need to see all available models from both providers. We must decide:
1. How to present models from multiple sources
2. How to handle same model from different providers
3. How to manage model metadata normalization

### Options Considered

#### Option A: Separate Catalogs
- Show "WebLLM Models" and "Ollama Models" separately
- **Pros**: Clear provider distinction, simple implementation
- **Cons**: Fragmented UX, duplicate models shown twice, confusing for users

#### Option B: Merged Catalog with Tags (Selected)
- Single list with provider badges/tags
- **Pros**: Unified experience, clear availability, single model shown once
- **Cons**: Requires model ID normalization, metadata merging logic

#### Option C: Provider-Specific Views with Toggle
- Show one catalog at a time, user toggles between providers
- **Pros**: Clean separation, no merging needed
- **Cons**: Poor UX, hides availability from other provider

### Decision
**Unified Merged Catalog with Provider Tags**

### Rationale
1. **Better UX**: Users see all options in one place
2. **Reduced Confusion**: Same model from different providers shown once
3. **Clear Availability**: Provider badges show where model is available
4. **Download Status**: Can show downloaded status per provider
5. **Hardware Awareness**: Single performance indicator per model

### Implications
- Need model ID normalization logic
- Metadata merging from multiple sources
- Provider-specific information stored separately
- UI shows provider badges and download status

---

## ADR-004: TOON Format Integration

### Status
**Accepted** - 2025-11-18

### Context
Long conversations exceed context windows. Need token optimization strategy that:
1. Works with both providers
2. Preserves semantic meaning
3. Provides significant compression
4. Maintains conversation coherence

### Options Considered

#### Option A: Simple Truncation
- Drop oldest messages when context full
- **Pros**: Simple, fast, no special processing
- **Cons**: Loses context, breaks conversation flow, poor UX

#### Option B: Summarization
- Summarize old messages into single text
- **Pros**: Preserves some context, reduces tokens
- **Cons**: Requires LLM call (slow), may lose important details

#### Option C: TOON Format (Selected)
- Token-optimized Object Notation with semantic preservation
- **Pros**: 30-50% compression, semantic preservation, fast, provider-agnostic
- **Cons**: New format to implement, requires testing

#### Option D: Embeddings-Based Compression
- Store embeddings, retrieve relevant context
- **Pros**: Very efficient, intelligent retrieval
- **Cons**: Complex, requires embedding model, storage overhead

### Decision
**TOON Format Processor with Automatic Activation**

### Rationale
1. **Significant Compression**: 30-50% token reduction proven
2. **Semantic Preservation**: Maintains meaning better than truncation
3. **Provider Agnostic**: Works with WebLLM and Ollama equally
4. **Automatic**: Activates only when needed, transparent to user
5. **Bidirectional**: Can compress and decompress for debugging

### Implications
- Implement TOON processor module
- Integrate with conversation manager
- Monitor token counts per request
- Provide compression metrics in response
- Option to disable for testing

---

## ADR-005: Browser Compatibility Strategy

### Status
**Accepted** - 2025-11-18

### Context
WebLLM requires modern browser features:
- WebGPU support (Chrome 113+, Edge 113+)
- WASM support (all modern browsers)
- SharedArrayBuffer (requires specific headers)

We must decide how to handle incompatible browsers.

### Options Considered

#### Option A: Hard Requirement
- Block app if WebGPU not available
- **Pros**: Ensures best experience
- **Cons**: Excludes Firefox/Safari users, poor accessibility

#### Option B: Silent Fallback (Selected)
- Automatically use Ollama if WebGPU unavailable
- **Pros**: Universal compatibility, seamless UX
- **Cons**: User may not know why different provider used

#### Option C: User Warning + Choice
- Show warning, let user proceed or use Ollama
- **Pros**: Informed choice, educational
- **Cons**: Interrupts workflow, requires decision

### Decision
**Silent Automatic Fallback with Status Indicator**

### Rationale
1. **Universal Access**: All users can use the app
2. **Seamless UX**: No interruptions or barriers
3. **Progressive Enhancement**: Best experience for supported browsers
4. **Transparent Status**: UI shows active provider clearly
5. **Manual Override**: User can switch if desired

### Implications
- Detect WebGPU support at startup
- Show browser compatibility in status
- Provide clear provider indicator in UI
- Document browser requirements
- Test across Chrome, Firefox, Safari, Edge

---

## ADR-006: Error Handling and Fallback

### Status
**Accepted** - 2025-11-18

### Context
Providers can fail for various reasons:
- WebGPU errors
- Ollama server down
- Out of memory
- Network issues

We need robust error handling strategy.

### Options Considered

#### Option A: Fail Fast
- Show error immediately, no retry
- **Pros**: Clear feedback, simple logic
- **Cons**: Poor UX, no resilience

#### Option B: Automatic Retry + Fallback (Selected)
- Retry same provider once, then try alternative provider
- **Pros**: Resilient, seamless, good UX
- **Cons**: Slightly more complex, may hide issues

#### Option C: User Intervention
- Ask user what to do on every error
- **Pros**: User control, transparent
- **Cons**: Interrupts flow, technical burden

### Decision
**Automatic Retry + Provider Fallback with Logging**

### Rationale
1. **Resilience**: System continues working despite failures
2. **Good UX**: Users don't experience errors unnecessarily
3. **Transparency**: Logged errors for debugging
4. **Graceful Degradation**: Falls back to working provider
5. **User Notification**: Subtle UI indicator shows fallback occurred

### Implications
- Implement retry logic in provider factory
- Log all errors with context
- Track provider health status
- Show fallback notification in UI
- Monitor error rates in production

---

## ADR-007: State Management

### Status
**Accepted** - 2025-11-18

### Context
Need to manage:
- Conversation history
- Provider selection
- Model downloads
- User preferences

Current system uses SQLite. Must decide on state strategy for dual-provider system.

### Options Considered

#### Option A: Keep Existing SQLite
- Continue using current database schema
- **Pros**: Proven, works well, minimal changes
- **Cons**: May need schema updates, server-side only

#### Option B: Add IndexedDB for Browser State
- Use IndexedDB for WebLLM state (cached models, etc.)
- Keep SQLite for server state
- **Pros**: Browser-native storage, works offline
- **Cons**: Two storage systems, sync complexity

#### Option C: Unified State Management Library (Redux/Zustand)
- **Pros**: Centralized state, predictable updates
- **Cons**: Overkill for current needs, adds dependency

### Decision
**Hybrid Approach: SQLite + IndexedDB**

### Rationale
1. **Best Tool for Each Job**: SQLite for server, IndexedDB for browser
2. **Backward Compatible**: Existing conversations preserved
3. **Provider-Specific**: Each provider can manage its own state
4. **Offline Support**: IndexedDB works without server
5. **Minimal Changes**: Keeps existing architecture mostly intact

### Implications
- Extend SQLite schema for provider info
- Implement IndexedDB wrapper for WebLLM
- Sync mechanism for shared state
- Clear separation of concerns
- Migration path for existing data

---

## ADR-008: API Design

### Status
**Accepted** - 2025-11-18

### Context
Current REST API designed for single provider (Ollama). Need to extend for dual-provider support while maintaining backward compatibility.

### Options Considered

#### Option A: New Versioned API (/v2/)
- Create completely new API version
- **Pros**: Clean slate, no breaking changes
- **Cons**: Dual maintenance, migration required

#### Option B: Extend Existing API (Selected)
- Add optional provider parameter, enhance responses
- **Pros**: Backward compatible, gradual migration
- **Cons**: API becomes more complex

#### Option C: Separate API per Provider
- /webllm/chat, /ollama/chat
- **Pros**: Clear separation, simple routing
- **Cons**: Duplicate endpoints, verbose

### Decision
**Extend Existing API with Provider Transparency**

### Rationale
1. **Backward Compatibility**: Existing clients continue working
2. **Gradual Enhancement**: Add provider info to responses
3. **Future-Proof**: Can add new providers without API changes
4. **Consistent Interface**: Same endpoints, different backend
5. **Clear Responses**: Provider info in every response

### API Changes:
```python
# Before
POST /chat
{ "message": "hello" }
→ { "response": "hi" }

# After (backward compatible)
POST /chat
{ "message": "hello", "provider": "webllm" }  # optional
→ {
    "response": "hi",
    "provider": "webllm",           # NEW
    "model": "llama-3-8b",         # NEW
    "fallback_from": null,         # NEW
    "tokens_used": 42              # NEW
  }
```

### Implications
- All responses include provider info
- Optional provider selection in requests
- Clear documentation of new fields
- Maintain backward compatibility
- Deprecation path if needed

---

## Summary of Key Decisions

| ADR | Decision | Impact |
|-----|----------|--------|
| 001 | WebLLM-first with Ollama fallback | Privacy-focused, future-proof |
| 002 | Strategy + Factory pattern | Clean architecture, extensible |
| 003 | Unified merged catalog | Better UX, single source of truth |
| 004 | TOON format integration | Context optimization, provider-agnostic |
| 005 | Silent fallback for compatibility | Universal access, seamless UX |
| 006 | Automatic retry + fallback | Resilient system, good error handling |
| 007 | Hybrid SQLite + IndexedDB | Best storage for each use case |
| 008 | Extend existing API | Backward compatible, consistent interface |

---

**Document Version**: 1.0
**Last Updated**: 2025-11-18
**Status**: Approved
**Next Review**: Before Phase 2 implementation
