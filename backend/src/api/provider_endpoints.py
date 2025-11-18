"""
Provider API Endpoints

FastAPI endpoints for managing LLM providers (Ollama, WebLLM).
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ..providers import ProviderType, ModelInfo as ProviderModelInfo
from ..providers.provider_manager import get_provider_manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/providers", tags=["providers"])


# Schemas
class ProviderStatus(BaseModel):
    """Provider status response"""
    name: str
    healthy: bool
    message: str
    details: Optional[dict] = None


class ProvidersHealthResponse(BaseModel):
    """Health status for all providers"""
    providers: dict
    active_provider: Optional[str]
    total_providers: int


class ModelListResponse(BaseModel):
    """Response with list of models"""
    models: List[dict]
    provider: Optional[str] = None
    total: int


class ProviderSwitchRequest(BaseModel):
    """Request to switch provider"""
    provider: str = Field(..., description="Provider to switch to (ollama or webllm)")


class ProviderSwitchResponse(BaseModel):
    """Response after switching provider"""
    success: bool
    provider: str
    message: str


# Endpoints
@router.get("/health", response_model=ProvidersHealthResponse)
async def get_providers_health():
    """
    Get health status for all registered providers.

    Returns:
        Health status for each provider
    """
    try:
        manager = get_provider_manager()
        health_status = await manager.health_check_all()
        return health_status

    except Exception as e:
        logger.error(f"Failed to get provider health: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/active")
async def get_active_provider():
    """
    Get the currently active provider.

    Returns:
        Active provider info
    """
    try:
        manager = get_provider_manager()
        active_provider = manager.get_active_provider()

        if not active_provider:
            return {
                "active": None,
                "message": "No active provider"
            }

        return {
            "active": manager.active_provider.value,
            "type": active_provider.get_provider_type().value,
            "initialized": active_provider.initialized
        }

    except Exception as e:
        logger.error(f"Failed to get active provider: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/switch", response_model=ProviderSwitchResponse)
async def switch_provider(request: ProviderSwitchRequest):
    """
    Switch to a different provider.

    Args:
        request: Provider switch request with provider name

    Returns:
        Success status and message
    """
    try:
        provider_name = request.provider.lower()

        # Map provider name to ProviderType
        provider_map = {
            "ollama": ProviderType.OLLAMA,
            "webllm": ProviderType.WEBLLM
        }

        if provider_name not in provider_map:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid provider: {provider_name}. Must be 'ollama' or 'webllm'"
            )

        provider_type = provider_map[provider_name]
        manager = get_provider_manager()

        success = await manager.switch_provider(provider_type)

        if not success:
            return ProviderSwitchResponse(
                success=False,
                provider=provider_name,
                message=f"Failed to switch to {provider_name}. Provider may not be healthy."
            )

        return ProviderSwitchResponse(
            success=True,
            provider=provider_name,
            message=f"Successfully switched to {provider_name}"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to switch provider: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models", response_model=ModelListResponse)
async def get_all_models():
    """
    Get all available models from all providers.

    Returns:
        List of all models across all providers
    """
    try:
        manager = get_provider_manager()
        models = await manager.get_all_models()

        # Convert to dict format
        model_dicts = [
            {
                "id": m.id,
                "name": m.name,
                "provider": m.provider.value,
                "size_gb": m.size_gb,
                "parameters": m.parameters,
                "description": m.description,
                "tags": m.tags,
                "family": m.family,
                "expected_performance": m.expected_performance,
                "speed_estimate": m.speed_estimate,
                "quality": m.quality,
                "recommended": m.recommended,
                "ram_required_gb": m.ram_required_gb,
                "compatible": m.compatible,
                "source_url": m.source_url,
                "license": m.license
            }
            for m in models
        ]

        return ModelListResponse(
            models=model_dicts,
            total=len(model_dicts)
        )

    except Exception as e:
        logger.error(f"Failed to get all models: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{provider_name}/models", response_model=ModelListResponse)
async def get_provider_models(provider_name: str):
    """
    Get models from a specific provider.

    Args:
        provider_name: Provider name (ollama or webllm)

    Returns:
        List of models from that provider
    """
    try:
        provider_name = provider_name.lower()

        # Map provider name to ProviderType
        provider_map = {
            "ollama": ProviderType.OLLAMA,
            "webllm": ProviderType.WEBLLM
        }

        if provider_name not in provider_map:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid provider: {provider_name}. Must be 'ollama' or 'webllm'"
            )

        provider_type = provider_map[provider_name]
        manager = get_provider_manager()

        models = await manager.get_models_by_provider(provider_type)

        # Convert to dict format
        model_dicts = [
            {
                "id": m.id,
                "name": m.name,
                "provider": m.provider.value,
                "size_gb": m.size_gb,
                "parameters": m.parameters,
                "description": m.description,
                "tags": m.tags,
                "family": m.family,
                "expected_performance": m.expected_performance,
                "speed_estimate": m.speed_estimate,
                "quality": m.quality,
                "recommended": m.recommended,
                "ram_required_gb": m.ram_required_gb,
                "compatible": m.compatible,
                "source_url": m.source_url,
                "license": m.license
            }
            for m in models
        ]

        return ModelListResponse(
            models=model_dicts,
            provider=provider_name,
            total=len(model_dicts)
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get models for provider {provider_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/config")
async def get_provider_config():
    """
    Get provider configuration.

    Returns:
        Provider configuration
    """
    import json
    from pathlib import Path

    try:
        config_path = Path(__file__).parent.parent.parent.parent / "config" / "provider-config.json"

        if config_path.exists():
            with open(config_path, 'r') as f:
                config = json.load(f)
                return config
        else:
            # Return default config
            return {
                "default_provider": "webllm",
                "providers": {
                    "webllm": {"enabled": True},
                    "ollama": {"enabled": True}
                }
            }

    except Exception as e:
        logger.error(f"Failed to get provider config: {e}")
        raise HTTPException(status_code=500, detail=str(e))
