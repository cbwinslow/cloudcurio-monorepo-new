"""Minimal 24/7 worker scaffold.

Design: poll a task source (GitHubFetcher) for tasks, process via Executor.
Start in `--propose-only` mode by default.
"""
from __future__ import annotations
import argparse
import logging
import os
import signal
import sys
import threading
import time
from dataclasses import dataclass
from typing import Any, Dict, List

logger = logging.getLogger('worker')
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
logger.addHandler(ch)

# Pluggable fetcher and executor
try:
    from agents.tasks.github_fetcher import GitHubFetcher
except Exception:
    GitHubFetcher = None  # for tests we can monkeypatch


@dataclass
class Task:
    id: str
    title: str
    body: str
    metadata: Dict[str, Any]


class Executor:
    def __init__(self, propose_only: bool = True):
        self.propose_only = propose_only

    def execute(self, task: Task) -> Dict[str, Any]:
        logger.info('Executor received task %s (propose_only=%s)', task.id, self.propose_only)
        # Default: simulate processing and return a result dict
        time.sleep(0.1)
        if self.propose_only:
            # In propose-only mode, return a proposed result without mutating remote state
            return {'status': 'proposed', 'task_id': task.id}
        else:
            # Execute real work here (subprocess, docker run, etc.)
            return {'status': 'completed', 'task_id': task.id}


class Worker:
    def __init__(self, fetcher=None, executor=None, poll_interval: float = 10.0, propose_only: bool = True):
        self.fetcher = fetcher or (GitHubFetcher() if GitHubFetcher else None)
        self.executor = executor or Executor(propose_only=propose_only)
        self.poll_interval = poll_interval
        self._stop = threading.Event()
        self._thread = None

    def run_once(self):
        logger.info('Worker run_once polling for tasks')
        tasks: List[Task] = []
        if self.fetcher:
            raw = self.fetcher.fetch_tasks()
            for r in raw:
                tasks.append(Task(id=str(r.get('id')), title=r.get('title', ''), body=r.get('body', ''), metadata=r))
        else:
            logger.debug('No fetcher configured; nothing to do')
        results = []
        for t in tasks:
            res = self.executor.execute(t)
            logger.info('Task %s processed -> %s', t.id, res.get('status'))
            results.append((t, res))
        return results

    def start(self):
        logger.info('Starting worker loop (poll_interval=%s)', self.poll_interval)
        self._stop.clear()
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def _loop(self):
        while not self._stop.is_set():
            try:
                self.run_once()
            except Exception:
                logger.exception('Error in worker run_once')
            self._stop.wait(self.poll_interval)

    def stop(self):
        logger.info('Stopping worker')
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=5)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--poll', type=float, default=10.0)
    p.add_argument('--propose-only', action='store_true', default=True)
    p.add_argument('--run-once', action='store_true', default=False)
    args = p.parse_args()

    worker = Worker(poll_interval=args.poll, propose_only=args.propose_only)

    def _sigterm(signum, frame):
        logger.info('Received signal %s, stopping', signum)
        worker.stop()
        sys.exit(0)

    signal.signal(signal.SIGTERM, _sigterm)
    signal.signal(signal.SIGINT, _sigterm)

    if args.run_once:
        worker.run_once()
    else:
        worker.start()
        # wait forever
        while True:
            time.sleep(60)


if __name__ == '__main__':
    main()
