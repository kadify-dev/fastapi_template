import logging

from sqlalchemy.exc import SQLAlchemyError

from app.errors.exceptions import DatabaseError

logger = logging.getLogger(__name__)


def log_db_operation(operation_name: str):
    def decorator(func):
        async def wrapper(self, *args, **kwargs):
            logger.debug(
                "Начало операции '%s'. Аргументы: args=%s, kwargs=%s",
                operation_name,
                args,
                kwargs,
            )
            try:
                result = await func(self, *args, **kwargs)
                logger.debug(
                    "Операция '%s' успешно завершена. Результат: %s",
                    operation_name,
                    result,
                )
                return result
            except SQLAlchemyError as e:
                logger.error(
                    "Ошибка базы данных при выполнении операции '%s'. "
                    "Аргументы: args=%s, kwargs=%s. Ошибка: %s",
                    operation_name,
                    args,
                    kwargs,
                    str(e),
                    exc_info=True,
                )
                raise DatabaseError(
                    detail=f"Ошибка при выполнении операции '{operation_name}': {str(e)}"
                )

        return wrapper

    return decorator
