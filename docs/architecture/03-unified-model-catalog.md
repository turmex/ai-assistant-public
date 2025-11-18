# Unified Model Catalog Architecture

## Overview

The Unified Model Catalog merges models from WebLLM and Ollama into a single, searchable catalog with consistent metadata. Users see all available models regardless of provider, with clear indicators showing which providers support each model.

## Design Goals

1. **Single Source of Truth**: One catalog for all models across providers
2. **Provider Transparency**: Clear indication of which provider(s) support each model
3. **Consistent Metadata**: Normalized model information across providers
4. **Hardware Awareness**: Performance indicators based on system capabilities
5. **Download Status**: Track which models are downloaded for each provider

## Catalog Data Model

### Unified Model Information

```python
# backend/models/unified_model.py

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum

class ModelCapability(Enum):
    """Model capabilities."""
    CHAT = "chat"
    CODE = "code"
    VISION = "vision"
    FUNCTION_CALLING = "function_calling"
    INSTRUCTION = "instruction"
    MULTILINGUAL = "multilingual"
    EMBEDDINGS = "embeddings"

class PerformanceLevel(Enum):
    """Hardware performance indicators."""
    EXCELLENT = "excellent"  # 🟢 10-15+ tok/s
    GOOD = "good"            # 🟡 5-10 tok/s
    ACCEPTABLE = "acceptable"  # 🟠 2-5 tok/s
    SLOW = "slow"            # 🔴 1-3 tok/s
    INCOMPATIBLE = "incompatible"  # ⚫ Cannot run

@dataclass
class ProviderModelInfo:
    """Provider-specific model information."""
    provider: str  # "webllm" | "ollama"
    model_id: str  # Provider-specific ID
    downloaded: bool  # Is model downloaded/cached?
    download_size_gb: float  # Download size for this provider
    download_url: Optional[str] = None
    supports_streaming: bool = True
    supports_functions: bool = False
    max_context_length: int = 4096
    quantization: Optional[str] = None  # "q4_0", "q8_0", etc.

@dataclass
class PerformanceInfo:
    """Hardware-specific performance information."""
    level: PerformanceLevel
    estimated_speed: str  # "10-15 tok/s"
    ram_required_gb: int
    vram_recommended_gb: Optional[int] = None  # For GPU models
    compatible: bool = True
    compatibility_reason: Optional[str] = None

@dataclass
class UnifiedModelInfo:
    """
    Unified model information across all providers.

    A single model may be available from multiple providers (WebLLM + Ollama).
    This structure represents the model once with provider-specific details.
    """
    # Core Identification
    id: str  # Unique identifier (e.g., "llama-3-8b")
    name: str  # Display name (e.g., "Llama 3 8B")
    family: str  # Model family (e.g., "llama", "mistral")
    version: Optional[str] = None  # Model version (e.g., "3.1", "7B")

    # Size & Parameters
    parameters: str = "Unknown"  # "1B", "7B", "70B"
    base_size_gb: float = 0.0  # Approximate unquantized size

    # Capabilities
    capabilities: List[ModelCapability] = field(default_factory=list)
    description: str = ""
    use_cases: List[str] = field(default_factory=list)

    # Provider Availability
    providers: List[str] = field(default_factory=list)  # ["webllm", "ollama"]
    provider_info: Dict[str, ProviderModelInfo] = field(default_factory=dict)
    primary_provider: Optional[str] = None  # Recommended provider

    # Performance
    performance: Optional[PerformanceInfo] = None
    recommended: bool = False  # Is this recommended for user's hardware?
    quality_tier: str = "medium"  # "high", "medium", "basic"

    # Metadata
    license: Optional[str] = None
    organization: Optional[str] = None  # "Meta", "Mistral", etc.
    release_date: Optional[str] = None
    homepage: Optional[str] = None
    tags: List[str] = field(default_factory=list)

    # Statistics (if available)
    downloads: Optional[int] = None
    likes: Optional[int] = None
    benchmark_scores: Optional[Dict[str, float]] = None

    def is_downloaded(self, provider: Optional[str] = None) -> bool:
        """Check if model is downloaded for given provider or any provider."""
        if provider:
            return self.provider_info.get(provider, ProviderModelInfo("", "", False, 0.0)).downloaded
        return any(info.downloaded for info in self.provider_info.values())

    def get_download_size(self, provider: str) -> float:
        """Get download size for specific provider."""
        return self.provider_info.get(provider, ProviderModelInfo("", "", False, 0.0)).download_size_gb

    def supports_provider(self, provider: str) -> bool:
        """Check if model is available from given provider."""
        return provider in self.providers
```

