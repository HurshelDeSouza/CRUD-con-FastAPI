import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestMiddleware:
    """Tests para middleware"""
    
    async def test_timing_middleware_adds_header(self, client: AsyncClient):
        """Test que TimingMiddleware agrega header X-Process-Time"""
        response = await client.get("/")
        
        assert "X-Process-Time" in response.headers
        process_time = float(response.headers["X-Process-Time"])
        assert process_time > 0
        assert process_time < 1  # Debería ser menos de 1 segundo
    
    async def test_timing_middleware_on_all_endpoints(self, client: AsyncClient):
        """Test que el middleware se aplica a todos los endpoints"""
        endpoints = [
            "/",
            "/health",
            "/posts",
        ]
        
        for endpoint in endpoints:
            response = await client.get(endpoint)
            assert "X-Process-Time" in response.headers
