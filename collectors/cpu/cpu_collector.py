from abc import abstractmethod
from dataclasses import dataclass, astuple, fields
from typing import Sequence

from prometheus_client import CollectorRegistry, Gauge

from ..base_collector import BaseCollector


@dataclass
class CPULabel:
    index: int
    name: str

    @classmethod
    def label_names(cls) -> list[str]:
        return [f.name for f in fields(cls)]


@dataclass
class CPUMetrics:
    utilization: float
    frequency: float
    temperature: float
    power_usage: float


class CPUCollector(BaseCollector):
    def __init__(self, registry: CollectorRegistry) -> None:
        super().__init__(registry)

        label_names = CPULabel.label_names()

        self.utilization = Gauge(
            "cpu_utilization_percent",
            "CPU core utilization percentage",
            label_names,
            registry=self.registry,
        )

        self.cpu_frequency = Gauge(
            "cpu_frequency_hz",
            "CPU core frequency in Hz",
            label_names,
            registry=self.registry,
        )

        self.cpu_temperature = Gauge(
            "cpu_temperature_celsius",
            "CPU core temperature in Celsius",
            label_names,
            registry=self.registry,
        )

        self.cpu_power_usage = Gauge(
            "cpu_power_usage_watts",
            "CPU package power usage in watts",
            label_names,
            registry=self.registry,
        )

    @abstractmethod
    def sample(self) -> Sequence[tuple[CPULabel, CPUMetrics]]:
        """Sample CPU metrics."""
        pass

    def _collect(self) -> None:
        """Collect hardware data and update metrics."""
        assert self.initialized

        for (label, metrics) in self.sample():
            self.utilization.labels(*astuple(label)).set(metrics.utilization)
            self.cpu_frequency.labels(*astuple(label)).set(metrics.frequency)
            self.cpu_temperature.labels(*astuple(label)).set(metrics.temperature)
            self.cpu_power_usage.labels(*astuple(label)).set(metrics.power_usage)