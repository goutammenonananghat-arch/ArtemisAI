Artemis AI
=============

This repository contains utility modules for structured logging, metrics, and tracing.

* ``src/utils/logging.py`` configures JSON-formatted logs and automatically attaches
  OpenTelemetry trace context.
* ``src/metrics/prometheus.py`` exposes Prometheus metrics for request latency and
  error counts.
* ``src/tracing/opentelemetry.py`` sets up OpenTelemetry tracing with a console span
  exporter.

Install dependencies with ``pip install -r requirements.txt``.