## Catalog Manager

```python
# backend/catalog/unified_catalog.py

import logging
from typing import List, Optional, Dict, Any, Set
from dataclasses import asdict
from ..models.unified_model import (
    UnifiedModelInfo, ProviderModelInfo, PerformanceInfo,
    ModelCapability, PerformanceLevel
)
from ..providers.base_provider import LLMProvider, ProviderType
from ..ollama_integration import OllamaModelInfo
from ..hardware_detector import get_hardware_detector

logger = logging.getLogger(__name__)

class UnifiedModelCatalog:
    """
    Manages unified model catalog across all providers.

    Merges models from WebLLM and Ollama, normalizes metadata,
    and provides search/filter capabilities.
    """

    # WebLLM model configurations
    # Based on https://github.com/mlc-ai/web-llm/blob/main/src/config.ts
    WEBLLM_MODELS = {
        "Llama-3-8B-Instruct-q4f32_1-MLC": {
            "id": "llama-3-8b",
            "name": "Llama 3 8B Instruct",
            "family": "llama",
            "version": "3",
            "parameters": "8B",
            "base_size_gb": 4.7,
            "download_size_gb": 4.3,
            "capabilities": ["chat", "instruction"],
            "context_length": 8192,
            "quantization": "q4f32_1"
        },
        "Llama-3-1-8B-Instruct-q4f16_1-MLC": {
            "id": "llama-3.1-8b",
            "name": "Llama 3.1 8B Instruct",
            "family": "llama",
            "version": "3.1",
            "parameters": "8B",
            "base_size_gb": 4.7,
            "download_size_gb": 4.3,
            "capabilities": ["chat", "instruction", "multilingual"],
            "context_length": 128000,
            "quantization": "q4f16_1"
        },
        "Phi-3-mini-4k-instruct-q4f16_1-MLC": {
            "id": "phi-3-mini",
            "name": "Phi 3 Mini 4K",
            "family": "phi",
            "version": "3",
            "parameters": "3.8B",
            "base_size_gb": 2.3,
            "download_size_gb": 2.2,
            "capabilities": ["chat", "code", "instruction"],
            "context_length": 4096,
            "quantization": "q4f16_1"
        },
        "Mistral-7B-Instruct-v0.3-q4f16_1-MLC": {
            "id": "mistral-7b",
            "name": "Mistral 7B Instruct v0.3",
            "family": "mistral",
            "version": "0.3",
            "parameters": "7B",
            "base_size_gb": 4.1,
            "download_size_gb": 3.9,
            "capabilities": ["chat", "instruction"],
            "context_length": 32768,
            "quantization": "q4f16_1"
        },
        "gemma-2b-it-q4f16_1-MLC": {
            "id": "gemma-2b",
            "name": "Gemma 2B Instruct",
            "family": "gemma",
            "version": "2b",
            "parameters": "2B",
            "base_size_gb": 1.5,
            "download_size_gb": 1.4,
            "capabilities": ["chat", "instruction"],
            "context_length": 8192,
            "quantization": "q4f16_1"
        },
        # Add more WebLLM models...
    }

    def __init__(self):
        self.hardware_detector = get_hardware_detector()
        self.hardware_info = self.hardware_detector.detect()
        self._catalog: Dict[str, UnifiedModelInfo] = {}
        self._initialized = False

    async def initialize(
        self,
        webllm_provider: Optional[LLMProvider] = None,
        ollama_provider: Optional[LLMProvider] = None
    ) -> None:
        """
        Initialize catalog by merging models from all providers.

        Args:
            webllm_provider: WebLLM provider instance
            ollama_provider: Ollama provider instance
        """
        logger.info("Initializing unified model catalog...")

        # Start with empty catalog
        self._catalog.clear()

        # Add WebLLM models
        if webllm_provider:
            await self._add_webllm_models(webllm_provider)

        # Add Ollama models
        if ollama_provider:
            await self._add_ollama_models(ollama_provider)

        # Calculate performance for all models
        self._calculate_performance()

        # Select recommended model
        self._select_recommended()

        self._initialized = True
        logger.info(f"Catalog initialized with {len(self._catalog)} unique models")

    async def _add_webllm_models(self, provider: LLMProvider) -> None:
        """Add WebLLM models to catalog."""
        try:
            webllm_models = await provider.list_models()
            for model in webllm_models:
                model_id = self._normalize_model_id(model.name)

                # Create or update unified model
                if model_id not in self._catalog:
                    self._catalog[model_id] = self._create_unified_model(model, "webllm")
                else:
                    # Model exists from another provider, add WebLLM info
                    self._add_provider_info(self._catalog[model_id], model, "webllm")

            logger.info(f"Added {len(webllm_models)} WebLLM models")
        except Exception as e:
            logger.error(f"Failed to add WebLLM models: {e}")

    async def _add_ollama_models(self, provider: LLMProvider) -> None:
        """Add Ollama models to catalog."""
        try:
            ollama_models = await provider.list_models()
            for model in ollama_models:
                model_id = self._normalize_model_id(model.name)

                # Create or update unified model
                if model_id not in self._catalog:
                    self._catalog[model_id] = self._create_unified_model(model, "ollama")
                else:
                    # Model exists from another provider, add Ollama info
                    self._add_provider_info(self._catalog[model_id], model, "ollama")

            logger.info(f"Added {len(ollama_models)} Ollama models")
        except Exception as e:
            logger.error(f"Failed to add Ollama models: {e}")

    def _normalize_model_id(self, model_name: str) -> str:
        """
        Normalize model names to common ID format.

        Examples:
            "llama3.1:8b" -> "llama-3.1-8b"
            "Llama-3-8B-Instruct-q4f32_1-MLC" -> "llama-3-8b"
            "mistral:7b" -> "mistral-7b"
        """
        # Remove special characters and quantization suffixes
        normalized = model_name.lower()
        normalized = normalized.replace("_", "-")
        normalized = normalized.replace(":", "-")

        # Remove quantization suffixes
        suffixes = ["-q4f32-1-mlc", "-q4f16-1-mlc", "-instruct", "-it", "-chat-hf"]
        for suffix in suffixes:
            normalized = normalized.replace(suffix, "")

        # Standardize version separators
        normalized = normalized.replace("llama3-", "llama-3-")
        normalized = normalized.replace("phi3-", "phi-3-")

        return normalized.strip("-")

    def _create_unified_model(
        self,
        provider_model: Any,
        provider_name: str
    ) -> UnifiedModelInfo:
        """Create a new unified model from provider-specific model."""
        # Extract common fields
        model_id = self._normalize_model_id(provider_model.name)

        unified = UnifiedModelInfo(
            id=model_id,
            name=provider_model.display_name,
            family=getattr(provider_model, "family", "unknown"),
            version=self._extract_version(provider_model.name),
            parameters=getattr(provider_model, "parameters", "Unknown"),
            base_size_gb=provider_model.size_gb,
            capabilities=self._map_capabilities(provider_model),
            description=getattr(provider_model, "description", ""),
            providers=[provider_name],
            quality_tier=getattr(provider_model, "quality", "medium"),
            license=getattr(provider_model, "license", None)
        )

        # Add provider-specific info
        self._add_provider_info(unified, provider_model, provider_name)

        return unified

    def _add_provider_info(
        self,
        unified_model: UnifiedModelInfo,
        provider_model: Any,
        provider_name: str
    ) -> None:
        """Add provider-specific information to unified model."""
        if provider_name not in unified_model.providers:
            unified_model.providers.append(provider_name)

        provider_info = ProviderModelInfo(
            provider=provider_name,
            model_id=provider_model.name,
            downloaded=getattr(provider_model, "downloaded", False),
            download_size_gb=provider_model.size_gb,
            supports_streaming=True,
            max_context_length=getattr(provider_model, "context_length", 4096),
            quantization=getattr(provider_model, "quantization", None)
        )

        unified_model.provider_info[provider_name] = provider_info

    def _map_capabilities(self, provider_model: Any) -> List[ModelCapability]:
        """Map provider-specific capabilities to unified capabilities."""
        caps = []
        tags = getattr(provider_model, "tags", [])

        mapping = {
            "chat": ModelCapability.CHAT,
            "conversation": ModelCapability.CHAT,
            "code": ModelCapability.CODE,
            "vision": ModelCapability.VISION,
            "instruction": ModelCapability.INSTRUCTION,
            "multilingual": ModelCapability.MULTILINGUAL,
        }

        for tag in tags:
            if tag in mapping:
                caps.append(mapping[tag])

        return caps

    def _calculate_performance(self) -> None:
        """Calculate performance levels for all models based on hardware."""
        ram_gb = self.hardware_info.ram_gb
        is_apple_silicon = self.hardware_info.chip_type == "Apple Silicon"

        for model in self._catalog.values():
            ram_required = int(model.base_size_gb * 2)  # 2x for safety

            # Determine performance level
            if ram_required > ram_gb:
                level = PerformanceLevel.INCOMPATIBLE
                speed = "Cannot run"
                compatible = False
                reason = f"Requires {ram_required}GB RAM, only {ram_gb}GB available"
            elif ram_required <= ram_gb // 2:
                level = PerformanceLevel.EXCELLENT
                speed = "10-15+ tok/s" if is_apple_silicon else "8-12 tok/s"
                compatible = True
                reason = None
            elif ram_required <= ram_gb * 0.7:
                level = PerformanceLevel.GOOD
                speed = "5-10 tok/s" if is_apple_silicon else "4-8 tok/s"
                compatible = True
                reason = None
            elif ram_required <= ram_gb:
                level = PerformanceLevel.ACCEPTABLE
                speed = "2-5 tok/s"
                compatible = True
                reason = "May be slow, consider smaller model"
            else:
                level = PerformanceLevel.SLOW
                speed = "1-3 tok/s"
                compatible = True
                reason = "Will be very slow, smaller model recommended"

            model.performance = PerformanceInfo(
                level=level,
                estimated_speed=speed,
                ram_required_gb=ram_required,
                compatible=compatible,
                compatibility_reason=reason
            )

    def _select_recommended(self) -> None:
        """Select recommended model based on hardware and availability."""
        # Sort by: compatible > excellent performance > size (smaller better)
        compatible_models = [
            m for m in self._catalog.values()
            if m.performance and m.performance.compatible
        ]

        if not compatible_models:
            return

        # Prefer models with excellent performance
        excellent = [m for m in compatible_models if m.performance.level == PerformanceLevel.EXCELLENT]
        if excellent:
            # Pick medium-sized model from excellent category
            recommended = sorted(excellent, key=lambda m: abs(m.base_size_gb - 4.0))[0]
            recommended.recommended = True
            recommended.primary_provider = "webllm" if "webllm" in recommended.providers else "ollama"

    def get_all_models(self) -> List[UnifiedModelInfo]:
        """Get all models in catalog."""
        return list(self._catalog.values())

    def get_model(self, model_id: str) -> Optional[UnifiedModelInfo]:
        """Get specific model by ID."""
        return self._catalog.get(model_id)

    def search_models(
        self,
        query: Optional[str] = None,
        provider: Optional[str] = None,
        capability: Optional[ModelCapability] = None,
        max_size_gb: Optional[float] = None,
        compatible_only: bool = False,
        downloaded_only: bool = False
    ) -> List[UnifiedModelInfo]:
        """
        Search and filter models.

        Args:
            query: Search in name/description
            provider: Filter by provider availability
            capability: Filter by capability
            max_size_gb: Maximum model size
            compatible_only: Only compatible models
            downloaded_only: Only downloaded models

        Returns:
            List of matching models
        """
        results = self.get_all_models()

        # Filter by query
        if query:
            query_lower = query.lower()
            results = [
                m for m in results
                if query_lower in m.name.lower() or query_lower in m.description.lower()
            ]

        # Filter by provider
        if provider:
            results = [m for m in results if provider in m.providers]

        # Filter by capability
        if capability:
            results = [m for m in results if capability in m.capabilities]

        # Filter by size
        if max_size_gb:
            results = [m for m in results if m.base_size_gb <= max_size_gb]

        # Filter by compatibility
        if compatible_only:
            results = [m for m in results if m.performance and m.performance.compatible]

        # Filter by download status
        if downloaded_only:
            results = [m for m in results if m.is_downloaded()]

        return results

    def get_recommended_model(self) -> Optional[UnifiedModelInfo]:
        """Get the recommended model for current hardware."""
        for model in self._catalog.values():
            if model.recommended:
                return model
        return None

    def to_dict(self) -> Dict[str, Any]:
        """Convert catalog to dictionary for JSON serialization."""
        return {
            "models": [asdict(model) for model in self._catalog.values()],
            "count": len(self._catalog),
            "hardware": {
                "chip": self.hardware_info.chip_type,
                "ram_gb": self.hardware_info.ram_gb
            }
        }

# Global catalog instance
_catalog_instance: Optional[UnifiedModelCatalog] = None

def get_unified_catalog() -> UnifiedModelCatalog:
    """Get or create the global unified catalog instance."""
    global _catalog_instance
    if _catalog_instance is None:
        _catalog_instance = UnifiedModelCatalog()
    return _catalog_instance
```

