"""
Ollama Model Catalog Integration

Provides a comprehensive catalog of Ollama models with metadata,
compatibility checking, and search functionality for both Ollama
and HuggingFace models.
"""

import logging
import re
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass
import httpx

logger = logging.getLogger(__name__)


@dataclass
class OllamaModelInfo:
    """Information about an Ollama model."""
    name: str  # Ollama name (e.g., "llama3.2:1b")
    display_name: str  # Human-readable name
    size_gb: float  # Model size in GB
    parameters: str  # e.g., "1.5B", "7B"
    description: str  # Model description
    tags: List[str]  # Categories (chat, code, vision, etc.)
    family: str  # Model family (llama, mistral, phi, etc.)
    expected_performance: str  # "fastest" | "fast" | "good" | "slow"
    speed_estimate: str  # e.g., "Fast (10-15 tok/s)"
    quality: str  # "high" | "medium" | "basic"
    recommended: bool  # Is this recommended for the hardware?
    ram_required_gb: int  # Minimum RAM required
    ollama_url: str  # Full Ollama library URL
    compatible: bool  # Hardware compatibility flag
    compatibility_reason: Optional[str] = None  # Why incompatible
    source: str = "ollama"  # Always "ollama" for this type
    downloads: Optional[int] = None  # Pull count if available
    license: Optional[str] = None  # Model license


