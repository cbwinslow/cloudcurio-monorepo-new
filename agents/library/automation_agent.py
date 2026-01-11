#!/usr/bin/env python3
"""
Automation Agent for Diagnostic and Monitoring Tasks

This agent automates the execution of diagnostic and monitoring tasks.
It also implements alerting mechanisms for issues detected during monitoring.
"""

import os
import json
import logging
import subprocess
import time
from typing import Dict, List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/automation_agent.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('AutomationAgent')


class AutomationAgent:
    """Agent to automate the execution of diagnostic and monitoring tasks."""

    def __init__(self, config_path: Optional[str] = None):
        """Initialize the AutomationAgent with a configuration file."""
        self.config = self._load_config(config_path)
        self.base_dir = self.config.get('base_dir', os.getcwd())
        self.log_dir = os.path.join(self.base_dir, self.config.get('log_dir', 'logs'))
        self.diagnostic_interval = self.config.get('diagnostic_interval', 3600)
        self.monitoring_interval = self.config.get('monitoring_interval', 60)
        self.alert_thresholds = self.config.get('alert_thresholds', {})

        # Ensure log directory exists
        os.makedirs(self.log_dir, exist_ok=True)

    def _load_config(self, config_path: Optional[str]) -> Dict:
        """Load configuration from a JSON file."""
        default_config = {
            'base_dir': os.getcwd(),
            'log_dir': 'logs',
            'diagnostic_interval': 3600,
            'monitoring_interval': 60,
            'alert_thresholds': {
                'stream_quality': {'latency': 1000, 'quality': 'good'},
                'network_traffic': {'rx_bytes': 1000000, 'tx_bytes': 1000000},
                'system_health': {'cpu': 80, 'memory': 80, 'disk': 80}
            },
            'alert_methods': ['email', 'sms', 'slack']
        }

        if config_path and os.path.exists(config_path):
            with open(config_path, 'r') as f:
                user_config = json.load(f)
                default_config.update(user_config)

        return default_config

    def run_diagnostic_agent(self) -> None:
        """Run the diagnostic agent."""
        logger.info("Running diagnostic agent...")

        try:
            result = subprocess.run(
                ['python3', 'agents/diagnostic_agent.py'],
                cwd=self.base_dir,
                capture_output=True,
                text=True,
                check=True
            )

            logger.info("Diagnostic agent completed successfully.")
            logger.debug(f"Diagnostic agent output: {result.stdout}")

        except subprocess.CalledProcessError as e:
            logger.error(f"Diagnostic agent failed: {e}")
            logger.debug(f"Diagnostic agent error output: {e.stderr}")

    def run_monitoring_agent(self) -> None:
        """Run the monitoring agent."""
        logger.info("Running monitoring agent...")

        try:
            result = subprocess.run(
                ['python3', 'agents/monitoring_agent.py'],
                cwd=self.base_dir,
                capture_output=True,
                text=True,
                check=True
            )

            logger.info("Monitoring agent completed successfully.")
            logger.debug(f"Monitoring agent output: {result.stdout}")

        except subprocess.CalledProcessError as e:
            logger.error(f"Monitoring agent failed: {e}")
            logger.debug(f"Monitoring agent error output: {e.stderr}")

    def check_alerts(self, metrics: Dict) -> List[str]:
        """Check if any metrics exceed the alert thresholds."""
        alerts = []

        # Check stream quality alerts
        for stream_id, stream_metrics in metrics.get('stream_quality', {}).items():
            if stream_metrics.get('latency', 0) > self.alert_thresholds.get('stream_quality', {}).get('latency', 1000):
                alerts.append(f"High latency detected in stream {stream_id}: {stream_metrics.get('latency')}")
            if stream_metrics.get('quality', 'unknown') != self.alert_thresholds.get('stream_quality', {}).get('quality', 'good'):
                alerts.append(f"Poor quality detected in stream {stream_id}: {stream_metrics.get('quality')}")

        # Check network traffic alerts
        for interface, network_metrics in metrics.get('network_traffic', {}).items():
            if network_metrics.get('rx_bytes', 0) > self.alert_thresholds.get('network_traffic', {}).get('rx_bytes', 1000000):
                alerts.append(f"High incoming traffic on {interface}: {network_metrics.get('rx_bytes')}")
            if network_metrics.get('tx_bytes', 0) > self.alert_thresholds.get('network_traffic', {}).get('tx_bytes', 1000000):
                alerts.append(f"High outgoing traffic on {interface}: {network_metrics.get('tx_bytes')}")

        # Check system health alerts
        for metric, system_metrics in metrics.get('system_health', {}).items():
            if system_metrics.get('value', 0) > self.alert_thresholds.get('system_health', {}).get(metric, 80):
                alerts.append(f"High {metric} usage: {system_metrics.get('value')}")

        return alerts

    def send_alerts(self, alerts: List[str]) -> None:
        """Send alerts using the configured alert methods."""
        if not alerts:
            return

        logger.info(f"Sending {len(alerts)} alerts...")

        for alert in alerts:
            logger.warning(f"Alert: {alert}")

            # Placeholder for sending alerts via email, SMS, Slack, etc.
            # This can be expanded to use APIs or services for sending alerts
            for method in self.config.get('alert_methods', []):
                logger.info(f"Sending alert via {method}: {alert}")

    def run_automation(self) -> None:
        """Run automation tasks at specified intervals."""
        logger.info("Starting automation...")

        try:
            while True:
                # Run diagnostic agent at diagnostic interval
                self.run_diagnostic_agent()
                time.sleep(self.diagnostic_interval)

                # Run monitoring agent at monitoring interval
                self.run_monitoring_agent()

                # Check for alerts and send them
                # Placeholder for loading metrics from monitoring agent
                # This can be expanded to load metrics from a file or database
                metrics = {}
                alerts = self.check_alerts(metrics)
                self.send_alerts(alerts)

                # Wait for the monitoring interval before running the next check
                time.sleep(self.monitoring_interval)

        except KeyboardInterrupt:
            logger.info("Automation stopped by user.")


if __name__ == '__main__':
    # Example usage
    agent = AutomationAgent('agents/config.json')
    agent.run_automation()
