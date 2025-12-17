import argparse
import logging
import sys

from prometheus_client import CollectorRegistry, start_http_server

from collector_manager import CollectorManager
from config import load_config, LoggingConfig


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Hardware Prometheus Exporter"
    )
    parser.add_argument(
        "-c", "--config",
        default="config.toml",
        help="Path to configuration file (default: config.toml)",
    )
    return parser.parse_args()


def configure_logging(log_config: LoggingConfig) -> logging.Logger:
    logging.basicConfig(
        level=log_config.level,
        format=log_config.format,
        stream=sys.stdout
    )
    return logging.getLogger("main")


def main() -> None:
    # Parse command line arguments
    args = parse_args()

    # Load configuration
    try:
        config = load_config(args.config)
    except Exception:
        return

    logger = configure_logging(config.logging)

    # Create registry
    registry = CollectorRegistry(auto_describe=True)

    # Initialize collector manager
    manager = CollectorManager(registry, config.collector)
    manager.initialize_collectors()

    # Start HTTP server
    start_http_server(config.exporter.port, registry=registry)
    logger.info(f"Collector started on port {config.exporter.port}")
    logger.info(
        f"Metrics available at "
        f"http://localhost:{config.exporter.port}/metrics"
    )

    # Run collection loop
    manager.run_collection_loop()


if __name__ == "__main__":
    main()
