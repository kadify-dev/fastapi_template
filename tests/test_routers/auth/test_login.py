import pytest
from fastapi import status

from tests.test_routers.auth.conftest import (
    get_invalid_emails,
    get_invalid_passwords,
    get_invalid_payload_cases,
    get_security_test_cases,
)


@pytest.mark.asyncio
class TestUserLogin:
    async def test_successful_login(self, client, valid_login_payload, existing_user):
        response = await client.post("/api/auth/login", json=valid_login_payload)
        assert response.status_code == status.HTTP_200_OK

        token_response = response.json()
        assert "access_token" in token_response
        assert "refresh_token" in token_response
        assert "token_type" in token_response
        assert token_response["token_type"].lower() == "bearer"
        assert isinstance(token_response["access_token"], str)
        assert isinstance(token_response["refresh_token"], str)
        assert len(token_response["access_token"]) > 0
        assert len(token_response["refresh_token"]) > 0

    async def test_login_nonexistent_user(self, client, valid_login_payload):
        response = await client.post("/api/auth/login", json=valid_login_payload)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_login_wrong_password(
        self, client, valid_login_payload, existing_user
    ):
        payload = valid_login_payload.copy()
        payload["password"] = "Wrong_password123"
        response = await client.post("/api/auth/login", json=payload)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.parametrize("email, desc", get_invalid_emails())
    async def test_invalid_emails(self, client, email, desc, valid_login_payload):
        payload = valid_login_payload.copy()
        payload["email"] = email
        response = await client.post("/api/auth/login", json=payload)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.parametrize("password, desc", get_invalid_passwords())
    async def test_invalid_passwords(self, client, password, desc, valid_login_payload):
        payload = valid_login_payload.copy()
        payload["password"] = password
        response = await client.post("/api/auth/login", json=payload)
        assert response.status_code in (
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            status.HTTP_401_UNAUTHORIZED,
        )

    @pytest.mark.parametrize("field", ["email", "password"])
    @pytest.mark.parametrize("malicious_input, desc", get_security_test_cases())
    async def test_security(
        self, client, field, malicious_input, desc, valid_login_payload
    ):
        payload = valid_login_payload.copy()
        payload[field] = malicious_input
        response = await client.post("/api/auth/login", json=payload)
        assert response.status_code in (
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            status.HTTP_401_UNAUTHORIZED,
        )

    @pytest.mark.parametrize("payload, desc", get_invalid_payload_cases())
    async def test_invalid_payload_structure(self, client, payload, desc):
        response = await client.post("/api/auth/login", json=payload)
        assert response.status_code in (
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            status.HTTP_401_UNAUTHORIZED,
        )

    async def test_case_insensitive_email(
        self, client, existing_user, valid_login_payload
    ):
        payload = valid_login_payload.copy()
        payload["email"] = payload["email"].upper()
        response = await client.post("/api/auth/login", json=payload)
        assert response.status_code == status.HTTP_200_OK
