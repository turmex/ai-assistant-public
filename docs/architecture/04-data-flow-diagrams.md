# Data Flow Diagrams: WebLLM/Ollama Dual-Mode System

## Overview

This document provides comprehensive data flow diagrams showing how data moves through the system for various operations in the dual-mode architecture.

## 1. System Initialization Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                      Application Startup                         │
└──────────────────────┬──────────────────────────────────────────┘
                       ↓
        ┌──────────────────────────────────┐
        │    Initialize Provider Factory    │
        └──────────────────┬────────────────┘
                           ↓
        ┌──────────────────────────────────────────────┐
        │         Detect Available Providers            │
        │  ┌─────────────────┐   ┌──────────────────┐  │
        │  │ Check WebLLM    │   │ Check Ollama     │  │
        │  │ - Browser caps  │   │ - Server status  │  │
        │  │ - WebGPU support│   │ - Health check   │  │
        │  └────────┬────────┘   └────────┬─────────┘  │
        └───────────┼─────────────────────┼────────────┘
                    ↓                     ↓
        ┌──────────────────────────────────────────────┐
        │      Initialize Detected Providers            │
        │  ┌──────────────────┐  ┌──────────────────┐  │
        │  │ WebLLM Adapter   │  │ Ollama Adapter   │  │
        │  │ - Load config    │  │ - Load config    │  │
        │  │ - Setup WebGPU   │  │ - Connect server │  │
        │  └────────┬─────────┘  └────────┬─────────┘  │
        └───────────┼─────────────────────┼────────────┘
                    ↓                     ↓
        ┌────────────────────────────────────────────────┐
        │      Initialize Unified Model Catalog          │
        │  - Fetch WebLLM models                         │
        │  - Fetch Ollama models                         │
        │  - Merge and normalize                         │
        │  - Calculate performance                       │
        │  - Select recommended model                    │
        └──────────────────┬─────────────────────────────┘
                           ↓
        ┌────────────────────────────────────────────────┐
        │       Select Active Provider                   │
        │  Priority:                                     │
        │  1. WebLLM (if available and healthy)          │
        │  2. Ollama (fallback)                          │
        │  3. Error if none available                    │
        └──────────────────┬─────────────────────────────┘
                           ↓
        ┌────────────────────────────────────────────────┐
        │          Application Ready                     │
        │  - Provider status: OK                         │
        │  - Models loaded: X total                      │
        │  - Recommended: [model]                        │
        └────────────────────────────────────────────────┘
```

## 2. Model Selection Flow

```
┌─────────────────────────────────────────────────────────────────┐
│               User Opens Model Selector UI                       │
└──────────────────────┬──────────────────────────────────────────┘
                       ↓
        ┌────────────────────────────────────────────────┐
        │     GET /models/unified?compatible_only=true   │
        └──────────────────┬─────────────────────────────┘
                           ↓
        ┌────────────────────────────────────────────────┐
        │         Unified Model Catalog                  │
        │  - Filter by hardware compatibility            │
        │  - Include provider availability               │
        │  - Include download status                     │
        │  - Include performance indicators              │
        └──────────────────┬─────────────────────────────┘
                           ↓
        ┌────────────────────────────────────────────────┐
        │         Return Model List with Metadata        │
        │  [                                             │
        │    {                                           │
        │      "id": "llama-3-8b",                       │
        │      "name": "Llama 3 8B",                     │
        │      "providers": ["webllm", "ollama"],        │
        │      "provider_info": {                        │
        │        "webllm": {                             │
        │          "downloaded": true,                   │
        │          "size_gb": 4.3                        │
        │        },                                      │
        │        "ollama": {                             │
        │          "downloaded": false,                  │
        │          "size_gb": 4.7                        │
        │        }                                       │
        │      },                                        │
        │      "performance": {                          │
        │        "level": "excellent",                   │
        │        "speed": "10-15 tok/s"                  │
        │      },                                        │
        │      "recommended": true                       │
        │    },                                          │
        │    ...                                         │
        │  ]                                             │
        └──────────────────┬─────────────────────────────┘
                           ↓
        ┌────────────────────────────────────────────────┐
        │            Display in UI                       │
        │  ┌──────────────────────────────────────────┐  │
        │  │  Llama 3 8B ⭐                           │  │
        │  │  [webllm] [ollama]                       │  │
        │  │  🟢 10-15 tok/s  |  4.3 GB  |  ✓ Ready  │  │
        │  ├──────────────────────────────────────────┤  │
        │  │  Mistral 7B                              │  │
        │  │  [ollama]                                │  │
        │  │  🟡 5-10 tok/s  |  4.1 GB  |  ⬇ Download│  │
        │  └──────────────────────────────────────────┘  │
        └────────────────────────────────────────────────┘
