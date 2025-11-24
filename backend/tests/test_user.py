from __future__ import annotations

import pytest
from httpx import AsyncClient
from core.security import create_access_token
from datetime import timedelta


@pytest.mark.asyncio
async def test_get_current_user(client: AsyncClient, test_user) -> None:
    """Тест получения текущего пользователя."""
    token = create_access_token(
        data={"id": str(test_user.id)},
        expires_delta=timedelta(minutes=15),
    )

    response = await client.get(
        "/api/user/",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["username"] == "testuser"


@pytest.mark.asyncio
async def test_get_current_user_unauthorized(client: AsyncClient) -> None:
    """Тест получения пользователя без токена."""
    response = await client.get("/api/user/")
    assert response.status_code == 403
