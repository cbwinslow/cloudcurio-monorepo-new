"""Simple health server and metrics integration for the worker."""
import json
import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Dict, Any

from prometheus_client import Gauge, start_http_server

_worker_uptime = Gauge('jcs_worker_uptime_seconds', 'Worker uptime in seconds')


class _HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            resp = self.server.health_info()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(resp).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        # suppress default logging
        return


class HealthServer:
    def __init__(self, host='0.0.0.0', port=0):
        self._host = host
        self._port = port
        self._server = None
        self._thread = None
        self._start_time = time.time()

    def health_info(self) -> Dict[str, Any]:
        uptime = time.time() - self._start_time
        _worker_uptime.set(uptime)
        return {'status': 'ok', 'uptime_seconds': uptime}

    def start(self):
        # start prometheus metrics on default port 8001 (non-blocking)
        try:
            start_http_server(8001)
        except Exception:
            pass
        # start a simple HTTP server for /health
        def serve():
            server = HTTPServer((self._host, self._port), _HealthHandler)
            # attach helper
            server.health_info = self.health_info
            self._server = server
            server.serve_forever()

        self._thread = threading.Thread(target=serve, daemon=True)
        self._thread.start()

    def stop(self):
        if self._server:
            self._server.shutdown()
            self._server.server_close()
        if self._thread:
            self._thread.join(timeout=2)
