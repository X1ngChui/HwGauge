import logging
from typing import Dict

from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.schedulers.blocking import BlockingScheduler
from prometheus_client import CollectorRegistry

from collectors import COLLECTORS
from collectors.base_collector import BaseCollector
from config import CollectorConfig

logger = logging.getLogger(__name__)


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
                logger.info(f"Enabled collector: {collector_name}")
            except Exception as e:
                logger.error(f"Failed to initialize {collector_name}: {e}")

    def collect_all(self) -> None:
        """Run collection for all active collectors."""
        for name, collector in self.collectors.items():
            try:
                logger.info(f"Collecting {name}")
                collector.collect()
            except Exception as e:
                logger.error(f"Error in {name} collector: {e}")

    def cleanup_all(self) -> None:
        """Cleanup all collectors."""
        for name, collector in self.collectors.items():
            try:
                logger.info(f"Cleaning up {name}")
                collector.cleanup()
            except Exception as e:
                logger.error(f"Error cleaning up {name}: {e}")

    def run_collection_loop(self) -> None:
        """Run the main collection loop using APScheduler."""
        interval = self.config.collect_interval
        logger.info(f"Starting collection loop (interval: {interval}s)")

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
            logger.info("Received interrupt signal")
        finally:
            self.scheduler.shutdown(wait=False)
            self.cleanup_all()
