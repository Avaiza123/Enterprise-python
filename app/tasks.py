"""
Celery worker + scheduled/periodic tasks.
Demonstrates GitLab 'Scheduled Jobs' capability: a pipeline can be triggered
on a cron schedule (GitLab Schedules) to run housekeeping / health-check jobs,
independent of the always-on Celery beat schedule used at runtime.
"""

from celery import Celery

from app.config import settings

celery_app = Celery("enterprise_demo", broker=settings.celery_broker_url)

celery_app.conf.beat_schedule = {
    "health-check-every-5-minutes": {
        "task": "app.tasks.scheduled_health_check",
        "schedule": 300.0,
    },
}


@celery_app.task
def scheduled_health_check():
    # In real life: ping DB, check disk space, clean stale rows, etc.
    return {"status": "healthy"}


@celery_app.task
def cleanup_old_items():
    # Placeholder maintenance task, also runnable from a GitLab
    # scheduled pipeline via `python -m app.tasks cleanup`.
    return {"cleaned": 0}


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "cleanup":
        print(cleanup_old_items())
