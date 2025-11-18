# Starting the AI Assistant

## Quick Start (Recommended)

The easiest way to start the server:

```bash
cd ~/Desktop/ai-assistant
./start-server.sh
```

This script will:
- Activate the virtual environment automatically
- Install dependencies if needed
- Start the server on port 8000

## Manual Start

If you prefer to start manually:

### Step 1: Activate Virtual Environment

```bash
cd ~/Desktop/ai-assistant/backend
source .venv/bin/activate  # or: source venv/bin/activate
```

### Step 2: Start the Backend

```bash
python main.py
```

Or using uvicorn directly:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Step 3: Access the Application

Open your browser and navigate to:

**http://localhost:8000**

or

**http://127.0.0.1:8000**

## What's Fixed

✅ **Model Selector**: Now in a separate modal screen - click the "Models" button in the header
✅ **Performance Colors**:
  - 🟢 Green = Fastest (real-time conversations)
  - 🔵 Blue = Fast (general chat, coding)
  - 🟡 Yellow = Good (complex reasoning)
  - 🔴 Red = Slow (expert-level tasks)
✅ **Hover Tooltips**: Hover over any model to see its best use cases
✅ **Localhost Access**: Frontend now served directly by the backend on port 8000

## Notes

- Port 8000 is the standard port for this application
- The frontend is served from `frontend-v2/index.html`
- API endpoints are available at `http://localhost:8000/api/*`
- Make sure Ollama is running before starting the backend
