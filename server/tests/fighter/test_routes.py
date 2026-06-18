import pytest

GATED_ROUTES: list[tuple[str, str]] = [
    ("GET", "/api/fighter/update-boxing-ranks"),
    ("GET", "/api/fighter/update-boxing-fight-cards"),
    ("POST", "/api/fighter/generate-avatars"),
]


@pytest.mark.asyncio
class TestScrapeRouteGating:
    @pytest.mark.parametrize("method,path", GATED_ROUTES)
    async def test_returns_401_without_auth(self, client, method: str, path: str) -> None:
        response = await client.request(method, path)
        assert response.status_code == 401

    @pytest.mark.parametrize("method,path", GATED_ROUTES)
    async def test_returns_403_for_non_superuser(self, auth_client, user_jwt, method: str, path: str) -> None:
        _, token = user_jwt
        response = await auth_client(token).request(method, path)
        assert response.status_code == 403


@pytest.mark.asyncio
class TestFeaturedRouteRemainsPublic:
    async def test_featured_no_auth_returns_200(self, client) -> None:
        response = await client.get("/api/fighter/featured")
        assert response.status_code == 200
