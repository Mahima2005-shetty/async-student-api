from contextlib import asynccontextmanager
import asyncio
import json

from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from database import engine, Base, get_db

from schemas import (
    StudentCreate,
    StudentUpdate,
    StudentResponse
)

from repositories.student_repository import StudentRepository
from services.student_service import StudentService

from redis_client import redis_client, CACHE_TTL

from auth.routes import router as auth_router
from auth.dependencies import require_permission


# ============================================================
# DAY 7 - CELERY IMPORTS
# ============================================================

from celery.result import AsyncResult

from background_tasks.celery_app import celery_app
from background_tasks.tasks import process_background_job


# ============================================================
# TASK 9 - EVENT-DRIVEN NOTIFICATION IMPORTS
# ============================================================

from events.consumer import consume_events
from events.producer import publish_event


# ============================================================
# APPLICATION LIFESPAN
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI):

    # --------------------------------------------------------
    # Create database tables
    # --------------------------------------------------------

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # --------------------------------------------------------
    # Test Redis connection during startup
    # --------------------------------------------------------

    try:
        await redis_client.ping()
        print("Redis connection successful!")

    except Exception as e:
        print(f"Redis connection failed: {e}")

    # --------------------------------------------------------
    # TASK 9 - START EVENT CONSUMER
    # --------------------------------------------------------

    consumer_task = asyncio.create_task(
        consume_events(redis_client)
    )

    print("Event consumer task started!")

    try:

        yield

    finally:

        # ----------------------------------------------------
        # STOP EVENT CONSUMER
        # ----------------------------------------------------

        consumer_task.cancel()

        try:
            await consumer_task

        except asyncio.CancelledError:
            print("Event consumer stopped.")

        # ----------------------------------------------------
        # CLOSE REDIS CONNECTION
        # ----------------------------------------------------

        await redis_client.aclose()


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="Async Student Management API",
    version="0.1.0",
    lifespan=lifespan
)


# ============================================================
# AUTHENTICATION ROUTES
# ============================================================

app.include_router(
    auth_router,
    tags=["Authentication"]
)


# ============================================================
# STUDENT SERVICE DEPENDENCY
# ============================================================

def get_student_service(
    db: AsyncSession = Depends(get_db)
):

    repository = StudentRepository(db)

    return StudentService(repository)


# ============================================================
# ROOT ENDPOINT
# ============================================================

@app.get("/")
async def root():

    return {
        "message": "Async Student Management API is running"
    }


# ============================================================
# GET ALL STUDENTS
# ============================================================

@app.get(
    "/students",
    response_model=list[StudentResponse]
)
async def get_students(

    current_user=Depends(
        require_permission("student:read")
    ),

    service: StudentService = Depends(
        get_student_service
    )
):

    return await service.get_students()


# ============================================================
# CREATE STUDENT
# ============================================================

@app.post(
    "/students",
    response_model=StudentResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_student(

    student: StudentCreate,

    current_user=Depends(
        require_permission("student:create")
    ),

    service: StudentService = Depends(
        get_student_service
    )
):

    return await service.create_student(student)


# ============================================================
# GET SINGLE STUDENT
# REDIS CACHED
# ============================================================

@app.get(
    "/students/{student_id}",
    response_model=StudentResponse
)
async def get_student(

    student_id: int,

    current_user=Depends(
        require_permission("student:read")
    ),

    service: StudentService = Depends(
        get_student_service
    )
):

    # --------------------------------------------------------
    # Redis cache key
    # --------------------------------------------------------

    cache_key = f"student:{student_id}"

    # --------------------------------------------------------
    # CHECK REDIS CACHE
    # --------------------------------------------------------

    cached_student = await redis_client.get(
        cache_key
    )

    if cached_student:

        print(
            f"REDIS CACHE HIT: {cache_key}"
        )

        return json.loads(cached_student)

    # --------------------------------------------------------
    # CACHE MISS
    # --------------------------------------------------------

    print(
        f"REDIS CACHE MISS: {cache_key}"
    )

    student = await service.get_student(
        student_id
    )

    if not student:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )

    # --------------------------------------------------------
    # CONVERT STUDENT TO DICTIONARY
    # --------------------------------------------------------

    student_data = {

        "id": student.id,

        "name": student.name,

        "email": student.email,

        "age": student.age
    }

    # --------------------------------------------------------
    # STORE IN REDIS
    # --------------------------------------------------------

    await redis_client.set(
        cache_key,
        json.dumps(student_data),
        ex=CACHE_TTL
    )

    print(
        f"REDIS CACHE SET: {cache_key}"
    )

    # --------------------------------------------------------
    # RETURN STUDENT
    # --------------------------------------------------------

    return student


