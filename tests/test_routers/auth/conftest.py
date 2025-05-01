import jwt
import pytest
from passlib.context import CryptContext

from app.core.config import settings
from app.db.models import User
from app.services.auth_service import AuthService

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


@pytest.fixture
def valid_user_data():
    return {"email": "valid@example.com", "password": "Strong_p@ss123"}


@pytest.fixture
def valid_user_payload(valid_user_data):
    return valid_user_data.copy()


@pytest.fixture
def valid_login_data(valid_user_data):
    return {"email": valid_user_data["email"], "password": valid_user_data["password"]}


@pytest.fixture
def valid_login_payload(valid_login_data):
    return valid_login_data.copy()


@pytest.fixture
def original_password(valid_user_data):
    return valid_user_data["password"]


@pytest.fixture
async def existing_user(session, valid_user_data):
    from app.db.models import User

    user = User(
        email=valid_user_data["email"],
        hashed_password=get_password_hash(valid_user_data["password"]),
    )
    session.add(user)
    await session.commit()
    return user


@pytest.fixture
def expired_refresh_token(user_with_refresh_token):
    """Фикстура для создания истёкшего токена"""
    user, _ = user_with_refresh_token
    expired_token = jwt.encode(
        {"sub": str(user.id), "exp": 1},
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )
    return expired_token


@pytest.fixture
def valid_refresh_token_payload():
    return {"refresh_token": "valid.refresh.token"}


@pytest.fixture
async def user_with_refresh_token(session, valid_refresh_token_payload):

    auth_service = AuthService(session)
    user = User(email="user@example.com", hashed_password="hashed_password")
    session.add(user)
    await session.commit()
    await session.refresh(user)

    refresh_token = auth_service.create_refresh_token(str(user.id))
    return user, refresh_token


def get_invalid_emails():
    return [
        ("", "пустая строка"),
        ("user @example.com", "пробел внутри"),
        ("user.example.com", "отсутствует @"),
        ("user@@example.com", "двойной @"),
        ("@example.com", "@ в начале"),
        ("user@", "@ в конце"),
        (".user@example.com", "точка в начале"),
        ("user.@example.com", "точка в конце"),
        ("user..name@example.com", "двойные точки"),
        ("user name@example.com", "пробел в имени"),
        ("user@example", "нет точки в домене"),
        ("user@.example.com", "точка в начале домена"),
        ("user@example.com.", "точка в конце домена"),
        ("user@example..com", "двойные точки в домене"),
        ("user@[127.0.0.1]", "IP-адрес"),
    ]


def get_valid_emails():
    return [
        ("user@example.com", "базовый"),
        ("user123@example.com", "с цифрами"),
        ("user.name@example.com", "с точкой"),
        ("user+tag@example.com", "с плюсом"),
        ("user-name@example.com", "с дефисом"),
        ("user_name@example.com", "с подчеркиванием"),
        ("user@sub.example.com", "поддомен"),
        ("user@example.co.uk", "многоуровневый домен"),
        ("юзер@example.com", "кириллица в имени"),
        ("user@example.ру", "кириллица в домене"),
    ]


def get_invalid_passwords():
    return [
        ("", "пустой"),
        ("a", "слишком короткий"),
        ("1234567", "7 символов"),
        ("a" * 65, "слишком длинный"),
        ("12345678", "только цифры"),
        ("abcdefgh", "только буквы"),
        ("ABCDEFGH", "только заглавные"),
        ("!@#$%^&*", "только символы"),
        ("Password", "без цифр"),
        ("1234!@#$", "без букв"),
        ("пароль123", "кириллица"),
        ("pass word", "пробел внутри"),
        (" password ", "пробелы вокруг"),
    ]


def get_valid_passwords():
    return [
        ("Strong_p@ss123", "стандартный"),
        ("A1b2@C3#d4$E5%", "сложный"),
        ("a" * 63 + "1", "максимальная длина"),
    ]


def get_edge_cases():
    return [
        ("a" * 64 + "@example.com", "ValidPass123!", "максимальная длина email"),
        ("user@example.com", "a" * 63 + "1", "максимальная длина пароля"),
        ("üser@exämple.com", "ValidPass123!", "unicode в email"),
        ("USER@EXAMPLE.COM", "ValidPass123!", "email в верхнем регистре"),
        ("user@example.com", "PaSsWoRd!1", "пароль с разным регистром"),
    ]


def get_security_test_cases():
    return [
        ("' OR 1=1 --", "SQL инъекция 1"),
        ("'; DROP TABLE users;", "SQL инъекция 2"),
        ("admin'--", "SQL комментарий"),
        ("' UNION SELECT * FROM users --", "SQL union"),
        ("<img src=x onerror=alert(1)>", "XSS"),
        ("{{7*7}}", "инъекция в шаблоны"),
        ("admin@example.com\r\nX-Injected: header", "инъекция заголовков"),
        ("\r\n\r\nGET / HTTP/1.1", "инъекция HTTP запроса"),
    ]


def get_invalid_payload_cases():
    return [
        ({"password": "12345678"}, "только пароль"),
        ({"email": "user@example.com"}, "только email"),
        ({}, "пустой payload"),
        (
            {"email": "user@example.com", "password": "12345678", "name": "John"},
            "лишнее поле",
        ),
        ({"email": 123, "password": "12345678"}, "email как число"),
        ({"email": "user@example.com", "password": 123}, "пароль как число"),
        ({"email": None, "password": "12345678"}, "email None"),
        ({"email": "user@example.com", "password": None}, "пароль None"),
        ({"email": ["user@example.com"], "password": "12345678"}, "email как список"),
        (
            {"email": "user@example.com", "password": {"value": "123"}},
            "пароль как словарь",
        ),
        ("not a json", "не JSON"),
        (42, "число вместо JSON"),
        (["user@example.com", "12345678"], "список вместо объекта"),
    ]


def get_invalid_refresh_tokens():
    return [
        ("", "пустая строка"),
        ("invalid.token", "невалидный токен"),
        ("<script>alert(1)</script>", "XSS инъекция"),
        ("' OR 1=1 --", "SQL инъекция"),
        ("..\\..\\..\\windows\\win.ini", "инъекция пути"),
        ("a" * 1001, "слишком длинный токен"),
    ]


def get_invalid_refresh_payload_cases():
    return [
        ({}, "пустой payload"),
        ({"token": "some.token"}, "неправильное имя поля"),
        ({"refresh_token": 123}, "токен как число"),
        ({"refresh_token": None}, "токен None"),
        ({"refresh_token": {"value": "some.token"}}, "токен как словарь"),
        ("not a json", "не JSON"),
        (42, "число вместо JSON"),
        (["some.token"], "список вместо объекта"),
    ]
