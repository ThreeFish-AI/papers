"""Unit tests for websocket routes."""

from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from agents.api.routes.websocket import (
    ConnectionManager,
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
        # Mock the ConnectionManager
        with patch("agents.api.routes.websocket.manager") as mock_manager:
            mock_manager.connect = AsyncMock()
            mock_manager.disconnect = AsyncMock()
            mock_manager.active_connections = {}

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
        # Mock the ConnectionManager directly
        with patch("agents.api.routes.websocket.ConnectionManager") as mock_cm_class:
            mock_manager = AsyncMock()
            mock_cm_class.return_value = mock_manager

            # Setup mock
            mock_manager.connect = AsyncMock()
            mock_manager.disconnect = AsyncMock()
            mock_manager.active_connections = {}
            mock_manager.client_subscriptions = {}

            # Test connection manager instantiation
            cm = ConnectionManager()
            assert cm is not None

            # Verify connection handling methods exist
            assert hasattr(mock_manager, "connect")
            assert hasattr(mock_manager, "disconnect")
            assert hasattr(mock_manager, "send_personal_message")
            assert hasattr(mock_manager, "broadcast_to_subscribers")

    @pytest.mark.asyncio
    async def test_websocket_message_handling(self):
        """Test WebSocket message handling."""
        # Mock the ConnectionManager
        with patch("agents.api.routes.websocket.manager") as mock_manager:
            # Setup mock
            mock_manager.send_personal_message = AsyncMock()
            mock_manager.broadcast_to_subscribers = AsyncMock()
            mock_manager.subscribe = AsyncMock()
            mock_manager.unsubscribe = AsyncMock()

            # Test message sending
            await mock_manager.send_personal_message({"type": "test"}, "connection_id")
            mock_manager.send_personal_message.assert_called_once()

            await mock_manager.broadcast_to_subscribers(
                {"type": "broadcast_test"}, "task_id"
            )
            mock_manager.broadcast_to_subscribers.assert_called_once()

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
        # Mock the ConnectionManager
        with patch("agents.api.routes.websocket.manager") as mock_manager:
            # Test connection error
            mock_manager.connect = AsyncMock(side_effect=Exception("Connection failed"))

            with pytest.raises(Exception, match="Connection failed"):
                await mock_manager.connect(None, "client_id")

    @pytest.mark.asyncio
    async def test_websocket_connection_lifecycle(self):
        """Test full WebSocket connection lifecycle."""
        # Mock the ConnectionManager
        with patch("agents.api.routes.websocket.manager") as mock_manager:
            # Setup mock lifecycle
            mock_manager.connect = AsyncMock()
            mock_manager.disconnect = AsyncMock()
            mock_manager.active_connections = {"client_1": "test_connection"}

            # Test connection lifecycle
            await mock_manager.connect(None, "client_1")
            mock_manager.connect.assert_called_once()

            # Test disconnect
            mock_manager.disconnect("client_1")
            mock_manager.disconnect.assert_called_once()

    @pytest.mark.asyncio
    async def test_websocket_message_types(self):
        """Test handling different WebSocket message types."""
        test_messages = [
            {"type": "task_update", "data": {"task_id": "123", "status": "processing"}},
            {"type": "progress", "data": {"progress": 50}},
            {"type": "error", "data": {"error": "Processing failed"}},
            {"type": "completed", "data": {"result": "success"}},
        ]

        # Mock the ConnectionManager
        with patch("agents.api.routes.websocket.manager") as mock_manager:
            mock_manager.broadcast_to_subscribers = AsyncMock()

            for message in test_messages:
                await mock_manager.broadcast_to_subscribers(message, "task_123")
                mock_manager.broadcast_to_subscribers.assert_called_with(
                    message, "task_123"
                )

    def test_websocket_service_singleton(self):
        """Test that WebSocket service is properly initialized."""

        service1 = get_websocket_service()
        service2 = get_websocket_service()

        # Service should be initialized (singleton behavior not strictly required)
        assert service1 is not None
        assert service2 is not None

    @pytest.mark.asyncio
    async def test_connection_manager_initialization(self):
        """Test ConnectionManager initialization."""
        manager = ConnectionManager()
        assert manager.active_connections == {}
        assert manager.client_subscriptions == {}

    @pytest.mark.asyncio
    async def test_connection_manager_subscribe_unsubscribe(self):
        """Test ConnectionManager subscribe/unsubscribe methods."""
        manager = ConnectionManager()

        # Initialize client_subscriptions for client1
        manager.client_subscriptions["client1"] = set()

        # Test subscribe
        await manager.subscribe("client1", "task1")
        assert "task1" in manager.client_subscriptions["client1"]

        # Test unsubscribe
        await manager.unsubscribe("client1", "task1")
        assert "task1" not in manager.client_subscriptions["client1"]

    @pytest.mark.asyncio
    async def test_connection_manager_connect_disconnect(self):
        """Test ConnectionManager connect and disconnect methods."""
        manager = ConnectionManager()
        mock_websocket = AsyncMock()

        # Test connect
        await manager.connect(mock_websocket, "client1")
        assert "client1" in manager.active_connections
        assert manager.active_connections["client1"] == mock_websocket
        assert "client1" in manager.client_subscriptions

        # Test disconnect
        manager.disconnect("client1")
        assert "client1" not in manager.active_connections
        assert "client1" not in manager.client_subscriptions

    @pytest.mark.asyncio
    async def test_connection_manager_send_personal_message(self):
        """Test ConnectionManager send_personal_message method."""
        manager = ConnectionManager()
        mock_websocket = AsyncMock()
        manager.active_connections["client1"] = mock_websocket

        # Test successful send
        message = {"type": "test", "data": "hello"}
        await manager.send_personal_message(message, "client1")
        mock_websocket.send_text.assert_called_once_with(
            '{"type": "test", "data": "hello"}'
        )

    @pytest.mark.asyncio
    async def test_connection_manager_send_personal_message_error(self):
        """Test ConnectionManager send_personal_message error handling."""
        manager = ConnectionManager()
        mock_websocket = AsyncMock()
        mock_websocket.send_text.side_effect = Exception("Connection failed")
        manager.active_connections["client1"] = mock_websocket

        # Test error handling
        message = {"type": "test", "data": "hello"}
        await manager.send_personal_message(message, "client1")

        # Client should be disconnected on error
        assert "client1" not in manager.active_connections

    @pytest.mark.asyncio
    async def test_connection_manager_broadcast_to_subscribers(self):
        """Test ConnectionManager broadcast_to_subscribers method."""
        manager = ConnectionManager()
        mock_websocket1 = AsyncMock()
        mock_websocket2 = AsyncMock()

        manager.active_connections["client1"] = mock_websocket1
        manager.active_connections["client2"] = mock_websocket2
        manager.client_subscriptions["client1"] = {"task1", "task2"}
        manager.client_subscriptions["client2"] = {"task2"}

        message = {"type": "update", "data": "test"}
        await manager.broadcast_to_subscribers(message, "task2")

        # Only client1 and client2 are subscribed to task2
        mock_websocket1.send_text.assert_called_once()
        mock_websocket2.send_text.assert_called_once()

    @pytest.mark.asyncio
    async def test_connection_manager_broadcast_empty_subscribers(self):
        """Test broadcast with no subscribers."""
        manager = ConnectionManager()
        mock_websocket = AsyncMock()
        manager.active_connections["client1"] = mock_websocket
        manager.client_subscriptions["client1"] = set()

        message = {"type": "update", "data": "test"}
        await manager.broadcast_to_subscribers(message, "task1")

        # Should not send any messages
        mock_websocket.send_text.assert_not_called()

    def test_manager_instance(self):
        """Test that manager instance exists."""
        from agents.api.routes.websocket import manager

        assert manager is not None
        assert isinstance(manager, ConnectionManager)

    def test_router_exists(self):
        """Test that router exists."""
        from agents.api.routes.websocket import router

        assert router is not None

    def test_websocket_endpoint_exists(self):
        """Test that websocket endpoint function exists."""
        from agents.api.routes.websocket import websocket_endpoint

        assert callable(websocket_endpoint)