# Comprehensive Ollama model catalog
# Based on popular models from https://ollama.com/library
OLLAMA_MODEL_CATALOG = [
    # Llama Family
    {
        "name": "llama3.2:1b",
        "display_name": "Llama 3.2 1B",
        "size_gb": 1.3,
        "parameters": "1B",
        "description": "Meta's smallest Llama 3.2 model, optimized for speed and efficiency",
        "tags": ["chat", "conversation", "fast"],
        "family": "llama",
        "quality": "basic",
        "license": "Llama 3.2"
    },
    {
        "name": "llama3.2:3b",
        "display_name": "Llama 3.2 3B",
        "size_gb": 2.0,
        "parameters": "3B",
        "description": "Balanced Llama 3.2 model with good quality and speed",
        "tags": ["chat", "conversation", "instruction"],
        "family": "llama",
        "quality": "medium",
        "license": "Llama 3.2"
    },
    {
        "name": "llama3.1:8b",
        "display_name": "Llama 3.1 8B",
        "size_gb": 4.7,
        "parameters": "8B",
        "description": "Meta's Llama 3.1 8B model, excellent for general tasks",
        "tags": ["chat", "conversation", "instruction", "multilingual"],
        "family": "llama",
        "quality": "high",
        "license": "Llama 3.1"
    },
    {
        "name": "llama3.1:70b",
        "display_name": "Llama 3.1 70B",
        "size_gb": 40.0,
        "parameters": "70B",
        "description": "Large Llama 3.1 model with exceptional capabilities",
        "tags": ["chat", "conversation", "instruction", "multilingual"],
        "family": "llama",
        "quality": "high",
        "license": "Llama 3.1"
    },
    {
        "name": "llama3:8b",
        "display_name": "Llama 3 8B",
        "size_gb": 4.7,
        "parameters": "8B",
        "description": "Meta's Llama 3 8B model for general-purpose tasks",
        "tags": ["chat", "conversation", "instruction"],
        "family": "llama",
        "quality": "high",
        "license": "Llama 3"
    },
    {
        "name": "llama3:70b",
        "display_name": "Llama 3 70B",
        "size_gb": 40.0,
        "parameters": "70B",
        "description": "Large Llama 3 model with advanced capabilities",
        "tags": ["chat", "conversation", "instruction"],
        "family": "llama",
        "quality": "high",
        "license": "Llama 3"
    },
    {
        "name": "codellama:7b",
        "display_name": "Code Llama 7B",
        "size_gb": 3.8,
        "parameters": "7B",
        "description": "Meta's Code Llama for code generation and completion",
        "tags": ["code", "programming", "completion"],
        "family": "llama",
        "quality": "high",
        "license": "Llama 2"
    },
    {
        "name": "codellama:13b",
        "display_name": "Code Llama 13B",
        "size_gb": 7.4,
        "parameters": "13B",
        "description": "Larger Code Llama model for complex coding tasks",
        "tags": ["code", "programming", "completion"],
        "family": "llama",
        "quality": "high",
        "license": "Llama 2"
    },

    # Mistral Family
    {
        "name": "mistral:7b",
        "display_name": "Mistral 7B",
        "size_gb": 4.1,
        "parameters": "7B",
        "description": "Mistral AI's efficient 7B model with excellent performance",
        "tags": ["chat", "conversation", "instruction"],
        "family": "mistral",
        "quality": "high",
        "license": "Apache 2.0"
    },
    {
        "name": "mixtral:8x7b",
        "display_name": "Mixtral 8x7B",
        "size_gb": 26.0,
        "parameters": "8x7B",
        "description": "Mistral's mixture-of-experts model with exceptional quality",
        "tags": ["chat", "conversation", "instruction", "moe"],
        "family": "mistral",
        "quality": "high",
        "license": "Apache 2.0"
    },

    # Phi Family (Microsoft)
    {
        "name": "phi3:mini",
        "display_name": "Phi 3 Mini",
        "size_gb": 2.3,
        "parameters": "3.8B",
        "description": "Microsoft's efficient Phi-3 model, great for code and reasoning",
        "tags": ["chat", "code", "reasoning", "fast"],
        "family": "phi",
        "quality": "medium",
        "license": "MIT"
    },
    {
        "name": "phi3:medium",
        "display_name": "Phi 3 Medium",
        "size_gb": 7.9,
        "parameters": "14B",
        "description": "Larger Phi-3 model with improved capabilities",
        "tags": ["chat", "code", "reasoning"],
        "family": "phi",
        "quality": "high",
        "license": "MIT"
    },

    # Gemma Family (Google)
    {
        "name": "gemma2:2b",
        "display_name": "Gemma 2 2B",
        "size_gb": 1.6,
        "parameters": "2B",
        "description": "Google's lightweight Gemma 2 model",
        "tags": ["chat", "conversation", "fast"],
        "family": "gemma",
        "quality": "basic",
        "license": "Gemma"
    },
    {
        "name": "gemma2:9b",
        "display_name": "Gemma 2 9B",
        "size_gb": 5.5,
        "parameters": "9B",
        "description": "Google's Gemma 2 model with strong performance",
        "tags": ["chat", "conversation", "instruction"],
        "family": "gemma",
        "quality": "high",
        "license": "Gemma"
    },

    # Qwen Family (Alibaba)
    {
        "name": "qwen2:0.5b",
        "display_name": "Qwen 2 0.5B",
        "size_gb": 0.4,
        "parameters": "0.5B",
        "description": "Ultra-lightweight Qwen 2 model for basic tasks",
        "tags": ["chat", "fast", "multilingual"],
        "family": "qwen",
        "quality": "basic",
        "license": "Apache 2.0"
    },
    {
        "name": "qwen2:1.5b",
        "display_name": "Qwen 2 1.5B",
        "size_gb": 0.9,
        "parameters": "1.5B",
        "description": "Compact Qwen 2 model with multilingual support",
        "tags": ["chat", "fast", "multilingual"],
        "family": "qwen",
        "quality": "basic",
        "license": "Apache 2.0"
    },
    {
        "name": "qwen2:7b",
        "display_name": "Qwen 2 7B",
        "size_gb": 4.4,
        "parameters": "7B",
        "description": "Qwen 2 7B model with strong multilingual capabilities",
        "tags": ["chat", "multilingual", "instruction"],
        "family": "qwen",
        "quality": "high",
        "license": "Apache 2.0"
    },

    # DeepSeek Family
    {
        "name": "deepseek-r1:1.5b",
        "display_name": "DeepSeek R1 1.5B",
        "size_gb": 1.1,
        "parameters": "1.5B",
        "description": "DeepSeek's reasoning model, distilled from larger variants",
        "tags": ["reasoning", "chat", "fast"],
        "family": "deepseek",
        "quality": "medium",
        "license": "MIT"
    },
    {
        "name": "deepseek-r1:7b",
        "display_name": "DeepSeek R1 7B",
        "size_gb": 4.7,
        "parameters": "7B",
        "description": "DeepSeek's reasoning model with strong analytical capabilities",
        "tags": ["reasoning", "chat", "instruction"],
        "family": "deepseek",
        "quality": "high",
        "license": "MIT"
    },
    {
        "name": "deepseek-coder:6.7b",
        "display_name": "DeepSeek Coder 6.7B",
        "size_gb": 3.8,
        "parameters": "6.7B",
        "description": "Specialized model for code generation and understanding",
        "tags": ["code", "programming", "completion"],
        "family": "deepseek",
        "quality": "high",
        "license": "DeepSeek"
    },

    # Specialized Models
    {
        "name": "dolphin-mixtral:8x7b",
        "display_name": "Dolphin Mixtral 8x7B",
        "size_gb": 26.0,
        "parameters": "8x7B",
        "description": "Fine-tuned Mixtral model for improved instruction following",
        "tags": ["chat", "instruction", "uncensored"],
        "family": "mistral",
        "quality": "high",
        "license": "Apache 2.0"
    },
    {
        "name": "neural-chat:7b",
        "display_name": "Neural Chat 7B",
        "size_gb": 4.1,
        "parameters": "7B",
        "description": "Intel's fine-tuned model for conversational AI",
        "tags": ["chat", "conversation", "instruction"],
        "family": "mistral",
        "quality": "high",
        "license": "Apache 2.0"
    },
    {
        "name": "orca-mini:3b",
        "display_name": "Orca Mini 3B",
        "size_gb": 1.9,
        "parameters": "3B",
        "description": "Small but capable model based on Llama",
        "tags": ["chat", "instruction", "fast"],
        "family": "llama",
        "quality": "medium",
        "license": "CC-BY-NC-SA-4.0"
    },
    {
        "name": "vicuna:7b",
        "display_name": "Vicuna 7B",
        "size_gb": 3.8,
        "parameters": "7B",
        "description": "Fine-tuned LLaMA model with strong conversational abilities",
        "tags": ["chat", "conversation", "instruction"],
        "family": "llama",
        "quality": "high",
        "license": "Non-commercial"
    },
    {
        "name": "wizardcoder:7b",
        "display_name": "WizardCoder 7B",
        "size_gb": 4.0,
        "parameters": "7B",
        "description": "Code-focused model with strong programming capabilities",
        "tags": ["code", "programming", "completion"],
        "family": "llama",
        "quality": "high",
        "license": "Non-commercial"
    },
    {
        "name": "nous-hermes2:11b",
        "display_name": "Nous Hermes 2 11B",
        "size_gb": 6.5,
        "parameters": "11B",
        "description": "Advanced instruction-following model",
        "tags": ["chat", "instruction", "reasoning"],
        "family": "llama",
        "quality": "high",
        "license": "Apache 2.0"
    },
    {
        "name": "starling-lm:7b",
        "display_name": "Starling LM 7B",
        "size_gb": 4.1,
        "parameters": "7B",
        "description": "RLHF-trained model with strong alignment",
        "tags": ["chat", "instruction", "helpful"],
        "family": "mistral",
        "quality": "high",
        "license": "Apache 2.0"
    },
]


