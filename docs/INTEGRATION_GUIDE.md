# WebLLM Integration Guide

This guide explains how to integrate the new WebLLM provider system into your AI Assistant application.

## Architecture Overview

The integration adds:
1. **Provider Abstraction Layer** - Base interfaces for all LLM providers
2. **WebLLM Provider** - Browser-based LLM using WebGPU
3. **Provider Manager** - Handles switching between providers
4. **Provider API Endpoints** - RESTful API for provider management
5. **Provider Toggle UI** - User interface for switching providers
6. **TOON Format** - Token optimization for reducing context length

## Files Created

### Backend (Python)
- `/backend/src/providers/base_provider.py` - Base provider interface
- `/backend/src/providers/webllm_provider.py` - WebLLM implementation
- `/backend/src/providers/provider_manager.py` - Provider management logic
- `/backend/src/providers/__init__.py` - Package exports
- `/backend/src/api/provider_endpoints.py` - Provider REST API
- `/backend/src/api/__init__.py` - API package exports
- `/backend/src/utils/toon_format.py` - Token optimization utility

### Frontend (JavaScript)
- `/frontend/src/webllm-integration.js` - WebLLM client wrapper
- `/frontend/src/provider-toggle.js` - Provider toggle component

### Configuration
- `/config/provider-config.json` - Provider configuration

## Integration Steps

### Step 1: Update main.py

Add these imports at the top of `backend/main.py`:

```python
# Add after existing imports
from src.providers.webllm_provider import WebLLMProvider
from src.providers.provider_manager import get_provider_manager
from src.api import provider_router
```

Add provider initialization in the `lifespan` function (after line ~115):

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    global hardware_info

    logger.info("🚀 Starting AI Assistant Backend...")

    # ... existing DB and hardware detection code ...

    # Initialize Provider Manager
    try:
        logger.info("Initializing provider manager...")
        provider_manager = get_provider_manager()

        # Register WebLLM provider
        webllm_provider = WebLLMProvider()
        await provider_manager.register_provider(webllm_provider)

        # TODO: Register Ollama provider (adapt existing ollama_integration.py)
        # ollama_provider = OllamaProvider()
        # await provider_manager.register_provider(ollama_provider)

        logger.info("✓ Provider manager initialized")
    except Exception as e:
        logger.error(f"✗ Provider manager initialization failed: {e}")

    # ... rest of lifespan code ...
```

Add provider router to the app (after line ~140):

```python
# Add provider endpoints
app.include_router(provider_router)
```

### Step 2: Update frontend/index.html

Add these imports in the `<head>` section:

```html
<!-- WebLLM Integration -->
<script type="module">
  import webllmClient from './src/webllm-integration.js';
  import ProviderToggle from './src/provider-toggle.js';

  window.webllmClient = webllmClient;
  window.ProviderToggle = ProviderToggle;
</script>
```

Add provider toggle container in the header (after line ~57):

```html
<div id="providerToggle" class="mb-4"></div>
```

Add provider toggle styles in the `<style>` section:

```css
<style>
  /* ... existing styles ... */

  /* Provider Toggle Styles */
  .provider-toggle-wrapper {
    margin-bottom: 1rem;
  }

  .provider-toggle-container {
    border-radius: 1rem;
    border: 1px solid rgba(100, 116, 139, 0.6);
    background: linear-gradient(to bottom right, rgba(30, 41, 59, 0.7), rgba(30, 41, 59, 0.3));
    padding: 1rem;
  }

  .provider-toggle-label {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 0.75rem;
    font-size: 0.875rem;
    font-weight: 600;
    color: rgb(226, 232, 240);
  }

  .provider-icon {
    width: 1.25rem;
    height: 1.25rem;
  }

  .provider-options {
    display: flex;
    gap: 0.5rem;
    margin-bottom: 1rem;
  }

  .provider-option {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    padding: 0.75rem 1rem;
    border-radius: 0.75rem;
    border: 1px solid rgba(100, 116, 139, 0.6);
    background: rgba(15, 23, 42, 0.6);
    color: rgb(203, 213, 225);
    cursor: pointer;
    transition: all 0.2s;
  }

  .provider-option:hover {
    border-color: rgba(99, 102, 241, 0.6);
    background: rgba(30, 41, 59, 0.6);
  }

  .provider-option.active {
    border-color: rgba(99, 102, 241, 0.8);
    background: linear-gradient(to bottom right, rgba(99, 102, 241, 0.2), rgba(6, 182, 212, 0.2));
    color: rgb(255, 255, 255);
  }

  .provider-option-icon {
    width: 1.25rem;
    height: 1.25rem;
  }

  .provider-option-text {
    font-weight: 500;
  }

  .provider-badge {
    font-size: 0.625rem;
    padding: 0.125rem 0.375rem;
    border-radius: 0.375rem;
    background: rgba(99, 102, 241, 0.3);
    border: 1px solid rgba(99, 102, 241, 0.4);
  }

  .provider-info {
    border-radius: 0.5rem;
    background: rgba(15, 23, 42, 0.4);
    padding: 0.75rem;
  }

  .provider-info-content {
    font-size: 0.75rem;
    color: rgb(203, 213, 225);
  }

  .provider-info-header {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 0.5rem;
    font-weight: 600;
  }

  .provider-info-icon {
    font-size: 1.25rem;
  }

  .provider-info-description {
    margin-bottom: 0.5rem;
    color: rgb(148, 163, 184);
  }

  .provider-info-features {
    margin: 0;
    padding-left: 1.25rem;
    list-style-type: disc;
  }

  .provider-info-features li {
    margin-bottom: 0.25rem;
    color: rgb(148, 163, 184);
  }
