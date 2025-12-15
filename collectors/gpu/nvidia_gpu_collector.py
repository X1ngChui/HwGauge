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


class NvidiaGPUCollector(GPUCollector):
    """Collector for NVIDIA GPU metrics using NVML."""

    def __init__(self, registry: CollectorRegistry) -> None:
        super().__init__(registry)
        self.gpu_count: int = 0

    def initialize(self) -> None:
        """Initialize NVML and create metrics. Raise exception on failure."""
        nvmlInit()
        self.gpu_count = nvmlDeviceGetCount()
        self.initialized = True
        print(f"Initialized NVIDIA GPU collector with {self.gpu_count} GPU(s)")

    def sample(self) -> Sequence[tuple[GPULabel, GPUMetrics]]:
        """Collect GPU metrics from all devices."""
        if not self.initialized:
            print("Sampling Nvidia GPU before initialization")
            return []

        samples: List[Tuple[GPULabel, GPUMetrics]] = []
        for index in range(self.gpu_count):
            handle = nvmlDeviceGetHandleByIndex(index)

            uuid = nvmlDeviceGetUUID(handle)
            name = nvmlDeviceGetName(handle)
            label = GPULabel(
                index=index,
                uuid=uuid,
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

            samples.append((label, metrics))
        return samples

    def cleanup(self) -> None:
        """Cleanup NVML resources."""
        if self.initialized:
            nvmlShutdown()
            self.initialized = False
