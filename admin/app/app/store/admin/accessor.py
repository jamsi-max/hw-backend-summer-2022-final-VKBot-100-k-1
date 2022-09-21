from hashlib import sha256
import typing
from typing import Optional

from sqlalchemy import insert, select
from sqlalchemy.exc import IntegrityError

from app.admin.models import Admin, AdminModel
from app.base.base_accessor import BaseAccessor

if typing.TYPE_CHECKING:
    from app.web.app import Application


class AdminAccessor(BaseAccessor):
    async def connect(self, app: "Application"):
        await super().connect(app)
        # try:
        #     await self.create_admin(
        #         email=app.config.admin.email, password=app.config.admin.password
        #     )
        # except IntegrityError:
        #     pass

    async def get_by_email(self, email: str) -> Optional[Admin]:
        async with self.app.database.session() as s:
            result = (
                (
                    await s.execute(
                        select(AdminModel).where(AdminModel.email == email)
                    )
                )
                .scalars()
                .first()
            )
        if not result:
            return

        return (
            Admin(
                id=result.id,
                email=result.email,
                password=result.password)
        )

    # async def create_admin(self, email: str, password: str) -> Admin:
    #     new_admin = AdminModel(
    #         email=email,
    #         password=sha256(password.encode()).hexdigest()
    #     )
    #     async with self.app.database.session() as s:
    #         s.add(new_admin)
    #         await s.commit()
    #
    #     return Admin(id=new_admin.id, email=new_admin.email)
