import pytest
from fastapi import status

from tests.test_routers.auth.conftest import (
    get_edge_cases,
    get_invalid_emails,
    get_invalid_passwords,
    get_invalid_payload_cases,
    get_security_test_cases,
    get_valid_emails,
    get_valid_passwords,
)


@pytest.mark.asyncio
class TestUserRegistration:
    async def test_successful_registration(self, client, valid_user_payload):
        response = await client.post("/api/auth/register", json=valid_user_payload)
        assert response.status_code == status.HTTP_200_OK

        user_response = response.json()
        assert "id" in user_response
        assert "email" in user_response
        assert user_response["email"] == valid_user_payload["email"].lower()
        assert "role" in user_response
        assert user_response["role"].lower() == "user"
        assert "password" not in user_response

    @pytest.mark.parametrize("email, _", get_valid_emails())
    async def test_case_insensitive_email(self, client, email, _, valid_user_payload):
        payload = valid_user_payload.copy()
        payload["email"] = email
        response = await client.post("/api/auth/register", json=payload)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["email"] == email.lower()

    async def test_register_existing_user(
        self, client, valid_user_payload, existing_user
    ):
        response = await client.post("/api/auth/register", json=valid_user_payload)
        assert response.status_code == status.HTTP_409_CONFLICT

    @pytest.mark.parametrize("email, desc", get_invalid_emails())
    async def test_invalid_emails(self, client, email, desc, valid_user_payload):
        payload = valid_user_payload.copy()
        payload["email"] = email
        response = await client.post("/api/auth/register", json=payload)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.parametrize("password, desc", get_invalid_passwords())
    async def test_invalid_passwords(self, client, password, desc, valid_user_payload):
        payload = valid_user_payload.copy()
        payload["password"] = password
        response = await client.post("/api/auth/register", json=payload)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.parametrize("password, desc", get_valid_passwords())
    async def test_valid_passwords(self, client, password, desc, valid_user_payload):
        payload = valid_user_payload.copy()
        payload["password"] = password
        response = await client.post("/api/auth/register", json=payload)
        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.parametrize("email, password, desc", get_edge_cases())
    async def test_edge_cases(self, client, email, password, desc, valid_user_payload):
        payload = valid_user_payload.copy()
        payload.update({"email": email, "password": password})
        response = await client.post("/api/auth/register", json=payload)
        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.parametrize("field", ["email", "password"])
    @pytest.mark.parametrize("malicious_input, desc", get_security_test_cases())
    async def test_security(
        self, client, field, malicious_input, desc, valid_user_payload
    ):
        payload = valid_user_payload.copy()
        payload[field] = malicious_input
        response = await client.post("/api/auth/register", json=payload)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.parametrize("payload, desc", get_invalid_payload_cases())
    async def test_invalid_payload_structure(self, client, payload, desc):
        response = await client.post("/api/auth/register", json=payload)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
