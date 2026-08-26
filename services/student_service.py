from repositories.student_repository import StudentRepository
from schemas import StudentCreate, StudentUpdate
from models import Student


class StudentService:

    def __init__(self, repository: StudentRepository):
        self.repository = repository

    async def get_students(self):
        return await self.repository.get_all()

    async def get_student(self, student_id: int):
        return await self.repository.get_by_id(student_id)

    async def create_student(self, student: StudentCreate):
        db_student = Student(
            name=student.name,
            email=student.email,
            age=student.age
        )
        return await self.repository.create(db_student)

    async def update_student(self, student_id: int, student: StudentUpdate):
        db_student = await self.repository.get_by_id(student_id)

        if not db_student:
            return None

        if student.name is not None:
            db_student.name = student.name

        if student.email is not None:
            db_student.email = student.email

        if student.age is not None:
            db_student.age = student.age

        return await self.repository.update(db_student)

    async def delete_student(self, student_id: int):
        db_student = await self.repository.get_by_id(student_id)

        if not db_student:
            return None

        return await self.repository.delete(db_student)
