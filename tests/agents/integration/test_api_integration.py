"""Integration tests for API endpoints."""

import asyncio
import json
from datetime import datetime
from unittest.mock import AsyncMock, patch

import pytest

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

    @pytest.mark.asyncio
    async def test_complete_paper_processing_flow(self, async_client, temp_dir):
        """Test complete flow from upload to processing completion."""
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

            # Mock services
            with patch(
                "agents.api.routes.papers.get_paper_service"
            ) as mock_get_service:
                service = mock_get_service.return_value
                # Mock upload to return dynamic paper ID
                mock_upload_result = {
                    "paper_id": "llm-agents_20251212_161959_test_paper.pdf",  # This will be the actual dynamic ID
                    "filename": "test_paper.pdf",
                    "category": "llm-agents",
                    "size": len(paper_content),
                    "upload_time": "2024-01-15T14:30:22Z",
                }
                service.upload_paper = AsyncMock(return_value=mock_upload_result)

                service.process_paper = AsyncMock(
                    return_value={"task_id": "task_123", "status": "processing"}
                )

                # Mock status to work with dynamic paper ID
                service.get_paper_status = AsyncMock(
                    side_effect=lambda paper_id: {
                        "paper_id": paper_id,
                        "status": "completed",
                        "workflows": {
                            "extract": {"status": "completed", "progress": 100},
                            "translate": {"status": "completed", "progress": 100},
                            "heartfelt": {"status": "completed", "progress": 100},
                        },
                    }
                )

                service.get_paper_content = AsyncMock(
                    return_value={
                        "content": "Translated paper content...",
                        "content_type": "translation",
                    }
                )

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
                # Check that paper_id follows the expected pattern with timestamp
                assert paper_id.startswith("llm-agents_")
                assert paper_id.endswith("_test_paper.pdf")

                # 2. Process paper
                process_response = await async_client.post(
                    f"/api/papers/{paper_id}/process",
                    json={"workflow": "full", "options": {"extract_images": True}},
                )

                assert process_response.status_code == 200
                process_data = process_response.json()
                task_id = process_data["task_id"]
                # Check that task_id exists
                assert task_id is not None
                assert len(task_id) > 0

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

    @pytest.mark.asyncio
    async def test_batch_processing_flow(self, async_client):
        """Test batch processing of multiple papers."""
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
                    f"/test/papers/source/{category}/{paper_id}", b"Mock PDF content"
                )

            with patch(
                "agents.api.routes.papers.get_paper_service"
            ) as mock_get_service:
                service = mock_get_service.return_value

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

                service.batch_process_papers = AsyncMock(side_effect=mock_batch_process)

                # Start batch processing
                batch_response = await async_client.post(
                    "/api/papers/batch?workflow=translate", json=paper_ids
                )

                assert batch_response.status_code == 200
                batch_data = batch_response.json()
                assert "batch_id" in batch_data
                assert batch_data["total_requested"] == 3
                assert batch_data["total_files"] == 3

    @pytest.mark.asyncio
    async def test_websocket_progress_updates(self, async_client):
        """Test WebSocket progress updates during paper processing."""
        from agents.api.routes.websocket import ConnectionManager
        from tests.agents.fixtures.mocks.mock_websocket import (
            mock_websocket_service,
        )

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

        # Verify content of messages
        for i, sent_msg in enumerate(sent_messages[:4]):
            msg_data = json.loads(sent_msg) if isinstance(sent_msg, str) else sent_msg
            assert msg_data["task_id"] == task_id
            assert msg_data["paper_id"] == paper_id
            assert msg_data["progress"] == progress_messages[i]["progress"]

        # Test disconnection
        mock_manager.disconnect(client_id)
        assert client_id not in mock_manager.active_connections

    @pytest.mark.asyncio
    async def test_error_handling_flow(self, async_client):
        """Test error handling in API flow."""
        with patch("agents.api.routes.papers.get_paper_service") as mock_get_service:
            service = mock_get_service.return_value

            # Test upload error - service should raise an exception
            service.upload_paper = AsyncMock(side_effect=Exception("Upload failed"))

            upload_response = await async_client.post(
                "/api/papers/upload",
                files={"file": ("test.pdf", b"content", "application/pdf")},
            )

            assert upload_response.status_code == 500
            assert "上传失败" in upload_response.json()["detail"]

            # Test processing error - reset the mock first
            service.upload_paper = AsyncMock(
                return_value={
                    "paper_id": "test_paper",
                    "filename": "test.pdf",
                    "category": "general",
                    "size": 100,
                    "upload_time": "2024-12-13T12:00:00Z",
                }
            )
            service.process_paper = AsyncMock(side_effect=ValueError("Paper not found"))

            process_response = await async_client.post(
                "/api/papers/test_paper/process", json={"workflow": "full"}
            )

            assert process_response.status_code == 404
            assert "Paper not found" in process_response.json()["detail"]

    @pytest.mark.asyncio
    async def test_concurrent_requests(self, async_client):
        """Test handling concurrent requests."""
        paper_ids = [f"paper_{i}" for i in range(5)]

        with patch("agents.api.routes.papers.get_paper_service") as mock_get_service:
            service = mock_get_service.return_value

            # Mock successful responses based on paper_id
            def mock_status(paper_id):
                return {
                    "paper_id": paper_id,
                    "status": "processing",
                    "progress": 50,
                }

            service.get_paper_status = AsyncMock(side_effect=mock_status)

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
    async def test_pagination_integration(self, async_client):
        """Test pagination in paper listing."""
        with patch("agents.api.routes.papers.get_paper_service") as mock_get_service:
            service = mock_get_service.return_value

            # Create test papers
            def mock_list_papers(category=None, status=None, limit=20, offset=0):
                all_papers = [
                    {
                        "paper_id": f"general_20241213_1200{i}_paper_{i}.pdf",
                        "category": "general",
                        "status": "completed",
                        "filename": f"paper_{i}.pdf",
                        "upload_time": "2024-12-13T12:00:00Z",
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

            service.list_papers = AsyncMock(side_effect=mock_list_papers)

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

    @pytest.mark.asyncio
    async def test_filtering_integration(self, async_client):
        """Test filtering in paper listing."""
        with patch("agents.api.routes.papers.get_paper_service") as mock_get_service:
            service = mock_get_service.return_value

            # Create test papers with different categories
            def mock_list_papers(category=None, status=None, limit=20, offset=0):
                all_papers = [
                    {
                        "paper_id": "llm-agents_20241213_120001_paper1.pdf",
                        "category": "llm-agents",
                        "status": "completed",
                        "filename": "paper1.pdf",
                        "upload_time": "2024-12-13T12:00:01Z",
                    },
                    {
                        "paper_id": "context-engineering_20241213_120002_paper2.pdf",
                        "category": "context-engineering",
                        "status": "completed",
                        "filename": "paper2.pdf",
                        "upload_time": "2024-12-13T12:00:02Z",
                    },
                    {
                        "paper_id": "general_20241213_120003_paper3.pdf",
                        "category": "general",
                        "status": "processing",
                        "filename": "paper3.pdf",
                        "upload_time": "2024-12-13T12:00:03Z",
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

            service.list_papers = AsyncMock(side_effect=mock_list_papers)

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
    async def test_delete_cascade(self, async_client):
        """Test cascade deletion of paper and related files."""
        with patch("agents.api.routes.papers.get_paper_service") as mock_get_service:
            service = mock_get_service.return_value

            # Mock paper exists
            service._get_metadata = AsyncMock(
                return_value={
                    "paper_id": "test_paper",
                    "category": "general",
                    "status": "completed",
                }
            )

            # Mock successful deletion
            service.delete_paper = AsyncMock(return_value=True)

            response = await async_client.delete("/api/papers/test_paper")
            assert response.status_code == 200
            assert response.json() is True

            # Verify delete was called
            service.delete_paper.assert_called_once_with("test_paper")

    @pytest.mark.asyncio
    async def test_report_generation(self, async_client):
        """Test report generation endpoint."""
        with patch("agents.api.routes.papers.get_paper_service") as mock_get_service:
            service = mock_get_service.return_value

            # Mock paper exists
            service._get_metadata = AsyncMock(
                return_value={
                    "paper_id": "test_paper",
                    "category": "general",
                    "status": "completed",
                }
            )

            # Mock heartfelt agent
            service.heartfelt_agent = AsyncMock()
            service.heartfelt_agent.generate_reading_report = AsyncMock(
                return_value={
                    "summary": "Paper summary...",
                    "insights": ["Insight 1", "Insight 2"],
                    "recommendations": ["Recommendation 1"],
                    "impact_score": 0.85,
                    "generated_at": "2024-01-15T14:30:22Z",
                }
            )

            # Mock the service method
            service.get_paper_report = AsyncMock(
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

    @pytest.mark.asyncio
    async def test_health_check(self, async_client):
        """Test health check endpoint."""
        response = await async_client.get("/api/papers/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
