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


@app.get(
    "/students",
    response_model=list[StudentResponse]
)
async def get_students(
    service: StudentService = Depends(get_student_service)
):
    return await service.get_students()


@app.post(
    "/students",
    response_model=StudentResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_student(
    student: StudentCreate,
    service: StudentService = Depends(get_student_service)
):
    return await service.create_student(student)


@app.get(
    "/students/{student_id}",
    response_model=StudentResponse
)
async def get_student(
    student_id: int,
    service: StudentService = Depends(get_student_service)
):
    student = await service.get_student(student_id)

    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )

    return student


@app.put(
    "/students/{student_id}",
    response_model=StudentResponse
)
async def update_student(
    student_id: int,
    student: StudentUpdate,
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


@app.delete(
    "/students/{student_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_student(
    student_id: int,
    service: StudentService = Depends(get_student_service)
):
    deleted = await service.delete_student(student_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )

    return None
