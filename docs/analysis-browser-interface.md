# Browser Interface Analysis

**File:** `frontend/index.html` (543 lines)
**Type:** Single-page application (SPA)
**Framework:** Vanilla JavaScript + Tailwind CSS

## UI Components

### 1. Header (line 40-58)
```html
<header class="mb-4">
  <div class="flex items-center justify-between gap-3">
    <div><!-- App logo and title --></div>
    <div id="statusBadge"><!-- Connection status --></div>
  </div>
</header>
```
- App title with animated logo
- Status badge showing "Online/Degraded/Offline"
- Color-coded status dot (green/amber/red)

### 2. Hardware Banner (line 61-95)
```html
<section class="mb-4">
  <div><!-- Hardware information display --></div>
</section>
```
Displays detected hardware:
- **Chip:** M1/M2/M3 or Intel model
- **RAM:** Total system RAM in GB
- **Cores:** Physical CPU cores
- **Compatible:** Number of compatible models

Updated by `loadHardware()` function (line 252-272)

### 3. Model Selector (line 102-122)
```html
<select id="modelSelector">
  <option>Model options populated dynamically</option>
</select>
<button id="downloadBtn">Download</button>
```
Dropdown showing:
- ⭐ Star for recommended model
- Performance badge (🟢🟡🟠🔴)
- Model name and size (e.g., "Llama 3.2 1B 🟢 - 1.3GB")
- "(Not downloaded)" suffix if needed

### 4. Chat Container (line 125)
```html
<div id="chatContainer" class="h-[50vh] overflow-y-auto">
  <!-- Message bubbles dynamically inserted -->
</div>
```
- Scrollable message area
- User messages (right-aligned, indigo)
- Assistant messages (left-aligned, slate)
- Model badge on assistant messages
- Typing indicator animation

### 5. Input Area (line 128-142)
```html
<textarea id="messageInput" placeholder="Ask anything..."></textarea>
<button id="sendBtn">Send</button>
<button id="resetBtn">New conversation</button>
```
- Auto-expanding textarea
- Enter to send, Shift+Enter for new line
- New conversation button clears history

### 6. Sidebar (line 146-177)
```html
<aside>
  <div id="currentModelInfo"><!-- Model details --></div>
  <div id="examples"><!-- Example prompts --></div>
</aside>
```
Shows current model:
- Name, Size, Performance, Speed estimate
- Example prompts (clickable to populate input)

## JavaScript State

### Global Variables (line 188-192)
```javascript
let conversationId = null;       // Current conversation ID
let availableModels = [];        // All compatible models
let downloadedModels = [];       // Installed models only
let selectedModel = null;        // Currently selected model
```

### Configuration
```javascript
const API = 'http://localhost:8000';  // Backend URL
```

## Key Functions

### Model Management

**`loadModels()`** (line 274-313)
- Fetches `/models/available` - compatible models
- Fetches `/models/downloaded` - installed models
- Populates `<select>` with options
- Adds performance badges and download status
- Selects recommended model if downloaded

**`updateModelInfo(model)`** (line 315-326)
- Updates sidebar with model details
- Shows performance badge and speed estimate
- Called on model selection change

**`downloadModel(modelName)`** (line 328-355)
- Shows loading spinner
- POST to `/models/download`
- Polls for completion (5 second delay)
- Refreshes model list when done

### Chat Functionality

**`sendMessage(text)`** (line 400-454)
- Appends user message bubble
- Shows typing indicator
- POST to `/chat` with message and model
- Handles response or error
- Updates conversation ID
- Removes typing indicator, shows reply

**`messageBubble({role, text, model})`** (line 360-379)
- Creates styled message bubble
- Different colors for user/assistant
- Includes model badge for assistant messages

**`typingBubble()`** (line 381-392)
- Animated three-dot indicator
- Shown during API request

### Hardware Detection

**`loadHardware()`** (line 252-272)
- Fetches `/hardware` endpoint
- Extracts chip, RAM, cores, compatible count
- Updates hardware banner display
- Stores `availableModels` array

**`updateHealthStatus()`** (line 236-250)
- Fetches `/health` endpoint
- Updates status badge color and text
- Polls every 30 seconds (line 533)

### Utilities

**`fetchJSON(url, opts, timeout)`** (line 217-234)
- Wrapper for fetch with timeout
- Handles JSON and text responses
- Extracts error messages from various response shapes
- Returns parsed data or throws error

**`toast(msg, type)`** (line 202-215)
- Shows temporary notification
- Types: info, success, error, warn
- Auto-dismisses after 3.8 seconds

**`scrollToBottom(force)`** (line 394-398)
- Auto-scrolls chat to latest message
- Only scrolls if user is near bottom (unless forced)

## Event Bindings (line 477-527)

### Input Handling
- `keydown` on textarea: Enter sends, Shift+Enter new line
- `input` on textarea: Auto-resize height
- `click` on send button: Trigger sendMessage()

### Model Selection
- `change` on selector: Update model info, show/hide download button

### Actions
- `click` on download button: Start model download
- `click` on reset button: Clear chat, start new conversation
- `click` on example prompts: Populate input field

## Performance Badges

```javascript
const perfBadges = {
  excellent: '🟢',
  good: '🟡',
  acceptable: '🟠',
  slow: '🔴'
};
```

Used in model dropdown to show expected performance tier.

## Initialization Flow (line 530-539)

```javascript
async function init() {
  await Promise.all([loadHardware(), updateHealthStatus()]);
  await loadModels();
  setInterval(updateHealthStatus, 30000);  // Poll health every 30s
  // Show welcome message
}
```

1. Load hardware info and health status in parallel
2. Load and populate model list
3. Start health status polling
4. Display welcome message in chat