# ============================================================
# UPDATE STUDENT
# ============================================================

@app.put(
    "/students/{student_id}",
    response_model=StudentResponse
)
async def update_student(

    student_id: int,

    student: StudentUpdate,

    current_user=Depends(
        require_permission("student:update")
    ),

    service: StudentService = Depends(
        get_student_service
    )
):

    updated_student = await service.update_student(
        student_id,
        student
    )

    if not updated_student:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )

    # --------------------------------------------------------
    # INVALIDATE REDIS CACHE
    # --------------------------------------------------------

    cache_key = f"student:{student_id}"

    await redis_client.delete(
        cache_key
    )

    print(
        f"REDIS CACHE INVALIDATED: {cache_key}"
    )

    return updated_student


# ============================================================
# DELETE STUDENT
# ============================================================

@app.delete(
    "/students/{student_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_student(

    student_id: int,

    current_user=Depends(
        require_permission("student:delete")
    ),

    service: StudentService = Depends(
        get_student_service
    )
):

    deleted = await service.delete_student(
        student_id
    )

    if not deleted:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )

    # --------------------------------------------------------
    # INVALIDATE REDIS CACHE
    # --------------------------------------------------------

    cache_key = f"student:{student_id}"

    await redis_client.delete(
        cache_key
    )

    print(
        f"REDIS CACHE INVALIDATED: {cache_key}"
    )

    return None


# ============================================================
# DAY 7 - BACKGROUND JOB MODEL
# ============================================================

class JobRequest(BaseModel):

    job_data: str


# ============================================================
# DAY 7 - SUBMIT BACKGROUND JOB
# ============================================================

@app.post(
    "/jobs",
    tags=["Background Jobs"]
)
async def submit_job(
    request: JobRequest
):

    # --------------------------------------------------------
    # Send task to Celery / Redis queue
    # --------------------------------------------------------

    task = process_background_job.delay(
        request.job_data
    )

    # --------------------------------------------------------
    # Return immediately
    # --------------------------------------------------------

    return {

        "message": "Job submitted successfully",

        "task_id": task.id,

        "status": "PENDING"
    }


# ============================================================
# DAY 7 - JOB STATUS
# ============================================================

@app.get(
    "/jobs/{task_id}",
    tags=["Background Jobs"]
)
async def get_job_status(
    task_id: str
):

    # --------------------------------------------------------
    # Get Celery task result
    # --------------------------------------------------------

    result = AsyncResult(
        task_id,
        app=celery_app
    )

    # --------------------------------------------------------
    # Basic response
    # --------------------------------------------------------

    response = {

        "task_id": task_id,

        "status": result.status
    }

    # --------------------------------------------------------
    # SUCCESS
    # --------------------------------------------------------

    if result.successful():

        response["result"] = result.result

    # --------------------------------------------------------
    # FAILURE
    # --------------------------------------------------------

    elif result.failed():

        response["error"] = str(
            result.result
        )

    return response


# ============================================================
# TASK 9 - EVENT REQUEST MODEL
# ============================================================

class EventRequest(BaseModel):

    event_type: str

    user_id: int

    data: dict = {}

    event_id: str | None = None


# ============================================================
# TASK 9 - EVENT PRODUCER
# ============================================================

@app.post(
    "/events",
    tags=["Event-Driven Notifications"]
)
async def create_event(
    event: EventRequest
):

    result = await publish_event(
        redis=redis_client,
        event_type=event.event_type,
        user_id=event.user_id,
        data=event.data,
        event_id=event.event_id
    )

    return result