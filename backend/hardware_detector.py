"""
Hardware detection module for optimal Ollama model selection on macOS.

This module detects Mac hardware specifications and recommends ALL compatible
Ollama models based on available system resources, with performance indicators.
"""

import logging
import platform
import subprocess
from dataclasses import dataclass
from typing import Optional, List

logger = logging.getLogger(__name__)


@dataclass
class ModelInfo:
    """Information about a specific Ollama model."""
    name: str  # e.g., "llama3.1:8b"
    display_name: str  # e.g., "Llama 3.1 8B"
    size_gb: float  # Model size in GB
    expected_performance: str  # "excellent" | "good" | "acceptable" | "slow"
    speed_estimate: str  # e.g., "Fast (10-15 tok/s)"
    quality: str  # "high" | "medium" | "basic"
    recommended: bool  # Is this the recommended model?
    ram_required_gb: int  # Minimum RAM required (2x model size)


@dataclass
class HardwareInfo:
    """Structured hardware information with compatible models."""
    chip_type: str  # "Apple Silicon" or "Intel"
    chip_model: Optional[str]  # e.g., "M2", "M1 Pro", "Intel Core i7"
    ram_gb: int
    cpu_cores: int
    compatible_models: List[ModelInfo]  # All models user can run
    recommended_model: ModelInfo  # Best balance of speed/quality
    detection_successful: bool
    error_message: Optional[str] = None


# Complete model catalog with metadata
MODEL_CATALOG = [
    {
        "name": "llama3.2:1b",
        "display_name": "Llama 3.2 1B",
        "size_gb": 1.3,
        "quality": "basic",
        "description": "Fastest, basic quality"
    },
    {
        "name": "llama3.2:3b",
        "display_name": "Llama 3.2 3B",
        "size_gb": 2.0,
        "quality": "medium",
        "description": "Fast, good quality"
    },
    {
        "name": "phi3:mini",
        "display_name": "Phi 3 Mini",
        "size_gb": 2.3,
        "quality": "medium",
        "description": "Fast, good for code"
    },
    {
        "name": "mistral:7b",
        "display_name": "Mistral 7B",
        "size_gb": 4.1,
        "quality": "high",
        "description": "Fast, high quality"
    },
    {
        "name": "llama3.1:8b",
        "display_name": "Llama 3.1 8B",
        "size_gb": 4.7,
        "quality": "high",
        "description": "Balanced, high quality"
    },
    {
        "name": "gemma2:9b",
        "display_name": "Gemma 2 9B",
        "size_gb": 5.5,
        "quality": "high",
        "description": "Slower, high quality"
    },
    {
        "name": "llama3.2:11b",
        "display_name": "Llama 3.2 11B",
        "size_gb": 6.5,
        "quality": "high",
        "description": "Slower, excellent quality"
    },
    {
        "name": "codellama:13b",
        "display_name": "CodeLlama 13B",
        "size_gb": 7.4,
        "quality": "high",
        "description": "Slow, excellent for code"
    },
]


