# AI Assistant - Model Management Architecture Design

## Executive Summary

This document outlines the architecture for enhanced model management in the AI Assistant application, focusing on separating downloaded models from available models, implementing proper load/unload state management, and ensuring automatic model transitions.

---

## Current State Analysis

### Existing Components

#### Frontend (`frontend-v2/index.html`)
- **Current Model Display** (line 150-155): Shows currently active model in header
- **Model Modal** (line 218-322): Single unified view for all models
- **Model Actions** (line 288-301): Download, Delete, Load, Unload buttons
- **State Variables** (line 329-335):
  - `availableModels`: Models from HuggingFace
  - `downloadedModels`: Models already downloaded via Ollama
  - `selectedModel`: Currently selected model in UI
  - `currentActiveModel`: Currently loaded/active model (string)

#### Backend (`backend/main.py`)
- **`/models/available`** (line 449-516): Returns HuggingFace models with compatibility flags
- **`/models/downloaded`** (line 519-543): Returns Ollama local models
- **`/models/download`** (line 433-446): Downloads a model via Ollama
- **`/models/{model_name}`** DELETE (line 657-699): Deletes a downloaded model

### Current Issues

1. **UI Organization**: Downloaded and available models are mixed together in one list
2. **State Management**: No explicit load/unload mechanism (only client-side tracking)
3. **Model Transitions**: When loading a new model, previous model is not unloaded
4. **Button Logic**: Complex visibility logic based on download + load state

---

## Proposed Architecture

### 1. UI Structure Redesign

#### A. New Section Layout

```
┌─────────────────────────────────────────┐
│ Modal Header: "Model Selection"        │
├─────────────────────────────────────────┤
│                                         │
│ ╔═══════════════════════════════════╗  │
│ ║ DOWNLOADED MODELS SECTION (TOP)  ║  │
│ ╠═══════════════════════════════════╣  │
│ ║ Model Card 1:                     ║  │
│ ║   [Load Model] [Delete Model]     ║  │
│ ║                                   ║  │
│ ║ Model Card 2 (LOADED):            ║  │
│ ║   [Unload Model]                  ║  │
│ ╚═══════════════════════════════════╝  │
│                                         │
│ ─────────────────────────────────────  │
│                                         │
│ ┌───────────────────────────────────┐  │
│ │ AVAILABLE MODELS SECTION          │  │
│ ├───────────────────────────────────┤  │
│ │ Model Card 3:                     │  │
│ │   [Download Model]                │  │
│ │                                   │  │
│ │ Model Card 4:                     │  │
│ │   [Download Model]                │  │
│ └───────────────────────────────────┘  │
│                                         │
│ ┌───────────────────────────────────┐  │
│ │ HuggingFace URL Search            │  │
│ └───────────────────────────────────┘  │
└─────────────────────────────────────────┘
```

#### B. HTML Structure Changes

**Location**: `index.html` lines 232-246 (replace model list container)

```html
<!-- DOWNLOADED MODELS SECTION (New) -->
<div class="mb-6">
  <div class="flex items-center justify-between mb-3">
    <label class="block text-sm font-medium text-gray-700">Downloaded Models</label>
    <span id="downloadedCount" class="text-xs text-gray-500">0 models</span>
  </div>
  <div id="downloadedModelsContainer" class="space-y-2 max-h-64 overflow-y-auto border border-gray-200 rounded-lg p-2 bg-green-50">
    <div class="text-sm text-gray-500 text-center py-4">No models downloaded yet</div>
  </div>
</div>

<!-- AVAILABLE MODELS SECTION (Existing, modified) -->
<div class="mb-4">
  <div class="flex items-center justify-between mb-3">
    <label class="block text-sm font-medium text-gray-700">Available Models</label>
    <div class="flex items-center gap-2">
      <span id="lastRefreshed" class="text-xs text-gray-500">Never refreshed</span>
      <button id="refreshModelsBtn" class="rounded-lg border border-gray-300 bg-white px-3 py-1 text-xs font-medium text-gray-700 hover:bg-gray-50">
        🔄 Refresh
      </button>
    </div>
  </div>
  <div id="availableModelsContainer" class="space-y-2 max-h-96 overflow-y-auto border border-gray-200 rounded-lg p-2">
    <div class="text-sm text-gray-500 text-center py-4">Loading models from HuggingFace...</div>
  </div>
</div>
```

### 2. State Management Architecture

#### A. Enhanced State Variables

**Location**: `index.html` lines 328-335 (update state section)

