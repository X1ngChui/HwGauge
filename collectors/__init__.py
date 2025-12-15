from typing import Type, Dict

from collectors.gpu.nvidia_gpu_collector import NvidiaGPUCollector
from .base_collector import BaseCollector

# Import all collectors here
COLLECTORS: Dict[str, Type[BaseCollector]] = {
    "nvidia_gpu_collector": NvidiaGPUCollector,
}
