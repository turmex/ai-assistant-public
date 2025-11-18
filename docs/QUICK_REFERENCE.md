# WebLLM Integration - Quick Reference

## 🚀 Quick Start (5 Minutes)

### 1. Start Backend
```bash
cd /Users/davidcelekli/Desktop/ai-assistant/backend
python -m uvicorn main:app --reload --port 8000
```

### 2. Open Frontend
Open `/Users/davidcelekli/Desktop/ai-assistant/frontend/index.html` in Chrome 113+

### 3. Test API
```bash
# Check provider health
curl http://localhost:8000/api/providers/health

# Get all models
curl http://localhost:8000/api/providers/models

# Switch to WebLLM
curl -X POST http://localhost:8000/api/providers/switch \
  -H "Content-Type: application/json" \
  -d '{"provider": "webllm"}'
```

## 📁 Files Created

```
backend/src/
├── providers/
│   ├── base_provider.py          # Abstract base class
│   ├── webllm_provider.py        # WebLLM implementation
│   ├── provider_manager.py       # Provider management
│   └── __init__.py
├── api/
│   ├── provider_endpoints.py     # REST API
│   └── __init__.py
└── utils/
    ├── toon_format.py            # Token optimization
    └── __init__.py

frontend/src/
├── webllm-integration.js         # WebLLM client
└── provider-toggle.js            # UI component

config/
└── provider-config.json          # Provider settings

docs/
├── INTEGRATION_GUIDE.md          # Full integration steps
├── IMPLEMENTATION_SUMMARY.md     # Complete summary
└── QUICK_REFERENCE.md            # This file
```

## 🎯 Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/providers/health` | Check all providers |
| GET | `/api/providers/active` | Get active provider |
| POST | `/api/providers/switch` | Switch provider |
| GET | `/api/providers/models` | Get all models |
| GET | `/api/providers/{provider}/models` | Get provider models |
| GET | `/api/providers/config` | Get configuration |

## 🧩 Code Snippets

### Initialize Provider Manager (main.py)
```python
from src.providers.webllm_provider import WebLLMProvider
from src.providers.provider_manager import get_provider_manager

# In lifespan function
provider_manager = get_provider_manager()
webllm_provider = WebLLMProvider()
await provider_manager.register_provider(webllm_provider)
```

### Add Provider Router (main.py)
```python
from src.api import provider_router

app.include_router(provider_router)
```

### Initialize Provider Toggle (index.html)
```javascript
const providerToggle = new ProviderToggle({
  defaultProvider: 'webllm',
  containerId: 'providerToggle',
  onProviderChange: async (provider) => {
    await fetchJSON(`${API}/api/providers/switch`, {
      method: 'POST',
      body: JSON.stringify({ provider })
    });
    await loadModels();
  }
});
providerToggle.initialize();
```

### Use WebLLM Client (index.html)
```javascript
// Initialize
await webllmClient.initialize();

// Load model
await webllmClient.loadModel('Llama-3.2-1B-Instruct-q4f16_1-MLC');

// Chat
const messages = [{ role: 'user', content: 'Hello!' }];
const response = await webllmClient.chat(messages);
```

## 🎨 WebLLM Models

| Model | Size | Speed | Quality | Recommended For |
|-------|------|-------|---------|-----------------|
| **Llama 3.2 1B** ⭐ | 0.7GB | ⚡⚡⚡ | Medium | Default, Quick responses |
| Qwen 2.5 0.5B | 0.4GB | ⚡⚡⚡⚡ | Basic | Ultra-fast, Simple tasks |
| TinyLlama 1.1B | 0.6GB | ⚡⚡⚡ | Basic | Fast, Lightweight |
| Llama 3.2 3B | 1.6GB | ⚡⚡ | High | Balanced quality/speed |
| Gemma 2 2B | 1.4GB | ⚡⚡ | High | Google tech, Quality |
| Phi 3.5 Mini | 2.2GB | ⚡⚡ | High | Microsoft, Reasoning |
| Mistral 7B | 4.0GB | ⚡ | High | Best quality, Slower |

