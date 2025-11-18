# WebLLM Migration Strategy

## Overview

**Goal:** Replace Ollama (local server) with WebLLM (browser-native inference)

**Key Differences:**
- **Ollama:** Server-side, HTTP API, GGUF models, disk storage
- **WebLLM:** Client-side, WASM+WebGPU, quantized models, IndexedDB cache

## Files to Modify

### 1. Frontend (frontend/index.html)

#### Changes Required

**A. Add WebLLM Library**
```html
<script type="module">
  import * as webllm from "https://esm.run/@mlc-ai/web-llm";
</script>
```

**B. Replace Model Loading (line 274-313)**

Current:
```javascript
async function loadModels() {
  const availData = await fetchJSON(`${API}/models/available`);
  const dlData = await fetchJSON(`${API}/models/downloaded`);
  // ...
}
```

New:
```javascript
async function loadModels() {
  // Get WebLLM's built-in model list
  const models = webllm.prebuiltAppConfig.model_list;

  // Filter for compatibility (GPU/RAM requirements)
  availableModels = models.filter(m =>
    checkWebLLMCompatibility(m)
  ).map(m => ({
    name: m.model_id,
    display_name: formatWebLLMName(m.model_id),
    size_gb: estimateModelSize(m),
    // ...map other fields
  }));

  // Check which models are cached in IndexedDB
  downloadedModels = await getWebLLMCachedModels();
}
```

**C. Replace Chat Function (line 400-454)**

Current:
```javascript
async function sendMessage(text) {
  const data = await fetchJSON(`${API}/chat`, {
    method: 'POST',
    body: JSON.stringify({ message: text, model: modelToUse })
  });
  // Display data.response
}
```

New:
```javascript
let engine = null; // Initialize once

async function sendMessage(text) {
  // Initialize engine if needed
  if (!engine) {
    engine = await webllm.CreateMLCEngine(selectedModel, {
      initProgressCallback: (progress) => {
        // Show loading progress
        updateModelLoadingProgress(progress);
      }
    });
  }

  // Build messages array from conversation history
  const messages = buildMessageHistory(conversationId, text);

  // Stream completion
  const completion = await engine.chat.completions.create({
    messages: messages,
    stream: true
  });

  let reply = '';
  for await (const chunk of completion) {
    const delta = chunk.choices[0]?.delta?.content || '';
    reply += delta;
    // Update UI with streaming text
    updateStreamingMessage(delta);
  }
}
```

**D. Add WebGPU Detection**
```javascript
async function checkWebGPUSupport() {
  if (!navigator.gpu) {
    toast('WebGPU not supported. Please use Chrome/Edge 113+', 'error');
    return false;
  }
  return true;
}
```

**E. Model Download/Caching**
- WebLLM auto-downloads on first use
- Shows progress via `initProgressCallback`
- Caches in IndexedDB automatically
- No explicit download button needed (or repurpose for pre-caching)

### 2. Backend (NEW: backend/webllm_integration.py)

Create new integration module similar to `ollama_integration.py`:

```python
@dataclass
class WebLLMModelInfo:
    model_id: str  # e.g., "Llama-3.2-1B-Instruct-q4f16_1-MLC"
    display_name: str  # e.g., "Llama 3.2 1B"
    size_gb: float
    quantization: str  # e.g., "q4f16_1"
    vram_required_mb: int
    context_length: int
    compatible: bool
    compatibility_reason: Optional[str]

WEBLLM_MODEL_CATALOG = [
    {
        "model_id": "Llama-3.2-1B-Instruct-q4f16_1-MLC",
        "display_name": "Llama 3.2 1B",
        "size_gb": 0.8,  # Smaller due to quantization
        "quantization": "q4f16_1",
        "vram_required_mb": 1024,
        # ...
    },
    # Map other models...
]

class WebLLMIntegration:
    def get_catalog(self, vram_mb: int) -> List[WebLLMModelInfo]:
        """Return compatible WebLLM models based on available VRAM."""
        # Similar to ollama_integration.get_catalog()
        pass
```