```

## 3. Chat Message Flow (WebLLM Path)

```
┌─────────────────────────────────────────────────────────────────┐
│             User Sends Message: "Hello, world!"                  │
└──────────────────────┬──────────────────────────────────────────┘
                       ↓
        ┌────────────────────────────────────────────────┐
        │     POST /chat                                 │
        │     {                                          │
        │       "message": "Hello, world!",              │
        │       "conversation_id": "123",                │
        │       "temperature": 0.7                       │
        │     }                                          │
        └──────────────────┬─────────────────────────────┘
                           ↓
        ┌────────────────────────────────────────────────┐
        │         Provider Factory                       │
        │  - Get active provider                         │
        │  - Current: WebLLM (browser-based)             │
        └──────────────────┬─────────────────────────────┘
                           ↓
        ┌────────────────────────────────────────────────┐
        │      Load Conversation Context                 │
        │  - Fetch from database (conversation_id: 123)  │
        │  - Convert to Message[] format                 │
        │  - Apply TOON compression (if enabled)         │
        └──────────────────┬─────────────────────────────┘
                           ↓
        ┌────────────────────────────────────────────────┐
        │       Prepare Generation Config                │
        │  {                                             │
        │    temperature: 0.7,                           │
        │    max_tokens: 2048,                           │
        │    stop_sequences: [],                         │
        │    stream: true                                │
        │  }                                             │
        └──────────────────┬─────────────────────────────┘
                           ↓
        ┌────────────────────────────────────────────────┐
        │       WebLLM Adapter.generate()                │
        │  - Format context for WebLLM                   │
        │  - Send to browser-based WebLLM instance       │
        │  - (Note: Actual inference happens in browser) │
        └──────────────────┬─────────────────────────────┘
                           ↓
        ┌────────────────────────────────────────────────┐
        │          WebLLM Browser Inference              │
        │  ┌──────────────────────────────────────────┐  │
        │  │  1. Load model (if not already loaded)   │  │
        │  │  2. Tokenize input                       │  │
        │  │  3. WebGPU inference                     │  │
        │  │  4. Stream tokens back                   │  │
        │  └──────────────────────────────────────────┘  │
        └──────────────────┬─────────────────────────────┘
                           ↓
        ┌────────────────────────────────────────────────┐
        │       Receive Generated Response               │
        │  GenerationResult {                            │
        │    text: "Hello! How can I help you today?",   │
        │    provider: "webllm",                         │
        │    model_id: "llama-3-8b",                     │
        │    tokens_used: 42,                            │
        │    latency_ms: 245                             │
        │  }                                             │
        └──────────────────┬─────────────────────────────┘
                           ↓
        ┌────────────────────────────────────────────────┐
        │       Save to Database                         │
        │  - Store user message                          │
        │  - Store assistant response                    │
        │  - Update conversation context                 │
        └──────────────────┬─────────────────────────────┘
                           ↓
        ┌────────────────────────────────────────────────┐
        │       Return Response to Frontend              │
        │  {                                             │
        │    "response": "Hello! How can I help...",     │
        │    "provider": "webllm",                       │
        │    "model": "llama-3-8b",                      │
        │    "tokens_used": 42,                          │
        │    "latency_ms": 245                           │
        │  }                                             │
        └──────────────────┬─────────────────────────────┘
                           ↓
        ┌────────────────────────────────────────────────┐
        │         Display in UI                          │
        │  ┌──────────────────────────────────────────┐  │
        │  │  You: Hello, world!                      │  │
        │  ├──────────────────────────────────────────┤  │
        │  │  Assistant (webllm):                     │  │
        │  │  Hello! How can I help you today?        │  │
        │  │  [245ms | 42 tokens]                     │  │
        │  └──────────────────────────────────────────┘  │
        └────────────────────────────────────────────────┘
