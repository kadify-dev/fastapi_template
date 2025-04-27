from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from app.core.exceptions import DatabaseError
from app.db.models import User
from app.repositories.base_repository import SQLAlchemyRepository


class UserRepository(SQLAlchemyRepository):
    model = User

    async def find_by_email(self, email):
        try:
            stmt = select(self.model).where(self.model.email == email)
            result = await self.session.execute(stmt)
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            raise DatabaseError(
                detail=f"Failed to fetch user by email {email}: {str(e)}"
            )
