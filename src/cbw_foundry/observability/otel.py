from __future__ import annotations

import os
from collections.abc import Iterator
from contextlib import contextmanager


def _env_bool(name: str, default: str = "0") -> bool:
    return str(os.getenv(name, default)).strip().lower() in {"1", "true", "yes", "on"}


@contextmanager
def maybe_otel_span(name: str) -> Iterator[None]:
    if not _env_bool("ENABLE_OTEL", "0"):
        yield
        return
    try:
        from opentelemetry import trace  # type: ignore

        tracer = trace.get_tracer(__name__)
        with tracer.start_as_current_span(name):
            yield
    except Exception:
        yield
