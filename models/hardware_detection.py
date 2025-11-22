"""
Hardware detection and configuration for optimal model loading.
"""
import os
import gc
from dataclasses import dataclass
from typing import Optional

import torch


@dataclass
class HardwareConfig:
    """Hardware configuration for model loading."""
    device: str
    gpu_memory_gb: float
    quantization: str
    torch_dtype: str
    device_map: str
    cpu_cores: int
    total_ram_gb: float


def get_gpu_memory() -> float:
    """Get available GPU memory in GB."""
    if torch.cuda.is_available():
        props = torch.cuda.get_device_properties(0)
        return props.total_memory / (1024 ** 3)
    return 0.0


def get_system_memory() -> float:
    """Get total system RAM in GB."""
    try:
        import psutil
        return psutil.virtual_memory().total / (1024 ** 3)
    except ImportError:
        return 16.0  # Default assumption


def get_cpu_cores() -> int:
    """Get number of CPU cores."""
    return os.cpu_count() or 4


def detect_hardware() -> HardwareConfig:
    """
    Detect hardware capabilities and return optimal configuration.

    Returns:
        HardwareConfig: Optimized configuration for the detected hardware.
    """
    # Check CUDA availability
    cuda_available = torch.cuda.is_available()
    device = "cuda" if cuda_available else "cpu"

    # Get hardware specs
    gpu_memory = get_gpu_memory()
    system_memory = get_system_memory()
    cpu_cores = get_cpu_cores()

    # Determine quantization and dtype based on available resources
    if cuda_available:
        if gpu_memory >= 16:
            # Plenty of VRAM - use full precision
            quantization = "none"
            torch_dtype = "float16"
        elif gpu_memory >= 8:
            # 8-bit quantization for moderate VRAM
            quantization = "8bit"
            torch_dtype = "float16"
        else:
            # 4-bit for low VRAM (if supported)
            quantization = "8bit"
            torch_dtype = "float16"
        device_map = "auto"
    else:
        # CPU mode
        quantization = "none"
        torch_dtype = "float32"
        device_map = "cpu"

    return HardwareConfig(
        device=device,
        gpu_memory_gb=gpu_memory,
        quantization=quantization,
        torch_dtype=torch_dtype,
        device_map=device_map,
        cpu_cores=cpu_cores,
        total_ram_gb=system_memory
    )


def clear_memory():
    """Aggressively clear GPU and CPU memory."""
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.synchronize()
    gc.collect()


def set_memory_optimizations():
    """Set environment variables for better memory management."""
    os.environ['PYTORCH_CUDA_ALLOC_CONF'] = 'expandable_segments:True'


def get_memory_stats() -> dict:
    """Get current memory usage statistics."""
    stats = {
        "cpu_memory_used_gb": 0,
        "gpu_memory_used_gb": 0,
        "gpu_memory_total_gb": 0,
        "gpu_memory_free_gb": 0
    }

    try:
        import psutil
        process = psutil.Process()
        stats["cpu_memory_used_gb"] = process.memory_info().rss / (1024 ** 3)
    except ImportError:
        pass

    if torch.cuda.is_available():
        stats["gpu_memory_used_gb"] = torch.cuda.memory_allocated(0) / (1024 ** 3)
        stats["gpu_memory_total_gb"] = torch.cuda.get_device_properties(0).total_memory / (1024 ** 3)
        stats["gpu_memory_free_gb"] = stats["gpu_memory_total_gb"] - stats["gpu_memory_used_gb"]

    return stats


if __name__ == "__main__":
    print("=" * 60)
    print("HARDWARE DETECTION MODULE TEST")
    print("=" * 60)

    # Test hardware detection
    config = detect_hardware()
    print(f"  Device: {config.device}")
    print(f"  GPU Memory: {config.gpu_memory_gb:.2f} GB")
    print(f"  Quantization: {config.quantization}")
    print(f"  Torch dtype: {config.torch_dtype}")
    print(f"  CPU cores: {config.cpu_cores}")
    print(f"  System RAM: {config.total_ram_gb:.2f} GB")

    # Test memory stats
    stats = get_memory_stats()
    print(f"\n  Memory Stats:")
    for key, value in stats.items():
        print(f"    {key}: {value:.2f}")

    print(f"\n  ✓ Hardware detection successful")

    print("=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)