```

## 4. Chat Message Flow (Ollama Fallback Path)

```
┌─────────────────────────────────────────────────────────────────┐
│             User Sends Message (WebLLM Unavailable)              │
└──────────────────────┬──────────────────────────────────────────┘
                       ↓
        ┌────────────────────────────────────────────────┐
        │     Provider Factory                           │
        │  - Check WebLLM: unavailable ❌                │
        │  - Fallback to Ollama                          │
        │  - Current: Ollama (server-based)              │
        └──────────────────┬─────────────────────────────┘
                           ↓
        ┌────────────────────────────────────────────────┐
        │      Load Conversation Context                 │
        │  (Same as WebLLM path)                         │
        └──────────────────┬─────────────────────────────┘
                           ↓
        ┌────────────────────────────────────────────────┐
        │       Ollama Adapter.generate()                │
        │  - Format context for Ollama                   │
        │  - Send HTTP request to Ollama server          │
        └──────────────────┬─────────────────────────────┘
                           ↓
        ┌────────────────────────────────────────────────┐
        │          Ollama Server Inference               │
        │  POST http://localhost:11434/api/chat          │
        │  {                                             │
        │    "model": "llama3.1:8b",                     │
        │    "messages": [...],                          │
        │    "stream": true                              │
        │  }                                             │
        └──────────────────┬─────────────────────────────┘
                           ↓
        ┌────────────────────────────────────────────────┐
        │       Receive Generated Response               │
        │  GenerationResult {                            │
        │    text: "Hello! How can I help you today?",   │
        │    provider: "ollama",                         │
        │    model_id: "llama3.1:8b",                    │
        │    tokens_used: 42,                            │
        │    latency_ms: 180                             │
        │  }                                             │
        └──────────────────┬─────────────────────────────┘
                           ↓
        ┌────────────────────────────────────────────────┐
        │       Save & Return (Same as WebLLM)           │
        └────────────────────────────────────────────────┘
```

## 5. Provider Switching Flow

```
┌─────────────────────────────────────────────────────────────────┐
│          User Clicks "Switch to Ollama" Button                   │
└──────────────────────┬──────────────────────────────────────────┘
                       ↓
        ┌────────────────────────────────────────────────┐
        │     POST /providers/select                     │
        │     { "provider": "ollama" }                   │
        └──────────────────┬─────────────────────────────┘
                           ↓
        ┌────────────────────────────────────────────────┐
        │       Validate Provider Availability           │
        │  - Check if "ollama" is initialized            │
        │  - Check provider health status                │
        └──────────────────┬─────────────────────────────┘
                           ↓
                  ┌────────┴────────┐
                  ↓                 ↓
        ┌─────────────────┐  ┌──────────────────┐
        │  Available ✓    │  │  Unavailable ❌  │
        └────────┬────────┘  └────────┬─────────┘
                 ↓                    ↓
        ┌─────────────────┐  ┌──────────────────┐
        │  Set Active     │  │  Return Error    │
        │  Provider       │  │  400: Provider   │
        │  to Ollama      │  │  not available   │
        └────────┬────────┘  └──────────────────┘
                 ↓
        ┌────────────────────────────────────────────────┐
        │       Update Preferred Provider                │
        │  - Set preferred_provider = Ollama             │
        │  - All future requests use Ollama              │
        │  - Until user switches again                   │
        └──────────────────┬─────────────────────────────┘
                           ↓
        ┌────────────────────────────────────────────────┐
        │       Return Success                           │
        │  {                                             │
        │    "success": true,                            │
        │    "active_provider": "ollama"                 │
        │  }                                             │
        └──────────────────┬─────────────────────────────┘
                           ↓
        ┌────────────────────────────────────────────────┐
        │       Update UI                                │
        │  - Show "Active: Ollama" badge                 │
        │  - Reload model list (Ollama models)           │
        │  - Update status indicators                    │
        └────────────────────────────────────────────────┘
