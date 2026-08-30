import time

from celery import Task

from .celery_app import celery_app


# ============================================================
# RETRY CONFIGURATION
# ============================================================

class RetryableTask(Task):

    autoretry_for = (
        ConnectionError,
        TimeoutError
    )

    retry_backoff = True

    retry_kwargs = {
        "max_retries": 3
    }


# ============================================================
# BACKGROUND JOB
# ============================================================

@celery_app.task(
    bind=True,
    base=RetryableTask
)
def process_background_job(
    self,
    job_data: str
):

    print(
        f"Starting background job: {job_data}"
    )

    # Simulate long-running task
    time.sleep(10)

    result = {

        "message":
            "Background job completed successfully",

        "input":
            job_data,

        "processed_by":
            "Celery Worker"
    }

    print(
        f"Completed background job: {job_data}"
    )

    return result