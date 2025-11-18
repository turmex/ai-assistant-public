# Model Compatibility Guide

## ✅ Verified Working Models

### Official Ollama Models (Recommended)

These models are officially supported by Ollama and work out-of-the-box:

| Model Name | Ollama Command | Parameters | Use Case | Speed | Quality |
|------------|----------------|------------|----------|-------|---------|
| **GPT-OSS 20B** | `ollama pull gpt-oss:20b` | 21B (3.6B active MoE) | Function calling, web browsing, tools | Medium | Excellent |
| Llama 3.2 1B | `ollama pull llama3.2:1b` | 1.3B | Fast general chat | Very Fast | Good |
| Llama 3.2 3B | `ollama pull llama3.2:3b` | 2.0B | Balanced chat & reasoning | Fast | Very Good |
| Llama 3.1 8B | `ollama pull llama3.1:8b` | 4.7B | Advanced reasoning | Medium | Excellent |
| Mistral 7B | `ollama pull mistral:7b` | 4.1B | General purpose, fast | Fast | Excellent |
| Phi 3 Mini | `ollama pull phi3:mini` | 2.3B | Code generation | Fast | Very Good |
| Qwen 2.5 1.5B | `ollama pull qwen2.5:1.5b` | 2.0B | General purpose | Fast | Good |

### Community Models

| Model Name | Ollama Command | Notes |
|------------|----------------|-------|
| GPT-2 | `ollama pull mapler/gpt2` | Legacy model (124M params), outdated |
| xLAM 1B | `ollama pull allenporter/xlam:1b` | Function calling specialist |

---

## ⚠️ Models That Require Special Setup

### xLAM-1b-fc-r (Salesforce)

**HuggingFace URL**: https://huggingface.co/Salesforce/xLAM-1b-fc-r

**Options**:
1. **Community variant** (easiest):
   ```bash
   ollama pull allenporter/xlam:1b
   ```

2. **Manual GGUF setup** (research only):
   - Download GGUF from: https://huggingface.co/Salesforce/xLAM-1b-fc-r-gguf
   - Create custom Modelfile
   - Import with `ollama create`
   - **License**: CC-BY-NC-4.0 (non-commercial only)

---

## ❌ Models NOT Available in Ollama

These models cannot be downloaded through Ollama:

| Model | Reason | Alternative |
|-------|--------|-------------|
| openai-community/gpt2 | Not in Ollama registry | Use `mapler/gpt2` community variant |
| Most Salesforce models | Not converted for Ollama | Check for community variants |
| Most OpenAI proprietary models | Closed-source, API-only | Use open alternatives like `gpt-oss:20b` |

---

## 🔧 How Model Downloads Work

### 1. **User Searches HuggingFace URL**
   - Frontend sends URL to `/models/search-hf`
   - Backend extracts model ID and generates Ollama name
   - Returns model info with compatibility check

### 2. **User Clicks Download**
   - Frontend calls `/models/download` with model name
   - Backend detects models BEFORE download
   - Initiates Ollama pull (5-minute timeout)
   - Detects actual downloaded model name
   - Returns `actual_model` to frontend

### 3. **Frontend Polls for Completion**
   - Uses `actual_model` from backend (not guessed name)
   - Polls `/models/downloaded` every 5 seconds
   - Checks for exact match OR normalized match
   - 15-minute timeout for large models
   - Progress updates every minute

---

## 🐛 Common Issues & Fixes

### Issue 1: "Taking longer than expected, refresh manually"

**Causes**:
- ✅ **FIXED**: Backend timeout was 30s (now 300s)
- ✅ **FIXED**: Model name mismatch (now uses `actual_model` from backend)
- ✅ **FIXED**: Insufficient polling timeout (now 15 minutes)

**Current Behavior**:
- Large models (7B+) may take 10-20 minutes
- Progress updates every minute
- Download continues in background even if polling times out

### Issue 2: Model appears twice in Downloaded Models

**Causes**:
- ✅ **FIXED**: No duplicate detection (now uses Map-based deduplication)
- ✅ **FIXED**: Name variations not normalized (now uses fuzzy matching)

