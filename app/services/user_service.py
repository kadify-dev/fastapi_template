from app.api.schemas.user import UserFromDB
from app.errors.exceptions import UserNotFoundError
from app.utils.unitofwork import IUnitOfWork


class UserService:

    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def get_user_by_id(self, id: int) -> UserFromDB:
        async with self.uow as uow:
            user_from_db = await uow.user_repo.find_by_id(id)
            if not user_from_db:
                raise UserNotFoundError()

            return UserFromDB.model_validate(user_from_db)