class HardwareDetector:
    """
    Detects Mac hardware specifications and recommends optimal Ollama models.

    The detector analyzes CPU type, RAM, and processing cores to recommend
    ALL compatible models for the user's hardware configuration, with
    performance indicators for each.
    """

    def __init__(self):
        """Initialize the hardware detector."""
        self.logger = logging.getLogger(__name__)
        self._hardware_info = self.detect()

    @property
    def recommended_model(self) -> ModelInfo:
        """Get recommended model from hardware info."""
        return self._hardware_info.recommended_model

    @property
    def hardware_info(self) -> HardwareInfo:
        """Get full hardware information."""
        return self._hardware_info

    def detect(self) -> HardwareInfo:
        """
        Detect hardware specifications and recommend optimal models.

        Returns:
            HardwareInfo: Complete hardware information and model recommendations
        """
        try:
            chip_type = self._detect_chip_type()
            chip_model = self._detect_chip_model()
            ram_gb = self._detect_ram_gb()
            cpu_cores = self._detect_cpu_cores()

            # Determine ALL compatible models based on hardware
            compatible_models = self._get_compatible_models(
                chip_type=chip_type,
                chip_model=chip_model,
                ram_gb=ram_gb,
                cpu_cores=cpu_cores
            )

            # Find the recommended model (marked with recommended=True)
            recommended_model = next(
                (m for m in compatible_models if m.recommended),
                compatible_models[0] if compatible_models else None
            )

            if not recommended_model:
                raise ValueError("No compatible models found for this hardware")

            self.logger.info(
                f"Hardware detected: {chip_model or chip_type}, "
                f"{ram_gb}GB RAM, {cpu_cores} cores → {recommended_model.name} "
                f"({len(compatible_models)} compatible models)"
            )

            return HardwareInfo(
                chip_type=chip_type,
                chip_model=chip_model,
                ram_gb=ram_gb,
                cpu_cores=cpu_cores,
                compatible_models=compatible_models,
                recommended_model=recommended_model,
                detection_successful=True
            )

        except Exception as e:
            self.logger.error(f"Hardware detection failed: {e}", exc_info=True)

            # Return fallback recommendation with basic model
            fallback_model = ModelInfo(
                name="llama3.2:3b",
                display_name="Llama 3.2 3B",
                size_gb=2.0,
                expected_performance="unknown",
                speed_estimate="Unknown",
                quality="medium",
                recommended=True,
                ram_required_gb=4
            )

            return HardwareInfo(
                chip_type="Unknown",
                chip_model=None,
                ram_gb=0,
                cpu_cores=0,
                compatible_models=[fallback_model],
                recommended_model=fallback_model,
                detection_successful=False,
                error_message=str(e)
            )

    def _detect_chip_type(self) -> str:
        """Detect whether the Mac has Apple Silicon or Intel processor."""
        try:
            machine = platform.machine().lower()
            if machine == "arm64":
                return "Apple Silicon"
            elif machine in ("x86_64", "amd64"):
                return "Intel"
            else:
                self.logger.warning(f"Unknown machine architecture: {machine}")
                return "Unknown"
        except Exception as e:
            self.logger.error(f"Failed to detect chip type: {e}")
            return "Unknown"

    def _detect_chip_model(self) -> Optional[str]:
        """Detect specific chip model (M1, M2, M3, etc. for Apple Silicon)."""
        try:
            result = subprocess.run(
                ["sysctl", "-n", "machdep.cpu.brand_string"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                brand_string = result.stdout.strip()
                if "Apple" in brand_string:
                    # Apple Silicon (e.g., "Apple M2 Pro")
                    parts = brand_string.split()
                    m_parts = [p for p in parts if p.startswith("M") and any(c.isdigit() for c in p)]
                    suffix = [p for p in parts if p in ["Pro", "Max", "Ultra"]]
                    return " ".join(m_parts + suffix) if m_parts else brand_string
                # Intel processor
                return brand_string
            return None
        except Exception as e:
            self.logger.warning(f"Failed to detect chip model: {e}")
            return None

    def _detect_ram_gb(self) -> int:
        """Detect total system RAM in GB."""
        try:
            result = subprocess.run(
                ["sysctl", "-n", "hw.memsize"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                ram_bytes = int(result.stdout.strip())
                return ram_bytes // (1024 ** 3)
            return 0
        except Exception as e:
            self.logger.error(f"Failed to detect RAM: {e}")
            return 0

    def _detect_cpu_cores(self) -> int:
        """Detect number of physical CPU cores."""
        try:
            result = subprocess.run(
                ["sysctl", "-n", "hw.physicalcpu"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return int(result.stdout.strip())
            return 0
        except Exception as e:
            self.logger.error(f"Failed to detect CPU cores: {e}")
            return 0

    def _calculate_performance(
        self,
        model_size_gb: float,
        chip_type: str,
        ram_gb: int
    ) -> tuple[str, str]:
        """
        Calculate expected performance and speed estimate for a model.

        Args:
            model_size_gb: Size of the model in GB
            chip_type: "Apple Silicon" or "Intel"
            ram_gb: Total system RAM in GB

        Returns:
            tuple: (expected_performance, speed_estimate)
        """
        # Calculate RAM headroom
        ram_headroom = ram_gb - (model_size_gb * 2)

        # Apple Silicon is 2-3x faster than Intel for same model
        is_apple_silicon = chip_type == "Apple Silicon"

        # Performance thresholds based on RAM headroom and chip type
        if is_apple_silicon:
            if ram_headroom >= 8 and model_size_gb <= 5:
                return ("excellent", "Fast (10-15 tok/s)")
            elif ram_headroom >= 4 and model_size_gb <= 7:
                return ("good", "Good (5-10 tok/s)")
            elif ram_headroom >= 0:
                return ("acceptable", "Acceptable (2-5 tok/s)")
            else:
                return ("slow", "Slow (1-3 tok/s)")
        else:  # Intel
            if ram_headroom >= 16 and model_size_gb <= 4:
                return ("good", "Good (5-10 tok/s)")
            elif ram_headroom >= 8 and model_size_gb <= 5:
                return ("acceptable", "Acceptable (3-5 tok/s)")
            elif ram_headroom >= 0:
                return ("slow", "Slow (1-3 tok/s)")
            else:
                return ("slow", "Very Slow (<1 tok/s)")

    def _get_compatible_models(
        self,
        chip_type: str,
        chip_model: Optional[str],
        ram_gb: int,
        cpu_cores: int
    ) -> List[ModelInfo]:
        """
        Get ALL compatible models for the hardware, sorted by performance.

        Args:
            chip_type: "Apple Silicon" or "Intel"
            chip_model: Specific chip model
            ram_gb: Total system RAM in GB
            cpu_cores: Number of CPU cores

        Returns:
            List[ModelInfo]: All compatible models, sorted by performance
        """
        compatible = []

        for model_data in MODEL_CATALOG:
            model_size = model_data["size_gb"]
            ram_required = int(model_size * 2)  # Need 2x model size in RAM

            # Check if model fits in RAM
            if ram_required <= ram_gb:
                performance, speed = self._calculate_performance(
                    model_size,
                    chip_type,
                    ram_gb
                )

                model_info = ModelInfo(
                    name=model_data["name"],
                    display_name=model_data["display_name"],
                    size_gb=model_size,
                    expected_performance=performance,
                    speed_estimate=speed,
                    quality=model_data["quality"],
                    recommended=False,  # Will be set below
                    ram_required_gb=ram_required
                )

                compatible.append(model_info)

        # Sort by performance: excellent > good > acceptable > slow
        # Then by quality: high > medium > basic
        # Then by size (smaller is faster)
        performance_order = {"excellent": 0, "good": 1, "acceptable": 2, "slow": 3}
        quality_order = {"high": 0, "medium": 1, "basic": 2}

        compatible.sort(
            key=lambda m: (
                performance_order.get(m.expected_performance, 99),
                quality_order.get(m.quality, 99),
                m.size_gb
            )
        )

        # Mark the best model as recommended
        if compatible:
            # Find the best balance: prefer "excellent" or "good" performance with "high" quality
            recommended_idx = 0
            for idx, model in enumerate(compatible):
                if model.expected_performance in ["excellent", "good"] and model.quality == "high":
                    recommended_idx = idx
                    break

            compatible[recommended_idx].recommended = True

        return compatible

    def get_hardware_summary(self) -> str:
        """Get a human-readable summary of detected hardware."""
        info = self._hardware_info
        if not info.detection_successful:
            return f"Hardware detection failed: {info.error_message}"

        summary = [
            f"Chip: {info.chip_model or info.chip_type}",
            f"RAM: {info.ram_gb}GB",
            f"CPU Cores: {info.cpu_cores}",
            f"Recommended Model: {info.recommended_model.display_name}",
            f"Compatible Models: {len(info.compatible_models)}",
        ]

        return "\n".join(summary)


# Singleton instance for easy access
_detector_instance: Optional[HardwareDetector] = None


def get_hardware_detector() -> HardwareDetector:
    """Get or create the singleton HardwareDetector instance."""
    global _detector_instance
    if _detector_instance is None:
        _detector_instance = HardwareDetector()
    return _detector_instance
