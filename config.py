import tomllib
from dataclasses import dataclass, field
from typing import List

from collectors import COLLECTORS


@dataclass
class ExporterConfig:
    port: int = 8000


@dataclass
class CollectorConfig:
    collect_interval: float = 5.0
    enabled_collectors: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not set(self.enabled_collectors).issubset(COLLECTORS.keys()):
            invalid = set(self.enabled_collectors) - COLLECTORS.keys()
            raise ValueError(
                f"Invalid collectors in config: {sorted(invalid)}. "
            )


@dataclass
class AppConfig:
    exporter: ExporterConfig
    collector: CollectorConfig


def load_config(path: str) -> AppConfig:
    with open(path, "rb") as f:
        raw = tomllib.load(f)

    return AppConfig(
        exporter=ExporterConfig(**raw.get("exporter", {})),
        collector=CollectorConfig(**raw.get("collector", {})),
    )