```javascript
// Enhanced State Management
let conversationId = null;
let availableModels = [];      // HuggingFace models (not downloaded)
let downloadedModels = [];      // Ollama local models (names array)
let selectedModel = null;       // Currently selected in UI
let currentActiveModel = null;  // Currently loaded/active model (string: model name)
let hfSearchedModel = null;
let lastRefreshedTime = null;

// New: Model State Tracker
const modelState = {
  loaded: null,              // Currently loaded model name
  downloading: new Set(),    // Models currently downloading

  isLoaded(modelName) {
    return this.loaded === modelName;
  },

  isDownloaded(modelName) {
    return downloadedModels.includes(modelName);
  },

  isDownloading(modelName) {
    return this.downloading.has(modelName);
  },

  setLoaded(modelName) {
    this.loaded = modelName;
    currentActiveModel = modelName;
  },

  clearLoaded() {
    this.loaded = null;
    currentActiveModel = null;
  }
};
```

#### B. State Transition Diagram

```
┌─────────────┐
│ Not         │
│ Downloaded  │────download────▶┌─────────────┐
└─────────────┘                 │ Downloaded  │
                                │ (Unloaded)  │
                                └─────────────┘
                                       │
                                       │ load
                                       ▼
                                ┌─────────────┐
                                │ Downloaded  │
                                │ (Loaded)    │◀────┐
                                └─────────────┘     │
                                       │            │
                                       │ unload     │ load new
                                       ▼            │
                                ┌─────────────┐     │
                                │ Downloaded  │─────┘
                                │ (Unloaded)  │
                                └─────────────┘
                                       │
                                       │ delete
                                       ▼
                                ┌─────────────┐
                                │ Not         │
                                │ Downloaded  │
                                └─────────────┘
```

### 3. Button Visibility Logic

#### A. Decision Matrix

| Model State | Downloaded? | Loaded? | Visible Buttons |
|------------|------------|---------|----------------|
| Available Only | No | No | [Download] |
| Downloaded, Unloaded | Yes | No | [Load] [Delete] |
| Downloaded, Loaded | Yes | Yes | [Unload] |

#### B. Implementation

**Location**: `index.html` lines 494-527 (replace `updateModelActions`)

```javascript
function updateModelActions(model, location = 'modal') {
  if (!model) return;

  const isDownloaded = modelState.isDownloaded(model.name);
  const isLoaded = modelState.isLoaded(model.name);

  if (location === 'modal') {
    // Modal action buttons (bottom of modal)
    const modelActions = $('modelActions');
    const downloadBtn = $('downloadBtn');
    const deleteBtn = $('deleteBtn');
    const loadBtn = $('loadBtn');
    const unloadBtn = $('unloadBtn');

    modelActions.classList.remove('hidden');

    // Hide all first
    [downloadBtn, deleteBtn, loadBtn, unloadBtn].forEach(btn =>
      btn.classList.add('hidden')
    );

    // Show appropriate buttons
    if (!isDownloaded) {
      downloadBtn.classList.remove('hidden');
    } else if (isLoaded) {
      unloadBtn.classList.remove('hidden');
    } else {
      loadBtn.classList.remove('hidden');
      deleteBtn.classList.remove('hidden');
    }
  }
}

function renderModelCard(model, isDownloaded) {
  const isLoaded = modelState.isLoaded(model.name);
  const isCompatible = model.is_compatible !== false;

  // ... existing card rendering ...

  // Button section for model card
  let buttons = '';
  if (!isDownloaded) {
    buttons = `<button class="download-btn" data-model="${model.name}">Download</button>`;
  } else if (isLoaded) {
    buttons = `<button class="unload-btn" data-model="${model.name}">Unload Model</button>`;
  } else {
    buttons = `
      <button class="load-btn" data-model="${model.name}">Load Model</button>
      <button class="delete-btn" data-model="${model.name}">Delete</button>
    `;
  }

  // Add buttons to card
  card.innerHTML += `<div class="mt-2 flex gap-2">${buttons}</div>`;

  return card;
}
```

### 4. Auto-Unload Mechanism

#### A. Load Model Flow

**Location**: `index.html` lines 840-854 (replace `loadModel`)