```

## 6. Model Download Flow

```
┌─────────────────────────────────────────────────────────────────┐
│        User Clicks "Download" on Mistral 7B (Ollama)            │
└──────────────────────┬──────────────────────────────────────────┘
                       ↓
        ┌────────────────────────────────────────────────┐
        │     POST /models/download                      │
        │     {                                          │
        │       "model_id": "mistral-7b",                │
        │       "provider": "ollama"                     │
        │     }                                          │
        └──────────────────┬─────────────────────────────┘
                           ↓
        ┌────────────────────────────────────────────────┐
        │       Get Provider Instance                    │
        │  - Factory.get_provider("ollama")              │
        └──────────────────┬─────────────────────────────┘
                           ↓
        ┌────────────────────────────────────────────────┐
        │       Ollama Adapter.download_model()          │
        │  - Map unified model_id to Ollama name         │
        │  - "mistral-7b" → "mistral:7b"                 │
        └──────────────────┬─────────────────────────────┘
                           ↓
        ┌────────────────────────────────────────────────┐
        │       Ollama Server Pull                       │
        │  POST http://localhost:11434/api/pull          │
        │  { "name": "mistral:7b", "stream": true }      │
        └──────────────────┬─────────────────────────────┘
                           ↓
        ┌────────────────────────────────────────────────┐
        │       Stream Download Progress                 │
        │  {                                             │
        │    "status": "downloading",                    │
        │    "completed": 1024000,                       │
        │    "total": 4100000,                           │
        │    "percent": 25.0                             │
        │  }                                             │
        │  → progress_callback(25.0)                     │
        └──────────────────┬─────────────────────────────┘
                           ↓
        ┌────────────────────────────────────────────────┐
        │       Update UI Progress Bar                   │
        │  ┌──────────────────────────────────────────┐  │
        │  │  Downloading Mistral 7B                  │  │
        │  │  ████████░░░░░░░░░░░░░░░░░░░░ 25%       │  │
        │  │  1.0 GB / 4.1 GB                         │  │
        │  └──────────────────────────────────────────┘  │
        └──────────────────┬─────────────────────────────┘
                           ↓
        ┌────────────────────────────────────────────────┐
        │       Download Complete                        │
        │  { "status": "success" }                       │
        └──────────────────┬─────────────────────────────┘
                           ↓
        ┌────────────────────────────────────────────────┐
        │       Update Catalog                           │
        │  - Mark model as downloaded for Ollama         │
        │  - provider_info["ollama"].downloaded = true   │
        └──────────────────┬─────────────────────────────┘
                           ↓
        ┌────────────────────────────────────────────────┐
        │       Refresh UI                               │
        │  - Remove "Download" button                    │
        │  - Show "✓ Ready" status                       │
        │  - Model now selectable                        │
        └────────────────────────────────────────────────┘
