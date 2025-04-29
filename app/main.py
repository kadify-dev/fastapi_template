from fastapi import FastAPI

from app.api.routers.auth import auth_router
from app.api.routers.users import user_router
from app.core.logger import configure_logger
from app.errors.exceptions import BaseHTTPException
from app.errors.handlers import http_exception_handler, unexpected_exception_handler

configure_logger()

app = FastAPI()

app.add_exception_handler(BaseHTTPException, http_exception_handler)
app.add_exception_handler(Exception, unexpected_exception_handler)

app.include_router(auth_router)
app.include_router(user_router)
