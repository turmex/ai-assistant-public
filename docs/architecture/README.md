# WebLLM/Ollama Dual-Mode Architecture Documentation

## Overview

This directory contains comprehensive architecture documentation for the WebLLM/Ollama dual-mode AI Assistant system. The architecture enables seamless switching between browser-based (WebLLM) and server-based (Ollama) LLM providers with a unified user experience.

## Documents

### 1. [System Overview](01-system-overview.md)
**Purpose**: High-level architecture and design principles

**Contents**:
- Current state analysis
- Target architecture vision
- High-level component diagram
- Provider selection logic
- Component responsibilities
- Data models
- API endpoints
- Browser compatibility
- Security considerations
- Performance optimization
- Migration strategy

**Key Takeaways**:
- WebLLM-first with Ollama fallback
- Strategy + Factory + Adapter patterns
- Unified model catalog
- TOON format for context compression
- Provider-agnostic interfaces

---

### 2. [Provider Abstraction Layer](02-provider-abstraction.md)
**Purpose**: Detailed design of provider abstraction

**Contents**:
- Design patterns (Strategy + Factory + Adapter)
- Base `LLMProvider` interface
- `LLMProviderFactory` implementation
- `WebLLMAdapter` structure
- `OllamaAdapter` structure
- FastAPI integration points
- Benefits and trade-offs

**Key Takeaways**:
- Clean separation of concerns
- Runtime provider switching
- Easy testing with mocks
- Extensible for new providers
- Backward compatible with existing code

---

### 3. [Unified Model Catalog](03-unified-model-catalog.md)
**Purpose**: Model catalog architecture and merging logic

**Contents**:
- Unified data model (`UnifiedModelInfo`)
- Catalog manager implementation
- WebLLM model configurations
- Model ID normalization
- Metadata merging algorithm
- Hardware-aware performance calculation
- Search and filter capabilities
- API integration
- Frontend integration

**Key Takeaways**:
- Single source of truth for all models
- Same model from different providers shown once
- Provider badges indicate availability
- Hardware-based performance indicators
- Download status per provider

---

### 4. [Data Flow Diagrams](04-data-flow-diagrams.md)
**Purpose**: Visualize data movement through the system

**Contents**:
- System initialization flow
- Model selection flow
- Chat message flow (WebLLM path)
- Chat message flow (Ollama fallback)
- Provider switching flow
- Model download flow
- TOON format processing flow
- Error handling flow

**Key Takeaways**:
- Clear request/response paths
- Automatic fallback mechanisms
- Provider-independent data flow
- Context compression triggers
- Error recovery strategies

---

### 5. [Architecture Decision Records](05-architecture-decisions.md)
**Purpose**: Document key architectural decisions and rationale

**ADRs Included**:
1. **ADR-001**: Provider Selection Strategy (WebLLM-first)
2. **ADR-002**: Provider Abstraction Pattern (Strategy + Factory)
3. **ADR-003**: Model Catalog Architecture (Unified merged catalog)
4. **ADR-004**: TOON Format Integration (Context optimization)
5. **ADR-005**: Browser Compatibility Strategy (Silent fallback)
6. **ADR-006**: Error Handling and Fallback (Automatic retry)
7. **ADR-007**: State Management (Hybrid SQLite + IndexedDB)
8. **ADR-008**: API Design (Backward compatible extension)

**Key Takeaways**:
- Each decision includes context, options, and rationale
- Trade-offs explicitly documented
- Implications clearly stated
- Reversible decisions with rollback plans

---

### 6. [Implementation Roadmap](06-implementation-roadmap.md)
**Purpose**: Phased implementation plan with timelines

**Phases**:
- **Phase 1** (Week 1): Foundation - Provider abstraction layer
- **Phase 2** (Week 2): WebLLM integration with browser detection
- **Phase 3** (Week 3): Unified model catalog
- **Phase 4** (Week 4): TOON format integration
- **Phase 5** (Week 5): Polish and optimization

**Key Takeaways**:
- 5-week timeline to full implementation
- Clear dependencies between phases
- Success criteria for each phase
- Risk assessment and mitigation
- Testing strategy
- Rollback plans

---

## Quick Reference