```

## 7. TOON Format Processing Flow

```
┌─────────────────────────────────────────────────────────────────┐
│          Long Conversation (Context > 4000 tokens)               │
└──────────────────────┬──────────────────────────────────────────┘
                       ↓
        ┌────────────────────────────────────────────────┐
        │       Load Conversation Context                │
        │  - 15 messages                                 │
        │  - Total: ~5500 tokens                         │
        │  - Model context limit: 4096 tokens            │
        └──────────────────┬─────────────────────────────┘
                           ↓
        ┌────────────────────────────────────────────────┐
        │       Detect Context Overflow                  │
        │  if tokens > context_limit:                    │
        │      apply_toon_compression()                  │
        └──────────────────┬─────────────────────────────┘
                           ↓
        ┌────────────────────────────────────────────────┐
        │       TOON Processor.compress()                │
        │  ┌──────────────────────────────────────────┐  │
        │  │ 1. Identify oldest messages              │  │
        │  │ 2. Extract key information               │  │
        │  │ 3. Semantic summarization                │  │
        │  │ 4. Compress to TOON format               │  │
        │  └──────────────────────────────────────────┘  │
        └──────────────────┬─────────────────────────────┘
                           ↓
        ┌────────────────────────────────────────────────┐
        │       Compressed Context                       │
        │  Original: 15 messages, 5500 tokens            │
        │  Compressed: 10 messages, 3200 tokens (42%)    │
        │  ┌──────────────────────────────────────────┐  │
        │  │ [TOON_SUMMARY]                           │  │
        │  │ Previous 5 messages discussed:           │  │
        │  │ - User asked about Python basics         │  │
        │  │ - Assistant explained variables          │  │
        │  │ - User requested examples                │  │
        │  │ [/TOON_SUMMARY]                          │  │
        │  │ ... (recent 10 messages uncompressed)    │  │
        │  └──────────────────────────────────────────┘  │
        └──────────────────┬─────────────────────────────┘
                           ↓
        ┌────────────────────────────────────────────────┐
        │       Send to Provider                         │
        │  - Compressed context fits in window           │
        │  - Semantic information preserved              │
        │  - Model can still access key context          │
        └──────────────────┬─────────────────────────────┘
                           ↓
        ┌────────────────────────────────────────────────┐
        │       Store Compression Metadata               │
        │  - Original token count: 5500                  │
        │  - Compressed token count: 3200                │
        │  - Compression ratio: 42%                      │
        │  - Timestamp: 2025-11-18T12:30:00Z             │
        └────────────────────────────────────────────────┘
```

## 8. Error Handling Flow

```
┌─────────────────────────────────────────────────────────────────┐
│              Provider Failure During Generation                  │
└──────────────────────┬──────────────────────────────────────────┘
                       ↓
        ┌────────────────────────────────────────────────┐
        │       WebLLM Adapter.generate()                │
        │  → throws WebGPUError                          │
        └──────────────────┬─────────────────────────────┘
                           ↓
        ┌────────────────────────────────────────────────┐
        │       Catch Exception                          │
        │  - Log error: "WebLLM inference failed"        │
        │  - Mark provider unhealthy                     │
        └──────────────────┬─────────────────────────────┘
                           ↓
        ┌────────────────────────────────────────────────┐
        │       Attempt Automatic Fallback               │
        │  - Factory.select_active_provider()            │
        │  - Try next available provider (Ollama)        │
        └──────────────────┬─────────────────────────────┘
                           ↓
                  ┌────────┴────────┐
                  ↓                 ↓
        ┌─────────────────┐  ┌──────────────────┐
        │ Fallback OK ✓   │  │ No Fallback ❌   │
        └────────┬────────┘  └────────┬─────────┘
                 ↓                    ↓
        ┌─────────────────┐  ┌──────────────────┐
        │  Retry with     │  │  Return Error    │
        │  Ollama         │  │  503: No healthy │
        │  → Success      │  │  providers       │
        └────────┬────────┘  └──────────────────┘
                 ↓
        ┌────────────────────────────────────────────────┐
        │       Return Response with Fallback Info       │
        │  {                                             │
        │    "response": "Hello! How can I help...",     │
        │    "provider": "ollama",                       │
        │    "fallback_from": "webllm",                  │
        │    "fallback_reason": "WebGPU error"           │
        │  }                                             │
        └──────────────────┬─────────────────────────────┘
                           ↓
        ┌────────────────────────────────────────────────┐
        │       Display Warning in UI                    │
        │  ⚠ Switched to Ollama due to WebLLM error      │
        └────────────────────────────────────────────────┘
```

## Key Observations

1. **Provider Independence**: Data flows through abstraction layer, allowing seamless provider switching
2. **Automatic Fallback**: System automatically tries alternative providers on failure
3. **Context Management**: TOON compression applied transparently when needed
4. **Unified Interface**: All providers return consistent data structures
5. **Error Resilience**: Multiple layers of error handling with graceful degradation

---

**Document Version**: 1.0
**Last Updated**: 2025-11-18
**Status**: Draft - Ready for Review
