import logging
from typing import List, Tuple, Sequence

from prometheus_client import CollectorRegistry
from pynvml import (
    nvmlInit,
    nvmlShutdown,
    nvmlDeviceGetCount,
    nvmlDeviceGetHandleByIndex,
    nvmlDeviceGetUUID,
    nvmlDeviceGetName,
    nvmlDeviceGetUtilizationRates,
    nvmlDeviceGetClockInfo,
    nvmlDeviceGetMemoryInfo,
    nvmlDeviceGetTemperature,
    nvmlDeviceGetPowerUsage,
    NVML_TEMPERATURE_GPU,
    NVML_CLOCK_SM,
)

from collectors.gpu.gpu_collector import GPUCollector, GPULabel, GPUMetrics


logger = logging.getLogger(__name__)

class NvidiaGPUCollector(GPUCollector):
    """Collector for NVIDIA GPU metrics using NVML."""

    def __init__(self, registry: CollectorRegistry) -> None:
        super().__init__(registry)
        self.gpu_count: int = 0

    def _initialize(self) -> None:
        """Initialize NVML and create metrics. Raise exception on failure."""
        nvmlInit()
        self.gpu_count = nvmlDeviceGetCount()
        logger.info(f"Initialized NVIDIA GPU collector with {self.gpu_count} GPU(s)")

    def sample(self) -> Sequence[tuple[GPULabel, GPUMetrics]]:
        """Collect GPU metrics from all devices."""
        collections: List[Tuple[GPULabel, GPUMetrics]] = []
        for index in range(self.gpu_count):
            handle = nvmlDeviceGetHandleByIndex(index)

            name = nvmlDeviceGetName(handle)
            label = GPULabel(
                index=index,
                name=name,
            )

            utilization = nvmlDeviceGetUtilizationRates(handle).gpu
            frequency = nvmlDeviceGetClockInfo(handle, NVML_CLOCK_SM) * 1e6  # MHz -> Hz
            memory_usage = nvmlDeviceGetMemoryInfo(handle).used
            temperature = nvmlDeviceGetTemperature(handle, NVML_TEMPERATURE_GPU)
            power_usage = nvmlDeviceGetPowerUsage(handle) / 1e3  # mW -> W

            metrics = GPUMetrics(
                utilization=utilization,
                frequency=frequency,
                memory_usage=memory_usage,
                temperature=temperature,
                power_usage=power_usage,
            )

            collections.append((label, metrics))
        return collections

    def _cleanup(self) -> None:
        """Cleanup NVML resources."""
        nvmlShutdown()
