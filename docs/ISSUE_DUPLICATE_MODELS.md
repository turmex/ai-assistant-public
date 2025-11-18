# Issue: Duplicate Qwen2.5 1.5B Models in Available List

**Issue ID:** MODEL-001
**Severity:** High
**Priority:** P1
**Status:** Identified
**Date:** November 15, 2025

---

## Problem Statement

The `/models/available` endpoint returns duplicate entries for the Qwen2.5 1.5B model because the HuggingFace integration fetches multiple model variants (Instruct and Base) that map to the same Ollama model name.

---

## Evidence

### Test Results
```
2025-11-15 21:21:20 - SCENARIO 2: Qwen2.5 1.5B Duplicate Check
Qwen2.5 1.5B in available models: 2 occurrences
Qwen2.5 1.5B in downloaded models: 1 occurrences
❌ TEST FAILED: Qwen2.5 1.5B appears 3 times (should be 1 or 0)
```

### API Response
```json
// GET /models/available returns TWO entries for qwen2.5:1.5b:

{
  "name": "qwen2.5:1.5b",
  "display_name": "Qwen2.5 1.5B",
  "size_gb": 1.1,
  "hf_url": "https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct",
  "downloads": 3629125,
  "likes": 541,
  "compatible": true
}

{
  "name": "qwen2.5:1.5b",
  "display_name": "Qwen2.5 1.5B",
  "size_gb": 1.1,
  "hf_url": "https://huggingface.co/Qwen/Qwen2.5-1.5B",
  "downloads": 1569953,
  "likes": 142,
  "compatible": true
}
```

---

## Root Cause Analysis

### Current Flow
1. **HuggingFace Integration** fetches models from HF API
2. Two different HF models are found:
   - `Qwen/Qwen2.5-1.5B-Instruct` (Instruction-tuned variant)
   - `Qwen/Qwen2.5-1.5B` (Base model variant)
3. Both map to the same Ollama model name: `qwen2.5:1.5b`
4. No deduplication logic exists
5. Both entries are returned in the API response

### Code Location
**File:** `/Users/davidcelekli/Desktop/ai-assistant/backend/main.py`
**Function:** `get_available_models()` (Line 449-516)

```python
@app.get("/models/available")
async def get_available_models():
    """
    Get ALL models from HuggingFace with compatibility flags.
    Returns both compatible and incompatible models dynamically fetched from HF API.
    """
    # ... fetches from HuggingFace ...

    # Convert to response format - include ALL models with compatibility flags
    all_models = [
        {
            "name": m.name,
            "display_name": m.display_name,
            # ... other fields ...
        }
        for m in hf_models  # ← No deduplication here
    ]

    return {"models": all_models}
```

**File:** `/Users/davidcelekli/Desktop/ai-assistant/backend/huggingface_integration.py`
**Function:** `fetch_models()` (needs investigation)

---

## Impact

### User Experience
- **Confusion:** Users see the same model listed twice
- **UI Clutter:** Unnecessary duplicate entries
- **Download Ambiguity:** Unclear which variant to download
- **Trust Issues:** Makes system appear buggy

### Technical Impact
- **Data Inconsistency:** Same model appears multiple times
- **Testing Failures:** Automated tests fail
- **Future Maintenance:** More complex to manage variants

### Affected Components
- ✅ `/models/available` endpoint
- ⚠️  Frontend model selection UI (likely affected)
- ⚠️  Download logic (may cause issues)
- ❌ `/models/downloaded` endpoint (not affected)

---

## Proposed Solutions

### Solution 1: Deduplication with Preference (Recommended)

**Implementation:**

```python
# File: backend/main.py or backend/huggingface_integration.py

def deduplicate_models_by_name(models: List[Dict]) -> List[Dict]:
    """
    Remove duplicate models with the same Ollama name.

    Preference order:
    1. Instruct variants over base variants
    2. Higher download count
    3. More recent modified date
    """
    seen = {}

    for model in models:
        name = model["name"]

        if name not in seen:
            seen[name] = model
        else:
            current = seen[name]

            # Prefer Instruct variants
            is_instruct = "instruct" in model.get("hf_url", "").lower()
            current_is_instruct = "instruct" in current.get("hf_url", "").lower()

            if is_instruct and not current_is_instruct:
                seen[name] = model
            elif is_instruct == current_is_instruct:
                # Both same type, prefer higher downloads
                if model.get("downloads", 0) > current.get("downloads", 0):
                    seen[name] = model

    return list(seen.values())


@app.get("/models/available")
async def get_available_models():
    # ... existing code ...

    all_models = [
        {
            "name": m.name,
            "display_name": m.display_name,
            # ... other fields ...
        }
        for m in hf_models
    ]

    # Apply deduplication
    unique_models = deduplicate_models_by_name(all_models)

    return {"models": unique_models}
```