## 🔧 TOON Format Example

```python
from src.utils.toon_format import TOONFormatter

# Compress
text = "Please implement a function that will return the configuration"
compressed = TOONFormatter.compress(text)
# Result: "pls impl fn tht wl ret cfg"

# Savings
stats = TOONFormatter.estimate_token_savings(text, compressed)
# Result: ~35% token reduction
```

## 🎨 CSS Classes (Provider Toggle)

Add to `<style>` in index.html:

```css
.provider-toggle-wrapper { margin-bottom: 1rem; }
.provider-toggle-container { /* gradient card */ }
.provider-option { /* toggle button */ }
.provider-option.active { /* selected state */ }
.provider-badge { /* Browser/Local badge */ }
.provider-info { /* info box */ }
```

## 🔍 Debugging

### Check Provider Health
```bash
curl http://localhost:8000/api/providers/health | jq
```

### Check WebGPU Support
```javascript
console.log('WebGPU:', navigator.gpu ? 'Supported' : 'Not supported');
```

### Check Browser Console
- Look for "WebLLM init progress"
- Check for errors in network tab
- Verify model loading messages

### Check Backend Logs
```
✓ WebLLM provider initialized with 7 models
✓ Provider manager initialized
```

## ⚠️ Common Issues

**WebGPU not supported:**
- Update Chrome/Edge to 113+
- Enable: `chrome://flags/#enable-unsafe-webgpu`

**Import errors:**
- Add `backend/src` to Python path
- Check `__init__.py` files exist

**CORS errors:**
- Check backend is running on port 8000
- Verify CORS middleware configured

## 📊 Performance

| Operation | Time |
|-----------|------|
| Provider switch | <100ms |
| Model load | 5-30s (first time) |
| Model load | <1s (cached) |
| Chat inference | 1-5s (depends on model) |
| Token/sec | 10-80 (depends on model) |

## 🔐 Browser Requirements

- **Chrome/Edge:** 113+
- **Safari:** Not supported (no WebGPU)
- **Firefox:** Experimental (flag required)
- **RAM:** 2GB+ (4GB+ recommended)
- **GPU:** WebGPU compatible

## 📦 Zero Dependencies

Backend uses existing:
- FastAPI
- Pydantic
- asyncio

Frontend uses:
- Native JavaScript (ES6+)
- WebLLM via ESM CDN
- Tailwind CSS (already loaded)

## 🚦 Integration Checklist

- [ ] Import provider classes in main.py
- [ ] Initialize provider manager in lifespan
- [ ] Add provider router to app
- [ ] Add provider toggle container to HTML
- [ ] Add CSS styles to HTML
- [ ] Import JS modules in HTML
- [ ] Initialize provider toggle in JS
- [ ] Update loadModels() function
- [ ] Update sendMessage() function
- [ ] Test provider switching
- [ ] Test WebLLM chat
- [ ] Test Ollama chat

## 📚 Documentation

- **INTEGRATION_GUIDE.md** - Full step-by-step integration
- **IMPLEMENTATION_SUMMARY.md** - Complete technical summary
- **QUICK_REFERENCE.md** - This file

## 🆘 Support

1. Check logs (backend + browser console)
2. Review INTEGRATION_GUIDE.md
3. Test API endpoints with curl
4. Verify WebGPU support
5. Check file paths are correct

## ✅ Quick Test

```bash
# 1. Test health
curl http://localhost:8000/api/providers/health

# 2. Test models
curl http://localhost:8000/api/providers/webllm/models

# 3. Test switch
curl -X POST http://localhost:8000/api/providers/switch \
  -H "Content-Type: application/json" \
  -d '{"provider": "webllm"}'
```

---

**Ready to integrate?** Follow **INTEGRATION_GUIDE.md** for detailed steps!
