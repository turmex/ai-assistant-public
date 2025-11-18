"""
WebLLM Provider Implementation

Browser-based LLM provider using WebLLM (runs entirely in browser).
This backend implementation serves model metadata; actual inference happens client-side.
"""

import logging
from typing import List, Dict, Any, Optional

from .base_provider import (
    BaseProvider,
    ProviderType,
    ModelInfo,
    ChatMessage,
    ChatResponse
)

logger = logging.getLogger(__name__)


# WebLLM model catalog
# Based on models available at https://github.com/mlc-ai/web-llm
WEBLLM_MODEL_CATALOG = [
    {
        "id": "Llama-3.2-1B-Instruct-q4f16_1-MLC",
        "name": "Llama 3.2 1B Instruct",
        "size_gb": 0.7,
        "parameters": "1B",
        "description": "Meta's Llama 3.2 1B optimized for WebGPU, extremely fast in-browser inference",
        "tags": ["chat", "conversation", "fast", "browser"],
        "family": "llama",
        "quality": "medium",
        "license": "Llama 3.2",
        "expected_performance": "fastest",
        "speed_estimate": "Very fast (30-50 tok/s in browser)",
        "ram_required_gb": 2
    },
    {
        "id": "Llama-3.2-3B-Instruct-q4f16_1-MLC",
        "name": "Llama 3.2 3B Instruct",
        "size_gb": 1.6,
        "parameters": "3B",
        "description": "Llama 3.2 3B for balanced quality and speed in browser",
        "tags": ["chat", "conversation", "browser"],
        "family": "llama",
        "quality": "high",
        "license": "Llama 3.2",
        "expected_performance": "fast",
        "speed_estimate": "Fast (20-30 tok/s in browser)",
        "ram_required_gb": 4
    },
    {
        "id": "Phi-3.5-mini-instruct-q4f16_1-MLC",
        "name": "Phi 3.5 Mini Instruct",
        "size_gb": 2.2,
        "parameters": "3.8B",
        "description": "Microsoft's Phi 3.5 optimized for browser, excellent reasoning",
        "tags": ["chat", "reasoning", "browser"],
        "family": "phi",
        "quality": "high",
        "license": "MIT",
        "expected_performance": "fast",
        "speed_estimate": "Fast (15-25 tok/s in browser)",
        "ram_required_gb": 4
    },
    {
        "id": "Mistral-7B-Instruct-v0.3-q4f16_1-MLC",
        "name": "Mistral 7B Instruct v0.3",
        "size_gb": 4.0,
        "parameters": "7B",
        "description": "Mistral AI's 7B model optimized for WebGPU",
        "tags": ["chat", "conversation", "browser"],
        "family": "mistral",
        "quality": "high",
        "license": "Apache 2.0",
        "expected_performance": "good",
        "speed_estimate": "Good (10-20 tok/s in browser)",
        "ram_required_gb": 8
    },
    {
        "id": "gemma-2-2b-it-q4f16_1-MLC",
        "name": "Gemma 2 2B IT",
        "size_gb": 1.4,
        "parameters": "2B",
        "description": "Google's Gemma 2 2B instruction-tuned for browser",
        "tags": ["chat", "conversation", "fast", "browser"],
        "family": "gemma",
        "quality": "high",
        "license": "Gemma License",
        "expected_performance": "fast",
        "speed_estimate": "Fast (20-30 tok/s in browser)",
        "ram_required_gb": 4
    },
    {
        "id": "Qwen2.5-0.5B-Instruct-q4f16_1-MLC",
        "name": "Qwen 2.5 0.5B Instruct",
        "size_gb": 0.4,
        "parameters": "0.5B",
        "description": "Ultra-lightweight Qwen model for instant browser inference",
        "tags": ["chat", "fast", "browser", "lightweight"],
        "family": "qwen",
        "quality": "basic",
        "license": "Apache 2.0",
        "expected_performance": "fastest",
        "speed_estimate": "Blazing fast (50-80 tok/s in browser)",
        "ram_required_gb": 1
    },
    {
        "id": "TinyLlama-1.1B-Chat-v1.0-q4f16_1-MLC",
        "name": "TinyLlama 1.1B Chat",
        "size_gb": 0.6,
        "parameters": "1.1B",
        "description": "Compact Llama-architecture model for fast browser inference",
        "tags": ["chat", "fast", "browser", "lightweight"],
        "family": "llama",
        "quality": "basic",
        "license": "Apache 2.0",
        "expected_performance": "fastest",
        "speed_estimate": "Very fast (40-60 tok/s in browser)",
        "ram_required_gb": 2
    }
]


class WebLLMProvider(BaseProvider):
    """
    WebLLM provider for browser-based LLM inference.

    Note: Actual inference happens in the browser using WebGPU.
    This backend class only provides model metadata and API endpoints.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.available_models = []

    def get_provider_type(self) -> ProviderType:
        return ProviderType.WEBLLM

    async def initialize(self) -> bool:
        """
        Initialize WebLLM provider (load model catalog).

        Returns:
            bool: Always True since WebLLM doesn't require server setup
        """
        try:
            logger.info("Initializing WebLLM provider...")

            # Load model catalog
            self.available_models = [
                ModelInfo(
                    id=model["id"],
                    name=model["name"],
                    provider=ProviderType.WEBLLM,
                    size_gb=model["size_gb"],
                    parameters=model["parameters"],
                    description=model["description"],
                    tags=model["tags"],
                    family=model["family"],
                    expected_performance=model["expected_performance"],
                    speed_estimate=model["speed_estimate"],
                    quality=model["quality"],
                    recommended=(model["id"] == "Llama-3.2-1B-Instruct-q4f16_1-MLC"),  # Default recommended
                    ram_required_gb=model["ram_required_gb"],
                    compatible=True,  # WebLLM runs in browser, always compatible
                    source_url=f"https://huggingface.co/mlc-ai/{model['id']}",
                    license=model.get("license")
                )
                for model in WEBLLM_MODEL_CATALOG
            ]

            self.initialized = True
            logger.info(f"✓ WebLLM provider initialized with {len(self.available_models)} models")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize WebLLM provider: {e}")
            return False

    async def health_check(self) -> Dict[str, Any]:
        """
        Check WebLLM provider health.

        Returns:
            Dict with health status
        """
        return {
            "healthy": True,
            "message": "WebLLM provider ready (browser-based inference)",
            "details": {
                "provider": "webllm",
                "inference_location": "browser",
                "available_models": len(self.available_models),
                "webgpu_required": True
            }
        }

    async def list_models(self) -> List[ModelInfo]:
        """
        List available WebLLM models.

        Returns:
            List of ModelInfo objects
        """
        if not self.initialized:
            await self.initialize()

        return self.available_models

    async def chat(
        self,
        messages: List[ChatMessage],
        model: Optional[str] = None,
        **kwargs
    ) -> ChatResponse:
        """
        WebLLM chat is handled entirely in the browser.
        This method is a placeholder that should not be called.

        Raises:
            NotImplementedError: Always, since chat happens client-side
        """
        raise NotImplementedError(
            "WebLLM chat inference happens in the browser. "
            "Use the WebLLM JavaScript client for actual chat."
        )

    async def cleanup(self):
        """
        Cleanup WebLLM provider resources.
        """
        logger.info("Cleaning up WebLLM provider...")
        self.available_models = []
        self.initialized = False
