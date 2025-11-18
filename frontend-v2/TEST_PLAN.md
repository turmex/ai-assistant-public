# Model Download and Display Testing Plan

## Prerequisites

1. Backend API server running on `http://localhost:8000`
2. Ollama installed and running
3. Browser with DevTools open (to monitor console logs)

## Test Cases

### Test 1: Llama 3.2 1B Download and Display

**Steps**:
1. Open frontend in browser
2. Click "Models" button
3. Find "Llama 3.2 1B" in Available Models
4. Click "↓ Download" button
5. Wait for download to complete (watch console logs)
6. Refresh the Models modal

**Expected Result**:
- ✅ Model appears in "Downloaded Models" section (green background)
- ✅ Model removed from "Available Models" section
- ✅ No duplicates appear
- ✅ Console shows: "Download confirmed! Model found in: [array]"

**Pass/Fail**: _______

---

### Test 2: Qwen2.5 1.5B Duplicate Prevention

**Steps**:
1. Open frontend in browser
2. Click "Models" button
3. Check if Qwen2.5 1.5B appears multiple times
4. Download Qwen2.5 1.5B if not already downloaded
5. Refresh Models modal
6. Count occurrences of Qwen2.5 1.5B

**Expected Result**:
- ✅ Only ONE entry for Qwen2.5 1.5B in total
- ✅ Either in Downloaded OR Available section, never both
- ✅ Console shows: "Skipping duplicate model: [name]" if any found

**Pass/Fail**: _______

---

### Test 3: GPT2 Download Timeout Fix

**Steps**:
1. Open frontend with browser DevTools console open
2. Click "Models" button
3. Find GPT2 in Available Models
4. Click "↓ Download" button
5. Watch console logs for polling attempts
6. Wait for completion (may take 1-2 minutes)

**Expected Result**:
- ✅ Console shows polling attempts: "Attempt 1/60 - Downloaded models: [...]"
- ✅ GPT2 detected when download completes
- ✅ Success toast: "Successfully downloaded gpt2!"
- ✅ Model appears in Downloaded Models section
- ✅ NO timeout warning

**Pass/Fail**: _______

---

### Test 4: Model Refresh Maintains State

**Steps**:
1. Download 2-3 models (if not already downloaded)
2. Note which models are in Downloaded Models section
3. Click "🔄 Refresh" button
4. Wait for refresh to complete
5. Compare model lists

**Expected Result**:
- ✅ All previously downloaded models still in Downloaded Models
- ✅ No models moved to wrong section
- ✅ No new duplicates introduced
- ✅ "Just now" refresh timestamp shown

**Pass/Fail**: _______

---

### Test 5: Multiple Simultaneous Downloads

**Steps**:
1. Open Models modal
2. Quickly download 2-3 models in succession
3. Watch console logs
4. Wait for all downloads to complete

**Expected Result**:
- ✅ Each model shows "⏳ Downloading..." status
- ✅ Downloads tracked independently
- ✅ All models appear in Downloaded Models when done
- ✅ No duplicates created
- ✅ Console shows separate polling for each model

**Pass/Fail**: _______

---

### Test 6: Console Debugging Output

**Steps**:
1. Open browser DevTools → Console tab
2. Click "Models" button
3. Observe console output
4. Download a model
5. Observe polling logs

**Expected Console Output**:
```
✅ Raw available models: [number]
✅ Downloaded models: [array]
✅ Unique available models after deduplication: [number]
✅ Available model names: [array]
✅ Downloaded models for UI: [number] [array]
✅ Available models for UI: [number] [array]
✅ Polling for download completion of: [model-name]
✅ Attempt 1/60 - Downloaded models: [array]
✅ Download confirmed! Model found in: [array]
```

**Pass/Fail**: _______

---

### Test 7: HuggingFace URL Search

**Steps**:
1. Open Models modal
2. Paste HuggingFace URL: `https://huggingface.co/meta-llama/Llama-3.2-1B-Instruct`
3. Click "Search"
4. Download the found model
5. Verify it appears correctly

**Expected Result**:
- ✅ Model added to available list
- ✅ No duplicates if already in list
- ✅ Download works correctly
- ✅ Model moves to Downloaded section

**Pass/Fail**: _______

---

### Test 8: Edge Cases

**Steps**:
1. Download a model with unusual name (e.g., `llama3.2:1b-instruct-q4_0`)
2. Refresh models
3. Check for correct categorization

**Expected Result**:
- ✅ Model appears in Downloaded Models
- ✅ Name normalization handles edge cases
- ✅ No errors in console

**Pass/Fail**: _______

---

## Debugging Tips

### If Model Not Appearing After Download:

1. Check console for polling logs
2. Verify actual downloaded name: Check backend response
3. Test normalization in console:
   ```javascript
   normalizeModelName("llama3.2:1b")  // Should return "llama:1b"
   normalizeModelName("llama:1b")      // Should return "llama:1b"
   ```
4. Check if `downloadedModels` array contains the model

### If Duplicates Appear:

1. Check console for "Skipping duplicate model" logs
2. Verify Map deduplication in `loadModels()`
3. Verify Set deduplication in `loadModelsUI()`
4. Check normalized names in console

### If Download Times Out:

1. Check if download actually completed (check Ollama directly)
2. Verify polling is using correct normalization
3. Increase `maxAttempts` if needed (currently 60 attempts = 5 minutes)

---

## Success Criteria

All tests must pass (✅) with:
- ✅ No duplicate model entries
- ✅ All downloaded models appear in Downloaded Models section
- ✅ Name variations handled correctly
- ✅ No timeout errors for standard models
- ✅ Clean console logs with helpful debugging info

---

## Quick Test Command

To quickly test if normalization is working:

```javascript
// Paste in browser console:
console.log('Testing normalization:');
console.log('llama3.2:1b →', normalizeModelName('llama3.2:1b'));
console.log('llama:1b →', normalizeModelName('llama:1b'));
console.log('qwen2.5:1.5b →', normalizeModelName('qwen2.5:1.5b'));
console.log('gpt-2 →', normalizeModelName('gpt-2'));
console.log('gpt2 →', normalizeModelName('gpt2'));
```

Expected output:
```
llama3.2:1b → llama:1b
llama:1b → llama:1b
qwen2.5:1.5b → qwen:1.5b
gpt-2 → gpt2
gpt2 → gpt2
```