## API Integration

```python
# backend/main.py (new endpoints)

from catalog.unified_catalog import get_unified_catalog
from models.unified_model import ModelCapability

# Get unified model catalog
@app.get("/models/unified")
async def get_unified_models(
    provider: Optional[str] = None,
    capability: Optional[str] = None,
    compatible_only: bool = False,
    downloaded_only: bool = False
):
    """Get unified model catalog with filtering."""
    catalog = get_unified_catalog()

    if not catalog._initialized:
        # Initialize with available providers
        factory = get_provider_factory()
        await catalog.initialize(
            webllm_provider=factory.get_provider(ProviderType.WEBLLM),
            ollama_provider=factory.get_provider(ProviderType.OLLAMA)
        )

    # Parse capability if provided
    cap = ModelCapability(capability) if capability else None

    models = catalog.search_models(
        provider=provider,
        capability=cap,
        compatible_only=compatible_only,
        downloaded_only=downloaded_only
    )

    return {
        "models": [asdict(m) for m in models],
        "count": len(models),
        "recommended": asdict(catalog.get_recommended_model()) if catalog.get_recommended_model() else None
    }

# Get specific model details
@app.get("/models/unified/{model_id}")
async def get_unified_model(model_id: str):
    """Get detailed information about a specific model."""
    catalog = get_unified_catalog()
    model = catalog.get_model(model_id)

    if not model:
        raise HTTPException(status_code=404, detail=f"Model not found: {model_id}")

    return asdict(model)
```