```javascript
async function loadModel(modelName, displayName) {
  if (!modelName) {
    toast('No model selected', 'warn');
    return;
  }

  try {
    // Step 1: Auto-unload current model if exists
    if (currentActiveModel && currentActiveModel !== modelName) {
      toast(`Unloading ${currentActiveModel}...`, 'info');
      await unloadModelInternal(currentActiveModel, false);
    }

    // Step 2: Load new model (future: call backend /models/load endpoint)
    toast(`Loading ${displayName}...`, 'info');

    // For now: client-side state update (future: await backend load)
    modelState.setLoaded(modelName);
    updateCurrentModelDisplay(displayName);

    // Step 3: Update UI
    refreshModelUI();
    toast(`✓ ${displayName} loaded`, 'success');

  } catch (error) {
    toast(`Failed to load model: ${error.message}`, 'error');
    console.error('Load model error:', error);
  }
}

async function unloadModel() {
  if (!currentActiveModel) {
    toast('No model is currently loaded', 'warn');
    return;
  }

  await unloadModelInternal(currentActiveModel, true);
}

async function unloadModelInternal(modelName, showToast = true) {
  try {
    // Future: call backend /models/unload endpoint

    // For now: client-side state update
    modelState.clearLoaded();
    updateCurrentModelDisplay(null);

    // Update UI
    refreshModelUI();

    if (showToast) {
      toast('Model unloaded', 'success');
    }
  } catch (error) {
    if (showToast) {
      toast(`Failed to unload: ${error.message}`, 'error');
    }
    console.error('Unload error:', error);
  }
}

function refreshModelUI() {
  // Refresh both downloaded and available sections
  loadModelsUI();
}
```

### 5. UI Rendering Logic

#### A. Dual Container Rendering

**Location**: `index.html` lines 634-762 (replace `loadModelsUI`)

```javascript
function loadModelsUI() {
  const downloadedContainer = $('downloadedModelsContainer');
  const availableContainer = $('availableModelsContainer');

  // Clear both containers
  downloadedContainer.innerHTML = '';
  availableContainer.innerHTML = '';

  // Split models into downloaded and available
  const downloaded = [];
  const available = [];

  availableModels.forEach(model => {
    if (downloadedModels.includes(model.name)) {
      downloaded.push(model);
    } else {
      available.push(model);
    }
  });

  // Update count badge
  $('downloadedCount').textContent = `${downloaded.length} model${downloaded.length !== 1 ? 's' : ''}`;

  // Render downloaded models (with load/unload buttons)
  if (downloaded.length === 0) {
    downloadedContainer.innerHTML = '<div class="text-sm text-gray-500 text-center py-4">No models downloaded yet</div>';
  } else {
    downloaded.forEach(model => {
      const card = renderModelCard(model, true);
      downloadedContainer.appendChild(card);
    });
  }

  // Render available models (with download buttons)
  if (available.length === 0) {
    availableContainer.innerHTML = '<div class="text-sm text-gray-500 text-center py-4">All models downloaded</div>';
  } else {
    available.forEach(model => {
      const card = renderModelCard(model, false);
      availableContainer.appendChild(card);
    });
  }
}
```

### 6. Data Flow Diagram

```
┌──────────────────────────────────────────────────────────┐
│                    USER ACTIONS                          │
└──────────────────────────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────┐
│                 FRONTEND STATE MANAGER                    │
│  ┌────────────────────────────────────────────────┐     │
│  │ modelState.loaded = "llama3.2:1b"              │     │
│  │ downloadedModels = ["llama3.2:1b", "phi4:14b"] │     │
│  │ availableModels = [Model1, Model2, ...]        │     │
│  └────────────────────────────────────────────────┘     │
└──────────────────────────────────────────────────────────┘
                           │
           ┌───────────────┼───────────────┐
           ▼               ▼               ▼
    ┌──────────┐    ┌──────────┐    ┌──────────┐
    │ Download │    │   Load   │    │  Unload  │
    │  Model   │    │  Model   │    │  Model   │
    └──────────┘    └──────────┘    └──────────┘
           │               │               │
           ▼               ▼               ▼
┌──────────────────────────────────────────────────────────┐
│                  BACKEND API CALLS                        │
│  POST /models/download                                    │
│  (future) POST /models/load                               │
│  (future) POST /models/unload                             │
│  GET /models/downloaded                                   │
└──────────────────────────────────────────────────────────┘
           │               │               │
           ▼               ▼               ▼
┌──────────────────────────────────────────────────────────┐
│                   OLLAMA SERVICE                          │
│  /api/pull     /api/tags     /api/delete                 │
└──────────────────────────────────────────────────────────┘
```

---

## Implementation Plan

### Phase 1: Frontend UI Restructuring
**Files**: `frontend-v2/index.html`

1. Add Downloaded Models section HTML (lines 232-246)
2. Update state variables with modelState object (lines 328-335)
3. Implement dual container rendering (replace loadModelsUI, lines 634-762)
4. Update button visibility logic (replace updateModelActions, lines 494-527)

