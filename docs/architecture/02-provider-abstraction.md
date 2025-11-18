# Provider Abstraction Layer Architecture

## Overview

The Provider Abstraction Layer implements a clean separation between the application logic and specific LLM provider implementations. This enables seamless switching between WebLLM and Ollama while maintaining a consistent interface.

## Design Pattern: Strategy + Factory + Adapter

### Strategy Pattern
Each provider (WebLLM, Ollama) implements the same `LLMProvider` interface, allowing runtime selection without code changes.

### Factory Pattern
`LLMProviderFactory` creates appropriate provider instances based on availability and configuration.

### Adapter Pattern
Each provider adapter translates provider-specific APIs to our unified interface.

## Core Interfaces

### 1. Base Provider Interface

```python
# backend/providers/base_provider.py

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, AsyncIterator
from dataclasses import dataclass
from enum import Enum

class ProviderType(Enum):
    """Supported LLM provider types."""
    WEBLLM = "webllm"
    OLLAMA = "ollama"
    UNKNOWN = "unknown"

@dataclass
class ProviderCapabilities:
    """Capabilities supported by a provider."""
    streaming: bool = False
    vision: bool = False
    function_calling: bool = False
    embeddings: bool = False
    max_context_length: int = 4096
    supports_system_prompt: bool = True
    supports_temperature: bool = True
    supports_top_p: bool = True

@dataclass
class ProviderStatus:
    """Current status of a provider."""
    provider_type: ProviderType
    available: bool
    healthy: bool
    loaded_model: Optional[str] = None
    error_message: Optional[str] = None
    capabilities: Optional[ProviderCapabilities] = None
    hardware_info: Optional[Dict[str, Any]] = None
    latency_ms: Optional[float] = None

@dataclass
class GenerationConfig:
    """Configuration for text generation."""
    temperature: float = 0.7
    top_p: float = 0.9
    max_tokens: int = 2048
    stop_sequences: List[str] = None
    system_prompt: Optional[str] = None
    stream: bool = False

@dataclass
class Message:
    """Chat message structure."""
    role: str  # "system" | "user" | "assistant"
    content: str
    timestamp: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class GenerationResult:
    """Result from text generation."""
    text: str
    provider: ProviderType
    model_id: str
    tokens_used: int
    latency_ms: float
    finish_reason: str  # "stop" | "length" | "error"
    metadata: Optional[Dict[str, Any]] = None

class LLMProvider(ABC):
    """
    Abstract base class for LLM providers.

    All provider implementations (WebLLM, Ollama) must implement this interface
    to ensure consistent behavior across the application.
    """

    @abstractmethod
    async def initialize(self, config: Optional[Dict[str, Any]] = None) -> bool:
        """
        Initialize the provider with optional configuration.

        Args:
            config: Provider-specific configuration

        Returns:
            True if initialization successful, False otherwise
        """
        pass

    @abstractmethod
    async def get_status(self) -> ProviderStatus:
        """
        Get current provider status and health.

        Returns:
            ProviderStatus with availability, health, and capabilities
        """
        pass

    @abstractmethod
    async def list_models(self) -> List['ModelInfo']:
        """
        List all models available from this provider.

        Returns:
            List of ModelInfo objects
        """
        pass

    @abstractmethod
    async def load_model(
        self,
        model_id: str,
        config: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Load a specific model into memory.

        Args:
            model_id: Model identifier
            config: Model-specific configuration

        Returns:
            True if load successful, False otherwise
        """
        pass

    @abstractmethod
    async def unload_model(self) -> bool:
        """
        Unload currently loaded model from memory.

        Returns:
            True if unload successful, False otherwise
        """
        pass

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        context: Optional[List[Message]] = None,
        config: Optional[GenerationConfig] = None
    ) -> GenerationResult:
        """
        Generate text from prompt with optional context.

        Args:
            prompt: User prompt
            context: Conversation history
            config: Generation configuration

        Returns:
            GenerationResult with generated text and metadata
        """
        pass

    @abstractmethod
    async def stream_generate(
        self,
        prompt: str,
        context: Optional[List[Message]] = None,
        config: Optional[GenerationConfig] = None
    ) -> AsyncIterator[str]:
        """
        Stream generated text token by token.

        Args:
            prompt: User prompt
            context: Conversation history
            config: Generation configuration

        Yields:
            Text tokens as they are generated
        """
        pass

    @abstractmethod
    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for given texts (if supported).

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors

        Raises:
            NotImplementedError if provider doesn't support embeddings
        """
        pass

    @abstractmethod
    async def count_tokens(self, text: str) -> int:
        """
        Count tokens in given text.

        Args:
            text: Text to count tokens for

        Returns:
            Number of tokens
        """
        pass

    @abstractmethod
    async def download_model(
        self,
        model_id: str,
        progress_callback: Optional[callable] = None
    ) -> bool:
        """
        Download a model if not already available.

        Args:
            model_id: Model identifier
            progress_callback: Optional callback for download progress

        Returns:
            True if download successful, False otherwise
        """
        pass

    @abstractmethod
    def get_provider_type(self) -> ProviderType:
        """
        Get the provider type.

        Returns:
            ProviderType enum value
        """
        pass
```

