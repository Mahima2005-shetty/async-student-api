from sqlalchemy.ext.asyncio import AsyncSession

from schemas import StudentCreate, StudentUpdate
from repositories.student_repository import StudentRepository


class StudentService:

    def __init__(self):
        self.repository = StudentRepository()

    async def create_student(
        self,
        db: AsyncSession,
        student_data: StudentCreate
    ):
        return await self.repository.create_student(
            db,
            student_data
        )

    async def get_student(
        self,
        db: AsyncSession,
        student_id: int
    ):
        return await self.repository.get(
            db,
            student_id
        )

    async def get_students(
        self,
        db: AsyncSession
    ):
        return await self.repository.get_all(db)

    async def update_student(
        self,
        db: AsyncSession,
        student_id: int,
        student_data: StudentUpdate
    ):
        student = await self.repository.get(
            db,
            student_id
        )

        if not student:
            return None

        return await self.repository.update_student(
            db,
            student,
            student_data
        )

    async def delete_student(
        self,
        db: AsyncSession,
        student_id: int
    ):
        student = await self.repository.get(
            db,
            student_id
        )

        if not student:
            return None

        await self.repository.delete(db, student)

        return student