# System Architecture Overview: WebLLM/Ollama Dual-Mode AI Assistant

## Executive Summary

This document defines the architecture for a dual-mode AI Assistant that seamlessly integrates WebLLM (browser-based) and Ollama (server-based) LLM providers. The system prioritizes WebLLM as the default provider with Ollama as an intelligent fallback, presenting a unified interface to users regardless of the underlying provider.

## Current State Analysis

### Existing Architecture
The current system is a FastAPI backend with HTML/JS frontend that:
- Uses Ollama exclusively as the LLM provider
- Implements hardware detection for Mac systems
- Provides model recommendation based on RAM/CPU
- Integrates HuggingFace model catalog
- Manages conversations with SQLite database

### Current Components
1. **Backend (Python/FastAPI)**
   - `main.py`: FastAPI app with REST endpoints
   - `ollama_integration.py`: Ollama model catalog (50+ models)
   - `hardware_detector.py`: Mac hardware detection
   - `huggingface_integration.py`: HF model fetching
   - `conversation_manager.py`: Conversation state
   - `database.py`: SQLAlchemy models

2. **Frontend (HTML/Tailwind/Vanilla JS)**
   - Single-page application
   - Model selection dropdown
   - Chat interface with conversation history
   - Hardware info display

## Target Architecture

### Design Principles

1. **Browser-First**: WebLLM runs entirely in the browser, providing privacy and offline capability
2. **Seamless Fallback**: Transparent failover to Ollama when WebLLM is unavailable
3. **Unified Interface**: Single API surface regardless of provider
4. **Progressive Enhancement**: Enhanced features when both providers are available
5. **Performance Optimization**: TOON format for token compression across providers

### Architecture Patterns

**Primary Pattern**: Strategy Pattern with Factory
- Encapsulates provider-specific behavior
- Runtime provider switching
- Consistent interface across implementations

**Secondary Pattern**: Adapter Pattern
- Adapts WebLLM and Ollama to common interface
- Normalizes model formats
- Standardizes response structures

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend Layer                        │
│  ┌────────────────────────────────────────────────────────┐ │
│  │          Unified Chat Interface (React/Vue)             │ │
│  │  - Single chat input/output                             │ │
│  │  - Provider status indicator                            │ │
│  │  - Model selector (unified list)                        │ │
│  │  - Provider toggle (manual override)                    │ │
│  └────────────────────────────────────────────────────────┘ │
│                            ↓                                 │
│  ┌────────────────────────────────────────────────────────┐ │
│  │         WebLLM Client (Browser-based)                   │ │
│  │  - Runs models in browser via WebGPU                    │ │
│  │  - Local inference, privacy-first                       │ │
│  │  - Automatic model caching                              │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            ↓ (fallback only)
┌─────────────────────────────────────────────────────────────┐
│                      Backend Layer (FastAPI)                 │
│  ┌────────────────────────────────────────────────────────┐ │
│  │           LLM Provider Abstraction Layer                │ │
│  │  ┌──────────────────┐    ┌──────────────────┐          │ │
│  │  │  WebLLM Adapter  │    │  Ollama Adapter  │          │ │
│  │  │  (for fallback)  │    │  (local server)  │          │ │
│  │  └──────────────────┘    └──────────────────┘          │ │
│  │             ↓                       ↓                    │ │
│  │  ┌────────────────────────────────────────────────────┐ │ │
│  │  │          Unified Model Catalog                      │ │ │
│  │  │  - WebLLM models (30+ browser-compatible)          │ │ │
│  │  │  - Ollama models (50+ local models)                │ │ │
│  │  │  - Unified format with provider tags                │ │ │
│  │  └────────────────────────────────────────────────────┘ │ │
│  └────────────────────────────────────────────────────────┘ │
│                            ↓                                 │
│  ┌────────────────────────────────────────────────────────┐ │
│  │        TOON Format Processor (Token Optimization)       │ │
│  │  - Cross-provider token compression                     │ │
│  │  - Context window management                            │ │
│  │  - Intelligent summarization                            │ │
│  └────────────────────────────────────────────────────────┘ │
│                            ↓                                 │
│  ┌────────────────────────────────────────────────────────┐ │
│  │         Conversation & State Management                 │ │
│  │  - SQLite persistence                                   │ │
│  │  - Provider-agnostic storage                            │ │
│  │  - Context window tracking                              │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Provider Selection Logic