### Phase 2: Auto-Unload Mechanism
**Files**: `frontend-v2/index.html`

1. Implement loadModel with auto-unload (lines 840-854)
2. Implement unloadModelInternal helper
3. Add event listeners for inline card buttons

### Phase 3: Backend Load/Unload Endpoints (Future Enhancement)
**Files**: `backend/main.py`

Currently, model loading is handled implicitly by Ollama when a chat request is made. For explicit load/unload control:

```python
@app.post("/models/load")
async def load_model(model_name: str):
    """
    Explicitly load a model into memory.
    Uses Ollama's /api/generate with empty prompt to warm up model.
    """
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            # Warm up model by sending empty generation
            await client.post(
                f"{settings.ollama_base_url}/api/generate",
                json={"model": model_name, "prompt": "", "stream": False}
            )
        return {"status": "loaded", "model": model_name}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/models/unload")
async def unload_model(model_name: str):
    """
    Unload a model from memory.
    Note: Ollama automatically manages memory, so this is informational.
    """
    # Ollama doesn't have explicit unload API
    # Could track in backend state for UI purposes
    return {"status": "unloaded", "model": model_name}
```

### Phase 4: Testing & Validation

1. **Unit Tests**: State transitions, button visibility logic
2. **Integration Tests**: Download → Load → Unload → Delete flow
3. **User Acceptance**: Verify auto-unload when switching models

---

## Key Design Decisions

### 1. Client-Side Load State
**Decision**: Track loaded model in frontend state (`currentActiveModel`)
**Rationale**: Ollama doesn't expose explicit load/unload API; models are loaded on first use
**Trade-off**: Backend doesn't know which model is "active" until chat request

### 2. Separate Containers
**Decision**: Two distinct UI sections for downloaded vs available
**Rationale**: Clear visual hierarchy, easier to find downloaded models
**Alternative**: Single list with filters (rejected due to complexity)

### 3. Auto-Unload on Load
**Decision**: Automatically unload previous model when loading new one
**Rationale**: Prevents memory issues from multiple loaded models
**Implementation**: Sequential unload → load in `loadModel()` function

### 4. Button Location
**Decision**: Buttons on each model card + modal action buttons
**Rationale**: Inline buttons for quick actions, modal buttons for selected model
**Consistency**: Both locations use same state logic

---

## Success Metrics

1. **User Experience**
   - Downloaded models appear at top of modal ✓
   - Currently loaded model shows only "Unload" button ✓
   - Auto-unload prevents multiple loaded models ✓

2. **Code Quality**
   - Single source of truth for model state (`modelState` object)
   - Consistent button visibility logic across UI
   - Clear separation of downloaded/available models

3. **Performance**
   - No redundant API calls on UI updates
   - Instant state updates for load/unload (client-side)
   - Efficient rendering with dual containers

---

## Migration Notes

### Breaking Changes
None - this is additive UI enhancement

### Backward Compatibility
- Existing `/models/available` and `/models/downloaded` endpoints unchanged
- Current model selection logic preserved
- Chat endpoint model parameter still works as before

### Rollback Plan
If issues occur, can revert to single container by:
1. Removing downloaded models section HTML
2. Reverting `loadModelsUI()` to original implementation
3. Keeping original `updateModelActions()` logic

---

## Future Enhancements

1. **Backend Load/Unload Tracking**
   - Add database table for loaded model state
   - Sync frontend state with backend on page load

2. **Multi-Model Support**
   - Allow multiple models loaded simultaneously
   - Model priority/preference system

3. **Model Preloading**
   - Background loading of frequently used models
   - Predictive model switching based on conversation context

4. **Resource Monitoring**
   - Show memory usage per loaded model
   - Warn when approaching system limits

---

## Appendix: Code Locations Reference

### Frontend (index.html)
- **State Variables**: Lines 328-335
- **Model Actions**: Lines 288-301
- **Modal HTML**: Lines 218-322
- **loadModelsUI()**: Lines 634-762
- **updateModelActions()**: Lines 494-527
- **loadModel()**: Lines 840-854
- **unloadModel()**: Lines 856-872

### Backend (main.py)
- **/models/available**: Lines 449-516
- **/models/downloaded**: Lines 519-543
- **/models/download**: Lines 433-446
- **DELETE /models/{model_name}**: Lines 657-699
- **Future /models/load**: TBD
- **Future /models/unload**: TBD

---

**Document Version**: 1.0
**Last Updated**: 2025-11-15
**Author**: System Architecture Designer
**Status**: Ready for Implementation
