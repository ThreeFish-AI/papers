"""Integration tests for API endpoints."""

import asyncio
from unittest.mock import AsyncMock, patch

import pytest

from tests.agents.fixtures.mocks.mock_file_operations import (
    mock_file_manager,
    patch_file_operations,
)
from tests.agents.fixtures.mocks.mock_websocket import (
    MockWebSocket,
    simulate_task_progress,
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
                "agents.api.services.paper_service.PaperService"
            ) as mock_service_class:
                service = mock_service_class.return_value
                service.upload_paper = AsyncMock(
                    return_value={
                        "paper_id": "llm-agents_test_paper.pdf",
                        "filename": "test_paper.pdf",
                        "category": "llm-agents",
                        "size": len(paper_content),
                        "upload_time": "2024-01-15T14:30:22Z",
                    }
                )

                service.process_paper = AsyncMock(
                    return_value={"task_id": "task_123", "status": "processing"}
                )

                service.get_paper_status = AsyncMock(
                    return_value={
                        "paper_id": "llm-agents_test_paper.pdf",
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

    @pytest.mark.asyncio
    async def test_batch_processing_flow(self, async_client):
        """Test batch processing of multiple papers."""
        paper_ids = ["paper_1", "paper_2", "paper_3"]

        with patch(
            "agents.api.services.paper_service.PaperService"
        ) as mock_service_class:
            service = mock_service_class.return_value

            # Mock batch processing
            service.batch_process_papers = AsyncMock(
                return_value={
                    "batch_id": "batch_123",
                    "total": len(paper_ids),
                    "status": "processing",
                    "results": [],
                }
            )

            # Start batch processing
            batch_response = await async_client.post(
                "/api/papers/batch", params={"workflow": "translate"}, json=paper_ids
            )

            assert batch_response.status_code == 200
            batch_data = batch_response.json()
            assert batch_data["batch_id"] == "batch_123"
            assert batch_data["total"] == 3

    @pytest.mark.websocket
    async def test_websocket_progress_updates(self, async_client):
        """Test WebSocket progress updates during paper processing."""
        from tests.agents.fixtures.mocks.mock_websocket import (
            mock_connection_manager,
            mock_websocket_service,
        )

        # Setup mock WebSocket
        ws = MockWebSocket("test_client")
        paper_id = "test_paper_123"
        task_id = "task_456"

        # Simulate WebSocket connection
        with patch("fastapi.WebSocket", return_value=ws):
            # Add active task
            mock_websocket_service.add_active_task(task_id, paper_id, "translate")

            # Simulate progress updates
            progress_steps = [
                (10, "Starting extraction..."),
                (30, "Translating content..."),
                (60, "Formatting output..."),
                (100, "Processing completed"),
            ]

            await simulate_task_progress(task_id, progress_steps)

            # Check that messages were sent
            messages = ws.get_sent_messages()
            assert len(messages) >= 4  # Should have progress updates

            # Verify subscription
            await mock_connection_manager.subscribe_to_task("test_client", task_id)
            subscribers = mock_connection_manager.get_task_subscribers(task_id)
            assert "test_client" in subscribers

    @pytest.mark.asyncio
    async def test_error_handling_flow(self, async_client):
        """Test error handling in API flow."""
        with patch(
            "agents.api.services.paper_service.PaperService"
        ) as mock_service_class:
            service = mock_service_class.return_value

            # Test upload error
            service.upload_paper = AsyncMock(side_effect=Exception("Upload failed"))

            upload_response = await async_client.post(
                "/api/papers/upload",
                files={"file": ("test.pdf", b"content", "application/pdf")},
            )

            assert upload_response.status_code == 500
            assert "上传失败" in upload_response.json()["detail"]

            # Test processing error
            service.upload_file.return_value = {"paper_id": "test_paper"}
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

        with patch(
            "agents.api.services.paper_service.PaperService"
        ) as mock_service_class:
            service = mock_service_class.return_value

            # Mock successful responses
            service.get_paper_status = AsyncMock(
                side_effect=[
                    {"paper_id": pid, "status": "processing"} for pid in paper_ids
                ]
            )

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
        with patch(
            "agents.api.services.paper_service.PaperService"
        ) as mock_service_class:
            service = mock_service_class.return_value

            # Mock paginated response
            service.list_papers = AsyncMock(
                return_value={
                    "papers": [
                        {
                            "paper_id": f"paper_{i}",
                            "category": "test",
                            "status": "completed",
                        }
                        for i in range(10)
                    ],
                    "total": 50,
                    "limit": 10,
                    "offset": 0,
                }
            )

            # Test first page
            response = await async_client.get(
                "/api/papers/", params={"limit": 10, "offset": 0}
            )
            assert response.status_code == 200
            data = response.json()
            assert len(data["papers"]) == 10
            assert data["total"] == 50

            # Test second page
            service.list_papers.return_value = {
                "papers": [
                    {
                        "paper_id": f"paper_{i}",
                        "category": "test",
                        "status": "completed",
                    }
                    for i in range(10, 20)
                ],
                "total": 50,
                "limit": 10,
                "offset": 10,
            }

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
        with patch(
            "agents.api.services.paper_service.PaperService"
        ) as mock_service_class:
            service = mock_service_class.return_value

            # Test category filter
            service.list_papers.return_value = {
                "papers": [
                    {
                        "paper_id": "paper_1",
                        "category": "llm-agents",
                        "status": "completed",
                    }
                ],
                "total": 1,
                "limit": 20,
                "offset": 0,
            }

            response = await async_client.get(
                "/api/papers/", params={"category": "llm-agents"}
            )
            assert response.status_code == 200
            data = response.json()
            assert len(data["papers"]) == 1
            assert data["papers"][0]["category"] == "llm-agents"

            # Verify service was called with correct parameters
            service.list_papers.assert_called_with(
                category="llm-agents", status=None, limit=20, offset=0
            )

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
        with patch(
            "agents.api.services.paper_service.PaperService"
        ) as mock_service_class:
            service = mock_service_class.return_value

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
        with patch(
            "agents.api.services.paper_service.PaperService"
        ) as mock_service_class:
            service = mock_service_class.return_value

            # Mock report data
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

    @pytest.mark.asyncio
    async def test_health_check(self, async_client):
        """Test health check endpoint."""
        response = await async_client.get("/api/papers/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
