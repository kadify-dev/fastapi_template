from app.api.schemas.user import UserFromDB
from app.utils.unitofwork import IUnitOfWork


class UserService:

    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def get_user_by_id(self, id: int) -> UserFromDB:
        async with self.uow as uow:
            user_from_db = await uow.user_repo.find_by_id(id)
            return UserFromDB.model_validate(user_from_db)
