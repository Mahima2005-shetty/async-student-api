from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import Student
from schemas import StudentCreate, StudentUpdate


async def create_student(
    db: AsyncSession,
    student_data: StudentCreate
):
    student = Student(
        name=student_data.name,
        email=student_data.email,
        age=student_data.age
    )

    db.add(student)

    await db.commit()
    await db.refresh(student)

    return student


async def get_students(db: AsyncSession):
    result = await db.execute(
        select(Student)
    )

    return result.scalars().all()


async def get_student(
    db: AsyncSession,
    student_id: int
):
    result = await db.execute(
        select(Student).where(
            Student.id == student_id
        )
    )

    return result.scalar_one_or_none()


async def update_student(
    db: AsyncSession,
    student_id: int,
    student_data: StudentUpdate
):
    student = await get_student(db, student_id)

    if student is None:
        return None

    student.name = student_data.name
    student.email = student_data.email
    student.age = student_data.age

    await db.commit()
    await db.refresh(student)

    return student


async def delete_student(
    db: AsyncSession,
    student_id: int
):
    student = await get_student(db, student_id)

    if student is None:
        return None

    await db.delete(student)
    await db.commit()

    return student