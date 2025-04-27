from abc import ABC, abstractmethod

from sqlalchemy import delete, insert, select, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.errors.exceptions import DatabaseError, UserNotFoundError


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

    async def find_all(self):
        try:
            result = await self.session.execute(select(self.model))
            return result.scalars().all()
        except SQLAlchemyError as e:
            raise DatabaseError(detail=f"Failed to fetch all records: {str(e)}")

    async def find_by_id(self, id: int):
        try:
            stmt = select(self.model).where(self.model.id == id)
            result = await self.session.execute(stmt)
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            raise DatabaseError(detail=f"Failed to fetch record by id {id}: {str(e)}")

    async def find_by_filters(self, **filters):
        try:
            stmt = select(self.model).filter_by(**filters)
            result = await self.session.execute(stmt)
            return result.scalars().all()
        except SQLAlchemyError as e:
            raise DatabaseError(detail=f"Failed to fetch records by filters: {str(e)}")

    async def create(self, data: dict):
        try:
            stmt = insert(self.model).values(**data).returning(self.model)
            result = await self.session.execute(stmt)
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            raise DatabaseError(detail=f"Failed to create record: {str(e)}")

    async def update(self, id: int, data: dict):
        try:
            stmt = (
                update(self.model)
                .where(self.model.id == id)
                .values(**data)
                .returning(self.model)
            )
            result = await self.session.execute(stmt)
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            raise DatabaseError(detail=f"Failed to update record {id}: {str(e)}")

    async def delete(self, id: int) -> bool:
        try:
            stmt = (
                delete(self.model).where(self.model.id == id).returning(self.model.id)
            )
            result = await self.session.execute(stmt)
            if result.scalar_one_or_none() is None:
                raise UserNotFoundError(detail=f"Record with id {id} not found")
            return True
        except SQLAlchemyError as e:
            raise DatabaseError(detail=f"Failed to delete record {id}: {str(e)}")
