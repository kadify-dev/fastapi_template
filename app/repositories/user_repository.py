import logging

from sqlalchemy import select

from app.db.models import User
from app.repositories.base_repository import SQLAlchemyRepository
from app.utils.logging_decorators import log_db_operation

logger = logging.getLogger(__name__)


class UserRepository(SQLAlchemyRepository):
    model = User

    @log_db_operation("Поиск пользователя по email")
    async def find_by_email(self, email):
        stmt = select(self.model).where(self.model.email == email)
        result = await self.session.execute(stmt)
        user = result.scalar_one_or_none()
        return user
