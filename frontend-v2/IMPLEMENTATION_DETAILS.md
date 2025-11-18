# Implementation Details: Model Download and Display Fixes

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Model Management Flow                    │
└─────────────────────────────────────────────────────────────┘

1. API Calls
   ├── GET /models/available  → Raw available models
   └── GET /models/downloaded → Raw downloaded model names

2. Normalization Layer (NEW)
   ├── normalizeModelName()   → Canonicalize names
   └── isModelDownloaded()    → Fuzzy matching

3. Deduplication Layer (NEW)
   ├── loadModels() Map       → Prevent duplicates on load
   └── loadModelsUI() Set     → Prevent duplicates on render

4. UI Rendering
   ├── Downloaded Models      → Green section
   └── Available Models       → White section
```

## Core Functions

### 1. `normalizeModelName(name)` - Line 407

**Purpose**: Canonicalize model names for consistent comparison

**Logic**:
```javascript
Input: "llama3.2:1b"     → Output: "llama:1b"
Input: "qwen2.5:1.5b"    → Output: "qwen:1.5b"
Input: "gpt-2"           → Output: "gpt2"
```

**Transformations**:
1. Convert to lowercase and trim
2. Replace `llama3.2:` or `llama-3.2:` → `llama:`
3. Replace `qwen2.5:` or `qwen2:` → `qwen:`
4. Replace `gpt-2` → `gpt2`

**Called By**:
- `isModelDownloaded()` - Every download check
- `loadModels()` - During deduplication
- `downloadModel()` - During polling
- `loadModelsUI()` - During categorization

---

### 2. `isModelDownloaded(modelName)` - Line 427

**Purpose**: Check if a model is downloaded with fuzzy matching

**Logic**:
```javascript
// Exact match after normalization
if (normalizedDl === normalized) return true;

// Base name match (before colon)
if (baseName === dlBaseName) {
  // Also verify size suffix matches if present
  return sizeMatch === dlSizeMatch;
}
```

**Examples**:
```javascript
isModelDownloaded("llama:1b")
  → Matches: "llama3.2:1b", "llama:1b", "llama-3.2:1b"
  → Doesn't match: "llama:3b", "llama3.2:3b"

isModelDownloaded("qwen2.5:1.5b")
  → Matches: "qwen:1.5b", "qwen2.5:1.5b", "qwen2:1.5b"
  → Doesn't match: "qwen:0.5b"
```

**Called By**:
- `downloadModel()` - Polling loop
- `loadModels()` - Auto-select recommended
- `loadModelsUI()` - Categorization

---

### 3. `loadModels(forceRefresh)` - Line 455

**Purpose**: Load and deduplicate models from API

**Deduplication Strategy**:
```javascript
const uniqueModels = new Map();

// Add available models (using normalized name as key)
rawAvailableModels.forEach(model => {
  const normalized = normalizeModelName(model.name);
  if (!uniqueModels.has(normalized)) {
    uniqueModels.set(normalized, model);
  }
});

// Add downloaded-only models (ensures they always appear)
downloadedModels.forEach(dlModelName => {
  const normalized = normalizeModelName(dlModelName);
  if (!uniqueModels.has(normalized)) {
    uniqueModels.set(normalized, {
      name: dlModelName,
      downloaded_only: true,
      // ... synthetic model data ...
    });
  }
});
```

**Console Output**:
```
Raw available models: 15
Downloaded models: ["llama3.2:1b", "qwen2.5:1.5b"]
Unique available models after deduplication: 15
Available model names: ["llama:1b", "qwen:1.5b", ...]
```

---

### 4. `downloadModel(modelName)` - Line 587

**Purpose**: Download model with improved polling

**Polling Logic**:
```javascript
// Old (BAD):
response.models.includes(modelName) ||
response.models.some(m => m.includes('llama3.2:1b'))  // Hardcoded!

// New (GOOD):
downloadedModels = currentDownloaded;
if (isModelDownloaded(modelName)) {
  // Success!
}
```

**Polling Parameters**:
- Interval: 5 seconds
- Max attempts: 60 (5 minutes total)
- Uses `isModelDownloaded()` for all checks

**Console Output**:
```
Polling for download completion of: llama:1b normalized: llama:1b
Attempt 1/60 - Downloaded models: []
Attempt 2/60 - Downloaded models: []
...
Attempt 8/60 - Downloaded models: ["llama3.2:1b"]
Download confirmed! Model found in: ["llama3.2:1b"]
```

---

### 5. `loadModelsUI()` - Line 902

**Purpose**: Render UI with categorization and duplicate prevention

**Categorization Logic**:
```javascript
const downloaded = [];
const available = [];
const seenModels = new Set();

