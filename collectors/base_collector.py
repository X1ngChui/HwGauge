from abc import ABC, abstractmethod

from prometheus_client import CollectorRegistry


class BaseCollector(ABC):
    """Abstract base class for all hardware collectors."""

    def __init__(self, registry: CollectorRegistry) -> None:
        self.registry = registry
        self.initialized = False

    @abstractmethod
    def initialize(self) -> None:
        """Initialize the hardware interface and metrics."""
        pass

    @abstractmethod
    def cleanup(self) -> None:
        """Clean up resources."""
        pass

    @property
    def name(self) -> str:
        """Return the collector name."""
        return self.__class__.__name__

    @abstractmethod
    def collect(self) -> None:
        """Collect hardware data and update metrics."""
        pass