### Automatic Provider Selection (Default Behavior)

```
┌─────────────────────────────────────────────────────────────┐
│                    User Sends Message                        │
└──────────────────────────┬──────────────────────────────────┘
                           ↓
                 ┌─────────────────────┐
                 │  WebLLM Available?  │
                 └──────────┬──────────┘
                            ↓
                   Yes ──→ [Use WebLLM]
                            │
                   No  ──→ ┌──────────────────┐
                           │ Ollama Running?  │
                           └────────┬─────────┘
                                    ↓
                           Yes ──→ [Use Ollama]
                                    │
                           No  ──→ [Error: No providers available]
```

### Manual Override
Users can manually select a provider from the UI:
- "Browser Only" - Force WebLLM, fail if unavailable
- "Server Only" - Force Ollama, fail if unavailable
- "Auto" (default) - Smart selection with fallback

## Component Responsibilities

### 1. Provider Factory (`llm_provider_factory.py`)
- Detects available providers
- Creates appropriate provider instances
- Manages provider lifecycle
- Handles provider switching

### 2. Base Provider Interface (`base_provider.py`)
```python
class LLMProvider(ABC):
    @abstractmethod
    async def list_models() -> List[ModelInfo]

    @abstractmethod
    async def load_model(model_id: str) -> bool

    @abstractmethod
    async def generate(prompt: str, context: List[Message]) -> str

    @abstractmethod
    async def stream_generate(prompt: str, context: List[Message]) -> AsyncIterator[str]

    @abstractmethod
    def get_status() -> ProviderStatus
```

### 3. WebLLM Adapter (`webllm_adapter.py`)
- Wraps WebLLM JavaScript library
- Manages WebGPU initialization
- Handles model loading/caching
- Provides browser compatibility checks

### 4. Ollama Adapter (`ollama_adapter.py`)
- Wraps existing Ollama integration
- Maintains backward compatibility
- Provides server health checks

### 5. Unified Model Catalog (`unified_catalog.py`)
- Merges WebLLM + Ollama models
- Normalizes model metadata
- Adds provider tags
- Implements search/filter

### 6. TOON Format Processor (`toon_processor.py`)
- Implements TOON compression
- Works with both providers
- Manages context windows
- Provides token counting

## Data Models

### Unified Model Information
```python
@dataclass
class UnifiedModelInfo:
    id: str                          # Unique identifier
    name: str                        # Display name
    provider: str                    # "webllm" | "ollama" | "both"
    providers: List[str]             # All available providers
    size_gb: float                   # Model size
    parameters: str                  # "1B", "7B", etc.
    context_length: int              # Max context tokens
    capabilities: List[str]          # ["chat", "code", etc.]
    performance: PerformanceInfo     # Hardware-specific
    webllm_id: Optional[str]         # WebLLM model ID
    ollama_id: Optional[str]         # Ollama model ID
    recommended: bool                # Hardware recommendation
    downloaded: Dict[str, bool]      # {"webllm": True, "ollama": False}
```

### Provider Status
```python
@dataclass
class ProviderStatus:
    provider: str                    # "webllm" | "ollama"
    available: bool                  # Is provider accessible?
    healthy: bool                    # Is provider functioning?
    loaded_model: Optional[str]      # Currently loaded model
    error: Optional[str]             # Error message if any
    capabilities: List[str]          # Supported features
    hardware: Optional[Dict]         # Hardware info (WebGPU, etc.)
```

