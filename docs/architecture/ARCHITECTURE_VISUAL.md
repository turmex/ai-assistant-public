# WebLLM/Ollama Architecture - Visual Diagrams

## System Architecture Overview

```
┌───────────────────────────────────────────────────────────────────────┐
│                              USER INTERFACE                            │
│  ┌──────────────────────────────────────────────────────────────────┐ │
│  │                    React/Vue Frontend (SPA)                       │ │
│  │  • Chat interface       • Provider selector                       │ │
│  │  • Model dropdown       • Status indicators                       │ │
│  │  • Settings panel       • Performance metrics                     │ │
│  └────────────────┬───────────────────────┬─────────────────────────┘ │
└───────────────────┼───────────────────────┼────────────────────────────┘
                    │                       │
         ┌──────────┴──────────┐   ┌────────┴───────────┐
         │   WebLLM Client     │   │   REST API Calls   │
         │   (Browser-based)   │   │   (Backend API)    │
         └──────────┬──────────┘   └────────┬───────────┘
                    │                       │
         ┌──────────▼──────────┐           │
         │  WebGPU Inference   │           │
         │  • Local models     │           │
         │  • IndexedDB cache  │           │
         │  • Privacy-first    │           │
         └─────────────────────┘           │
                                            │
┌───────────────────────────────────────────▼────────────────────────────┐
│                        BACKEND LAYER (FastAPI)                          │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                  LLM Provider Factory                             │  │
│  │  • Provider detection      • Health monitoring                    │  │
│  │  • Lifecycle management    • Automatic fallback                   │  │
│  │  • Runtime selection       • Error handling                       │  │
│  └──────────────┬───────────────────────┬─────────────────────────────│
│                 │                       │                              │
│  ┌──────────────▼──────────┐   ┌───────▼────────────┐                │
│  │   WebLLM Adapter        │   │   Ollama Adapter    │                │
│  │  • Browser coordination │   │  • Server API calls │                │
│  │  • Model metadata       │   │  • HTTP client      │                │
│  │  • Status tracking      │   │  • Stream handling  │                │
│  └──────────────┬──────────┘   └───────┬────────────┘                │
│                 │                       │                              │
│                 └───────────┬───────────┘                              │
│                             │                                          │
│  ┌──────────────────────────▼────────────────────────────────┐        │
│  │              Unified Model Catalog                         │        │
│  │  • Model merging        • Performance calculation          │        │
│  │  • Metadata normalization  • Hardware compatibility        │        │
│  │  • Search & filter      • Download tracking                │        │
│  └──────────────────────────┬────────────────────────────────┘        │
│                             │                                          │
│  ┌──────────────────────────▼────────────────────────────────┐        │
│  │              TOON Format Processor                         │        │
│  │  • Context compression  • Token optimization               │        │
│  │  • Semantic preservation  • Window management              │        │
│  └──────────────────────────┬────────────────────────────────┘        │
│                             │                                          │
│  ┌──────────────────────────▼────────────────────────────────┐        │
│  │           Conversation & State Management                  │        │
│  │  • SQLite persistence   • Context tracking                 │        │
│  │  • Message history      • Provider-agnostic storage        │        │
│  └────────────────────────────────────────────────────────────┘        │
└─────────────────────────────────────────────────────────────────────────┘
                             │
                             ▼
         ┌───────────────────────────────────┐
         │     Ollama Server (Optional)      │
         │  • Local LLM inference            │
         │  • Model management               │
         │  • GPU acceleration               │
         └───────────────────────────────────┘
```

## Provider Selection Flow

```
                    ┌─────────────────┐
                    │  User Request   │
                    └────────┬────────┘
                             │
                             ▼
                ┌────────────────────────┐
                │  Provider Factory      │
                │  get_provider()        │
                └────────┬───────────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │  WebLLM Available?   │
              └──────┬───────┬───────┘
                     │       │
                YES  │       │  NO
                     ▼       ▼
         ┌───────────────────────────────┐
         │                               │
    ┌────▼─────┐              ┌──────────▼──────┐
    │ WebLLM   │              │ Ollama Running? │
    │ Healthy? │              └──────┬────┬─────┘
    └────┬─────┘                     │    │
         │                      YES  │    │  NO
    YES  │  NO                       ▼    ▼
         │  │              ┌──────────────────────┐
         ▼  │              │                      │
    ┌────────▼────┐   ┌────▼───────┐    ┌────────▼────────┐
    │ USE WEBLLM  │   │ USE OLLAMA │    │ ERROR: No       │
    │ ✓ Privacy   │   │ ✓ Reliable │    │ providers       │
    │ ✓ Offline   │   │ ✓ Fast     │    │ available       │
    └─────────────┘   └────────────┘    └─────────────────┘
```

## Component Interaction Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                          Frontend (Browser)                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ChatUI ──────► ModelSelector ──────► ProviderToggle                │
│     │                 │                      │                       │
│     │                 │                      │                       │
│     ▼                 ▼                      ▼                       │
│  WebLLMClient    ModelCatalog         ProviderStatus                │
│     │                 │                      │                       │
└─────┼─────────────────┼──────────────────────┼───────────────────────┘
      │                 │                      │
      │ (browser)       │ (HTTP)               │ (HTTP)
      │                 │                      │
