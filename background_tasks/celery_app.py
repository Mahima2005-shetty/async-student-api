from celery import Celery


# ============================================================
# REDIS CONFIGURATION
# ============================================================

REDIS_URL = "redis://localhost:6379/0"


# ============================================================
# CELERY APPLICATION
# ============================================================

celery_app = Celery(

    "background_tasks",

    broker=REDIS_URL,

    backend=REDIS_URL,

    include=[
        "background_tasks.tasks"
    ]
)


# ============================================================
# CELERY CONFIGURATION
# ============================================================

celery_app.conf.update(

    task_serializer="json",

    accept_content=[
        "json"
    ],

    result_serializer="json",

    result_expires=3600,

    timezone="Asia/Kolkata",

    enable_utc=False,
)