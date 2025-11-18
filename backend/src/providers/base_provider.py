"""
Base Provider Interface

Abstract base class defining the interface for LLM providers.
All providers (Ollama, WebLLM, etc.) must implement this interface.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum


class ProviderType(Enum):
    """Supported provider types"""
    OLLAMA = "ollama"
    WEBLLM = "webllm"


@dataclass
class ModelInfo:
    """Unified model information across providers"""
    id: str  # Unique model identifier
    name: str  # Display name
    provider: ProviderType  # Which provider serves this model
    size_gb: float  # Model size in GB
    parameters: str  # e.g., "1B", "7B", "70B"
    description: str  # Model description
    tags: List[str]  # Categories (chat, code, vision, etc.)
    family: str  # Model family (llama, mistral, phi, etc.)
    expected_performance: str  # "fastest" | "fast" | "good" | "slow"
    speed_estimate: str  # Human-readable speed estimate
    quality: str  # "high" | "medium" | "basic"
    recommended: bool  # Is this recommended?
    ram_required_gb: int  # Minimum RAM required
    compatible: bool  # Hardware compatibility
    compatibility_reason: Optional[str] = None
    source_url: Optional[str] = None  # Model URL/path
    license: Optional[str] = None  # License info


@dataclass
class ChatMessage:
    """Unified chat message format"""
    role: str  # "user" | "assistant" | "system"
    content: str


@dataclass
class ChatResponse:
    """Unified chat response format"""
    message: str  # Response text
    model_used: str  # Which model was used
    tokens: Optional[int] = None  # Token count if available
    metadata: Optional[Dict[str, Any]] = None  # Provider-specific metadata


class BaseProvider(ABC):
    """
    Abstract base class for LLM providers.

    All providers must implement:
    - initialize(): Setup/connection
    - health_check(): Verify availability
    - list_models(): Get available models
    - chat(): Send messages and get responses
    - cleanup(): Cleanup resources
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize provider with optional configuration.

        Args:
            config: Provider-specific configuration dict
        """
        self.config = config or {}
        self.initialized = False

    @abstractmethod
    async def initialize(self) -> bool:
        """
        Initialize the provider (setup connections, load models, etc.)

        Returns:
            bool: True if initialization successful, False otherwise
        """
        pass

    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """
        Check provider health and availability.

        Returns:
            Dict with status information:
            {
                "healthy": bool,
                "message": str,
                "details": dict (optional)
            }
        """
        pass

    @abstractmethod
    async def list_models(self) -> List[ModelInfo]:
        """
        List all available models from this provider.

        Returns:
            List of ModelInfo objects
        """
        pass

    @abstractmethod
    async def chat(
        self,
        messages: List[ChatMessage],
        model: Optional[str] = None,
        **kwargs
    ) -> ChatResponse:
        """
        Send chat messages and get response.

        Args:
            messages: List of ChatMessage objects
            model: Optional model override
            **kwargs: Provider-specific options

        Returns:
            ChatResponse object

        Raises:
            Exception: If chat fails
        """
        pass

    @abstractmethod
    async def cleanup(self):
        """
        Cleanup provider resources (close connections, unload models, etc.)
        """
        pass

    def get_provider_type(self) -> ProviderType:
        """Get the provider type"""
        raise NotImplementedError("Subclass must implement get_provider_type()")