### Key Architecture Principles

1. **Browser-First**: WebLLM as default, Ollama as fallback
2. **Privacy-Focused**: Browser-based inference keeps data local
3. **Unified Experience**: Single interface regardless of provider
4. **Automatic Fallback**: Seamless provider switching on failure
5. **Hardware-Aware**: Performance indicators based on system specs
6. **Extensible**: Easy to add new providers (OpenAI, Anthropic, etc.)

### Core Components

| Component | Purpose | Location |
|-----------|---------|----------|
| `LLMProvider` | Base interface for all providers | `backend/providers/base_provider.py` |
| `LLMProviderFactory` | Provider lifecycle management | `backend/providers/provider_factory.py` |
| `WebLLMAdapter` | WebLLM integration | `backend/providers/webllm_adapter.py` |
| `OllamaAdapter` | Ollama integration | `backend/providers/ollama_adapter.py` |
| `UnifiedModelCatalog` | Model merging and search | `backend/catalog/unified_catalog.py` |
| `TOONProcessor` | Context compression | `backend/toon/toon_processor.py` |

### Key Data Models

```python
# Provider Status
@dataclass
class ProviderStatus:
    provider_type: ProviderType
    available: bool
    healthy: bool
    loaded_model: Optional[str]
    error_message: Optional[str]

# Unified Model Info
@dataclass
class UnifiedModelInfo:
    id: str
    name: str
    providers: List[str]
    provider_info: Dict[str, ProviderModelInfo]
    performance: PerformanceInfo
    recommended: bool

# Generation Result
@dataclass
class GenerationResult:
    text: str
    provider: ProviderType
    model_id: str
    tokens_used: int
    latency_ms: float
```

### API Endpoints

#### New Endpoints
- `GET /providers` - List providers and status
- `POST /providers/select` - Manually select provider
- `GET /models/unified` - Unified model catalog

#### Modified Endpoints
- `POST /chat` - Now includes provider info in response
- `GET /models` - Returns unified catalog with provider tags

### Provider Selection Logic

```
User Request
    ↓
Check WebLLM available?
    ↓ Yes → Use WebLLM
    ↓ No
Check Ollama running?
    ↓ Yes → Use Ollama
    ↓ No
Error: No providers
```

### Error Handling

1. **Provider Failure**: Automatic fallback to alternative provider
2. **Model Not Found**: Clear error with recommendations
3. **Context Overflow**: Automatic TOON compression
4. **Browser Incompatible**: Silent fallback to Ollama
5. **Network Error**: Retry with exponential backoff

## Implementation Status

- [x] Architecture design complete
- [x] Documentation written
- [x] ADRs documented
- [x] Roadmap defined
- [ ] Phase 1: Foundation (Week 1)
- [ ] Phase 2: WebLLM (Week 2)
- [ ] Phase 3: Catalog (Week 3)
- [ ] Phase 4: TOON (Week 4)
- [ ] Phase 5: Polish (Week 5)

## Next Steps

1. **Review**: Architecture review meeting with team
2. **Approval**: Get stakeholder sign-off on design
3. **Phase 1**: Begin provider abstraction implementation
4. **Testing**: Set up test infrastructure
5. **Documentation**: Keep docs updated as implementation progresses

## Resources

### External References
- [WebLLM Documentation](https://github.com/mlc-ai/web-llm)
- [Ollama API Reference](https://github.com/ollama/ollama/blob/main/docs/api.md)
- [WebGPU Specification](https://www.w3.org/TR/webgpu/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

### Internal Resources
- Current codebase: `/Users/davidcelekli/Desktop/ai-assistant/`
- Backend: `backend/`
- Frontend: `frontend-v2/`
- Tests: `tests/`

## Contact

**Architecture Owner**: System Architect Agent (Hive Mind Swarm)
**Hive Session**: swarm-1763486942621-6lwk8micx
**Created**: 2025-11-18
**Status**: Ready for Implementation

---

**Total Documentation**: 6 comprehensive documents, 126KB
**Architecture Stored**: Hive Memory (ReasoningBank)
**Implementation Timeline**: 5 weeks
**Team Ready**: ✓ Ready to Begin Phase 1