### 3. Backend API (backend/main.py)

#### New Endpoint

```python
@app.get("/models/webllm")
async def get_webllm_models():
    """
    Get WebLLM-compatible models with browser compatibility checks.
    Returns models that can run via WebGPU in the browser.
    """
    webllm_integration = get_webllm_integration()

    # Estimate available VRAM (can't detect from server, use conservative estimate)
    models = webllm_integration.get_catalog(vram_mb=4096)

    return {"models": [asdict(m) for m in models]}
```

#### Modified Endpoint

```python
@app.get("/models/available")
async def get_available_models():
    """
    Get ALL models with BOTH Ollama and WebLLM options.
    """
    # Existing Ollama catalog code...

    # ADD: WebLLM models
    webllm_integration = get_webllm_integration()
    webllm_models = webllm_integration.get_catalog(vram_mb=4096)

    for m in webllm_models:
        all_models.append({
            "name": m.model_id,
            "display_name": m.display_name,
            "size_gb": m.size_gb,
            "source": "webllm",  # NEW: Distinguish from "ollama"
            # ...other fields
        })

    return {"models": all_models}
```

## Model Name Mapping

### Ollama → WebLLM

| Ollama | WebLLM | Notes |
|--------|--------|-------|
| `llama3.2:1b` | `Llama-3.2-1B-Instruct-q4f16_1-MLC` | Quantized |
| `llama3.2:3b` | `Llama-3.2-3B-Instruct-q4f16_1-MLC` | Quantized |
| `phi3:mini` | `Phi-3-mini-4k-instruct-q4f16_1-MLC` | - |
| `mistral:7b` | `Mistral-7B-Instruct-v0.3-q4f16_1-MLC` | - |
| `gemma2:2b` | `gemma-2-2b-it-q4f16_1-MLC` | - |

WebLLM model IDs: https://github.com/mlc-ai/web-llm/blob/main/src/config.ts

## Compatibility Checking

### WebLLM Requirements

1. **WebGPU Support** - Chrome/Edge 113+, Firefox Nightly
2. **VRAM** - Typically 2-8GB depending on model
3. **Browser Storage** - IndexedDB for model caching
4. **Network** - Initial download (models are 500MB-4GB)

### Detection Strategy

```javascript
async function checkWebLLMCompatibility(model) {
  // Check WebGPU
  if (!navigator.gpu) return false;

  // Estimate available VRAM (not directly accessible)
  const adapter = await navigator.gpu.requestAdapter();
  // Conservative estimate: assume 4GB VRAM minimum

  // Check storage
  if ('storage' in navigator && 'estimate' in navigator.storage) {
    const estimate = await navigator.storage.estimate();
    const availableGB = (estimate.quota - estimate.usage) / 1e9;
    if (availableGB < model.size_gb * 1.5) return false;
  }

  return true;
}
```

## Migration Phases

### Phase 1: Add WebLLM Support (Keep Ollama)
1. Add WebLLM to frontend as alternative
2. Create webllm_integration.py backend module
3. Update model selector to show "Source: Ollama/WebLLM"
4. User can choose between Ollama or WebLLM models

### Phase 2: Make WebLLM Default
1. Prioritize WebLLM models in dropdown
2. Only fallback to Ollama if WebGPU not supported
3. Show compatibility warnings

### Phase 3: Remove Ollama (Optional)
1. Remove ollama_integration.py
2. Remove Ollama API calls from main.py
3. Frontend becomes fully standalone

## Key Advantages of WebLLM

1. **No server required** - Pure client-side inference
2. **Privacy** - All data stays in browser
3. **Portability** - Works on any device with WebGPU
4. **No installation** - Just open the webpage
5. **Offline capable** - After initial model download

## Key Challenges

1. **Browser compatibility** - WebGPU still new
2. **Large downloads** - Models are 500MB-4GB
3. **VRAM limits** - Smaller models than Ollama
4. **Initial load time** - First inference can be slow
5. **Storage space** - IndexedDB has quotas
