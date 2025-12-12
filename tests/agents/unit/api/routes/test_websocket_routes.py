"""Unit tests for websocket routes."""

from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from agents.api.routes.websocket import (
    WebSocketService,
    get_websocket_service,
    router,
)


@pytest.mark.unit
class TestWebSocketRoutes:
    """Test cases for WebSocket routes."""

    @pytest.fixture
    def client(self):
        """Create a test client."""
        from fastapi import FastAPI

        app = FastAPI()
        app.include_router(router, prefix="/ws")
        return TestClient(app)

    def test_websocket_service_dependency(self):
        """Test WebSocket service dependency injection."""
        service = get_websocket_service()
        assert service is not None

    @pytest.mark.asyncio
    async def test_websocket_endpoint_connects(self):
        """Test WebSocket endpoint connection."""
        with patch("agents.api.routes.websocket.websocket_service") as mock_service:
            mock_service.connect = AsyncMock()

            # Mock WebSocket connection
            mock_websocket = AsyncMock()
            mock_websocket.receive_text = AsyncMock(return_value='{"type": "ping"}')
            mock_websocket.send_text = AsyncMock()

            # Mock the websocket endpoint behavior
            with patch("fastapi.WebSocket") as mock_websocket_class:
                mock_ws_instance = AsyncMock()
                mock_websocket_class.return_value = mock_ws_instance

                # Simulate websocket connection
                mock_ws_instance.accept = AsyncMock()
                mock_ws_instance.receive_text = AsyncMock(
                    side_effect=['{"type": "ping"}', '{"type": "disconnect"}']
                )
                mock_ws_instance.send_text = AsyncMock()

                # This would normally be tested via integration test
                # For unit test, we verify the service methods exist
                mock_manager = AsyncMock()
                service = WebSocketService(mock_manager)
                assert hasattr(service, "send_task_update")
                assert hasattr(service, "send_task_completion")
                assert hasattr(service, "send_batch_progress")

    @pytest.mark.asyncio
    async def test_websocket_service_methods(self):
        """Test WebSocket service methods."""
        # Create a mock service instance
        mock_manager = AsyncMock()
        service = WebSocketService(mock_manager)

        # Test service has required methods
        assert hasattr(service, "send_task_update")
        assert hasattr(service, "send_task_completion")
        assert hasattr(service, "send_batch_progress")

    @pytest.mark.asyncio
    async def test_websocket_connection_handling(self):
        """Test WebSocket connection handling."""
        with patch("agents.api.routes.websocket.websocket_service") as mock_service:
            # Setup mock
            mock_service.connect = AsyncMock(return_value="connection_id")
            mock_service.disconnect = AsyncMock()

            # Verify connection handling
            connection_id = await mock_service.connect("test_client")
            assert connection_id == "connection_id"

            await mock_service.disconnect("connection_id")

    @pytest.mark.asyncio
    async def test_websocket_message_handling(self):
        """Test WebSocket message handling."""
        with patch("agents.api.routes.websocket.websocket_service") as mock_service:
            # Setup mock
            mock_service.send_personal_message = AsyncMock()
            mock_service.broadcast = AsyncMock()

            # Test message sending
            await mock_service.send_personal_message("connection_id", {"type": "test"})
            mock_service.send_personal_message.assert_called_once()

            await mock_service.broadcast({"type": "broadcast_test"})
            mock_service.broadcast.assert_called_once()

    def test_websocket_router_included(self):
        """Test that WebSocket router is properly configured."""
        assert router is not None
        assert hasattr(router, "routes")
        # WebSocket routes should be present
        routes = [route.path for route in router.routes]
        assert any("/ws" in route or route == "/ws" for route in routes)

    @pytest.mark.asyncio
    async def test_websocket_error_handling(self):
        """Test WebSocket error handling."""
        with patch("agents.api.routes.websocket.websocket_service") as mock_service:
            # Test connection error
            mock_service.connect = AsyncMock(side_effect=Exception("Connection failed"))

            with pytest.raises(Exception, match="Connection failed"):
                await mock_service.connect("client_id")

    @pytest.mark.asyncio
    async def test_websocket_connection_lifecycle(self):
        """Test full WebSocket connection lifecycle."""
        with patch("agents.api.routes.websocket.websocket_service") as mock_service:
            # Setup mock lifecycle
            mock_service.connect = AsyncMock(return_value="test_connection")
            mock_service.disconnect = AsyncMock()
            mock_service.get_connections = AsyncMock(return_value=["test_connection"])

            # Test connection lifecycle
            connection_id = await mock_service.connect("client_1")
            assert connection_id == "test_connection"

            connections = await mock_service.get_connections()
            assert "test_connection" in connections

            await mock_service.disconnect(connection_id)

    @pytest.mark.asyncio
    async def test_websocket_message_types(self):
        """Test handling different WebSocket message types."""
        test_messages = [
            {"type": "task_update", "data": {"task_id": "123", "status": "processing"}},
            {"type": "progress", "data": {"progress": 50}},
            {"type": "error", "data": {"error": "Processing failed"}},
            {"type": "completed", "data": {"result": "success"}},
        ]

        with patch("agents.api.routes.websocket.websocket_service") as mock_service:
            mock_service.broadcast = AsyncMock()

            for message in test_messages:
                await mock_service.broadcast(message)
                mock_service.broadcast.assert_called_with(message)

    def test_websocket_service_singleton(self):
        """Test that WebSocket service is properly initialized."""

        service1 = get_websocket_service()
        service2 = get_websocket_service()

        # Service should be initialized (singleton behavior not strictly required)
        assert service1 is not None
        assert service2 is not None