class OllamaIntegration:
    """
    Manages Ollama model catalog and provides search functionality
    for both Ollama and HuggingFace models.
    """

    OLLAMA_LIBRARY_URL = "https://ollama.com/library"

    def __init__(self):
        """Initialize Ollama integration."""
        self.logger = logging.getLogger(__name__)
        self._catalog_cache: Optional[List[OllamaModelInfo]] = None

    def get_catalog(
        self,
        ram_gb: int,
        chip_type: str = "Apple Silicon"
    ) -> List[OllamaModelInfo]:
        """
        Get Ollama model catalog with compatibility flags.

        Args:
            ram_gb: Available system RAM in GB
            chip_type: "Apple Silicon" or "Intel"

        Returns:
            List of OllamaModelInfo with compatibility flags
        """
        models = []

        for model_data in OLLAMA_MODEL_CATALOG:
            # Calculate RAM requirement (2x model size)
            ram_required = int(model_data["size_gb"] * 2)

            # Check compatibility
            is_compatible = ram_required <= ram_gb
            compatibility_reason = None
            if not is_compatible:
                compatibility_reason = f"Requires {ram_required}GB RAM (you have {ram_gb}GB)"

            # Calculate performance tier
            perf_tier, speed_est = self._calculate_performance(
                model_data["size_gb"],
                chip_type,
                ram_gb
            )

            # Create model info
            model = OllamaModelInfo(
                name=model_data["name"],
                display_name=model_data["display_name"],
                size_gb=model_data["size_gb"],
                parameters=model_data["parameters"],
                description=model_data["description"],
                tags=model_data["tags"],
                family=model_data["family"],
                expected_performance=perf_tier,
                speed_estimate=speed_est,
                quality=model_data["quality"],
                recommended=False,  # Will be set by caller
                ram_required_gb=ram_required,
                ollama_url=f"{self.OLLAMA_LIBRARY_URL}/{model_data['name'].split(':')[0]}",
                compatible=is_compatible,
                compatibility_reason=compatibility_reason,
                license=model_data.get("license")
            )

            models.append(model)

        # Sort: compatible first, then by performance, then by size
        models.sort(
            key=lambda m: (
                not m.compatible,
                self._perf_rank(m.expected_performance),
                m.size_gb
            )
        )

        # Mark top compatible model as recommended
        compatible_models = [m for m in models if m.compatible]
        if compatible_models:
            # Find best balance of speed and quality
            for model in compatible_models:
                if model.expected_performance in ["fastest", "fast"] and model.quality in ["medium", "high"]:
                    model.recommended = True
                    break
            # If no balanced model found, recommend the first compatible one
            if not any(m.recommended for m in compatible_models):
                compatible_models[0].recommended = True

        return models

    def _calculate_performance(
        self,
        model_size_gb: float,
        chip_type: str,
        ram_gb: int
    ) -> Tuple[str, str]:
        """
        Calculate performance tier based on hardware.

        Returns:
            Tuple of (performance_tier, speed_estimate)
        """
        ram_headroom = ram_gb - (model_size_gb * 2)

        if chip_type == "Apple Silicon":
            if ram_headroom >= 8 and model_size_gb <= 5:
                return ("fastest", "Very Fast (15-20 tok/s)")
            elif ram_headroom >= 4 and model_size_gb <= 7:
                return ("fast", "Fast (10-15 tok/s)")
            elif ram_headroom >= 2 and model_size_gb <= 10:
                return ("good", "Good (5-10 tok/s)")
            else:
                return ("slow", "Slow (2-5 tok/s)")
        else:  # Intel
            if ram_headroom >= 8 and model_size_gb <= 3:
                return ("fast", "Fast (8-12 tok/s)")
            elif ram_headroom >= 4 and model_size_gb <= 5:
                return ("good", "Good (4-8 tok/s)")
            elif ram_headroom >= 2 and model_size_gb <= 7:
                return ("slow", "Slow (2-4 tok/s)")
            else:
                return ("slow", "Very Slow (<2 tok/s)")

    def _perf_rank(self, perf: str) -> int:
        """Convert performance tier to sortable rank."""
        ranks = {"fastest": 0, "fast": 1, "good": 2, "slow": 3}
        return ranks.get(perf, 99)

    def _extract_size_from_model_name(self, model_name: str) -> Optional[float]:
        """
        Extract model size in GB from model name.

        Examples:
            xlam:1b -> 0.7GB
            llama3.2:3b -> 2.0GB
            mistral:7b -> 4.1GB
            mixtral:8x7b -> 26.0GB
        """
        import re

        # Pattern for parameter count (e.g., :1b, :3b, :7b, :70b)
        pattern = r':?(\d+(?:\.\d+)?)\s*b(?:illion)?'
        match = re.search(pattern, model_name.lower())

        if match:
            params = float(match.group(1))

            # Estimate size based on parameter count
            # Rough formula: size_gb = params * 0.6 (for quantized models)
            if params < 1:
                size_gb = 0.4
            elif params < 2:
                size_gb = params * 0.7
            elif params < 4:
                size_gb = params * 0.65
            elif params < 8:
                size_gb = params * 0.6
            elif params < 15:
                size_gb = params * 0.57
            elif params < 35:
                size_gb = params * 0.55
            else:
                size_gb = params * 0.58

            return round(size_gb, 1)

        # Check for mixtral/mixture of experts pattern (e.g., 8x7b)
        moe_pattern = r'(\d+)x(\d+)\s*b'
        moe_match = re.search(moe_pattern, model_name.lower())
        if moe_match:
            # For MoE, approximate size is larger
            experts = int(moe_match.group(1))
            size_per = int(moe_match.group(2))
            total_params = experts * size_per * 0.2  # Only some experts active
            return round(total_params * 0.55, 1)

        return None

    def _extract_parameters(self, model_name: str) -> str:
        """Extract parameter count from model name."""
        import re

        # Pattern for parameter count
        pattern = r':?(\d+(?:\.\d+)?)\s*b(?:illion)?'
        match = re.search(pattern, model_name.lower())

        if match:
            params = match.group(1)
            return f"{params}B"

        # Check for MoE pattern
        moe_pattern = r'(\d+)x(\d+)\s*b'
        moe_match = re.search(moe_pattern, model_name.lower())
        if moe_match:
            return f"{moe_match.group(1)}x{moe_match.group(2)}B"

        return "Unknown"

    def _format_display_name(self, model_name: str) -> str:
        """Format model name for display."""
        # Remove namespace if present
        if '/' in model_name:
            parts = model_name.split('/')
            name = parts[-1]
        else:
            name = model_name

        # Split on : to separate model from tag
        if ':' in name:
            base, tag = name.split(':', 1)
            # Capitalize base, keep tag lowercase
            base = base.replace('-', ' ').replace('_', ' ').title()
            return f"{base} {tag.upper()}"
        else:
            return name.replace('-', ' ').replace('_', ' ').title()

    def _extract_family(self, model_name: str) -> str:
        """Extract model family from name."""
        name_lower = model_name.lower()

        if 'llama' in name_lower or 'vicuna' in name_lower or 'orca' in name_lower:
            return "llama"
        elif 'mistral' in name_lower or 'mixtral' in name_lower:
            return "mistral"
        elif 'phi' in name_lower:
            return "phi"
        elif 'gemma' in name_lower:
            return "gemma"
        elif 'qwen' in name_lower:
            return "qwen"
        elif 'deepseek' in name_lower:
            return "deepseek"
        elif 'xlam' in name_lower:
            return "xlam"
        else:
            return "other"

    def _infer_use_cases(self, model_name: str) -> List[str]:
        """Infer use cases from model name."""
        name_lower = model_name.lower()
        use_cases = []

        if 'code' in name_lower or 'coder' in name_lower:
            use_cases.extend(["code", "programming"])
        if 'chat' in name_lower or 'instruct' in name_lower:
            use_cases.extend(["chat", "conversation"])
        if 'vision' in name_lower or 'vl' in name_lower:
            use_cases.append("vision")
        if 'embed' in name_lower:
            use_cases.append("embedding")
        if 'xlam' in name_lower or 'function' in name_lower:
            use_cases.extend(["function-calling", "tools"])

        # Default use cases if none found
        if not use_cases:
            use_cases = ["chat", "general"]

        return use_cases

    async def search_ollama_url(
        self,
        url: str,
        ram_gb: int,
        chip_type: str = "Apple Silicon"
    ) -> Dict[str, Any]:
        """
        Search for an Ollama model by URL.

        Args:
            url: Ollama URL (e.g., "https://ollama.com/library/deepseek-r1:1.5b" or
                 "https://ollama.com/allenporter/xlam:1b")
            ram_gb: Available system RAM
            chip_type: Chip type for performance calculation

        Returns:
            Dict with model information or error
        """
        # Extract model name from URL
        # Patterns:
        # - https://ollama.com/library/model:tag
        # - https://ollama.com/library/model
        # - https://ollama.com/namespace/model:tag
        # - https://ollama.com/namespace/model
        # Allow dots in model names (e.g., llama3.2, gemma2.9b)
        pattern = r"ollama\.com/(?:library/)?([a-zA-Z0-9._-]+(?:/[a-zA-Z0-9._-]+)?(?::[a-zA-Z0-9._-]+)?)"
        match = re.search(pattern, url)

        if not match:
            return {
                "found": False,
                "error": "Invalid Ollama URL. Expected format: https://ollama.com/library/model:tag or https://ollama.com/namespace/model:tag"
            }

        model_name = match.group(1)

        # Search in catalog
        catalog = self.get_catalog(ram_gb, chip_type)
        for model in catalog:
            if model.name == model_name or model.name.split(":")[0] == model_name.split(":")[0]:
                return {
                    "found": True,
                    "model_id": model_name,
                    "ollama_name": model.name,
                    "display_name": model.display_name,
                    "size_gb": model.size_gb,
                    "parameters": model.parameters,
                    "is_compatible": model.compatible,
                    "compatibility_reason": model.compatibility_reason,
                    "description": model.description,
                    "use_cases": model.tags,
                    "expected_performance": model.expected_performance,
                    "speed_estimate": model.speed_estimate,
                    "quality": model.quality,
                    "ram_required_gb": model.ram_required_gb,
                    "source": "ollama",
                    "license": model.license
                }

        # Not in catalog - try to extract size and calculate performance
        size_gb = self._extract_size_from_model_name(model_name)

        if size_gb:
            # Calculate RAM requirement
            ram_required = int(size_gb * 2)

            # Check compatibility
            is_compatible = ram_required <= ram_gb
            compatibility_reason = None
            if not is_compatible:
                compatibility_reason = f"Requires {ram_required}GB RAM (you have {ram_gb}GB)"

            # Calculate performance
            perf_tier, speed_est = self._calculate_performance(
                size_gb,
                chip_type,
                ram_gb
            )

            # Extract quality estimate from size
            if size_gb < 2:
                quality = "basic"
            elif size_gb < 5:
                quality = "medium"
            else:
                quality = "high"

            return {
                "found": True,
                "model_id": model_name,
                "ollama_name": model_name,
                "display_name": self._format_display_name(model_name),
                "size_gb": size_gb,
                "parameters": self._extract_parameters(model_name),
                "is_compatible": is_compatible,
                "compatibility_reason": compatibility_reason,
                "description": f"Ollama model: {model_name}. Size estimated from model name.",
                "use_cases": self._infer_use_cases(model_name),
                "expected_performance": perf_tier,
                "speed_estimate": speed_est,
                "quality": quality,
                "ram_required_gb": ram_required,
                "source": "ollama",
                "family": self._extract_family(model_name),
                "recommended": False
            }
        else:
            # Can't determine size - return minimal info
            return {
                "found": True,
                "model_id": model_name,
                "ollama_name": model_name,
                "display_name": self._format_display_name(model_name),
                "size_gb": 0,
                "is_compatible": None,
                "compatibility_reason": "Model size unknown. Download to see full details.",
                "description": f"Ollama model: {model_name}. Size will be determined after download.",
                "use_cases": self._infer_use_cases(model_name),
                "expected_performance": "good",
                "speed_estimate": "Performance unknown",
                "quality": "medium",
                "ram_required_gb": 0,
                "source": "ollama",
                "warning": "Model size unknown. Download to see full details."
            }

    def check_hf_ollama_compatibility(
        self,
        hf_model_id: str,
        model_size_gb: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Check if a HuggingFace model can be run in Ollama.

        Args:
            hf_model_id: HuggingFace model ID
            model_size_gb: Model size if known

        Returns:
            Dict with compatibility information
        """
        # Common HF model patterns that have Ollama equivalents
        ollama_mappings = {
            "meta-llama/Llama-3.2-1B": "llama3.2:1b",
            "meta-llama/Llama-3.2-3B": "llama3.2:3b",
            "meta-llama/Llama-3.1-8B": "llama3.1:8b",
            "meta-llama/Llama-3-8B": "llama3:8b",
            "mistralai/Mistral-7B": "mistral:7b",
            "microsoft/phi-3": "phi3:mini",
            "google/gemma-2-2b": "gemma2:2b",
            "google/gemma-2-9b": "gemma2:9b",
            "Qwen/Qwen2-0.5B": "qwen2:0.5b",
            "Qwen/Qwen2-1.5B": "qwen2:1.5b",
            "Qwen/Qwen2-7B": "qwen2:7b",
            "deepseek-ai/deepseek-r1": "deepseek-r1:7b",
        }

        # Check for exact match
        for hf_pattern, ollama_name in ollama_mappings.items():
            if hf_pattern.lower() in hf_model_id.lower():
                return {
                    "compatible": True,
                    "ollama_name": ollama_name,
                    "reason": f"This model is available in Ollama as '{ollama_name}'"
                }

        # Check if it's a GGUF format (Ollama compatible)
        if "gguf" in hf_model_id.lower():
            return {
                "compatible": True,
                "ollama_name": None,
                "reason": "This is a GGUF model which can be imported into Ollama",
                "requires_manual_import": True
            }

        # Otherwise, not compatible
        return {
            "compatible": False,
            "reason": "This HuggingFace model is not available in Ollama format. "
                     "Ollama requires models in GGUF format or officially supported models."
        }


# Singleton instance
_ollama_integration: Optional[OllamaIntegration] = None


def get_ollama_integration() -> OllamaIntegration:
    """Get singleton OllamaIntegration instance."""
    global _ollama_integration
    if _ollama_integration is None:
        _ollama_integration = OllamaIntegration()
    return _ollama_integration
