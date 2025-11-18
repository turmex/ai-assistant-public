"""
Provider Manager

Manages multiple LLM providers (Ollama, WebLLM) and handles provider switching.
"""

import logging
from typing import Dict, List, Optional, Any
from enum import Enum

from .base_provider import (
    BaseProvider,
    ProviderType,
    ModelInfo,
    ChatMessage,
    ChatResponse
)
from .webllm_provider import WebLLMProvider

logger = logging.getLogger(__name__)


class ProviderManager:
    """
    Manages multiple LLM providers and handles provider selection.

    Features:
    - Register multiple providers
    - Switch between providers
    - Unified model catalog
    - Provider-specific health checks
    - Fallback mechanisms
    """

    def __init__(self):
        self.providers: Dict[ProviderType, BaseProvider] = {}
        self.active_provider: Optional[ProviderType] = None
        self.default_provider: ProviderType = ProviderType.WEBLLM

    async def register_provider(self, provider: BaseProvider):
        """
        Register a new provider.

        Args:
            provider: Provider instance to register
        """
        provider_type = provider.get_provider_type()
        logger.info(f"Registering provider: {provider_type.value}")

        # Initialize provider
        success = await provider.initialize()
        if success:
            self.providers[provider_type] = provider
            logger.info(f"✓ Provider {provider_type.value} registered successfully")

            # Set as active if it's the default or first provider
            if self.active_provider is None or provider_type == self.default_provider:
                self.active_provider = provider_type
                logger.info(f"✓ Active provider set to: {provider_type.value}")
        else:
            logger.error(f"✗ Failed to initialize provider: {provider_type.value}")

    async def switch_provider(self, provider_type: ProviderType) -> bool:
        """
        Switch to a different provider.

        Args:
            provider_type: Provider to switch to

        Returns:
            bool: True if switch successful, False otherwise
        """
        if provider_type not in self.providers:
            logger.error(f"Provider {provider_type.value} not registered")
            return False

        # Check provider health before switching
        health = await self.providers[provider_type].health_check()
        if not health.get("healthy", False):
            logger.warning(f"Provider {provider_type.value} is not healthy: {health.get('message')}")
            return False

        self.active_provider = provider_type
        logger.info(f"✓ Switched to provider: {provider_type.value}")
        return True

    def get_active_provider(self) -> Optional[BaseProvider]:
        """
        Get the currently active provider.

        Returns:
            BaseProvider instance or None if no active provider
        """
        if self.active_provider and self.active_provider in self.providers:
            return self.providers[self.active_provider]
        return None

    async def get_all_models(self) -> List[ModelInfo]:
        """
        Get models from all registered providers.

        Returns:
            List of all available models across all providers
        """
        all_models = []

        for provider_type, provider in self.providers.items():
            try:
                models = await provider.list_models()
                all_models.extend(models)
                logger.debug(f"Loaded {len(models)} models from {provider_type.value}")
            except Exception as e:
                logger.error(f"Failed to get models from {provider_type.value}: {e}")

        # Sort models: recommended first, then by size
        all_models.sort(key=lambda m: (not m.recommended, m.size_gb))

        return all_models

    async def get_models_by_provider(self, provider_type: ProviderType) -> List[ModelInfo]:
        """
        Get models from a specific provider.

        Args:
            provider_type: Provider to get models from

        Returns:
            List of models from that provider
        """
        if provider_type not in self.providers:
            logger.error(f"Provider {provider_type.value} not registered")
            return []

        try:
            return await self.providers[provider_type].list_models()
        except Exception as e:
            logger.error(f"Failed to get models from {provider_type.value}: {e}")
            return []

    async def health_check_all(self) -> Dict[str, Any]:
        """
        Check health of all registered providers.

        Returns:
            Dict with health status for each provider
        """
        health_status = {}

        for provider_type, provider in self.providers.items():
            try:
                health = await provider.health_check()
                health_status[provider_type.value] = health
            except Exception as e:
                health_status[provider_type.value] = {
                    "healthy": False,
                    "message": f"Health check failed: {str(e)}"
                }

        return {
            "providers": health_status,
            "active_provider": self.active_provider.value if self.active_provider else None,
            "total_providers": len(self.providers)
        }

    async def chat(
        self,
        messages: List[ChatMessage],
        model: Optional[str] = None,
        provider_override: Optional[ProviderType] = None,
        **kwargs
    ) -> ChatResponse:
        """
        Send chat messages using the active provider.

        Args:
            messages: List of chat messages
            model: Optional model override
            provider_override: Optional provider override
            **kwargs: Provider-specific options

        Returns:
            ChatResponse object

        Raises:
            ValueError: If no active provider or provider not found
        """
        # Determine which provider to use
        provider_to_use = provider_override or self.active_provider

        if not provider_to_use or provider_to_use not in self.providers:
            raise ValueError("No active provider available")

        provider = self.providers[provider_to_use]

        # Special handling for WebLLM (chat happens in browser)
        if provider_to_use == ProviderType.WEBLLM:
            raise ValueError(
                "WebLLM chat must be handled in the browser. "
                "Use the JavaScript WebLLM client for inference."
            )

        # Use the provider's chat method
        return await provider.chat(messages, model=model, **kwargs)

    async def cleanup(self):
        """
        Cleanup all providers.
        """
        logger.info("Cleaning up all providers...")

        for provider_type, provider in self.providers.items():
            try:
                await provider.cleanup()
                logger.info(f"✓ Cleaned up provider: {provider_type.value}")
            except Exception as e:
                logger.error(f"Error cleaning up {provider_type.value}: {e}")

        self.providers.clear()
        self.active_provider = None
        logger.info("✓ All providers cleaned up")


# Global provider manager instance
_provider_manager: Optional[ProviderManager] = None


def get_provider_manager() -> ProviderManager:
    """
    Get the global provider manager instance (singleton).

    Returns:
        ProviderManager instance
    """
    global _provider_manager

    if _provider_manager is None:
        _provider_manager = ProviderManager()

    return _provider_manager
