"""
HuggingFace Model Catalog Integration

Fetches and manages open-source LLM models from HuggingFace Hub,
filtering by hardware compatibility and providing performance estimates.
"""

import logging
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
import httpx
import asyncio

logger = logging.getLogger(__name__)


@dataclass
class HFModelInfo:
    """Information about a HuggingFace model compatible with Ollama."""
    model_id: str  # HF model ID (e.g., "meta-llama/Llama-2-7b-chat-hf")
    name: str  # Ollama-compatible name (e.g., "llama2:7b")
    display_name: str  # Human-readable name
    size_gb: float  # Estimated model size in GB
    downloads: int  # Number of downloads on HF
    likes: int  # Number of likes on HF
    tags: List[str]  # Model tags (e.g., ["conversational", "code"])
    description: str  # Model-specific description from HuggingFace
    use_cases: List[str]  # Extracted from tags/description
    expected_performance: str  # "fastest" | "fast" | "good" | "slow"
    speed_estimate: str  # e.g., "Fast (10-15 tok/s)"
    quality: str  # "high" | "medium" | "basic"
    recommended: bool  # Is this recommended for the hardware?
    ram_required_gb: int  # Minimum RAM required
    hf_url: str  # Full HuggingFace URL
    compatible: bool  # Hardware compatibility flag
    compatibility_reason: Optional[str] = None  # Why incompatible


