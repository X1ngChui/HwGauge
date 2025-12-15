from typing import Optional

from prometheus_client import Gauge, CollectorRegistry
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
    NVMLError,
)

from collectors.base import BaseCollector


class NvidiaGPUCollector(BaseCollector):
    """Collector for NVIDIA GPU metrics using NVML."""

    def __init__(self, registry: CollectorRegistry) -> None:
        super().__init__(registry)
        self.gpu_count: int = 0

        # Metrics
        self.gpu_utilization: Optional[Gauge] = None
        self.gpu_frequency: Optional[Gauge] = None
        self.gpu_memory_used: Optional[Gauge] = None
        self.gpu_memory_total: Optional[Gauge] = None
        self.gpu_temperature: Optional[Gauge] = None
        self.gpu_power_usage: Optional[Gauge] = None

    def initialize(self) -> None:
        """Initialize NVML and create metrics. Raise exception on failure."""
        try:
            nvmlInit()
            self.gpu_count = nvmlDeviceGetCount()

            if self.gpu_count <= 0:
                raise RuntimeError("No NVIDIA GPU detected")

            label_names = ["gpu_index", "gpu_uuid", "gpu_name"]

            self.gpu_utilization = Gauge(
                "gpu_utilization_percent",
                "GPU utilization percentage",
                label_names,
                registry=self.registry,
            )

            self.gpu_frequency = Gauge(
                "gpu_frequency_hz",
                "GPU frequency hz",
                label_names,
                registry=self.registry,
            )

            self.gpu_memory_used = Gauge(
                "gpu_memory_used_bytes",
                "GPU memory used in bytes",
                label_names,
                registry=self.registry,
            )

            self.gpu_memory_total = Gauge(
                "gpu_memory_total_bytes",
                "GPU memory total in bytes",
                label_names,
                registry=self.registry,
            )

            self.gpu_temperature = Gauge(
                "gpu_temperature_celsius",
                "GPU temperature in Celsius",
                label_names,
                registry=self.registry,
            )

            self.gpu_power_usage = Gauge(
                "gpu_power_usage_watts",
                "GPU power usage in watts",
                label_names,
                registry=self.registry,
            )

            self._initialized = True
            print(f"Initialized NVIDIA GPU collector with {self.gpu_count} GPU(s)")

        except (NVMLError, Exception) as e:
            try:
                nvmlShutdown()
            except Exception:
                pass
            raise RuntimeError(f"Failed to initialize NVIDIA GPU collector: {e}") from e

    def collect(self) -> None:
        """Collect GPU metrics from all devices."""
        if not self._initialized:
            return

        try:
            for i in range(self.gpu_count):
                handle = nvmlDeviceGetHandleByIndex(i)

                gpu_uuid = nvmlDeviceGetUUID(handle)
                gpu_name = nvmlDeviceGetName(handle)

                util = nvmlDeviceGetUtilizationRates(handle)
                freq = nvmlDeviceGetClockInfo(handle, NVML_CLOCK_SM) * 1e6  # MHz -> Hz
                mem = nvmlDeviceGetMemoryInfo(handle)
                temp = nvmlDeviceGetTemperature(handle, NVML_TEMPERATURE_GPU)
                power = nvmlDeviceGetPowerUsage(handle) / 1000.0  # mW -> W

                labels = (str(i), gpu_uuid, gpu_name)
                self.gpu_utilization.labels(*labels).set(util.gpu)
                self.gpu_frequency.labels(*labels).set(freq)
                self.gpu_memory_used.labels(*labels).set(mem.used)
                self.gpu_memory_total.labels(*labels).set(mem.total)
                self.gpu_temperature.labels(*labels).set(temp)
                self.gpu_power_usage.labels(*labels).set(power)

        except NVMLError as e:
            print(f"Error collecting GPU metrics: {e}")

    def cleanup(self) -> None:
        """Cleanup NVML resources."""
        if self._initialized:
            try:
                nvmlShutdown()
                self._initialized = False
                print("NVIDIA GPU collector cleaned up")
            except NVMLError as e:
                print(f"Error during NVML shutdown: {e}")
