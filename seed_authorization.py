import asyncio

from sqlalchemy import select, insert

from database import AsyncSessionLocal
from models import Role, Permission, role_permissions


PERMISSIONS = [
    "student:create",
    "student:read",
    "student:update",
    "student:delete",
]


ROLE_PERMISSIONS = {
    "admin": PERMISSIONS,
    "teacher": [
        "student:create",
        "student:read",
        "student:update",
    ],
    "student": [
        "student:read",
    ],
}


async def seed_authorization():
    async with AsyncSessionLocal() as db:

        permission_objects = {}

        for permission_name in PERMISSIONS:
            result = await db.execute(
                select(Permission).where(
                    Permission.name == permission_name
                )
            )

            permission = result.scalar_one_or_none()

            if not permission:
                permission = Permission(name=permission_name)
                db.add(permission)
                await db.flush()

            permission_objects[permission_name] = permission

        role_objects = {}

        for role_name in ROLE_PERMISSIONS:
            result = await db.execute(
                select(Role).where(
                    Role.name == role_name
                )
            )

            role = result.scalar_one_or_none()

            if not role:
                role = Role(name=role_name)
                db.add(role)
                await db.flush()

            role_objects[role_name] = role

        for role_name, permission_names in ROLE_PERMISSIONS.items():

            for permission_name in permission_names:

                existing = await db.execute(
                    select(role_permissions).where(
                        role_permissions.c.role_id
                        == role_objects[role_name].id,
                        role_permissions.c.permission_id
                        == permission_objects[permission_name].id
                    )
                )

                if existing.first() is None:
                    await db.execute(
                        insert(role_permissions).values(
                            role_id=role_objects[role_name].id,
                            permission_id=permission_objects[permission_name].id
                        )
                    )

        await db.commit()

        print("Roles and permissions seeded successfully!")


if __name__ == "__main__":
    asyncio.run(seed_authorization())