┌─────┼─────────────────┼──────────────────────┼───────────────────────┐
│     │                 │                      │                       │
│     │                 ▼                      ▼                       │
│     │          GET /models/unified    GET /providers                │
│     │                 │                      │                       │
│     │                 ▼                      ▼                       │
│     │          UnifiedCatalog         ProviderFactory                │
│     │                 │                      │                       │
│     │                 │       ┌──────────────┴──────────┐           │
│     │                 │       │                         │           │
│     │                 ▼       ▼                         ▼           │
│     │             WebLLMAdapter                    OllamaAdapter     │
│     │                 │                                 │           │
│     │                 └────────────┬────────────────────┘           │
│     │                              │                                │
│     │                              ▼                                │
│     │                      POST /chat                               │
│     │                              │                                │
│     │                              ▼                                │
│     │                  ConversationManager                          │
│     │                              │                                │
│     │                              ▼                                │
│     │                       TOONProcessor                           │
│     │                              │                                │
│     │                              ▼                                │
│     │                        Database (SQLite)                      │
│     │                                                               │
│     └───────────────────────────────────────────────────────────────│
│                          Backend (FastAPI)                          │
└─────────────────────────────────────────────────────────────────────┘
```

## Class Hierarchy

```
                    ┌──────────────────┐
                    │  LLMProvider     │
                    │  (ABC)           │
                    └────────┬─────────┘
                             │
                 ┌───────────┴───────────┐
                 │                       │
         ┌───────▼────────┐     ┌───────▼────────┐
         │ WebLLMAdapter  │     │ OllamaAdapter  │
         ├────────────────┤     ├────────────────┤
         │ + initialize() │     │ + initialize() │
         │ + get_status() │     │ + get_status() │
         │ + list_models()│     │ + list_models()│
         │ + load_model() │     │ + load_model() │
         │ + generate()   │     │ + generate()   │
         └────────────────┘     └────────────────┘


                    ┌──────────────────┐
                    │ ProviderFactory  │
                    ├──────────────────┤
                    │ - providers: {}  │
                    │ - active: ?      │
                    ├──────────────────┤
                    │ + initialize()   │
                    │ + get_provider() │
                    │ + set_active()   │
                    │ + get_statuses() │
                    └──────────────────┘


         ┌──────────────────────────────────────┐
         │      UnifiedModelCatalog             │
         ├──────────────────────────────────────┤
         │ - catalog: Dict[str, UnifiedModel]  │
         ├──────────────────────────────────────┤
         │ + initialize()                       │
         │ + get_all_models()                   │
         │ + search_models()                    │
         │ + get_recommended()                  │
         └──────────────────────────────────────┘
```

## Data Model Relationships

```
┌─────────────────────────────────────────────────────────────────┐
│                    UnifiedModelInfo                              │
├─────────────────────────────────────────────────────────────────┤
│ id: str                                                          │
│ name: str                                                        │
│ family: str                                                      │
│ providers: List[str] ────┐                                       │
│ provider_info: Dict ─────┼─────┐                                │
│ performance: PerformanceInfo ───┼─────┐                         │
│ recommended: bool               │     │                         │
└─────────────────────────────────┼─────┼─────┐                   │
                                  │     │     │                   │
         ┌────────────────────────┘     │     │                   │
         │                              │     │                   │
         ▼                              │     │                   │
┌─────────────────────────┐             │     │                   │
│  List[str]              │             │     │                   │
│  ["webllm", "ollama"]   │             │     │                   │
└─────────────────────────┘             │     │                   │
                                        │     │                   │
         ┌──────────────────────────────┘     │                   │
         │                                    │                   │
         ▼                                    │                   │
┌─────────────────────────┐                   │                   │
│ Dict[str, ProviderInfo] │                   │                   │
│ {                       │                   │                   │
│   "webllm": {...},      │────┐              │                   │
│   "ollama": {...}       │    │              │                   │
│ }                       │    │              │                   │
└─────────────────────────┘    │              │                   │
                               │              │                   │
         ┌─────────────────────┘              │                   │
         │                                    │                   │
         ▼                                    ▼                   │
┌─────────────────────────┐    ┌─────────────────────────┐       │
│  ProviderModelInfo      │    │  PerformanceInfo        │       │
├─────────────────────────┤    ├─────────────────────────┤       │
│ provider: str           │    │ level: PerformanceLevel │       │
│ model_id: str           │    │ estimated_speed: str    │       │
│ downloaded: bool        │    │ ram_required_gb: int    │       │
│ download_size_gb: float │    │ compatible: bool        │       │
│ supports_streaming: bool│    │ compatibility_reason: ? │       │
│ max_context_length: int │    └─────────────────────────┘       │
└─────────────────────────┘                                      │
                                                                 │
         ┌───────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────┐
│    recommended: bool    │
│    (hardware-based)     │
└─────────────────────────┘
```

## Request Flow: Chat Message

```
1. User Input
   │
   ├─► "Hello, world!"
   │
   ▼