availableModels.forEach(model => {
  const normalized = normalizeModelName(model.name);

  // Skip duplicates
  if (seenModels.has(normalized)) {
    console.log('Skipping duplicate model:', model.name);
    return;
  }
  seenModels.add(normalized);

  // Categorize
  if (isModelDownloaded(model.name)) {
    downloaded.push(model);
  } else {
    available.push(model);
  }
});
```

**Console Output**:
```
Downloaded models for UI: 2 ["llama:1b", "qwen:1.5b"]
Available models for UI: 13 ["gpt2", "mistral:7b", ...]
```

---

## Data Flow Example

### Scenario: Download Llama 3.2 1B

```
1. User clicks "Download" on llama:1b card
   ↓
2. downloadModel("llama:1b") called
   ↓
3. POST /models/download { model_name: "llama:1b" }
   ↓
4. Backend downloads → Ollama stores as "llama3.2:1b"
   ↓
5. Polling loop starts:
   normalizedTarget = "llama:1b"
   ↓
6. Poll attempt 1-7: No match
   ↓
7. Poll attempt 8:
   GET /models/downloaded → ["llama3.2:1b"]
   downloadedModels = ["llama3.2:1b"]
   isModelDownloaded("llama:1b")
     ├── normalize("llama:1b") → "llama:1b"
     ├── normalize("llama3.2:1b") → "llama:1b"
     └── "llama:1b" === "llama:1b" ✅
   ↓
8. Success! Reload models
   ↓
9. loadModels():
   - Add to uniqueModels Map with key "llama:1b"
   - No duplicate since key already exists
   ↓
10. loadModelsUI():
    - seenModels.add("llama:1b")
    - isModelDownloaded("llama:1b") → true
    - Push to downloaded[] array
    - Render in Downloaded Models section
```

---

## Edge Cases Handled

### 1. Name Variations
```javascript
// All treated as same model:
"llama:1b"
"llama3.2:1b"
"llama-3.2:1b"
"Llama:1B"  // Case insensitive
" llama:1b " // Whitespace trimmed
```

### 2. Downloaded But Not in Available List
```javascript
// If Ollama has a model not returned by /models/available:
downloadedModels = ["custom-model:latest"];
availableModels = [/* doesn't include custom-model */];

// Solution: Auto-create synthetic entry
uniqueModels.set("custom-model:latest", {
  name: "custom-model:latest",
  downloaded_only: true,
  // ... default values ...
});
```

### 3. Duplicate Prevention
```javascript
// Scenario: API returns duplicate
availableModels = [
  { name: "llama:1b", ... },
  { name: "llama3.2:1b", ... }  // Duplicate!
];

// Solution 1: Map in loadModels()
uniqueModels.set("llama:1b", firstModel);
uniqueModels.set("llama:1b", secondModel); // Overwrites, not duplicate

// Solution 2: Set in loadModelsUI()
seenModels.add("llama:1b");
// Second occurrence skipped
```

### 4. Concurrent Downloads
```javascript
downloadingModels = new Set([
  "llama:1b",
  "qwen:1.5b",
  "gpt2"
]);

// Each download:
// 1. Adds to Set (prevents re-download)
// 2. Polls independently
// 3. Removes from Set when done
// 4. Reloads UI (no conflicts)
```

---

## Performance Considerations

### Memory Usage
- Map-based deduplication: O(n) space for n unique models
- Set-based duplicate tracking: O(n) space
- Total overhead: ~2n for safety

### Time Complexity
- Normalization: O(1) - regex replacements
- Duplicate check: O(n) - linear scan of downloaded models
- Load models: O(n) - single pass
- Render UI: O(n) - single pass

### Network Calls
- Initial load: 2 API calls (available + downloaded)
- Download polling: Up to 60 calls per model (5 min max)
- Refresh: 2 API calls

---

## Debugging Checklist

If issues occur, check console for:

1. ✅ "Raw available models: X"
2. ✅ "Downloaded models: [array]"
3. ✅ "Unique available models after deduplication: X"
4. ✅ "Polling for download completion of: [name]"
5. ✅ "Attempt X/60 - Downloaded models: [array]"
6. ✅ "Download confirmed! Model found in: [array]"
7. ✅ "Downloaded models for UI: X [array]"
8. ✅ "Skipping duplicate model: [name]" (if any)

Missing logs = Function not executing correctly

---

## Future Enhancements

Potential improvements:
1. **Persistent normalization cache** - Store normalized names
2. **WebSocket polling** - Replace HTTP polling with real-time updates
3. **Download progress** - Show actual download percentage
4. **Retry logic** - Auto-retry failed downloads
5. **Batch operations** - Download multiple models simultaneously
