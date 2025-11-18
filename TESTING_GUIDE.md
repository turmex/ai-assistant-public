# Testing Guide - AI Assistant MVP

This guide walks through testing all features of the AI Assistant MVP.

## Prerequisites

1. Ollama is running (`ollama serve`)
2. Backend server is running (`./start.sh` or `python main.py`)
3. Frontend is open in browser (`open frontend/index.html`)

---

## ✅ Test 1: Hardware Detection

**What to test**: System automatically detects your Mac hardware

**Steps**:
1. Open frontend in browser
2. Look at the "Your Hardware" section

**Expected Results**:
- ✓ Chip type displays (e.g., "M2" or "Intel Core i7")
- ✓ RAM displays in GB (e.g., "16 GB")
- ✓ CPU cores displays (e.g., "8")
- ✓ Compatible models count displays (e.g., "5 models")

**Pass/Fail**: ___________

---

## ✅ Test 2: Model Catalog Display

**What to test**: All compatible models are shown with performance indicators

**Steps**:
1. Click the "Model:" dropdown
2. Review all available models

**Expected Results**:
- ✓ Multiple models listed (varies by your hardware)
- ✓ Recommended model has ⭐ star
- ✓ Each model shows:
  - Display name (e.g., "Llama 3.1 8B")
  - Performance badge (🟢🟡🟠🔴)
  - Size in GB
  - "(Not downloaded)" if not installed
- ✓ Models are sorted by performance/quality

**Example dropdown entry**:
```
⭐ Llama 3.1 8B 🟢 - 4.7GB
```

**Pass/Fail**: ___________

---

## ✅ Test 3: Model Information Panel

**What to test**: Model details update when selecting different models

**Steps**:
1. Select first model in dropdown
2. Check "Current Model" panel on right
3. Select different model
4. Check panel updates

**Expected Results**:
- ✓ Model name updates
- ✓ Size displays correctly
- ✓ Performance shows with badge
- ✓ Speed estimate displays (e.g., "Fast (10-15 tok/s)")

**Pass/Fail**: ___________

---

## ✅ Test 4: Model Download (if you have undownloaded models)

**What to test**: One-click model download functionality

**Steps**:
1. Select a model with "(Not downloaded)" label
2. Click the "Download" button that appears
3. Wait for download to start

**Expected Results**:
- ✓ Download button disappears
- ✓ "Downloading..." progress indicator shows
- ✓ Success toast notification appears
- ✓ Ollama pulls the model in background

**Note**: Large models (7B+) can take several minutes!

**Pass/Fail**: ___________

---

## ✅ Test 5: Basic Chat

**What to test**: Send message and receive response

**Steps**:
1. Ensure a downloaded model is selected
2. Type "Hello, what can you help me with?" in input
3. Press Enter or click Send
4. Wait for response

**Expected Results**:
- ✓ Message appears on right (blue bubble) as "You"
- ✓ Typing indicator shows (3 animated dots)
- ✓ Response appears on left as "Assistant"
- ✓ Model name badge shows on assistant message
- ✓ Response is relevant to question

**Pass/Fail**: ___________

---

## ✅ Test 6: Conversation Context

**What to test**: Assistant remembers previous messages

**Steps**:
1. Send: "My favorite color is blue"
2. Wait for response
3. Send: "What's my favorite color?"
4. Check response

**Expected Results**:
- ✓ Assistant responds with "blue" or mentions blue
- ✓ Both messages appear in chat history
- ✓ Context is maintained across messages

**Pass/Fail**: ___________

---

## ✅ Test 7: Model Switching

**What to test**: Can switch models mid-conversation

**Steps**:
1. Send a message with Model A selected
2. Switch to Model B in dropdown
3. Send another message
4. Check model badges on responses

**Expected Results**:
- ✓ First response shows Model A badge
- ✓ Second response shows Model B badge
- ✓ Conversation context preserved
- ✓ No errors when switching

**Pass/Fail**: ___________

---

## ✅ Test 8: New Conversation

**What to test**: Starting fresh conversation clears context

**Steps**:
1. Send: "Remember this: My name is Alice"
2. Wait for response
3. Click "New conversation" button
4. Send: "What's my name?"

**Expected Results**:
- ✓ Chat clears after clicking "New conversation"
- ✓ Welcome message appears
- ✓ Assistant doesn't remember "Alice"
- ✓ Fresh conversation starts

**Pass/Fail**: ___________

---

## ✅ Test 9: Connection Status

**What to test**: Health status indicator

**Steps**:
1. Check status badge (top right)
2. Should show "Online" with green dot

**Expected Results**:
- ✓ Status shows "Online" (or "Degraded" if Ollama has issues)
- ✓ Green dot (or yellow/red if issues)

**Optional**: Stop Ollama and refresh page to see "Offline" status

**Pass/Fail**: ___________

---

## ✅ Test 10: Example Prompts

**What to test**: Quick example buttons work

**Steps**:
1. Click any example prompt in sidebar (e.g., "What can you help me with?")
2. Check input field

**Expected Results**:
- ✓ Example text populates in input field
- ✓ Input field gets focus
- ✓ Can edit before sending or send as-is

**Pass/Fail**: ___________

---

## 🔧 API Testing (Optional - for developers)

Test backend endpoints directly:

```bash
# 1. Health check
curl http://localhost:8000/health | jq
# Expected: {"status": "healthy", "ollama_available": true, ...}

# 2. Hardware info
curl http://localhost:8000/hardware | jq
# Expected: Full hardware details + compatible_models array

# 3. Available models
curl http://localhost:8000/models/available | jq
# Expected: {"models": [{name, display_name, performance, ...}]}

# 4. Downloaded models
curl http://localhost:8000/models/downloaded | jq
# Expected: {"models": ["llama3.1:8b", ...]}

# 5. Send chat message
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello!"}' | jq
# Expected: {"response": "...", "conversation_id": "...", "model_used": "..."}
```

---

## 🐛 Common Issues & Solutions

### Issue: "Offline" status
**Solution**:
```bash
# Check Ollama
curl http://localhost:11434/api/tags
# If fails, start Ollama
ollama serve
```

### Issue: No models in dropdown
**Solution**:
```bash
# Check backend logs for errors
# Verify hardware detection worked
python -c "from hardware_detector import get_hardware_detector; print(get_hardware_detector().get_hardware_summary())"
```

### Issue: Chat not responding
**Solution**:
- Check browser console (F12) for errors
- Verify model is downloaded: `ollama list`
- Check backend logs for errors

### Issue: Empty response from model
**Solution**:
- Try a different model
- Check Ollama logs: `journalctl -u ollama -f` (Linux) or console where `ollama serve` is running
- Ensure model is fully downloaded

---

## ✅ Final Checklist

Before considering testing complete, verify:

- [ ] Hardware detection works
- [ ] All compatible models show in dropdown
- [ ] Can download a new model (if needed)
- [ ] Can send messages and get responses
- [ ] Context is maintained in conversation
- [ ] Can switch models mid-conversation
- [ ] "New conversation" clears context
- [ ] Status indicator shows correct state
- [ ] No console errors in browser
- [ ] No errors in backend logs

---

## 📊 Test Results Summary

**Date**: ___________
**Tester**: ___________
**Hardware**: ___________

**Tests Passed**: ___ / 10
**Overall Status**: ⬜ Pass ⬜ Fail ⬜ Partial

**Notes**:
_________________________________________
_________________________________________
_________________________________________

---

**Questions or Issues?** Check the main README.md for troubleshooting!
