from typing import Dict

from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.schedulers.blocking import BlockingScheduler
from prometheus_client import CollectorRegistry

from collectors import COLLECTORS
from collectors.base_collector import BaseCollector
from config import CollectorConfig


class CollectorManager:
    """Manages all hardware collectors."""

    def __init__(
            self,
            registry: CollectorRegistry,
            config: CollectorConfig,
    ) -> None:
        self.registry = registry
        self.config = config
        self.collectors: Dict[str, BaseCollector] = {}

        self.scheduler = BlockingScheduler(
            executors={
                "default": ThreadPoolExecutor(max_workers=1),
            }
        )

    def initialize_collectors(self) -> None:
        """Initialize all enabled and available collectors."""
        for collector_name in self.config.enabled_collectors:
            collector_class = COLLECTORS[collector_name]
            collector = collector_class(self.registry)

            try:
                collector.initialize()
                self.collectors[collector_name] = collector
                print(f"Enabled collector: {collector_name}")
            except Exception as e:
                print(f"Failed to initialize {collector_name}: {e}")

    def collect_all(self) -> None:
        """Run collection for all active collectors."""
        for name, collector in self.collectors.items():
            try:
                collector.collect()
            except Exception as e:
                print(f"Error in {name} collector: {e}")

    def cleanup_all(self) -> None:
        """Cleanup all collectors."""
        for name, collector in self.collectors.items():
            try:
                collector.cleanup()
            except Exception as e:
                print(f"Error cleaning up {name}: {e}")

    def run_collection_loop(self) -> None:
        """Run the main collection loop using APScheduler."""
        interval = self.config.collect_interval
        print(f"Starting collection loop (interval: {interval}s)")

        self.scheduler.add_job(
            self.collect_all,
            trigger="interval",
            seconds=interval,
            max_instances=1,
            coalesce=True,
            id="collect_all",
        )

        try:
            self.scheduler.start()
        except KeyboardInterrupt:
            print("\nReceived interrupt signal")
        finally:
            self.scheduler.shutdown(wait=False)
            self.cleanup_all()
