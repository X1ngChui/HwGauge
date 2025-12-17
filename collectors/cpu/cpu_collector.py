from abc import abstractmethod
from dataclasses import dataclass, astuple, fields
from typing import Sequence

from prometheus_client import CollectorRegistry, Gauge

from ..base_collector import BaseCollector


@dataclass
class CPULabel:
    socket: int

    @classmethod
    def label_names(cls) -> list[str]:
        return [f.name for f in fields(cls)]


@dataclass
class CPUMetrics:
    freq_hz: float
    ipc: float

    l2_hit_rate: float
    l3_hit_rate: float

    cpu_power_w: float
    dram_power_w: float

    mem_read_bps: float
    mem_write_bps: float
    mem_total_bps: float

    c0_residency: float
    c6_residency: float


class CPUCollector(BaseCollector):
    def __init__(self, registry: CollectorRegistry) -> None:
        super().__init__(registry)

        labels = CPULabel.label_names()

        self.cpu_frequency = Gauge(
            "cpu_frequency_hz",
            "CPU socket frequency in Hz",
            labels,
            registry=self.registry,
        )

        self.cpu_ipc = Gauge(
            "cpu_ipc",
            "CPU instructions per cycle",
            labels,
            registry=self.registry,
        )

        self.l2_hit_rate = Gauge(
            "cpu_l2_hit_rate_percent",
            "CPU L2 cache hit rate percentage",
            labels,
            registry=self.registry,
        )

        self.l3_hit_rate = Gauge(
            "cpu_l3_hit_rate_percent",
            "CPU L3 cache hit rate percentage",
            labels,
            registry=self.registry,
        )

        self.cpu_power = Gauge(
            "cpu_power_watts",
            "CPU package power consumption",
            labels,
            registry=self.registry,
        )

        self.dram_power = Gauge(
            "dram_power_watts",
            "DRAM power consumption",
            labels,
            registry=self.registry,
        )

        self.mem_read_bw = Gauge(
            "memory_read_bytes_per_second",
            "Memory read bandwidth",
            labels,
            registry=self.registry,
        )

        self.mem_write_bw = Gauge(
            "memory_write_bytes_per_second",
            "Memory write bandwidth",
            labels,
            registry=self.registry,
        )

        self.mem_total_bw = Gauge(
            "memory_total_bytes_per_second",
            "Memory total bandwidth",
            labels,
            registry=self.registry,
        )

        self.c0_residency = Gauge(
            "cpu_c0_residency_percent",
            "CPU C0 residency percentage",
            labels,
            registry=self.registry,
        )

        self.c6_residency = Gauge(
            "cpu_c6_residency_percent",
            "CPU C6 residency percentage",
            labels,
            registry=self.registry,
        )

        self._pcm = None

    @abstractmethod
    def sample(self) -> Sequence[tuple[CPULabel, CPUMetrics]]:
        """Sample CPU metrics."""
        pass

    def _collect(self) -> None:
        """Collect hardware data and update metrics."""
        assert self.initialized

        for label, m in self.sample():
            l = astuple(label)

            self.cpu_frequency.labels(*l).set(m.freq_hz)
            self.cpu_ipc.labels(*l).set(m.ipc)

            self.l2_hit_rate.labels(*l).set(m.l2_hit_rate)
            self.l3_hit_rate.labels(*l).set(m.l3_hit_rate)

            self.cpu_power.labels(*l).set(m.cpu_power_w)
            self.dram_power.labels(*l).set(m.dram_power_w)

            self.mem_read_bw.labels(*l).set(m.mem_read_bps)
            self.mem_write_bw.labels(*l).set(m.mem_write_bps)
            self.mem_total_bw.labels(*l).set(m.mem_total_bps)

            self.c0_residency.labels(*l).set(m.c0_residency)
            self.c6_residency.labels(*l).set(m.c6_residency)