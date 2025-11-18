# Ollama Integration Analysis

## Primary Integration File

**File:** `backend/ollama_integration.py` (811 lines)

### OllamaIntegration Class

Main class managing model catalog and compatibility checking.

#### Key Methods

1. **`get_catalog(ram_gb, chip_type)`** (line 370-447)
   - Returns list of OllamaModelInfo with compatibility flags
   - Filters models based on available RAM
   - Calculates performance tiers
   - Sorts by compatibility, performance, and size

2. **`search_ollama_url(url, ram_gb, chip_type)`** (line 618-742)
   - Search for model by Ollama library URL
   - Extracts model name from URL patterns
   - Returns model details with compatibility info

3. **`check_hf_ollama_compatibility(hf_model_id, model_size_gb)`** (line 744-798)
   - Checks if HuggingFace model available in Ollama format
   - Maps common HF models to Ollama equivalents
   - Detects GGUF format models

### Model Catalog

**OLLAMA_MODEL_CATALOG** (line 43-354) - Comprehensive database with 25+ models:

- **Llama Family**: 3.2 (1B, 3B), 3.1 (8B, 70B), 3 (8B, 70B), CodeLlama (7B, 13B)
- **Mistral Family**: 7B, Mixtral 8x7B
- **Phi Family** (Microsoft): Mini (3.8B), Medium (14B)
- **Gemma Family** (Google): 2B, 9B
- **Qwen Family** (Alibaba): 0.5B, 1.5B, 7B
- **DeepSeek Family**: R1 (1.5B, 7B), Coder (6.7B)
- **Specialized**: Dolphin Mixtral, Neural Chat, Orca Mini, Vicuna, WizardCoder, Nous Hermes, Starling LM

Each model includes:
- Name (e.g., `llama3.2:1b`)
- Display name, size (GB), parameters
- Description, tags, family
- Quality level, license
- Performance characteristics

## API Endpoints (main.py)

### Model Management

1. **`GET /models`** (line 415-436)
   - Lists all downloaded Ollama models
   - Calls Ollama: `GET /api/tags`

2. **`GET /models/available`** (line 495-609)
   - Returns ALL models with compatibility flags
   - Prioritizes Ollama catalog, adds HuggingFace models
   - Includes compatibility reasons for incompatible models

3. **`GET /models/downloaded`** (line 612-636)
   - Lists models currently installed locally
   - Extracts model names from Ollama API

4. **`POST /models/download`** (line 439-492)
   - Initiates model download via Ollama
   - Polls for new model appearance
   - Returns actual model name from Ollama

5. **`DELETE /models/{model_name}`** (line 863-905)
   - Removes downloaded model
   - Calls Ollama: `DELETE /api/delete`

6. **`POST /models/search-url`** (line 698-808)
   - Unified search for Ollama and HuggingFace URLs
   - Detects URL type and routes appropriately

## Ollama API Integration

**Base URL:** `http://localhost:11434` (configurable via OLLAMA_BASE_URL)

### API Calls Made

1. **`GET /api/tags`** - List available models
2. **`POST /api/pull`** - Download/pull a model
3. **`POST /api/chat`** - Chat completion with context
4. **`POST /api/generate`** - Simple text generation (fallback)
5. **`DELETE /api/delete`** - Remove a model

### Chat Flow (main.py line 908-1004)

Multi-fallback strategy for robust chat:

1. **First attempt:** `POST /api/chat` with full sanitized context
2. **Second attempt:** `POST /api/chat` with only last user message
3. **Third attempt:** `POST /api/generate` with flattened prompt string

Returns empty response error only if all three attempts fail.

## Configuration

**Environment Variables:**
- `OLLAMA_BASE_URL` - Default: `http://localhost:11434`
- `DEFAULT_LOCAL_MODEL` - Fallback model name

**Auto-initialization:**
- Checks Ollama availability on startup (line 88-115)
- Auto-downloads `llama3.2:1b` if no models present
- Non-fatal if Ollama not running (degraded mode)