## API Endpoints

### New Endpoints
- `GET /providers` - List available providers and their status
- `GET /providers/{provider}/status` - Detailed provider status
- `POST /providers/select` - Manually select a provider
- `GET /models/unified` - Unified model list (WebLLM + Ollama)
- `GET /models/{model_id}/providers` - Which providers support this model

### Modified Endpoints
- `GET /models` - Now returns unified catalog with provider tags
- `POST /chat` - Automatically selects provider, includes provider in response
- `POST /models/download` - Supports both providers

## Browser Compatibility

### WebLLM Requirements
- **WebGPU Support**: Chrome 113+, Edge 113+, Firefox Nightly
- **WASM Support**: All modern browsers
- **SharedArrayBuffer**: Requires CORS headers

### Fallback Strategy
1. Check WebGPU availability
2. Check WASM support
3. If either fails, automatically use Ollama
4. Display clear browser compatibility message

## Security Considerations

### WebLLM (Browser-Based)
- All data stays in browser (privacy-first)
- No network calls for inference
- Model downloads over HTTPS
- CSP headers for security

### Ollama (Server-Based)
- Local server only (no external calls)
- API authentication (optional)
- Rate limiting
- Request validation

### TOON Format
- No sensitive data in compressed format
- Client-side compression option
- Encrypted storage for context

## Performance Optimization

### WebLLM
- Progressive model loading
- Model caching in IndexedDB
- WebGPU acceleration
- Quantized models (INT4, INT8)

### Ollama
- Keep-alive for loaded models
- Connection pooling
- Request queuing
- GPU acceleration (CUDA/Metal)

### TOON Compression
- 30-50% token reduction
- Semantic preservation
- Bidirectional (compress/decompress)
- Provider-agnostic

## Migration Strategy

### Phase 1: Infrastructure
1. Create provider abstraction layer
2. Implement base interfaces
3. Refactor existing Ollama code into adapter

### Phase 2: WebLLM Integration
1. Add WebLLM client library
2. Implement WebLLM adapter
3. Create unified model catalog

### Phase 3: Provider Selection
1. Add provider detection
2. Implement selection logic
3. Create UI toggle

### Phase 4: TOON Integration
1. Implement TOON processor
2. Integrate with both providers
3. Add compression UI controls

## Testing Strategy

### Unit Tests
- Provider adapters (mock responses)
- Model catalog merging
- TOON compression/decompression
- Provider selection logic

### Integration Tests
- WebLLM + Ollama together
- Provider switching mid-conversation
- Model download across providers
- Error handling and fallbacks

### Browser Tests
- WebGPU availability detection
- WASM initialization
- IndexedDB caching
- Cross-browser compatibility

## Monitoring & Observability

### Metrics to Track
- Provider selection frequency
- WebLLM vs Ollama usage ratio
- Model load times per provider
- Inference latency comparison
- TOON compression ratios
- Error rates by provider

### Logging
- Provider selection decisions
- Model load events
- Provider switches
- TOON processing stats
- Performance benchmarks

## Future Enhancements

1. **Multi-Provider Load Balancing**: Use both providers simultaneously
2. **Hybrid Inference**: Start with WebLLM, offload to Ollama for complex queries
3. **Model Ensembling**: Combine responses from multiple providers
4. **Cloud Provider Support**: Add OpenAI/Anthropic as tertiary fallback
5. **Fine-Tuning**: Support provider-specific model customization

## References

- WebLLM Documentation: https://github.com/mlc-ai/web-llm
- Ollama API Reference: https://github.com/ollama/ollama/blob/main/docs/api.md
- TOON Format Specification: [To be linked]
- WebGPU Specification: https://www.w3.org/TR/webgpu/

---

**Document Version**: 1.0
**Last Updated**: 2025-11-18
**Author**: System Architect Agent (Hive Mind Swarm)
**Status**: Draft - Ready for Review