class HuggingFaceIntegration:
    """
    Integrates with HuggingFace API to fetch and manage open-source LLM models.

    Fetches models compatible with Ollama, estimates their hardware requirements,
    and provides performance predictions based on system specifications.
    """

    HF_API_BASE = "https://huggingface.co/api"
    HF_MODELS_API = f"{HF_API_BASE}/models"

    # Target number of models to fetch
    TARGET_MODEL_COUNT = 50

    # Model filters for HuggingFace API
    MODEL_FILTERS = {
        "filter": "text-generation",
        "sort": "downloads",
        "direction": -1,
        "limit": 100  # Fetch more than needed to account for filtering
    }

    def __init__(self):
        """Initialize HuggingFace integration."""
        self.logger = logging.getLogger(__name__)
        self._model_cache: Optional[List[HFModelInfo]] = None
        self._cache_timestamp = 0
        self.CACHE_TTL = 3600  # Cache for 1 hour

    async def fetch_models(
        self,
        ram_gb: int,
        chip_type: str = "Apple Silicon",
        force_refresh: bool = False
    ) -> List[HFModelInfo]:
        """
        Fetch ALL models from HuggingFace with compatibility flags.

        Args:
            ram_gb: Available system RAM in GB
            chip_type: "Apple Silicon" or "Intel"
            force_refresh: Force refresh cache

        Returns:
            List of ALL HFModelInfo with compatibility flags set
        """
        import time

        # Check cache
        if not force_refresh and self._model_cache:
            if time.time() - self._cache_timestamp < self.CACHE_TTL:
                self.logger.info("Using cached HuggingFace models")
                return self._mark_compatibility(self._model_cache, ram_gb, chip_type)

        try:
            # Fetch model metadata from HuggingFace API
            models = await self._fetch_from_huggingface()

            # Update cache
            self._model_cache = models
            self._cache_timestamp = time.time()

            # Mark compatibility for all models
            models_with_flags = self._mark_compatibility(models, ram_gb, chip_type)

            compatible_count = sum(1 for m in models_with_flags if m.compatible)
            self.logger.info(
                f"Fetched {len(models)} total models, "
                f"{compatible_count} compatible with {ram_gb}GB RAM"
            )

            return models_with_flags

        except Exception as e:
            self.logger.error(f"Failed to fetch HuggingFace models: {e}", exc_info=True)
            # Return fallback models
            return self._get_fallback_models(ram_gb, chip_type)

    async def _fetch_from_huggingface(self) -> List[HFModelInfo]:
        """
        Fetch model metadata dynamically from HuggingFace API.

        Returns:
            List of all HFModelInfo (30-50 popular models)
        """
        models = []

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Fetch popular text-generation models from HF API
                params = self.MODEL_FILTERS.copy()
                url = self.HF_MODELS_API

                self.logger.info(f"Fetching models from HuggingFace API: {url}")
                response = await client.get(url, params=params)

                if response.status_code != 200:
                    self.logger.error(f"Failed to fetch models: HTTP {response.status_code}")
                    return []

                api_models = response.json()
                self.logger.info(f"Received {len(api_models)} models from HuggingFace API")

                # Filter and process models
                tasks = []
                processed_count = 0

                for model_data in api_models:
                    if processed_count >= self.TARGET_MODEL_COUNT:
                        break

                    model_id = model_data.get("id") or model_data.get("modelId")
                    if not model_id:
                        continue

                    # Skip non-instruct/chat models for better UX
                    tags = model_data.get("tags", []) or []

                    # Prioritize instruct/chat models but include others
                    is_priority = any(tag in model_id.lower() for tag in ["instruct", "chat", "it"])

                    tasks.append(self._fetch_model_with_description(client, model_id, model_data))
                    processed_count += 1

                # Wait for all requests (with timeout protection)
                results = await asyncio.gather(*tasks, return_exceptions=True)

                # Process results
                for result in results:
                    if isinstance(result, HFModelInfo):
                        models.append(result)
                    elif isinstance(result, Exception):
                        self.logger.warning(f"Failed to fetch model: {result}")

        except Exception as e:
            self.logger.error(f"Error fetching models from HuggingFace: {e}", exc_info=True)

        self.logger.info(f"Successfully fetched {len(models)} models")
        return models

    async def _fetch_model_with_description(
        self,
        client: httpx.AsyncClient,
        model_id: str,
        model_data: Dict[str, Any]
    ) -> Optional[HFModelInfo]:
        """
        Fetch model information with description from model card.

        Args:
            client: HTTP client
            model_id: HuggingFace model ID
            model_data: Basic model data from API

        Returns:
            HFModelInfo with description or None if fetch failed
        """
        try:
            # Extract basic metadata
            downloads = model_data.get("downloads", 0) or 0
            likes = model_data.get("likes", 0) or 0
            tags = model_data.get("tags", []) or []

            # Fetch model card for description
            description = await self._fetch_model_description(client, model_id)

            # Extract use cases from tags and description
            use_cases = self._extract_use_cases(tags, description)

            # Estimate model size from model ID or default
            size_gb = self._estimate_model_size(model_id, tags)

            # Generate Ollama-compatible name
            ollama_name = self._generate_ollama_name(model_id)

            # Format display name
            display_name = self._format_display_name(model_id)

            # Determine quality tier based on size and popularity
            quality = self._determine_quality(size_gb, downloads, likes)

            # Calculate RAM requirement
            ram_required_gb = int(size_gb * 2)

            return HFModelInfo(
                model_id=model_id,
                name=ollama_name,
                display_name=display_name,
                size_gb=size_gb,
                downloads=downloads,
                likes=likes,
                tags=tags,
                description=description,
                use_cases=use_cases,
                expected_performance="good",  # Will be recalculated
                speed_estimate="Good (5-10 tok/s)",  # Will be recalculated
                quality=quality,
                recommended=False,
                ram_required_gb=ram_required_gb,
                hf_url=f"https://huggingface.co/{model_id}",
                compatible=True,  # Will be set during compatibility check
                compatibility_reason=None
            )

        except Exception as e:
            self.logger.error(f"Error fetching model {model_id}: {e}")
            return None

    async def _fetch_model_description(
        self,
        client: httpx.AsyncClient,
        model_id: str
    ) -> str:
        """
        Fetch model description from model card README.

        Args:
            client: HTTP client
            model_id: HuggingFace model ID

        Returns:
            First paragraph of description or default message
        """
        try:
            # Try to fetch model card
            readme_url = f"https://huggingface.co/{model_id}/raw/main/README.md"
            response = await client.get(readme_url, timeout=10.0)

            if response.status_code == 200:
                readme_content = response.text

                # Extract first meaningful paragraph (skip YAML frontmatter)
                lines = readme_content.split("\n")
                description_lines = []
                in_frontmatter = False

                for line in lines:
                    stripped = line.strip()

                    # Skip YAML frontmatter
                    if stripped == "---":
                        in_frontmatter = not in_frontmatter
                        continue

                    if in_frontmatter:
                        continue

                    # Skip headers and empty lines at start
                    if not description_lines and (not stripped or stripped.startswith("#")):
                        continue

                    # Collect lines until we have a paragraph
                    if stripped:
                        description_lines.append(stripped)

                    # Stop after first paragraph
                    if len(description_lines) > 0 and not stripped:
                        break

                if description_lines:
                    description = " ".join(description_lines)
                    # Limit length
                    if len(description) > 300:
                        description = description[:297] + "..."
                    return description

        except Exception as e:
            self.logger.debug(f"Could not fetch description for {model_id}: {e}")

        # Default description
        return f"A text generation model from {model_id.split('/')[0]}"

    def _extract_use_cases(self, tags: List[str], description: str) -> List[str]:
        """
        Extract use cases from tags and description.

        Args:
            tags: Model tags
            description: Model description

        Returns:
            List of use case strings
        """
        use_cases = []

        # Map tags to use cases
        tag_mapping = {
            "conversational": "Chat & Conversation",
            "text-generation": "Text Generation",
            "code": "Code Generation",
            "text-classification": "Classification",
            "question-answering": "Question Answering",
            "summarization": "Summarization",
            "translation": "Translation",
            "text2text-generation": "Text-to-Text",
            "fill-mask": "Fill Mask",
        }

        for tag in tags:
            if tag in tag_mapping and tag_mapping[tag] not in use_cases:
                use_cases.append(tag_mapping[tag])

        # Extract from description (look for common keywords)
        description_lower = description.lower()
        keyword_mapping = {
            "chat": "Chat & Conversation",
            "conversation": "Chat & Conversation",
            "code": "Code Generation",
            "programming": "Code Generation",
            "instruct": "Instruction Following",
            "assistant": "AI Assistant",
            "reasoning": "Reasoning",
            "math": "Mathematics",
            "multilingual": "Multilingual",
        }

        for keyword, use_case in keyword_mapping.items():
            if keyword in description_lower and use_case not in use_cases:
                use_cases.append(use_case)

        # Default if no use cases found
        if not use_cases:
            use_cases = ["General Purpose"]

        return use_cases[:3]  # Limit to 3 use cases

    def _estimate_model_size(self, model_id: str, tags: List[str]) -> float:
        """
        Estimate model size from model ID or tags.

        Args:
            model_id: HuggingFace model ID
            tags: Model tags

        Returns:
            Estimated size in GB
        """
        model_lower = model_id.lower()

        # Extract size from model name
        size_patterns = [
            (r"1b", 1.3),
            (r"1\.5b", 1.1),
            (r"2b", 1.6),
            (r"3b", 2.0),
            (r"7b", 4.1),
            (r"8b", 4.7),
            (r"9b", 5.5),
            (r"13b", 7.4),
            (r"70b", 40.0),
        ]

        import re
        for pattern, size in size_patterns:
            if re.search(pattern, model_lower):
                return size

        # Default size
        return 4.0

    def _generate_ollama_name(self, model_id: str) -> str:
        """
        Generate Ollama-compatible name from HuggingFace model ID.

        Args:
            model_id: HuggingFace model ID

        Returns:
            Ollama-compatible name
        """
        # Extract base name
        name = model_id.split("/")[-1].lower()

        # Remove common suffixes
        name = name.replace("-instruct", "").replace("-chat", "").replace("-hf", "")

        # Extract size if present
        import re
        size_match = re.search(r"(\d+\.?\d*b)", name)
        size_suffix = f":{size_match.group(1)}" if size_match else ""

        # Get base model name
        base_name = name.split("-")[0]

        return f"{base_name}{size_suffix}"

    def _determine_quality(self, size_gb: float, downloads: int, likes: int) -> str:
        """
        Determine quality tier based on size and popularity.

        Args:
            size_gb: Model size in GB
            downloads: Download count
            likes: Like count

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

    async def _fetch_model_info(
        self,
        client: httpx.AsyncClient,
        hf_model_id: str
    ) -> Optional[HFModelInfo]:
        """
        Fetch information for a specific HuggingFace model.

        Args:
            client: HTTP client
            hf_model_id: HuggingFace model ID

        Returns:
            HFModelInfo or None if fetch failed
        """
        try:
            # Get model metadata from HF API
            url = f"{self.HF_MODELS_API}/{hf_model_id}"
            response = await client.get(url)

            if response.status_code != 200:
                self.logger.warning(f"Failed to fetch {hf_model_id}: HTTP {response.status_code}")
                return None

            data = response.json()

            # Get Ollama mapping
            ollama_info = self.OLLAMA_COMPATIBLE_MODELS.get(hf_model_id, {})
            ollama_name = ollama_info.get("ollama", hf_model_id.split("/")[-1])
            size_gb = ollama_info.get("size_gb", 4.0)
            quality = ollama_info.get("quality", "medium")

            # Extract metadata
            display_name = self._format_display_name(hf_model_id)
            downloads = data.get("downloads", 0) or 0
            likes = data.get("likes", 0) or 0
            tags = data.get("tags", []) or []

            # Calculate requirements (placeholder - will be calculated per hardware)
            ram_required = int(size_gb * 2)

            return HFModelInfo(
                model_id=hf_model_id,
                name=ollama_name,
                display_name=display_name,
                size_gb=size_gb,
                downloads=downloads,
                likes=likes,
                tags=tags,
                description=f"A text generation model from {hf_model_id.split('/')[0]}",
                use_cases=["General Purpose"],
                expected_performance="good",  # Will be recalculated
                speed_estimate="Good (5-10 tok/s)",  # Will be recalculated
                quality=quality,
                recommended=False,  # Will be set during filtering
                ram_required_gb=ram_required,
                hf_url=f"https://huggingface.co/{hf_model_id}",
                compatible=True,  # Will be set during compatibility check
                compatibility_reason=None
            )

        except Exception as e:
            self.logger.error(f"Error fetching {hf_model_id}: {e}")
            return None

    def _format_display_name(self, hf_model_id: str) -> str:
        """Convert HF model ID to human-readable display name."""
        # Extract model name from ID
        name = hf_model_id.split("/")[-1]

        # Format: "Llama-3.2-1B-Instruct" -> "Llama 3.2 1B"
        name = name.replace("-", " ")
        name = name.replace("Instruct", "").replace("hf", "").replace("chat", "")
        name = " ".join(name.split())  # Remove extra spaces

        return name

    def _mark_compatibility(
        self,
        models: List[HFModelInfo],
        ram_gb: int,
        chip_type: str
    ) -> List[HFModelInfo]:
        """
        Mark ALL models with compatibility flags and calculate performance.

        Args:
            models: All available models
            ram_gb: System RAM in GB
            chip_type: "Apple Silicon" or "Intel"

        Returns:
            All models with compatibility flags set and sorted
        """
        for model in models:
            # Check if model fits in RAM (need 2x model size)
            if model.ram_required_gb <= ram_gb:
                # Compatible - calculate performance
                performance, speed = self._calculate_performance(
                    model.size_gb,
                    chip_type,
                    ram_gb
                )

                model.expected_performance = performance
                model.speed_estimate = speed
                model.compatible = True
                model.compatibility_reason = None

            else:
                # Incompatible - mark with reason
                model.compatible = False
                model.compatibility_reason = (
                    f"Requires {model.ram_required_gb}GB RAM, "
                    f"but only {ram_gb}GB available"
                )

                # Still calculate performance for display
                performance, speed = self._calculate_performance(
                    model.size_gb,
                    chip_type,
                    ram_gb
                )
                model.expected_performance = performance
                model.speed_estimate = speed

        # Sort: compatible first, then by performance, then popularity
        performance_order = {"fastest": 0, "fast": 1, "good": 2, "slow": 3}
        models.sort(
            key=lambda m: (
                not m.compatible,  # Compatible models first
                performance_order.get(m.expected_performance, 99),
                -m.downloads,  # Higher downloads first
                m.size_gb  # Smaller size first
            )
        )

        # Mark recommended model (best performance + high quality + compatible)
        compatible_models = [m for m in models if m.compatible]
        if compatible_models:
            for model in compatible_models:
                if model.expected_performance in ["fastest", "fast"] and model.quality == "high":
                    model.recommended = True
                    break
            else:
                # If no high-quality fast model, recommend the first compatible one
                compatible_models[0].recommended = True

        return models

    def _calculate_performance(
        self,
        model_size_gb: float,
        chip_type: str,
        ram_gb: int
    ) -> tuple[str, str]:
        """
        Calculate expected performance tier for a model on given hardware.

        Args:
            model_size_gb: Model size in GB
            chip_type: "Apple Silicon" or "Intel"
            ram_gb: System RAM in GB

        Returns:
            (performance_tier, speed_description)
        """
        # Calculate RAM headroom
        ram_headroom = ram_gb - (model_size_gb * 2)
        is_apple_silicon = chip_type == "Apple Silicon"

        # Performance tiers based on hardware
        if is_apple_silicon:
            if ram_headroom >= 8 and model_size_gb <= 3:
                return ("fastest", "Fastest (15-20 tok/s)")
            elif ram_headroom >= 8 and model_size_gb <= 5:
                return ("fast", "Fast (10-15 tok/s)")
            elif ram_headroom >= 4 and model_size_gb <= 7:
                return ("good", "Good (5-10 tok/s)")
            else:
                return ("slow", "Slow (2-5 tok/s)")
        else:  # Intel
            if ram_headroom >= 16 and model_size_gb <= 4:
                return ("fast", "Fast (8-12 tok/s)")
            elif ram_headroom >= 8 and model_size_gb <= 5:
                return ("good", "Good (4-8 tok/s)")
            else:
                return ("slow", "Slow (2-4 tok/s)")

    def _get_fallback_models(
        self,
        ram_gb: int,
        chip_type: str
    ) -> List[HFModelInfo]:
        """
        Return hardcoded fallback models when HF API is unavailable.

        Args:
            ram_gb: System RAM in GB
            chip_type: "Apple Silicon" or "Intel"

        Returns:
            List of fallback models
        """
        self.logger.warning("Using fallback model catalog")

        # Hardcoded fallback models
        fallback = [
            HFModelInfo(
                model_id="meta-llama/Llama-3.2-1B-Instruct",
                name="llama3.2:1b",
                display_name="Llama 3.2 1B",
                size_gb=1.3,
                downloads=50000,
                likes=500,
                tags=["conversational"],
                description="A compact 1B parameter instruction-tuned model for general conversation and tasks.",
                use_cases=["Chat & Conversation", "Instruction Following"],
                expected_performance="fastest",
                speed_estimate="Fastest (15-20 tok/s)",
                quality="basic",
                recommended=False,
                ram_required_gb=3,
                hf_url="https://huggingface.co/meta-llama/Llama-3.2-1B-Instruct",
                compatible=True,
                compatibility_reason=None
            ),
            HFModelInfo(
                model_id="meta-llama/Meta-Llama-3.1-8B-Instruct",
                name="llama3.1:8b",
                display_name="Llama 3.1 8B",
                size_gb=4.7,
                downloads=200000,
                likes=2000,
                tags=["conversational"],
                description="An 8B parameter instruction-tuned model with strong reasoning and conversation capabilities.",
                use_cases=["Chat & Conversation", "Reasoning", "Instruction Following"],
                expected_performance="fast",
                speed_estimate="Fast (10-15 tok/s)",
                quality="high",
                recommended=True,
                ram_required_gb=10,
                hf_url="https://huggingface.co/meta-llama/Meta-Llama-3.1-8B-Instruct",
                compatible=True,
                compatibility_reason=None
            ),
        ]

        # Mark compatibility for all models
        return self._mark_compatibility(fallback, ram_gb, chip_type)

    async def download_from_url(self, hf_url: str) -> Optional[str]:
        """
        Download a model from a HuggingFace URL.

        Args:
            hf_url: HuggingFace model URL (e.g., https://huggingface.co/meta-llama/Llama-2-7b-chat-hf)

        Returns:
            Ollama model name if successful, None otherwise
        """
        try:
            # Extract model ID from URL
            if "huggingface.co/" in hf_url:
                parts = hf_url.split("huggingface.co/")[-1].split("?")[0].strip("/")
                model_id = parts
            else:
                model_id = hf_url

            # Generate Ollama-compatible name from HuggingFace model ID
            self.logger.info(f"Generating Ollama name for model: {model_id}")
            ollama_name = self._generate_ollama_name(model_id)
            self.logger.info(f"Generated Ollama name: {ollama_name}")
            return ollama_name

        except Exception as e:
            self.logger.error(f"Error parsing HuggingFace URL: {e}")
            return None

    async def search_huggingface_model(
        self,
        hf_url: str,
        ram_gb: int = 16,
        chip_type: str = "Apple Silicon"
    ) -> Optional[Dict[str, Any]]:
        """
        Search for a model on HuggingFace and return its details with hardware compatibility.

        Args:
            hf_url: HuggingFace model URL or ID
            ram_gb: Available system RAM in GB
            chip_type: "Apple Silicon" or "Intel"

        Returns:
            Dict with model information including hardware compatibility or None if not found
        """
        try:
            # Extract model ID from URL
            if "huggingface.co/" in hf_url:
                model_id = hf_url.split("huggingface.co/")[-1].split("?")[0].strip("/")
            else:
                model_id = hf_url

            # Fetch from HuggingFace API
            async with httpx.AsyncClient(timeout=30.0) as client:
                url = f"{self.HF_MODELS_API}/{model_id}"
                response = await client.get(url)

                if response.status_code != 200:
                    return None

                data = response.json()

                # Generate Ollama name
                ollama_name = self._generate_ollama_name(model_id)

                # Extract tags
                tags = data.get("tags", []) or []

                # Fetch description from model card
                description = await self._fetch_model_description(client, model_id)

                # Extract use cases
                use_cases = self._extract_use_cases(tags, description)

                # Estimate size and quality
                size_gb = self._estimate_model_size(model_id, tags)
                downloads = data.get("downloads", 0) or 0
                likes = data.get("likes", 0) or 0
                quality = self._determine_quality(size_gb, downloads, likes)

                # Calculate RAM requirement
                ram_required_gb = int(size_gb * 2)

                # Check hardware compatibility
                is_compatible = ram_required_gb <= ram_gb
                compatibility_reason = None if is_compatible else (
                    f"Requires {ram_required_gb}GB RAM, but only {ram_gb}GB available"
                )

                # Calculate performance
                performance, speed_estimate = self._calculate_performance(
                    size_gb, chip_type, ram_gb
                )

                return {
                    "model_id": model_id,
                    "ollama_name": ollama_name,
                    "display_name": self._format_display_name(model_id),
                    "size_gb": size_gb,
                    "quality": quality,
                    "downloads": downloads,
                    "likes": likes,
                    "tags": tags,
                    "description": description,
                    "use_cases": use_cases,
                    "hf_url": f"https://huggingface.co/{model_id}",
                    "ram_required_gb": ram_required_gb,
                    "compatible": is_compatible,
                    "compatibility_reason": compatibility_reason,
                    "expected_performance": performance,
                    "speed_estimate": speed_estimate,
                    "recommended": False
                }

        except Exception as e:
            self.logger.error(f"Error searching HuggingFace model: {e}")
            return None


# Singleton instance
_hf_integration: Optional[HuggingFaceIntegration] = None


def get_huggingface_integration() -> HuggingFaceIntegration:
    """Get or create the singleton HuggingFaceIntegration instance."""
    global _hf_integration
    if _hf_integration is None:
        _hf_integration = HuggingFaceIntegration()
    return _hf_integration
