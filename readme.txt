Artemis AI

Utilities for coordinating security sensitive operations.

## Alerting

Use ``src/alerts.py`` to route notifications to different channels::

    from alerts import send
    send("email", "Job complete")

The ``Scheduler`` and ``Orchestrator`` modules can both trigger alerts using
this function.
