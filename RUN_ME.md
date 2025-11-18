# 🚀 RUN ME - One Command Launch

## Quick Start (Easiest Way)

Run this **ONE command** to start everything:

```bash
cd ~/Desktop/ai-assistant && ./setup-and-run.sh
```

This script will:
1. ✅ Kill any existing Ollama/Backend/Frontend processes
2. ✅ Free up ports 11434, 8000, 5173
3. ✅ Check if Ollama is installed
4. ✅ Create/setup Python virtual environment
5. ✅ Install all dependencies
6. ✅ Initialize database
7. ✅ Open 3 tabs in Terminal (Ollama, Backend, Frontend)
8. ✅ Start all services automatically

---

## What You'll See

The script will open **3 tabs** in your Terminal:

- **Tab 1**: Ollama server (running on port 11434)
- **Tab 2**: Python backend (running on port 8000)
- **Tab 3**: Frontend server (running on port 5173)

**After 5-10 seconds**, open your browser to:
```
http://localhost:5173/index.html
```

---

## If Virtual Environment Issues

If you get errors about `venv`, run this **first**:

```bash
cd ~/Desktop/ai-assistant && ./fix-venv.sh
```

This will recreate the virtual environment from scratch.

Then run:
```bash
./setup-and-run.sh
```

---

## To Stop Everything

Two options:

**Option 1: Press Ctrl+C in each tab**

**Option 2: Run cleanup script**
```bash
cd ~/Desktop/ai-assistant && ./cleanup.sh
```

This kills all processes and frees all ports.

---

## First Time Users

If this is your **first time**, make sure Ollama is installed:

```bash
brew install ollama
```

Then run:
```bash
cd ~/Desktop/ai-assistant && ./setup-and-run.sh
```

---

## Scripts Explained

### `setup-and-run.sh`
- **Complete automation**: Kills old processes, sets up environment, launches everything
- **Opens 3 tabs**: All services in one Terminal window
- **Automatic**: Just run and wait

### `cleanup.sh`
- **Stops everything**: Kills all AI Assistant processes
- **Frees ports**: 11434, 8000, 5173
- **Safe**: Won't affect other apps

### `fix-venv.sh`
- **Fixes Python environment**: Recreates virtual environment
- **Reinstalls dependencies**: Fresh install of all packages
- **Resets database**: Initializes from scratch

---

## Common Issues & Solutions

### "Ollama is already running"
**Solution**: The script automatically handles this. Just run:
```bash
./setup-and-run.sh
```

### "Virtual environment not found"
**Solution**:
```bash
./fix-venv.sh
./setup-and-run.sh
```

### "Port already in use"
**Solution**: Run cleanup first:
```bash
./cleanup.sh
./setup-and-run.sh
```

### "Permission denied"
**Solution**: Make scripts executable:
```bash
chmod +x setup-and-run.sh cleanup.sh fix-venv.sh
```

---

## What Happens on First Run

1. **Ollama starts** (Tab 1)
2. **Backend starts** (Tab 2)
   - Detects your hardware
   - **Auto-downloads Llama 3.2 1B** if no models exist
   - Shows: `✓ AI Assistant Backend is ready!`
3. **Frontend starts** (Tab 3)
   - Serves UI on port 5173
4. **You open browser** to http://localhost:5173/index.html

---

## Expected Output

After running `./setup-and-run.sh`, you should see:

```
🚀 AI Assistant - Setup and Run
================================

🧹 Step 1: Cleaning up existing processes...
  ✓ Ollama stopped
  ✓ Port 11434 freed
  ✓ Port 8000 freed
  ✓ Port 5173 freed

🔍 Step 2: Checking Ollama installation...
  ✓ Ollama is installed

🐍 Step 3: Setting up Python environment...
  ✓ Virtual environment created
  ✓ Dependencies installed
  ✓ Database initialized

📝 Step 4: Creating launch script...
  ✓ Launch script created

🚀 Step 5: Launching AI Assistant...
  Opening 3 tabs in Terminal...

═══════════════════════════════════════════════════════
  ✅ AI Assistant is launching!
═══════════════════════════════════════════════════════

📱 Next Steps:
  1. Check the 3 Terminal tabs that just opened
  2. Wait for all services to finish starting (~10 seconds)
  3. Open your browser to:
     http://localhost:5173/index.html
```

---

## Video Walkthrough (What to Expect)

1. **Run command**: `cd ~/Desktop/ai-assistant && ./setup-and-run.sh`
2. **Wait 5 seconds**: Script runs cleanup and setup
3. **3 tabs open**: Terminal opens with Ollama, Backend, Frontend
4. **Wait 10 seconds**: Services start up
5. **Open browser**: Go to http://localhost:5173/index.html
6. **Use the app**: Chat with local AI models!

---

## Need Help?

1. **Check tab outputs**: Look for errors in each Terminal tab
2. **Run cleanup**: `./cleanup.sh` then try again
3. **Fix venv**: `./fix-venv.sh` then try again
4. **Check ports**: `lsof -i:11434,8000,5173`

---

## Success Checklist

- [ ] Ran `./setup-and-run.sh`
- [ ] 3 tabs opened in Terminal
- [ ] No errors in any tab
- [ ] Backend shows: `✓ AI Assistant Backend is ready!`
- [ ] Opened http://localhost:5173/index.html
- [ ] UI loads with hardware info
- [ ] Model selector shows models
- [ ] Can chat with AI

---

**You're ready! Just run:**
```bash
cd ~/Desktop/ai-assistant && ./setup-and-run.sh
```

Then open: **http://localhost:5173/index.html** 🎉
