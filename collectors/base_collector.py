from abc import ABC, abstractmethod

from prometheus_client import CollectorRegistry


class BaseCollector(ABC):
    """Abstract base class for all hardware collectors."""

    def __init__(self, registry: CollectorRegistry) -> None:
        self.registry = registry
        self.initialized = False

    @abstractmethod
    def _initialize(self) -> None:
        """Initialize the hardware interface and metrics."""
        pass

    def initialize(self) -> None:
        """Initialize the hardware interface and metrics."""
        self._initialize()
        self.initialized = True

    @abstractmethod
    def _cleanup(self) -> None:
        """Clean up resources."""
        pass

    def cleanup(self) -> None:
        if self.initialized:
            self._cleanup()
            self.initialized = False

    @abstractmethod
    def _collect(self) -> None:
        """Collect hardware data and update metrics."""
        pass

    def collect(self) -> None:
        """Collect hardware data and update metrics."""
        assert self.initialized, "Collector must be initialized before collecting data"
        self._collect()

    @property
    def name(self) -> str:
        """Return the collector name."""
        return self.__class__.__name__