2. Frontend
   │
   ├─► POST /chat { message: "Hello, world!" }
   │
   ▼
3. Backend: FastAPI
   │
   ├─► Validate request
   │
   ▼
4. Provider Factory
   │
   ├─► Get active provider (WebLLM)
   │
   ▼
5. Conversation Manager
   │
   ├─► Load conversation history
   ├─► Convert to Message[] format
   │
   ▼
6. TOON Processor (if needed)
   │
   ├─► Check token count
   ├─► Compress if > context limit
   │
   ▼
7. WebLLM Adapter
   │
   ├─► Format for WebLLM
   ├─► Call WebLLM generate()
   │
   ▼
8. WebLLM (Browser)
   │
   ├─► Load model (if not cached)
   ├─► WebGPU inference
   ├─► Stream tokens
   │
   ▼
9. Adapter: Collect Response
   │
   ├─► GenerationResult { text, provider, tokens, latency }
   │
   ▼
10. Save to Database
    │
    ├─► Store user message
    ├─► Store assistant response
    │
    ▼
11. Return to Frontend
    │
    ├─► { response, provider, model, tokens, latency }
    │
    ▼
12. Display in UI
    │
    └─► Assistant: "Hello! How can I help you today?"
        [webllm | 245ms | 42 tokens]
```

## Error Handling Flow

```
                ┌──────────────┐
                │ Provider Call│
                └──────┬───────┘
                       │
                       ▼
                ┌──────────────┐
                │   Try WebLLM │
                └──────┬───────┘
                       │
                ┌──────┴──────┐
                │             │
            SUCCESS        ERROR
                │             │
                ▼             ▼
        ┌───────────┐  ┌────────────┐
        │  Return   │  │ Log Error  │
        │  Result   │  │ Mark       │
        └───────────┘  │ Unhealthy  │
                       └─────┬──────┘
                             │
                             ▼
                       ┌────────────┐
                       │   Retry    │
                       │   Once?    │
                       └─────┬──────┘
                             │
                       ┌─────┴─────┐
                       │           │
                     YES          NO
                       │           │
                       ▼           ▼
                ┌────────────┐  ┌───────────┐
                │Try Again   │  │  Try      │
                └─────┬──────┘  │  Fallback │
                      │         │  (Ollama) │
                      │         └─────┬─────┘
                      │               │
                ┌─────┴─────┐         │
                │           │         │
            SUCCESS      ERROR        │
                │           │         │
                ▼           ▼         ▼
        ┌───────────┐  ┌─────────────────┐
        │  Return   │  │   Ollama Try    │
        │  Result   │  └────────┬────────┘
        └───────────┘           │
                          ┌─────┴─────┐
                          │           │
                      SUCCESS      ERROR
                          │           │
                          ▼           ▼
                  ┌───────────┐  ┌────────────┐
                  │  Return   │  │ Return 503 │
                  │  Result + │  │ No healthy │
                  │  Fallback │  │ providers  │
                  │  Indicator│  └────────────┘
                  └───────────┘
```

## TOON Compression Flow

```
┌───────────────────────────────────────────────────────────┐
│         Long Conversation (5500 tokens)                    │
│  ┌─────────────────────────────────────────────────────┐  │
│  │ Message 1 (100 tokens)                              │  │
│  │ Message 2 (150 tokens)                              │  │
│  │ Message 3 (200 tokens)                              │  │
│  │ ...                                                 │  │
│  │ Message 15 (300 tokens)                             │  │
│  └─────────────────────────────────────────────────────┘  │
└──────────────────┬────────────────────────────────────────┘
                   │
                   ▼
         ┌─────────────────────┐
         │ Token Count Check   │
         │ 5500 > 4096 limit   │
         └──────────┬──────────┘
                    │
                    ▼
         ┌─────────────────────┐
         │  TOON Processor     │
         │  • Identify old     │
         │  • Extract key info │
         │  • Summarize        │
         │  • Compress         │
         └──────────┬──────────┘
                    │
                    ▼
┌───────────────────────────────────────────────────────────┐
│      Compressed Context (3200 tokens)                      │
│  ┌─────────────────────────────────────────────────────┐  │
│  │ [TOON_SUMMARY]                                      │  │
│  │ Previous 5 messages:                                │  │
│  │ - User asked about Python                           │  │
│  │ - Assistant explained variables                     │  │
│  │ - User requested examples                           │  │
│  │ [/TOON_SUMMARY]                                     │  │
│  │ Message 11 (280 tokens)                             │  │
│  │ Message 12 (290 tokens)                             │  │
│  │ Message 13 (300 tokens)                             │  │
│  │ Message 14 (310 tokens)                             │  │
│  │ Message 15 (300 tokens)                             │  │
│  └─────────────────────────────────────────────────────┘  │
└──────────────────┬────────────────────────────────────────┘
                   │
                   ▼
         ┌─────────────────────┐
         │  Send to Provider   │
         │  ✓ Fits in window   │
         │  ✓ Context preserved│
         └─────────────────────┘
```

---

**Document Version**: 1.0
**Created**: 2025-11-18
**Status**: Complete
**Total Diagrams**: 10 comprehensive visual representations
