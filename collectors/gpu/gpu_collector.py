from abc import abstractmethod
from dataclasses import dataclass, astuple, fields
from typing import Sequence

from prometheus_client import CollectorRegistry, Gauge

from collectors import BaseCollector


@dataclass
class GPULabel:
    index: int
    uuid: str
    name: str

    @classmethod
    def label_names(cls) -> list[str]:
        return [f.name for f in fields(cls)]


@dataclass
class GPUMetrics:
    utilization: float
    frequency: float
    memory_usage: float
    temperature: float
    power_usage: float


class GPUCollector(BaseCollector):
    def __init__(self, registry: CollectorRegistry) -> None:
        super().__init__(registry)

        label_names = GPULabel.label_names()

        self.utilization = Gauge(
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

        self.gpu_memory_usage = Gauge(
            "gpu_memory_usage_bytes",
            "GPU memory used in bytes",
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

    @abstractmethod
    def sample(self) -> Sequence[tuple[GPULabel, GPUMetrics]]:
        """Sample GPU metrics."""
        pass

    def collect(self) -> None:
        """Collect hardware data and update metrics."""
        for (label, metrics) in self.sample():
            self.utilization.labels(*astuple(label)).set(metrics.utilization)
            self.gpu_frequency.labels(*astuple(label)).set(metrics.frequency)
            self.gpu_memory_usage.labels(*astuple(label)).set(metrics.memory_usage)
            self.gpu_temperature.labels(*astuple(label)).set(metrics.temperature)
            self.gpu_power_usage.labels(*astuple(label)).set(metrics.power_usage)
