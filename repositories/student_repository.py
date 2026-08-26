from sqlalchemy.ext.asyncio import AsyncSession

from models import Student
from schemas import StudentCreate, StudentUpdate
from .repository import Repository


class StudentRepository(Repository[Student]):

    def __init__(self):
        super().__init__(Student)

    async def create_student(
        self,
        db: AsyncSession,
        student_data: StudentCreate
    ):
        student = Student(**student_data.model_dump())
        return await self.create(db, student)

    async def update_student(
        self,
        db: AsyncSession,
        student: Student,
        student_data: StudentUpdate
    ):
        update_data = student_data.model_dump(exclude_unset=True)

        for key, value in update_data.items():
            setattr(student, key, value)

        await db.commit()
        await db.refresh(student)

        return student