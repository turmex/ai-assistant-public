# 🚀 AI Assistant - Quick Start Guide

## ONE-COMMAND LAUNCH

Run this single command to start everything:

```bash
cd ~/Desktop/ai-assistant && ./launch.sh
```

This will:
1. ✅ Kill any existing processes on ports 8000, 11434, 5173
2. ✅ Start Ollama service
3. ✅ Launch Backend in new Terminal tab
4. ✅ Launch Frontend in new Terminal tab
5. ✅ Open browser to http://localhost:5173/index.html

---

## 🎯 New Model Management Features

### **Downloaded Models Section**
- Located at the **TOP** of the model selector modal
- Green background for easy identification
- Shows all models you've already downloaded

### **Button States**

**When model is NOT downloaded:**
- Shows: `[Download]` button

**When model IS downloaded but NOT loaded:**
- Shows: `[Load Model]` + `[Delete Model]` buttons

**When model IS loaded:**
- Shows: `[Unload Model]` button ONLY

### **Auto-Unload Feature**
When you click "Load Model" on a different model:
1. If another model is currently loaded → it **automatically unloads** first
2. Then loads the new model
3. UI updates to show new model state

---

## 🛑 How to Stop

### Option 1: Close Terminal Tabs
Just close the 2 Terminal tabs that were opened for Backend and Frontend.

### Option 2: One-Command Stop
```bash
lsof -ti:8000,11434,5173 | xargs kill -9
```

---

## ✨ Default Model

The system defaults to **llama3.2:1b** (Llama 3.2 1B) as the recommended model.

**Enjoy your AI Assistant!** 🎉
