from contextlib import asynccontextmanager
import json

from fastapi import FastAPI, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession

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

from rate_limit.limiter import rate_limit


# ==============================
# APPLICATION LIFESPAN
# ==============================

@asynccontextmanager
async def lifespan(app: FastAPI):

    # Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Test Redis connection during startup
    try:
        await redis_client.ping()
        print("Redis connection successful!")
    except Exception as e:
        print(f"Redis connection failed: {e}")

    yield

    # Close Redis connection when application shuts down
    await redis_client.aclose()


# ==============================
# FASTAPI APPLICATION
# ==============================

app = FastAPI(
    title="Async Student Management API",
    version="0.1.0",
    lifespan=lifespan
)


# ==============================
# AUTHENTICATION ROUTES
# ==============================

app.include_router(
    auth_router,
    tags=["Authentication"]
)


# ==============================
# STUDENT SERVICE DEPENDENCY
# ==============================

def get_student_service(
    db: AsyncSession = Depends(get_db)
):
    repository = StudentRepository(db)
    return StudentService(repository)


# ==============================
# RATE LIMIT DEPENDENCIES
# ==============================

async def student_rate_limit(request: Request):
    return await rate_limit(
        request,
        limit=5,
        window=60
    )


async def create_student_rate_limit(request: Request):
    return await rate_limit(
        request,
        limit=3,
        window=60
    )


# ==============================
# ROOT ENDPOINT
# ==============================

@app.get("/")
async def root():
    return {
        "message": "Async Student Management API is running"
    }


# ==============================
# GET ALL STUDENTS
# ==============================

@app.get(
    "/students",
    response_model=list[StudentResponse]
)
async def get_students(
    current_user=Depends(
        require_permission("student:read")
    ),
    rate_limit_check=Depends(
        student_rate_limit
    ),
    service: StudentService = Depends(
        get_student_service
    )
):
    return await service.get_students()


# ==============================
# CREATE STUDENT
# ==============================

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
    rate_limit_check=Depends(
        create_student_rate_limit
    ),
    service: StudentService = Depends(
        get_student_service
    )
):
    return await service.create_student(student)


# ==============================
# GET SINGLE STUDENT
# REDIS CACHED
# ==============================

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

    # Redis cache key
    cache_key = f"student:{student_id}"

    # --------------------------------
    # 1. CHECK REDIS CACHE
    # --------------------------------

    cached_student = await redis_client.get(
        cache_key
    )

    if cached_student:

        print(
            f"REDIS CACHE HIT: {cache_key}"
        )

        return json.loads(cached_student)

    # --------------------------------
    # 2. CACHE MISS
    # --------------------------------

    print(
        f"REDIS CACHE MISS: {cache_key}"
    )

    # Get student from database
    student = await service.get_student(
        student_id
    )

    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )

    # --------------------------------
    # 3. CONVERT STUDENT TO DICTIONARY
    # --------------------------------

    student_data = {
        "id": student.id,
        "name": student.name,
        "email": student.email,
        "age": student.age
    }

    # --------------------------------
    # 4. STORE IN REDIS
    # --------------------------------

    await redis_client.set(
        cache_key,
        json.dumps(student_data),
        ex=CACHE_TTL
    )

    print(
        f"REDIS CACHE SET: {cache_key}"
    )

    # --------------------------------
    # 5. RETURN STUDENT
    # --------------------------------

    return student


# ==============================
# UPDATE STUDENT
# ==============================

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

    # --------------------------------
    # INVALIDATE REDIS CACHE
    # --------------------------------

    cache_key = f"student:{student_id}"

    await redis_client.delete(
        cache_key
    )

    print(
        f"REDIS CACHE INVALIDATED: {cache_key}"
    )

    return updated_student


# ==============================
# DELETE STUDENT
# ==============================

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

    # --------------------------------
    # INVALIDATE REDIS CACHE
    # --------------------------------

    cache_key = f"student:{student_id}"

    await redis_client.delete(
        cache_key
    )

    print(
        f"REDIS CACHE INVALIDATED: {cache_key}"
    )

    return None