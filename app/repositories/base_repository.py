import logging
from abc import ABC, abstractmethod

from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.utils.logging_decorators import log_db_operation

logger = logging.getLogger(__name__)


class AbstractRepository(ABC):

    @abstractmethod
    async def find_all(self):
        raise NotImplementedError

    @abstractmethod
    async def find_by_id(self, id: int):
        raise NotImplementedError

    @abstractmethod
    async def find_by_filters(self, **filters):
        raise NotImplementedError

    @abstractmethod
    async def create(self, data: dict):
        raise NotImplementedError

    @abstractmethod
    async def update(self, id: int, data: dict):
        raise NotImplementedError

    @abstractmethod
    async def delete(self, id: int) -> bool:
        raise NotImplementedError


class SQLAlchemyRepository(AbstractRepository):
    model = None

    def __init__(self, session: AsyncSession):
        self.session = session

    @log_db_operation("Получение всех записей")
    async def find_all(self):
        result = await self.session.execute(select(self.model))
        return result.scalars().all()

    @log_db_operation("Получение записи по ID")
    async def find_by_id(self, id: int):
        stmt = select(self.model).where(self.model.id == id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    @log_db_operation("Поиск записей по фильтрам")
    async def find_by_filters(self, **filters):
        stmt = select(self.model).filter_by(**filters)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    @log_db_operation("Создание новой записи")
    async def create(self, data: dict):
        stmt = insert(self.model).values(**data).returning(self.model)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    @log_db_operation("Обновление записи")
    async def update(self, id: int, data: dict):
        stmt = (
            update(self.model)
            .where(self.model.id == id)
            .values(**data)
            .returning(self.model)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    @log_db_operation("Удаление записи")
    async def delete(self, id: int):
        stmt = delete(self.model).where(self.model.id == id).returning(self.model.id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
