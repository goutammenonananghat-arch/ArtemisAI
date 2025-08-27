Artemis AI
===========

This project now includes a simple persistent job scheduler built on
APScheduler.  Use ``schedule`` to queue tasks and ``cancel`` to remove them.
Jobs are stored in ``logs/jobs.sqlite`` so scheduled reminders persist across
restarts.