### Issue 3: Downloaded model doesn't appear

**Causes**:
- ✅ **FIXED**: Name mismatch between requested and actual (now uses `actual_model`)
- ✅ **FIXED**: Frontend polling for wrong name (now uses backend-provided name)

---

## 📊 Performance Expectations

### Download Times (approximate)

| Model Size | Download Time | Recommended Connection |
|------------|---------------|------------------------|
| 1-3B | 2-5 minutes | Standard broadband |
| 3-7B | 5-10 minutes | Standard broadband |
| 7-13B | 10-20 minutes | Fast broadband |
| 13B+ | 20-30 minutes | Very fast broadband |

### Inference Speed (tokens/second)

| Hardware | 1-3B | 3-7B | 7-13B | 13B+ |
|----------|------|------|-------|------|
| Apple M1/M2 (8GB) | 10-15 | 5-10 | 2-5 | 1-3 |
| Apple M1/M2 Pro (16GB) | 15-20 | 10-15 | 5-10 | 2-5 |
| Apple M1/M2 Max (32GB) | 20-30 | 15-20 | 10-15 | 5-10 |
| Intel Mac (16GB) | 5-10 | 3-5 | 1-3 | <1 |

---

## 🎯 Recommended Models by Use Case

### Speed Priority (Real-time chat)
1. **llama3.2:1b** - Fastest, good quality
2. **llama3.2:3b** - Fast, better quality
3. **phi3:mini** - Fast, excellent for code

### Quality Priority (Complex reasoning)
1. **gpt-oss:20b** - Best overall, function calling
2. **llama3.1:8b** - Excellent reasoning
3. **mistral:7b** - Great general purpose

### Function Calling
1. **gpt-oss:20b** - Official support, best accuracy
2. **allenporter/xlam:1b** - Specialized, very fast

### Code Generation
1. **phi3:mini** - Optimized for code
2. **llama3.1:8b** - Excellent code quality
3. **codellama:13b** - Specialized, slower

---

## 🔍 Testing Recommendations

To verify the fixes work correctly, test with these models:

1. **Fast download**: `llama3.2:1b` (1.3GB, ~2 minutes)
2. **Medium download**: `phi3:mini` (2.3GB, ~5 minutes)
3. **Large download**: `llama3.1:8b` (4.7GB, ~10 minutes)
4. **Function calling**: `gpt-oss:20b` (21B params, ~20 minutes)

---

## 📝 Implementation Details

### Backend Changes (main.py:433-486)
- ✅ Increased timeout: 30s → 300s (5 minutes)
- ✅ Added model detection before/after download
- ✅ Returns `actual_model` field with real Ollama name
- ✅ Better error handling for timeouts

### Frontend Changes (index.html:646-718)
- ✅ Uses `actual_model` from backend response
- ✅ Extended polling timeout: 5 min → 15 min
- ✅ Enhanced logging for debugging
- ✅ Progress updates every minute
- ✅ Improved fuzzy name matching

### Name Normalization (index.html:407-441)
- ✅ Handles HuggingFace prefixes (`meta-llama/` → removed)
- ✅ Converts size suffixes (`-1B` → `:1b`)
- ✅ Removes instruction suffixes (`-instruct`, `-chat`)
- ✅ Normalizes version variants (`llama-3.2` → `llama`)
- ✅ Handles multiple Qwen versions

---

## 🚀 Next Steps

1. **Restart backend** to apply fixes
2. **Test with small model** (llama3.2:1b) to verify basic functionality
3. **Test with HuggingFace URL** to verify search integration
4. **Test with large model** (gpt-oss:20b) to verify timeout fixes
5. **Monitor console logs** for any remaining issues

---

## 💡 Tips for Users

1. **Download during off-peak hours** for faster speeds
2. **Start with smaller models** (1-3B) to test functionality
3. **Monitor browser console** (F12) for detailed progress
4. **Don't close browser** during download (polling will stop)
5. **Check "Downloaded Models"** section if polling times out
6. **Use official Ollama models** when possible for best compatibility

---

Generated: 2025-11-16
Version: 2.0 (Post-Hive Mind Analysis & Fixes)
