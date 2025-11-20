"""
Shared Utilities Module

Consolidates common functionality used across hardware detection,
Ollama integration, and HuggingFace integration modules.

This module provides:
- Unified performance calculation
- Common model metadata extraction
- Shared constants and types
"""

import re
import logging
from typing import Tuple, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


# =============================================================================
# Common Constants
# =============================================================================

# Performance tier rankings (lower is better)
PERFORMANCE_RANKS = {
    "fastest": 0,
    "excellent": 0,
    "fast": 1,
    "good": 2,
    "acceptable": 2,
    "slow": 3
}

# Quality tier rankings (lower is better)
QUALITY_RANKS = {
    "high": 0,
    "medium": 1,
    "basic": 2
}

# Model family patterns for identification
MODEL_FAMILIES = {
    "llama": ["llama", "vicuna", "orca", "codellama"],
    "mistral": ["mistral", "mixtral"],
    "phi": ["phi"],
    "gemma": ["gemma"],
    "qwen": ["qwen"],
    "deepseek": ["deepseek"],
    "other": []
}


# =============================================================================
# Performance Calculation
# =============================================================================

def calculate_performance(
    model_size_gb: float,
    chip_type: str,
    ram_gb: int
) -> Tuple[str, str]:
    """
    Calculate expected performance tier and speed estimate for a model.

    This is the unified performance calculation function used across
    all integration modules.

    Args:
        model_size_gb: Size of the model in GB
        chip_type: "Apple Silicon" or "Intel"
        ram_gb: Total system RAM in GB

    Returns:
        Tuple of (performance_tier, speed_estimate)

    Examples:
        >>> calculate_performance(2.0, "Apple Silicon", 16)
        ("fastest", "Very Fast (15-20 tok/s)")
        >>> calculate_performance(8.0, "Intel", 16)
        ("slow", "Slow (2-4 tok/s)")
    """
    # Calculate RAM headroom (RAM available after loading model)
    ram_headroom = ram_gb - (model_size_gb * 2)
    is_apple_silicon = chip_type == "Apple Silicon"

    if is_apple_silicon:
        # Apple Silicon performance tiers
        if ram_headroom >= 8 and model_size_gb <= 3:
            return ("fastest", "Very Fast (15-20 tok/s)")
        elif ram_headroom >= 8 and model_size_gb <= 5:
            return ("fast", "Fast (10-15 tok/s)")
        elif ram_headroom >= 4 and model_size_gb <= 7:
            return ("good", "Good (5-10 tok/s)")
        elif ram_headroom >= 2 and model_size_gb <= 10:
            return ("good", "Good (5-10 tok/s)")
        elif ram_headroom >= 0:
            return ("slow", "Slow (2-5 tok/s)")
        else:
            return ("slow", "Very Slow (<2 tok/s)")
    else:
        # Intel performance tiers (generally slower)
        if ram_headroom >= 16 and model_size_gb <= 4:
            return ("fast", "Fast (8-12 tok/s)")
        elif ram_headroom >= 8 and model_size_gb <= 5:
            return ("good", "Good (4-8 tok/s)")
        elif ram_headroom >= 4 and model_size_gb <= 7:
            return ("slow", "Slow (2-4 tok/s)")
        elif ram_headroom >= 0:
            return ("slow", "Slow (1-3 tok/s)")
        else:
            return ("slow", "Very Slow (<1 tok/s)")


def get_performance_rank(performance: str) -> int:
    """
    Convert performance tier to sortable rank.

    Args:
        performance: Performance tier string

    Returns:
        Integer rank (lower is better)
    """
    return PERFORMANCE_RANKS.get(performance.lower(), 99)


def get_quality_rank(quality: str) -> int:
    """
    Convert quality tier to sortable rank.

    Args:
        quality: Quality tier string

    Returns:
        Integer rank (lower is better)
    """
    return QUALITY_RANKS.get(quality.lower(), 99)


# =============================================================================
# Model Metadata Extraction
# =============================================================================

def extract_size_from_name(model_name: str) -> Optional[float]:
    """
    Extract model size in GB from model name.

    Handles various naming patterns:
    - Standard: llama3.2:1b, mistral:7b
    - MoE: mixtral:8x7b
    - With decimals: qwen:1.5b

    Args:
        model_name: Model name string

    Returns:
        Estimated size in GB or None if cannot determine

    Examples:
        >>> extract_size_from_name("llama3.2:1b")
        0.7
        >>> extract_size_from_name("mistral:7b")
        4.2
        >>> extract_size_from_name("mixtral:8x7b")
        7.7
    """
    name_lower = model_name.lower()

    # Pattern for parameter count (e.g., :1b, :3b, :7b, :70b)
    pattern = r':?(\d+(?:\.\d+)?)\s*b(?:illion)?'
    match = re.search(pattern, name_lower)

    if match:
        params = float(match.group(1))

        # Size estimation based on parameter count (for quantized models)
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

    # Check for mixture-of-experts pattern (e.g., 8x7b)
    moe_pattern = r'(\d+)x(\d+)\s*b'
    moe_match = re.search(moe_pattern, name_lower)

    if moe_match:
        experts = int(moe_match.group(1))
        size_per = int(moe_match.group(2))
        # For MoE, only some experts are active at once
        total_params = experts * size_per * 0.2
        return round(total_params * 0.55, 1)

    return None