## Provider Factory

```python
# backend/providers/provider_factory.py

import logging
from typing import Optional, Dict, Any, List
from .base_provider import LLMProvider, ProviderType, ProviderStatus
from .webllm_adapter import WebLLMAdapter
from .ollama_adapter import OllamaAdapter

logger = logging.getLogger(__name__)

class LLMProviderFactory:
    """
    Factory for creating and managing LLM provider instances.

    Handles provider detection, initialization, and lifecycle management.
    Implements automatic fallback logic when preferred provider is unavailable.
    """

    def __init__(self):
        self._providers: Dict[ProviderType, LLMProvider] = {}
        self._active_provider: Optional[LLMProvider] = None
        self._preferred_provider: ProviderType = ProviderType.WEBLLM

    async def initialize(self, config: Optional[Dict[str, Any]] = None) -> None:
        """
        Initialize all available providers.

        Args:
            config: Optional configuration for providers
        """
        config = config or {}

        # Initialize WebLLM adapter
        try:
            webllm = WebLLMAdapter()
            if await webllm.initialize(config.get("webllm", {})):
                self._providers[ProviderType.WEBLLM] = webllm
                logger.info("WebLLM provider initialized successfully")
        except Exception as e:
            logger.warning(f"Failed to initialize WebLLM: {e}")

        # Initialize Ollama adapter
        try:
            ollama = OllamaAdapter()
            if await ollama.initialize(config.get("ollama", {})):
                self._providers[ProviderType.OLLAMA] = ollama
                logger.info("Ollama provider initialized successfully")
        except Exception as e:
            logger.warning(f"Failed to initialize Ollama: {e}")

        # Set active provider
        await self._select_active_provider()

    async def _select_active_provider(self) -> None:
        """Select the best available provider based on preference and availability."""
        # Try preferred provider first
        if self._preferred_provider in self._providers:
            status = await self._providers[self._preferred_provider].get_status()
            if status.available and status.healthy:
                self._active_provider = self._providers[self._preferred_provider]
                logger.info(f"Selected preferred provider: {self._preferred_provider.value}")
                return

        # Try other providers
        for provider_type, provider in self._providers.items():
            status = await provider.get_status()
            if status.available and status.healthy:
                self._active_provider = provider
                logger.info(f"Selected fallback provider: {provider_type.value}")
                return

        logger.error("No healthy providers available")
        self._active_provider = None

    def get_provider(
        self,
        provider_type: Optional[ProviderType] = None
    ) -> Optional[LLMProvider]:
        """
        Get a provider instance.

        Args:
            provider_type: Specific provider type, or None for active provider

        Returns:
            LLMProvider instance or None if unavailable
        """
        if provider_type is None:
            return self._active_provider
        return self._providers.get(provider_type)

    async def set_active_provider(self, provider_type: ProviderType) -> bool:
        """
        Manually set the active provider.

        Args:
            provider_type: Provider to activate

        Returns:
            True if provider was set, False if unavailable
        """
        if provider_type not in self._providers:
            logger.error(f"Provider not available: {provider_type.value}")
            return False

        status = await self._providers[provider_type].get_status()
        if not (status.available and status.healthy):
            logger.error(f"Provider not healthy: {provider_type.value}")
            return False

        self._active_provider = self._providers[provider_type]
        self._preferred_provider = provider_type
        logger.info(f"Active provider changed to: {provider_type.value}")
        return True

    async def get_all_statuses(self) -> Dict[str, ProviderStatus]:
        """
        Get status of all providers.

        Returns:
            Dictionary mapping provider type to status
        """
        statuses = {}
        for provider_type, provider in self._providers.items():
            try:
                statuses[provider_type.value] = await provider.get_status()
            except Exception as e:
                logger.error(f"Error getting status for {provider_type.value}: {e}")
                statuses[provider_type.value] = ProviderStatus(
                    provider_type=provider_type,
                    available=False,
                    healthy=False,
                    error_message=str(e)
                )
        return statuses

    def get_available_providers(self) -> List[ProviderType]:
        """
        Get list of available provider types.

        Returns:
            List of ProviderType enums
        """
        return list(self._providers.keys())

    def get_active_provider_type(self) -> Optional[ProviderType]:
        """
        Get the currently active provider type.

        Returns:
            ProviderType or None if no active provider
        """
        if self._active_provider is None:
            return None
        return self._active_provider.get_provider_type()

# Global factory instance
_factory_instance: Optional[LLMProviderFactory] = None

def get_provider_factory() -> LLMProviderFactory:
    """Get or create the global provider factory instance."""
    global _factory_instance
    if _factory_instance is None:
        _factory_instance = LLMProviderFactory()
    return _factory_instance
```

