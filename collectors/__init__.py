from typing import Type, Dict

from .gpu.nvidia_gpu_collector import NvidiaGPUCollector
from .base_collector import BaseCollector
# from .cpu.intel_cpu_collector import IntelCPUCollector

# Import all collectors here
COLLECTORS: Dict[str, Type[BaseCollector]] = {
    # "intel_cpu_collector": IntelCPUCollector,
    "nvidia_gpu_collector": NvidiaGPUCollector,
}
