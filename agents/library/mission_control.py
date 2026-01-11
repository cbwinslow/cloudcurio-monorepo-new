#!/usr/bin/env python3
"""
Mission Control Center Dashboard

This script provides a web-based dashboard to view the status of all streams,
diagnostics, and alerts. It uses Flask to serve the dashboard.
"""

import os
import json
import logging
from flask import Flask, render_template, jsonify
from typing import Dict, List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/mission_control.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('MissionControl')


class MissionControl:
    """Mission Control Center Dashboard."""

    def __init__(self, config_path: Optional[str] = None):
        """Initialize the MissionControl with a configuration file."""
        self.config = self._load_config(config_path)
        self.base_dir = self.config.get('base_dir', os.getcwd())
        self.log_dir = os.path.join(self.base_dir, self.config.get('log_dir', 'logs'))
        self.app = Flask(__name__)

        # Ensure log directory exists
        os.makedirs(self.log_dir, exist_ok=True)

        # Set up Flask routes
        self._setup_routes()

    def _load_config(self, config_path: Optional[str]) -> Dict:
        """Load configuration from a JSON file."""
        default_config = {
            'base_dir': os.getcwd(),
            'log_dir': 'logs',
            'port': 5000,
            'host': '0.0.0.0'
        }

        if config_path and os.path.exists(config_path):
            with open(config_path, 'r') as f:
                user_config = json.load(f)
                default_config.update(user_config)

        return default_config

    def _setup_routes(self) -> None:
        """Set up Flask routes for the dashboard."""

        @self.app.route('/')
        def index():
            """Render the main dashboard page."""
            return render_template('index.html')

        @self.app.route('/api/status')
        def status():
            """Get the status of all streams, diagnostics, and alerts."""
            status_data = self._get_status_data()
            return jsonify(status_data)

        @self.app.route('/api/logs')
        def logs():
            """Get the logs from the monitoring and diagnostic agents."""
            log_files = self._get_log_files()
            return jsonify(log_files)

    def _get_status_data(self) -> Dict:
        """Get the status data for all streams, diagnostics, and alerts."""
        # Placeholder for status data
        # This can be expanded to load status data from files or databases
        status_data = {
            'streams': [],
            'diagnostics': [],
            'alerts': []
        }

        return status_data

    def _get_log_files(self) -> List[str]:
        """Get the list of log files from the log directory."""
        log_files = []

        if os.path.exists(self.log_dir):
            for file_name in os.listdir(self.log_dir):
                if file_name.endswith('.log'):
                    log_files.append(file_name)

        return log_files

    def run(self) -> None:
        """Run the Mission Control Center Dashboard."""
        logger.info("Starting Mission Control Center Dashboard...")

        # Create templates directory if it doesn't exist
        templates_dir = os.path.join(self.base_dir, 'templates')
        os.makedirs(templates_dir, exist_ok=True)

        # Create a simple HTML template for the dashboard
        self._create_template()

        # Run the Flask app
        self.app.run(
            host=self.config.get('host', '0.0.0.0'),
            port=self.config.get('port', 5000),
            debug=True
        )

    def _create_template(self) -> None:
        """Create a simple HTML template for the dashboard."""
        templates_dir = os.path.join(self.base_dir, 'templates')
        template_path = os.path.join(templates_dir, 'index.html')

        if not os.path.exists(template_path):
            with open(template_path, 'w') as f:
                f.write('''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mission Control Center</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f4f4f4;
        }
        .container {
            width: 80%;
            margin: 0 auto;
            padding: 20px;
        }
        h1 {
            text-align: center;
            color: #333;
        }
        .status-box {
            background-color: #fff;
            border-radius: 5px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            padding: 20px;
            margin-bottom: 20px;
        }
        .status-box h2 {
            margin-top: 0;
            color: #555;
        }
        .status-item {
            padding: 10px;
            border-bottom: 1px solid #eee;
        }
        .status-item:last-child {
            border-bottom: none;
        }
        .alert {
            background-color: #ffdddd;
            border-left: 5px solid #ff0000;
        }
        .ok {
            background-color: #ddffdd;
            border-left: 5px solid #00ff00;
        }
        .warning {
            background-color: #ffffdd;
            border-left: 5px solid #ffff00;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Mission Control Center</h1>
        <div class="status-box">
            <h2>Streams</h2>
            <div id="streams"></div>
        </div>
        <div class="status-box">
            <h2>Diagnostics</h2>
            <div id="diagnostics"></div>
        </div>
        <div class="status-box">
            <h2>Alerts</h2>
            <div id="alerts"></div>
        </div>
        <div class="status-box">
            <h2>Logs</h2>
            <div id="logs"></div>
        </div>
    </div>
    <script>
        // Fetch status data from the API
        fetch('/api/status')
            .then(response => response.json())
            .then(data => {
                // Update streams
                const streamsDiv = document.getElementById('streams');
                data.streams.forEach(stream => {
                    const streamDiv = document.createElement('div');
                    streamDiv.className = 'status-item ok';
                    streamDiv.innerHTML = `<strong>${stream.name}</strong>: ${stream.status}`;
                    streamsDiv.appendChild(streamDiv);
                });

                // Update diagnostics
                const diagnosticsDiv = document.getElementById('diagnostics');
                data.diagnostics.forEach(diagnostic => {
                    const diagnosticDiv = document.createElement('div');
                    diagnosticDiv.className = 'status-item ok';
                    diagnosticDiv.innerHTML = `<strong>${diagnostic.name}</strong>: ${diagnostic.status}`;
                    diagnosticsDiv.appendChild(diagnosticDiv);
                });

                // Update alerts
                const alertsDiv = document.getElementById('alerts');
                data.alerts.forEach(alert => {
                    const alertDiv = document.createElement('div');
                    alertDiv.className = 'status-item alert';
                    alertDiv.innerHTML = `<strong>${alert.name}</strong>: ${alert.message}`;
                    alertsDiv.appendChild(alertDiv);
                });
            });

        // Fetch log files from the API
        fetch('/api/logs')
            .then(response => response.json())
            .then(data => {
                const logsDiv = document.getElementById('logs');
                data.forEach(log => {
                    const logDiv = document.createElement('div');
                    logDiv.className = 'status-item';
                    logDiv.innerHTML = `<a href="/logs/${log}">${log}</a>`;
                    logsDiv.appendChild(logDiv);
                });
            });
    </script>
</body>
</html>
''')

            logger.info(f"Created template at {template_path}")


if __name__ == '__main__':
    # Example usage
    mission_control = MissionControl('agents/config.json')
    mission_control.run()
