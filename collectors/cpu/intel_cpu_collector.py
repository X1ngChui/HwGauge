# intel_cpu_collector.py
from dataclasses import dataclass, astuple, fields
from typing import Sequence, Tuple

from prometheus_client import CollectorRegistry, Gauge

from .cpu_collector import CPUCollector, CPULabel, CPUMetrics
from . import pcm_binding

# =========================
# Collector
# =========================

class IntelCPUCollector(CPUCollector):
    def __init__(self, registry: CollectorRegistry) -> None:
        super().__init__(registry)

    def _initialize(self) -> None:
        self._pcm = pcm_binding.PCMWrapper()

    def _cleanup(self) -> None:
        # 如果 pcm_binding 有 close / cleanup 接口可以在这里调用
        self._pcm = None

    # =========================
    # Sampling
    # =========================

    def sample(self) -> Sequence[Tuple[CPULabel, CPUMetrics]]:
        assert self._pcm is not None

        results = []
        metrics = self._pcm.sample()

        for m in metrics:
            label = CPULabel(socket=m.socket)
            data = CPUMetrics(
                freq_hz=m.freq_hz,
                ipc=m.ipc,
                l2_hit_rate=m.l2_hit_rate,
                l3_hit_rate=m.l3_hit_rate,
                cpu_power_w=m.cpu_power_w,
                dram_power_w=m.dram_power_w,
                mem_read_bps=m.mem_read_bps,
                mem_write_bps=m.mem_write_bps,
                mem_total_bps=m.mem_total_bps,
                c0_residency=m.c0_residency,
                c6_residency=m.c6_residency,
            )
            results.append((label, data))

        return results