</style>
```

### Step 3: Initialize Provider Toggle

Add this code in the `init` function at the bottom of `<script>`:

```javascript
// Initialize provider toggle
const providerToggle = new window.ProviderToggle({
  defaultProvider: 'webllm',
  containerId: 'providerToggle',
  onProviderChange: async (provider) => {
    console.log('Provider changed to:', provider);

    // Switch provider via API
    try {
      const response = await fetchJSON(`${API}/api/providers/switch`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ provider })
      });

      if (response.success) {
        // Reload models for the new provider
        await loadModels();
      }
    } catch (error) {
      console.error('Failed to switch provider:', error);
    }
  }
});

providerToggle.initialize();
```

### Step 4: Update Model Loading

Modify the `loadModels()` function to support multiple providers:

```javascript
async function loadModels() {
  try {
    // Get models from all providers
    const response = await fetchJSON(`${API}/api/providers/models`, { method:'GET' }, 8000);
    availableModels = response.models || [];

    // Populate selector with provider badges
    const selector = $('modelSelector');
    selector.innerHTML = '';

    availableModels.forEach(model => {
      const option = document.createElement('option');
      option.value = model.id;

      const providerBadge = model.provider === 'webllm' ? '⚡' : '🖥️';
      const perfBadge = perfBadges[model.expected_performance] || '⚪';
      const star = model.recommended ? '⭐ ' : '';

      option.textContent = `${star}${providerBadge} ${model.name} ${perfBadge} - ${model.size_gb}GB`;
      option.dataset.model = JSON.stringify(model);
      option.dataset.provider = model.provider;

      if (model.recommended) {
        option.selected = true;
      }

      selector.appendChild(option);
    });

    // Trigger change to update UI
    selector.dispatchEvent(new Event('change'));
  } catch (e) {
    toast('Failed to load models: ' + e.message, 'error');
  }
}
```

### Step 5: Handle Provider-Specific Chat

Update the `sendMessage()` function to route to correct provider:

```javascript
async function sendMessage(text) {
  // ... existing code ...

  const selector = $('modelSelector');
  const selectedOption = selector.selectedOptions[0];
  const provider = selectedOption ? selectedOption.dataset.provider : 'webllm';
  const modelToUse = selector.value || null;

  try {
    let reply, model;

    if (provider === 'webllm') {
      // Use WebLLM (browser-based)
      if (!window.webllmClient.isInitialized) {
        await window.webllmClient.initialize();
      }

      // Load model if different
      if (window.webllmClient.getCurrentModel() !== modelToUse) {
        await window.webllmClient.loadModel(modelToUse);
      }

      // Generate response
      const messages = [{ role: 'user', content: text }];
      reply = await window.webllmClient.chat(messages);
      model = modelToUse;

    } else {
      // Use Ollama (existing backend logic)
      const body = { message: text };
      if (conversationId) body.conversation_id = conversationId;
      if (modelToUse) body.model = modelToUse;

      const data = await fetchJSON(`${API}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
      }, 120000);

      reply = data.response || '';
      model = data.model_used || '';

      if (data.conversation_id) {
        conversationId = data.conversation_id;
      }
    }

    // ... rest of existing code to display reply ...
  } catch (e) {
    // ... error handling ...
  }
}
```

## Testing

1. **Start the backend:**
   ```bash
   cd backend
   python -m uvicorn main:app --reload --port 8000
   ```

2. **Open the frontend:**
   Open `frontend/index.html` in a browser that supports WebGPU (Chrome/Edge 113+)

3. **Test provider switching:**
   - Click on "WebLLM" button - should show browser-based models
   - Click on "Ollama" button - should show Ollama models
   - Send a message with each provider selected

4. **Check logs:**
   - Backend logs should show provider initialization
   - Browser console should show WebLLM loading progress

## API Endpoints

- `GET /api/providers/health` - Check all providers health
- `GET /api/providers/active` - Get active provider
- `POST /api/providers/switch` - Switch provider
- `GET /api/providers/models` - Get all models from all providers
- `GET /api/providers/{provider}/models` - Get models from specific provider
- `GET /api/providers/config` - Get provider configuration

## Browser Requirements

WebLLM requires:
- Chrome/Edge 113+ with WebGPU support
- Modern GPU (supports WebGPU)
- At least 4GB RAM for small models

## Troubleshooting

### WebGPU not supported
- Update browser to latest version
- Enable WebGPU in browser flags: `chrome://flags/#enable-unsafe-webgpu`

### Models not loading
- Check browser console for errors
- Verify backend is running: `http://localhost:8000/api/providers/health`
- Check network tab for failed API calls

### Provider switch fails
- Check backend logs for provider initialization errors
- Verify provider config at `/config/provider-config.json`

## Next Steps

1. Implement Ollama provider adapter (refactor existing ollama_integration.py)
2. Add streaming support for WebLLM
3. Implement TOON format UI toggle
4. Add model download progress UI
5. Implement fallback mechanism when WebLLM fails
