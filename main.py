import argparse
import sys

from prometheus_client import CollectorRegistry, start_http_server

from collector_manager import CollectorManager
from config import load_config


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Hardware Prometheus Exporter"
    )
    parser.add_argument(
        "-c",
        "--config",
        default="config.toml",
        help="Path to configuration file (default: config.toml)",
    )
    return parser.parse_args()


def main() -> None:
    # Parse command line arguments
    args = parse_args()

    # Load configuration
    try:
        config = load_config(args.config)
    except Exception as exc:
        print(f"Failed to load config '{args.config}': {exc}", file=sys.stderr)
        sys.exit(1)

    # Create registry
    registry = CollectorRegistry(auto_describe=True)

    # Initialize collector manager
    manager = CollectorManager(registry, config.collector)
    manager.initialize_collectors()

    if not manager.collectors:
        print("Error: No collectors were initialized", file=sys.stderr)
        sys.exit(1)

    # Start HTTP server
    start_http_server(config.exporter.port, registry=registry)
    print(f"Exporter listening on port {config.exporter.port}")
    print(
        f"Metrics available at "
        f"http://localhost:{config.exporter.port}/metrics"
    )

    # Run collection loop
    manager.run_collection_loop()


if __name__ == "__main__":
    main()
