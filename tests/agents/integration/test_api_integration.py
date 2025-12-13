"""Integration tests for API endpoints."""

import asyncio
import json
from datetime import datetime
from unittest.mock import AsyncMock

import pytest

from agents.api.main import app
from agents.api.routes.papers import get_paper_service
from tests.agents.fixtures.mocks.mock_file_operations import (
    mock_file_manager,
    patch_file_operations,
)
from tests.agents.fixtures.mocks.mock_websocket import (
    MockWebSocket,
)


@pytest.mark.integration
class TestAPIIntegration:
    """Integration tests for API endpoints."""

    @staticmethod
    def setup_dependency_override(mock_service):
        """Setup FastAPI dependency override for a test."""
        app.dependency_overrides[get_paper_service] = lambda: mock_service

    @staticmethod
    def cleanup_dependency_override():
        """Clean up FastAPI dependency override after a test."""
        app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_complete_paper_processing_flow(
        self, async_client, mock_paper_service_instance
    ):
        """Test complete flow from upload to processing completion."""
        # Override dependency injection
        self.setup_dependency_override(mock_paper_service_instance)

        try:
            # 1. Upload paper
            paper_content = b"%PDF-1.4\nTest paper content for integration testing"

            # Mock file operations
            with patch_file_operations():
                # Setup mock storage
                mock_file_manager.mkdir(
                    "/test/papers/source/llm-agents", parents=True, exist_ok=True
                )
                mock_file_manager.add_file(
                    "/test/papers/source/llm-agents/test_paper.pdf", paper_content
                )

                # Configure mock to return expected results
                mock_paper_service_instance.upload_paper.return_value = {
                    "paper_id": "llm-agents_test_paper.pdf",
                    "filename": "test_paper.pdf",
                    "category": "llm-agents",
                    "size": len(paper_content),
                    "upload_time": "2024-01-15T14:30:22Z",
                }

                mock_paper_service_instance.process_paper.return_value = {
                    "task_id": "task_123",
                    "status": "processing",
                }

                mock_paper_service_instance.get_status.return_value = {
                    "paper_id": "llm-agents_test_paper.pdf",
                    "status": "completed",
                    "workflows": {
                        "extract": {"status": "completed", "progress": 100},
                        "translate": {"status": "completed", "progress": 100},
                        "heartfelt": {"status": "completed", "progress": 100},
                    },
                }

                mock_paper_service_instance.get_content.return_value = {
                    "content": "Translated test content",
                    "content_type": "translation",
                }

                # Upload paper
                upload_response = await async_client.post(
                    "/api/papers/upload",
                    files={
                        "file": ("test_paper.pdf", paper_content, "application/pdf")
                    },
                    params={"category": "llm-agents"},
                )

                assert upload_response.status_code == 200
                upload_data = upload_response.json()
                paper_id = upload_data["paper_id"]
                assert paper_id == "llm-agents_test_paper.pdf"

                # 2. Process paper
                process_response = await async_client.post(
                    f"/api/papers/{paper_id}/process",
                    json={"workflow": "full", "options": {"extract_images": True}},
                )

                assert process_response.status_code == 200
                process_data = process_response.json()
                task_id = process_data["task_id"]
                assert task_id == "task_123"

                # 3. Check status
                status_response = await async_client.get(
                    f"/api/papers/{paper_id}/status"
                )
                assert status_response.status_code == 200
                status_data = status_response.json()
                assert status_data["status"] == "completed"

                # 4. Get translated content
                content_response = await async_client.get(
                    f"/api/papers/{paper_id}/content",
                    params={"content_type": "translation"},
                )
                assert content_response.status_code == 200
                content_data = content_response.json()
                assert "content" in content_data

        finally:
            # Clean up dependency override
            self.cleanup_dependency_override()

    @pytest.mark.asyncio
    async def test_batch_processing_flow(
        self, async_client, mock_paper_service_instance
    ):
        """Test batch processing of multiple papers."""
        # Override dependency injection
        self.setup_dependency_override(mock_paper_service_instance)

        try:
            paper_ids = [
                "llm-agents_paper1.pdf",
                "llm-agents_paper2.pdf",
                "llm-agents_paper3.pdf",
            ]

            # Mock file operations
            with patch_file_operations():
                # Setup mock files for batch processing
                for paper_id in paper_ids:
                    category = paper_id.split("_")[0] if "_" in paper_id else "general"
                    mock_file_manager.mkdir(
                        f"/test/papers/source/{category}", parents=True, exist_ok=True
                    )
                    mock_file_manager.add_file(
                        f"/test/papers/source/{category}/{paper_id}",
                        b"Mock PDF content",
                    )

                # Mock batch processing to simulate real behavior
                def mock_batch_process(paper_ids_list, workflow):
                    return {
                        "batch_id": f"batch_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                        "total_requested": len(paper_ids_list),
                        "total_files": len(paper_ids_list),
                        "workflow": workflow,
                        "stats": {"processed": len(paper_ids_list), "failed": 0},
                        "results": [
                            {"paper_id": pid, "status": "completed"}
                            for pid in paper_ids_list
                        ],
                    }

                mock_paper_service_instance.batch_process_papers = AsyncMock(
                    side_effect=mock_batch_process
                )

                # Start batch processing
                batch_response = await async_client.post(
                    "/api/papers/batch?workflow=translate", json=paper_ids
                )

                assert batch_response.status_code == 200
                batch_data = batch_response.json()
                assert "batch_id" in batch_data
                assert batch_data["total_requested"] == 3
                assert batch_data["total_files"] == 3

        finally:
            # Clean up dependency override
            self.cleanup_dependency_override()

    @pytest.mark.asyncio
    async def test_websocket_progress_updates(
        self, async_client, mock_paper_service_instance
    ):
        """Test WebSocket progress updates during paper processing."""
        from agents.api.routes.websocket import ConnectionManager
        from tests.agents.fixtures.mocks.mock_websocket import (
            mock_websocket_service,
        )

        # Override dependency injection
        self.setup_dependency_override(mock_paper_service_instance)

        try:
            # Test the connection manager directly since WebSocket testing requires special handling
            client_id = "test_client_123"
            task_id = "task_456"
            paper_id = "test_paper_123"

            # Mock connection manager
            mock_manager = ConnectionManager()
            mock_ws = MockWebSocket(client_id)

            # Test connection
            await mock_manager.connect(mock_ws, client_id)
            assert client_id in mock_manager.active_connections

            # Add task to mock service
            mock_websocket_service.add_active_task(task_id, paper_id, "translate")
            mock_manager.client_subscriptions[client_id].add(task_id)

            # Simulate progress messages
            progress_messages = [
                {
                    "task_id": task_id,
                    "paper_id": paper_id,
                    "progress": 25,
                    "status": "extracting",
                },
                {
                    "task_id": task_id,
                    "paper_id": paper_id,
                    "progress": 50,
                    "status": "translating",
                },
                {
                    "task_id": task_id,
                    "paper_id": paper_id,
                    "progress": 75,
                    "status": "analyzing",
                },
                {
                    "task_id": task_id,
                    "paper_id": paper_id,
                    "progress": 100,
                    "status": "completed",
                },
            ]

            # Send messages through manager
            for msg in progress_messages:
                await mock_manager.send_personal_message(msg, client_id)

            # Verify messages were sent
            sent_messages = mock_ws.get_sent_messages()
            assert len(sent_messages) >= 4  # Should have progress updates

            # Verify content of messages - MockWebSocket wraps messages in dict with "type" and "data"
            for i, sent_msg in enumerate(sent_messages[:4]):
                # Extract the actual message from the MockWebSocket format
                if isinstance(sent_msg, dict) and "data" in sent_msg:
                    # data might be a string (JSON), need to parse it
                    data_str = sent_msg["data"]
                    if isinstance(data_str, str):
                        msg_data = json.loads(data_str)
                    else:
                        msg_data = data_str
                else:
                    msg_data = (
                        json.loads(sent_msg) if isinstance(sent_msg, str) else sent_msg
                    )

                assert msg_data["task_id"] == task_id
                assert msg_data["paper_id"] == paper_id
                assert msg_data["progress"] == progress_messages[i]["progress"]

            # Test disconnection
            mock_manager.disconnect(client_id)
            assert client_id not in mock_manager.active_connections

        finally:
            # Clean up dependency override
            self.cleanup_dependency_override()

    @pytest.mark.asyncio
    async def test_error_handling_flow(self, async_client, mock_paper_service_instance):
        """Test error handling in API flow."""
        # Override dependency injection
        self.setup_dependency_override(mock_paper_service_instance)

        try:
            # Test upload error - service should raise an exception
            mock_paper_service_instance.upload_paper = AsyncMock(
                side_effect=Exception("Upload failed")
            )

            upload_response = await async_client.post(
                "/api/papers/upload",
                files={"file": ("test.pdf", b"content", "application/pdf")},
            )

            assert upload_response.status_code == 500
            assert "上传失败" in upload_response.json()["detail"]

            # Test processing error - reset the mock first
            mock_paper_service_instance.upload_paper = AsyncMock(
                return_value={
                    "paper_id": "test_paper",
                    "filename": "test.pdf",
                    "category": "general",
                    "size": 100,
                    "upload_time": "2024-12-13T12:00:00Z",
                }
            )
            mock_paper_service_instance.process_paper = AsyncMock(
                side_effect=ValueError("Paper not found")
            )

            process_response = await async_client.post(
                "/api/papers/test_paper/process", json={"workflow": "full"}
            )

            assert process_response.status_code == 404
            assert "Paper not found" in process_response.json()["detail"]

        finally:
            # Clean up dependency override
            self.cleanup_dependency_override()

    @pytest.mark.asyncio
    async def test_concurrent_requests(self, async_client, mock_paper_service_instance):
        """Test handling concurrent requests."""
        # Override dependency injection
        self.setup_dependency_override(mock_paper_service_instance)

        try:
            paper_ids = [f"paper_{i}" for i in range(5)]

            # Mock successful responses based on paper_id
            def mock_status(paper_id):
                return {
                    "paper_id": paper_id,
                    "status": "processing",
                    "workflows": {
                        "extract": {"status": "completed", "progress": 100},
                        "translate": {"status": "processing", "progress": 50},
                    },
                    "upload_time": "2024-01-15T14:30:22Z",
                    "updated_at": "2024-01-15T14:35:22Z",
                    "category": "general",
                    "filename": f"{paper_id}.pdf",
                }

            mock_paper_service_instance.get_status = AsyncMock(side_effect=mock_status)

            # Send concurrent requests
            tasks = []
            for paper_id in paper_ids:
                task = async_client.get(f"/api/papers/{paper_id}/status")
                tasks.append(task)

            # Wait for all responses
            responses = await asyncio.gather(*tasks)

            # Verify all requests succeeded
            for i, response in enumerate(responses):
                assert response.status_code == 200
                data = response.json()
                assert data["paper_id"] == paper_ids[i]
                assert data["status"] == "processing"

        finally:
            # Clean up dependency override
            self.cleanup_dependency_override()

    @pytest.mark.asyncio
    async def test_file_validation_integration(self, async_client):
        """Test file validation in upload endpoint."""
        # Test invalid file type
        response = await async_client.post(
            "/api/papers/upload", files={"file": ("test.txt", b"content", "text/plain")}
        )
        assert response.status_code == 400
        assert "只支持 PDF 文件" in response.json()["detail"]

        # Test large file
        large_content = b"x" * (51 * 1024 * 1024)  # 51MB
        response = await async_client.post(
            "/api/papers/upload",
            files={"file": ("large.pdf", large_content, "application/pdf")},
            headers={"content-length": str(len(large_content))},
        )
        assert response.status_code == 400
        assert "文件大小不能超过 50MB" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_pagination_integration(
        self, async_client, mock_paper_service_instance
    ):
        """Test pagination in paper listing."""
        # Override dependency injection
        self.setup_dependency_override(mock_paper_service_instance)

        try:
            # Create test papers
            def mock_list_papers(category=None, status=None, limit=20, offset=0):
                all_papers = [
                    {
                        "paper_id": f"general_20241213_1200{i}_paper_{i}.pdf",
                        "category": "general",
                        "status": "completed",
                        "filename": f"paper_{i}.pdf",
                        "upload_time": "2024-12-13T12:00:00Z",
                        "size": 1024000,
                    }
                    for i in range(50)
                ]

                # Apply filters
                filtered = all_papers
                if category:
                    filtered = [p for p in filtered if p["category"] == category]
                if status:
                    filtered = [p for p in filtered if p["status"] == status]

                # Apply pagination
                paginated = filtered[offset : offset + limit]

                return {
                    "papers": paginated,
                    "total": len(filtered),
                    "limit": limit,
                    "offset": offset,
                }

            mock_paper_service_instance.list_papers = AsyncMock(
                side_effect=mock_list_papers
            )

            # Test first page
            response = await async_client.get(
                "/api/papers/", params={"limit": 10, "offset": 0}
            )
            assert response.status_code == 200
            data = response.json()
            assert len(data["papers"]) == 10
            assert data["total"] == 50
            assert data["limit"] == 10
            assert data["offset"] == 0

            # Test second page
            response = await async_client.get(
                "/api/papers/", params={"limit": 10, "offset": 10}
            )
            assert response.status_code == 200
            data = response.json()
            assert len(data["papers"]) == 10
            assert data["offset"] == 10

        finally:
            # Clean up dependency override
            self.cleanup_dependency_override()

    @pytest.mark.asyncio
    async def test_filtering_integration(
        self, async_client, mock_paper_service_instance
    ):
        """Test filtering in paper listing."""
        # Override dependency injection
        self.setup_dependency_override(mock_paper_service_instance)

        try:
            # Create test papers with different categories
            def mock_list_papers(category=None, status=None, limit=20, offset=0):
                all_papers = [
                    {
                        "paper_id": "llm-agents_20241213_120001_paper1.pdf",
                        "category": "llm-agents",
                        "status": "completed",
                        "filename": "paper1.pdf",
                        "upload_time": "2024-12-13T12:00:01Z",
                        "size": 1024000,
                    },
                    {
                        "paper_id": "context-engineering_20241213_120002_paper2.pdf",
                        "category": "context-engineering",
                        "status": "completed",
                        "filename": "paper2.pdf",
                        "upload_time": "2024-12-13T12:00:02Z",
                        "size": 1024000,
                    },
                    {
                        "paper_id": "general_20241213_120003_paper3.pdf",
                        "category": "general",
                        "status": "processing",
                        "filename": "paper3.pdf",
                        "upload_time": "2024-12-13T12:00:03Z",
                        "size": 1024000,
                    },
                ]

                # Apply filters
                filtered = all_papers
                if category:
                    filtered = [p for p in filtered if p["category"] == category]
                if status:
                    filtered = [p for p in filtered if p["status"] == status]

                # Apply pagination
                paginated = filtered[offset : offset + limit]

                return {
                    "papers": paginated,
                    "total": len(filtered),
                    "limit": limit,
                    "offset": offset,
                }

            mock_paper_service_instance.list_papers = AsyncMock(
                side_effect=mock_list_papers
            )

            # Test category filter
            response = await async_client.get(
                "/api/papers/", params={"category": "llm-agents"}
            )
            assert response.status_code == 200
            data = response.json()
            assert len(data["papers"]) == 1
            assert data["papers"][0]["category"] == "llm-agents"
            assert data["total"] == 1

            # Test status filter
            response = await async_client.get(
                "/api/papers/", params={"status": "processing"}
            )
            assert response.status_code == 200
            data = response.json()
            assert len(data["papers"]) == 1
            assert data["papers"][0]["status"] == "processing"

            # Test combined filters
            response = await async_client.get(
                "/api/papers/", params={"category": "llm-agents", "status": "completed"}
            )
            assert response.status_code == 200
            data = response.json()
            assert len(data["papers"]) == 1
            assert data["papers"][0]["category"] == "llm-agents"
            assert data["papers"][0]["status"] == "completed"

        finally:
            # Clean up dependency override
            self.cleanup_dependency_override()

    @pytest.mark.asyncio
    async def test_content_type_validation(self, async_client):
        """Test content type validation in content endpoint."""
        paper_id = "test_paper"

        # Test invalid content type
        response = await async_client.get(
            f"/api/papers/{paper_id}/content", params={"content_type": "invalid_type"}
        )
        assert response.status_code == 400
        assert "无效的内容类型" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_delete_cascade(self, async_client, mock_paper_service_instance):
        """Test cascade deletion of paper and related files."""
        # Override dependency injection
        self.setup_dependency_override(mock_paper_service_instance)

        try:
            # Mock paper exists
            mock_paper_service_instance._get_metadata = AsyncMock(
                return_value={
                    "paper_id": "test_paper",
                    "category": "general",
                    "status": "completed",
                }
            )

            # Mock successful deletion
            mock_paper_service_instance.delete_paper = AsyncMock(return_value=True)

            response = await async_client.delete("/api/papers/test_paper")
            assert response.status_code == 200
            assert response.json() == {"deleted": True, "paper_id": "test_paper"}

            # Verify delete was called
            mock_paper_service_instance.delete_paper.assert_called_once_with(
                "test_paper"
            )

        finally:
            # Clean up dependency override
            self.cleanup_dependency_override()

    @pytest.mark.asyncio
    async def test_report_generation(self, async_client, mock_paper_service_instance):
        """Test report generation endpoint."""
        # Override dependency injection
        self.setup_dependency_override(mock_paper_service_instance)

        try:
            # Mock paper exists
            mock_paper_service_instance._get_metadata = AsyncMock(
                return_value={
                    "paper_id": "test_paper",
                    "category": "general",
                    "status": "completed",
                }
            )

            # Mock heartfelt agent
            mock_paper_service_instance.heartfelt_agent = AsyncMock()
            mock_paper_service_instance.heartfelt_agent.generate_reading_report = (
                AsyncMock(
                    return_value={
                        "summary": "Paper summary...",
                        "insights": ["Insight 1", "Insight 2"],
                        "recommendations": ["Recommendation 1"],
                        "impact_score": 0.85,
                        "generated_at": "2024-01-15T14:30:22Z",
                    }
                )
            )

            # Mock the service method
            mock_paper_service_instance.get_paper_report = AsyncMock(
                return_value={
                    "summary": "Paper summary...",
                    "insights": ["Insight 1", "Insight 2"],
                    "recommendations": ["Recommendation 1"],
                    "impact_score": 0.85,
                    "generated_at": "2024-01-15T14:30:22Z",
                }
            )

            response = await async_client.get("/api/papers/test_paper/report")
            assert response.status_code == 200
            data = response.json()
            assert "summary" in data
            assert "insights" in data
            assert len(data["insights"]) == 2
            assert data["impact_score"] == 0.85

        finally:
            # Clean up dependency override
            self.cleanup_dependency_override()

    @pytest.mark.asyncio
    async def test_health_check(self, async_client):
        """Test health check endpoint."""
        response = await async_client.get("/api/papers/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