**Pros:**
- ✅ Simple implementation
- ✅ Preserves user experience
- ✅ Handles future variants automatically
- ✅ Prefers most popular/useful variant

**Cons:**
- ⚠️  Users don't see alternative variants
- ⚠️  May hide legitimate different models

**Recommendation:** ⭐ **Implement this solution**

---

### Solution 2: Add Variant Suffix to Model Names

**Implementation:**

```python
# File: backend/huggingface_integration.py

def map_hf_to_ollama_name(hf_repo_id: str) -> str:
    """
    Map HuggingFace repository ID to Ollama model name with variant.

    Examples:
    - Qwen/Qwen2.5-1.5B-Instruct → qwen2.5:1.5b-instruct
    - Qwen/Qwen2.5-1.5B → qwen2.5:1.5b-base
    - meta-llama/Llama-2-7b-chat-hf → llama2:7b-chat
    """
    # Extract base name and variant
    if "instruct" in hf_repo_id.lower():
        variant = "-instruct"
    elif "chat" in hf_repo_id.lower():
        variant = "-chat"
    else:
        variant = "-base"

    # Build Ollama name
    base_name = extract_base_name(hf_repo_id)
    return f"{base_name}{variant}"
```

**Pros:**
- ✅ Users can see all variants
- ✅ Clear distinction between versions
- ✅ More granular control

**Cons:**
- ❌ Breaks existing naming convention
- ❌ Ollama may not support variant suffixes
- ❌ Requires UI changes
- ❌ More complex to maintain

**Recommendation:** ⚠️  **Not recommended** (breaks Ollama compatibility)

---

### Solution 3: Filter to Instruct-Only Models

**Implementation:**

```python
@app.get("/models/available")
async def get_available_models():
    # ... existing code ...

    # Filter to Instruct variants only
    all_models = [
        {
            "name": m.name,
            "display_name": m.display_name,
            # ... other fields ...
        }
        for m in hf_models
        if "instruct" in m.hf_url.lower() or "chat" in m.hf_url.lower()
    ]

    return {"models": all_models}
```

**Pros:**
- ✅ Simple implementation
- ✅ Removes duplicates
- ✅ Focuses on most useful variants

**Cons:**
- ❌ May exclude useful base models
- ❌ Too restrictive
- ❌ Doesn't handle all cases

**Recommendation:** ⚠️  **Not recommended** (too restrictive)

---

## Implementation Plan

### Phase 1: Immediate Fix (Recommended)
1. Implement deduplication function
2. Add to `/models/available` endpoint
3. Add unit tests for deduplication logic
4. Deploy and verify

### Phase 2: Testing
1. Re-run comprehensive test suite
2. Verify Qwen2.5 1.5B appears only once
3. Test with other model families
4. Check UI display

### Phase 3: Documentation
1. Document deduplication logic
2. Add code comments
3. Update API documentation

---

## Test Plan

### Unit Tests
```python
def test_deduplicate_models():
    """Test deduplication with preference for Instruct variants"""
    models = [
        {
            "name": "qwen2.5:1.5b",
            "hf_url": "https://huggingface.co/Qwen/Qwen2.5-1.5B",
            "downloads": 1500000
        },
        {
            "name": "qwen2.5:1.5b",
            "hf_url": "https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct",
            "downloads": 3600000
        }
    ]

    result = deduplicate_models_by_name(models)

    assert len(result) == 1
    assert "Instruct" in result[0]["hf_url"]
    assert result[0]["downloads"] == 3600000
```

### Integration Tests
```bash
# Test API endpoint
curl http://localhost:8000/models/available | \
  grep -c "qwen2.5:1.5b"
# Expected: 1 (not 2)
```

---

## Related Issues

- **MODEL-002:** Filter downloaded models from available list
- **MODEL-003:** Add visual indicators for model variants
- **UI-001:** Model selection dropdown shows duplicates

---

## References

- Test Report: `/Users/davidcelekli/Desktop/ai-assistant/docs/TEST_REPORT_MODEL_MANAGEMENT.md`
- Main API: `/Users/davidcelekli/Desktop/ai-assistant/backend/main.py`
- HF Integration: `/Users/davidcelekli/Desktop/ai-assistant/backend/huggingface_integration.py`

---

**Created:** November 15, 2025
**Updated:** November 15, 2025
**Reporter:** QA Agent (Automated Test Suite)