def extract_parameters(model_name: str) -> str:
    """
    Extract parameter count string from model name.

    Args:
        model_name: Model name string

    Returns:
        Parameter count string (e.g., "7B", "8x7B")

    Examples:
        >>> extract_parameters("llama3.1:8b")
        "8B"
        >>> extract_parameters("mixtral:8x7b")
        "8x7B"
    """
    name_lower = model_name.lower()

    # Standard parameter pattern
    pattern = r':?(\d+(?:\.\d+)?)\s*b(?:illion)?'
    match = re.search(pattern, name_lower)

    if match:
        return f"{match.group(1)}B"

    # MoE pattern
    moe_pattern = r'(\d+)x(\d+)\s*b'
    moe_match = re.search(moe_pattern, name_lower)

    if moe_match:
        return f"{moe_match.group(1)}x{moe_match.group(2)}B"

    return "Unknown"


def extract_family(model_name: str) -> str:
    """
    Extract model family from name.

    Args:
        model_name: Model name string

    Returns:
        Family name string

    Examples:
        >>> extract_family("llama3.2:1b")
        "llama"
        >>> extract_family("phi3:mini")
        "phi"
    """
    name_lower = model_name.lower()

    for family, patterns in MODEL_FAMILIES.items():
        if family == "other":
            continue
        for pattern in patterns:
            if pattern in name_lower:
                return family

    return "other"


def format_display_name(model_name: str) -> str:
    """
    Format model name for human-readable display.

    Args:
        model_name: Model name or ID string

    Returns:
        Formatted display name

    Examples:
        >>> format_display_name("llama3.2:1b")
        "Llama3.2 1B"
        >>> format_display_name("meta-llama/Llama-3.2-1B-Instruct")
        "Llama 3.2 1B"
    """
    # Handle HuggingFace IDs with namespace
    if '/' in model_name:
        name = model_name.split('/')[-1]
    else:
        name = model_name

    # Split on colon to separate model from tag
    if ':' in name:
        base, tag = name.split(':', 1)
        base = base.replace('-', ' ').replace('_', ' ').title()
        return f"{base} {tag.upper()}"
    else:
        # Clean up HuggingFace format names
        name = name.replace('-', ' ').replace('_', ' ')
        name = name.replace("Instruct", "").replace("hf", "").replace("chat", "")
        name = ' '.join(name.split())  # Remove extra spaces
        return name


def infer_use_cases(model_name: str) -> List[str]:
    """
    Infer use cases from model name.

    Args:
        model_name: Model name string

    Returns:
        List of use case strings

    Examples:
        >>> infer_use_cases("codellama:7b")
        ["code", "programming"]
        >>> infer_use_cases("llama3.2:1b-instruct")
        ["chat", "conversation"]
    """
    name_lower = model_name.lower()
    use_cases = []

    # Keyword to use case mapping
    patterns = {
        "code": ["code", "programming"],
        "coder": ["code", "programming"],
        "chat": ["chat", "conversation"],
        "instruct": ["chat", "conversation"],
        "vision": ["vision"],
        "vl": ["vision"],
        "embed": ["embedding"],
        "xlam": ["function-calling", "tools"],
        "function": ["function-calling", "tools"],
        "math": ["mathematics"],
        "reason": ["reasoning"]
    }

    for keyword, cases in patterns.items():
        if keyword in name_lower:
            for case in cases:
                if case not in use_cases:
                    use_cases.append(case)

    # Default if no use cases found
    if not use_cases:
        use_cases = ["chat", "general"]

    return use_cases


def calculate_ram_required(size_gb: float) -> int:
    """
    Calculate minimum RAM required to run a model.

    The rule of thumb is 2x model size for comfortable operation.

    Args:
        size_gb: Model size in GB

    Returns:
        Required RAM in GB (integer)
    """
    return int(size_gb * 2)


def determine_quality_tier(
    size_gb: float,
    downloads: int = 0,
    likes: int = 0
) -> str:
    """
    Determine quality tier based on model characteristics.

    Args:
        size_gb: Model size in GB
        downloads: Download count (optional)
        likes: Like count (optional)

    Returns:
        Quality tier: "high", "medium", or "basic"
    """
    # High quality: large models or very popular
    if size_gb >= 7.0 or downloads > 100000 or likes > 1000:
        return "high"

    # Basic quality: very small models
    if size_gb < 2.0:
        return "basic"

    # Medium quality: everything else
    return "medium"


# =============================================================================
# Compatibility Checking
# =============================================================================

def check_model_compatibility(
    model_size_gb: float,
    ram_gb: int
) -> Tuple[bool, Optional[str]]:
    """
    Check if a model is compatible with the available RAM.

    Args:
        model_size_gb: Size of the model in GB
        ram_gb: Available system RAM in GB

    Returns:
        Tuple of (is_compatible, reason_if_incompatible)
    """
    ram_required = calculate_ram_required(model_size_gb)

    if ram_required <= ram_gb:
        return (True, None)
    else:
        return (
            False,
            f"Requires {ram_required}GB RAM (you have {ram_gb}GB)"
        )
