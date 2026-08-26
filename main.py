from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from database import engine, Base, get_db
from schemas import (
    StudentCreate,
    StudentUpdate,
    StudentResponse
)

from services.student_service import StudentService


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(
            Base.metadata.create_all
        )

    yield


app = FastAPI(
    title="Async Student Management API",
    description="REST API built using FastAPI, Pydantic, SQLAlchemy and SQLite",
    version="1.0.0",
    lifespan=lifespan
)


student_service = StudentService()


@app.get("/")
async def root():
    return {
        "message": "Async Student API is running"
    }


@app.post(
    "/students",
    response_model=StudentResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_student(
    student: StudentCreate,
    db: AsyncSession = Depends(get_db)
):
    return await student_service.create_student(
        db,
        student
    )


@app.get(
    "/students",
    response_model=list[StudentResponse]
)
async def read_students(
    db: AsyncSession = Depends(get_db)
):
    return await student_service.get_students(
        db
    )


@app.get(
    "/students/{student_id}",
    response_model=StudentResponse
)
async def read_student(
    student_id: int,
    db: AsyncSession = Depends(get_db)
):
    student = await student_service.get_student(
        db,
        student_id
    )

    if student is None:
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
    db: AsyncSession = Depends(get_db)
):
    updated_student = await student_service.update_student(
        db,
        student_id,
        student
    )

    if updated_student is None:
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
    db: AsyncSession = Depends(get_db)
):
    deleted_student = await student_service.delete_student(
        db,
        student_id
    )

    if deleted_student is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )

    return None