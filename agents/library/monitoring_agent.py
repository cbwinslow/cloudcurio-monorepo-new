#!/usr/bin/env python3
"""
Monitoring Agent for Stream Quality and System Health

This agent monitors stream quality, network traffic, and system health.
It collects, analyzes, and aggregates data in real-time.
"""

import os
import json
import logging
import time
import subprocess
from typing import Dict, List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/monitoring_agent.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('MonitoringAgent')


class MonitoringAgent:
    """Agent to monitor stream quality, network traffic, and system health."""

    def __init__(self, config_path: Optional[str] = None):
        """Initialize the MonitoringAgent with a configuration file."""
        self.config = self._load_config(config_path)
        self.base_dir = self.config.get('base_dir', os.getcwd())
        self.log_dir = os.path.join(self.base_dir, self.config.get('log_dir', 'logs'))
        self.interval = self.config.get('interval', 60)
        self.stream_urls = self.config.get('stream_urls', [])

        # Ensure log directory exists
        os.makedirs(self.log_dir, exist_ok=True)

    def _load_config(self, config_path: Optional[str]) -> Dict:
        """Load configuration from a JSON file."""
        default_config = {
            'base_dir': os.getcwd(),
            'log_dir': 'logs',
            'interval': 60,
            'stream_urls': [],
            'network_interfaces': ['eth0', 'wlan0'],
            'system_metrics': ['cpu', 'memory', 'disk']
        }

        if config_path and os.path.exists(config_path):
            with open(config_path, 'r') as f:
                user_config = json.load(f)
                default_config.update(user_config)

        return default_config

    def check_stream_quality(self) -> Dict[str, Dict]:
        """Check the quality of streams listed in the configuration."""
        results = {}

        for stream_url in self.stream_urls:
            stream_id = stream_url.split('/')[-1]
            # Placeholder for stream quality checks
            # This can be expanded to use tools like ffprobe to check stream quality
            results[stream_id] = {
                'url': stream_url,
                'status': 'unknown',
                'quality': 'unknown',
                'latency': 'unknown'
            }
            logger.info(f"Checking stream quality for {stream_url}")

        return results

    def check_network_traffic(self) -> Dict[str, Dict]:
        """Check the network traffic on specified interfaces."""
        results = {}

        for interface in self.config.get('network_interfaces', []):
            # Placeholder for network traffic checks
            # This can be expanded to use tools like iftop or nload to monitor network traffic
            results[interface] = {
                'rx_bytes': 0,
                'tx_bytes': 0,
                'rx_packets': 0,
                'tx_packets': 0
            }
            logger.info(f"Checking network traffic on {interface}")

        return results

    def check_system_health(self) -> Dict[str, Dict]:
        """Check the health of the system."""
        results = {}

        for metric in self.config.get('system_metrics', []):
            # Placeholder for system health checks
            # This can be expanded to use tools like top, vmstat, or iostat to monitor system health
            results[metric] = {
                'status': 'unknown',
                'value': 'unknown'
            }
            logger.info(f"Checking system health for {metric}")

        return results

    def log_metrics(self, metrics: Dict) -> None:
        """Log the collected metrics to a file."""
        timestamp = time.strftime('%Y-%m-%d_%H-%M-%S')
        log_file = os.path.join(self.log_dir, f'metrics_{timestamp}.json')

        with open(log_file, 'w') as f:
            json.dump(metrics, f, indent=2)

        logger.info(f"Metrics logged to {log_file}")

    def run_monitoring(self) -> None:
        """Run monitoring checks at specified intervals."""
        logger.info("Starting monitoring...")

        try:
            while True:
                metrics = {
                    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'stream_quality': self.check_stream_quality(),
                    'network_traffic': self.check_network_traffic(),
                    'system_health': self.check_system_health()
                }

                self.log_metrics(metrics)

                # Wait for the specified interval before running the next check
                time.sleep(self.interval)

        except KeyboardInterrupt:
            logger.info("Monitoring stopped by user.")


if __name__ == '__main__':
    # Example usage
    agent = MonitoringAgent('agents/config.json')
    agent.run_monitoring()