## Frontend Integration

```javascript
// Fetch unified catalog
async function loadModels() {
    const response = await fetch('http://localhost:8000/models/unified?compatible_only=true');
    const data = await response.json();

    // Group by provider
    const webllmModels = data.models.filter(m => m.providers.includes('webllm'));
    const ollamaModels = data.models.filter(m => m.providers.includes('ollama'));
    const bothModels = data.models.filter(m =>
        m.providers.includes('webllm') && m.providers.includes('ollama')
    );

    // Display in UI with provider badges
    displayModels(data.models, data.recommended);
}

function displayModels(models, recommended) {
    const modelList = document.getElementById('model-list');

    models.forEach(model => {
        const card = document.createElement('div');
        card.className = 'model-card';

        // Provider badges
        const badges = model.providers.map(p =>
            `<span class="badge badge-${p}">${p}</span>`
        ).join('');

        // Performance indicator
        const perfColor = {
            'excellent': 'green',
            'good': 'yellow',
            'acceptable': 'orange',
            'slow': 'red'
        }[model.performance.level];

        card.innerHTML = `
            <h3>${model.name} ${model.recommended ? '⭐' : ''}</h3>
            <div class="providers">${badges}</div>
            <div class="performance" style="color: ${perfColor}">
                ${model.performance.estimated_speed}
            </div>
            <div class="size">${model.base_size_gb.toFixed(1)} GB</div>
            <div class="capabilities">
                ${model.capabilities.map(c => `<span>${c}</span>`).join('')}
            </div>
        `;

        modelList.appendChild(card);
    });
}
```

## Benefits

1. **Single Interface**: Users see all models in one place
2. **Provider Transparency**: Clear indication of availability
3. **Intelligent Merging**: Same model from different providers shown once
4. **Hardware-Aware**: Performance indicators based on system specs
5. **Flexible Filtering**: Search by provider, capability, size, etc.

---

**Document Version**: 1.0
**Last Updated**: 2025-11-18
**Status**: Draft - Ready for Implementation
