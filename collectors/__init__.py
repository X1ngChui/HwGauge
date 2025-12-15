from typing import Type

from .base_collector import BaseCollector
from collectors.gpu.nvidia_gpu_collector import NvidiaGPUCollector

# Import all collectors here
COLLECTORS: dict[str, Type[BaseCollector]] = {
    "nvidia_gpu_collector": NvidiaGPUCollector,
}
