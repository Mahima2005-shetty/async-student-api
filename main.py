from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from database import engine, Base, get_db
from schemas import (
    StudentCreate,
    StudentUpdate,
    StudentResponse
)

from repositories.student_repository import StudentRepository
from services.student_service import StudentService

from auth.routes import router as auth_router
from auth.dependencies import require_permission


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield


app = FastAPI(
    title="Async Student Management API",
    version="0.1.0",
    lifespan=lifespan
)


# Authentication routes
app.include_router(
    auth_router,
    tags=["Authentication"]
)


def get_student_service(
    db: AsyncSession = Depends(get_db)
):
    repository = StudentRepository(db)
    return StudentService(repository)


@app.get("/")
async def root():
    return {
        "message": "Async Student Management API is running"
    }


# GET ALL STUDENTS
@app.get(
    "/students",
    response_model=list[StudentResponse]
)
async def get_students(
    current_user=Depends(require_permission("student:read")),
    service: StudentService = Depends(get_student_service)
):
    return await service.get_students()


# CREATE STUDENT
@app.post(
    "/students",
    response_model=StudentResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_student(
    student: StudentCreate,
    current_user=Depends(require_permission("student:create")),
    service: StudentService = Depends(get_student_service)
):
    return await service.create_student(student)


# GET SINGLE STUDENT
@app.get(
    "/students/{student_id}",
    response_model=StudentResponse
)
async def get_student(
    student_id: int,
    current_user=Depends(require_permission("student:read")),
    service: StudentService = Depends(get_student_service)
):
    student = await service.get_student(student_id)

    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )

    return student


# UPDATE STUDENT
@app.put(
    "/students/{student_id}",
    response_model=StudentResponse
)
async def update_student(
    student_id: int,
    student: StudentUpdate,
    current_user=Depends(require_permission("student:update")),
    service: StudentService = Depends(get_student_service)
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

    return updated_student


# DELETE STUDENT
@app.delete(
    "/students/{student_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_student(
    student_id: int,
    current_user=Depends(require_permission("student:delete")),
    service: StudentService = Depends(get_student_service)
):
    deleted = await service.delete_student(student_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )

    return None