import pytest
from fastapi import status

from tests.test_routers.auth.conftest import (
    get_invalid_refresh_payload_cases,
    get_invalid_refresh_tokens,
)


@pytest.mark.asyncio
class TestRefreshToken:
    async def test_successful_refresh(self, client, user_with_refresh_token):
        _, refresh_token = user_with_refresh_token
        payload = {"refresh_token": refresh_token}
        response = await client.post("/api/auth/refresh", json=payload)

        assert response.status_code == status.HTTP_200_OK
        token_response = response.json()
        assert "access_token" in token_response
        assert isinstance(token_response["access_token"], str)
        assert len(token_response["access_token"]) > 0

    async def test_expired_refresh_token(self, client, expired_refresh_token):
        payload = {"refresh_token": expired_refresh_token}
        response = await client.post("/api/auth/refresh", json=payload)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.parametrize("refresh_token, desc", get_invalid_refresh_tokens())
    async def test_invalid_refresh_tokens(self, client, refresh_token, desc):
        payload = {"refresh_token": refresh_token}
        response = await client.post("/api/auth/refresh", json=payload)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.parametrize("payload, desc", get_invalid_refresh_payload_cases())
    async def test_invalid_payload_structure(self, client, payload, desc):
        response = await client.post("/api/auth/refresh", json=payload)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
