from app.api.schemas.user import UserResponse
from app.errors.exceptions import UserNotFoundError
from app.utils.unitofwork import IUnitOfWork


class UserService:

    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def get_user_by_id(self, id: int) -> UserResponse:
        async with self.uow as uow:
            user = await uow.user_repo.find_by_id(id)
            if not user:
                raise UserNotFoundError()

            return UserResponse.model_validate(user)