## WebLLM Adapter Structure

```python
# backend/providers/webllm_adapter.py

from typing import List, Optional, Dict, Any, AsyncIterator
from .base_provider import (
    LLMProvider, ProviderType, ProviderStatus,
    GenerationConfig, Message, GenerationResult,
    ProviderCapabilities
)

class WebLLMAdapter(LLMProvider):
    """
    Adapter for WebLLM browser-based inference.

    Provides server-side coordination for browser-based WebLLM.
    Actual inference happens in the browser, this adapter handles:
    - Model metadata management
    - Status tracking
    - Request coordination
    """

    def __init__(self):
        self.provider_type = ProviderType.WEBLLM
        self.initialized = False
        self.available_models = []

    async def initialize(self, config: Optional[Dict[str, Any]] = None) -> bool:
        """Initialize WebLLM adapter with browser detection."""
        # Implementation details in next document
        pass

    async def get_status(self) -> ProviderStatus:
        """Get WebLLM availability (checks browser capabilities)."""
        # Implementation details in next document
        pass

    # ... other method implementations
```

## Ollama Adapter Structure

```python
# backend/providers/ollama_adapter.py

from typing import List, Optional, Dict, Any, AsyncIterator
from .base_provider import (
    LLMProvider, ProviderType, ProviderStatus,
    GenerationConfig, Message, GenerationResult,
    ProviderCapabilities
)
from ..ollama_integration import get_ollama_integration

class OllamaAdapter(LLMProvider):
    """
    Adapter for Ollama local server inference.

    Wraps existing Ollama integration to conform to provider interface.
    Maintains backward compatibility with existing code.
    """

    def __init__(self):
        self.provider_type = ProviderType.OLLAMA
        self.ollama_integration = get_ollama_integration()
        self.initialized = False

    async def initialize(self, config: Optional[Dict[str, Any]] = None) -> bool:
        """Initialize Ollama adapter and check server availability."""
        # Implementation wraps existing Ollama code
        pass

    async def get_status(self) -> ProviderStatus:
        """Get Ollama server status."""
        # Implementation uses existing Ollama health checks
        pass

    # ... other method implementations
```

## Integration Points

### FastAPI Integration

```python
# backend/main.py (modifications)

from providers.provider_factory import get_provider_factory
from providers.base_provider import ProviderType, GenerationConfig, Message

# Initialize during startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    # ... existing code ...

    # Initialize provider factory
    factory = get_provider_factory()
    await factory.initialize({
        "webllm": {"browser_check": True},
        "ollama": {"base_url": settings.ollama_base_url}
    })

    logger.info(f"Active provider: {factory.get_active_provider_type()}")

    yield

# New endpoint: Get provider status
@app.get("/providers")
async def get_providers():
    factory = get_provider_factory()
    statuses = await factory.get_all_statuses()
    return {
        "active": factory.get_active_provider_type().value if factory.get_active_provider_type() else None,
        "available": [p.value for p in factory.get_available_providers()],
        "statuses": {k: v.__dict__ for k, v in statuses.items()}
    }

# New endpoint: Select provider
@app.post("/providers/select")
async def select_provider(provider: str):
    factory = get_provider_factory()
    provider_type = ProviderType(provider)
    success = await factory.set_active_provider(provider_type)
    if success:
        return {"success": True, "active_provider": provider}
    raise HTTPException(status_code=400, detail=f"Provider not available: {provider}")

# Modified chat endpoint
@app.post("/chat")
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    factory = get_provider_factory()
    provider = factory.get_provider()

    if provider is None:
        raise HTTPException(status_code=503, detail="No LLM provider available")

    # Use provider interface
    result = await provider.generate(
        prompt=request.message,
        context=get_conversation_history(db, request.conversation_id),
        config=GenerationConfig(
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )
    )

    return {
        "response": result.text,
        "provider": result.provider.value,
        "model": result.model_id,
        "tokens_used": result.tokens_used,
        "latency_ms": result.latency_ms
    }
```

## Benefits of This Architecture

1. **Separation of Concerns**: Application logic decoupled from provider specifics
2. **Easy Testing**: Mock providers for unit tests
3. **Extensibility**: Add new providers by implementing interface
4. **Runtime Flexibility**: Switch providers without code changes
5. **Backward Compatibility**: Existing Ollama code wrapped in adapter

## Next Steps

See the following documents for implementation details:
- `03-webllm-integration.md` - WebLLM adapter implementation
- `04-unified-model-catalog.md` - Model catalog merging
- `05-toon-integration.md` - TOON format processor

---

**Document Version**: 1.0
**Last Updated**: 2025-11-18
**Status**: Draft - Ready for Implementation
