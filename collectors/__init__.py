from typing import Type

from collectors.base import BaseCollector
from collectors.gpu_nvidia import NvidiaGPUCollector

# Import all collectors here
COLLECTORS: dict[str, Type[BaseCollector]] = {
    "gpu_nvidia": NvidiaGPUCollector,
}
