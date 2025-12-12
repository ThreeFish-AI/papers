"""Unit tests for PaperService."""

import io
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import UploadFile

from agents.api.models.paper import PaperInfo
from agents.api.services.paper_service import PaperService
from tests.agents.fixtures.mocks.mock_file_operations import (
    mock_file_manager,
    patch_file_operations,
)


@pytest.mark.unit
class TestPaperService:
    """Test cases for PaperService."""

    @pytest.fixture
    def paper_service(self, temp_dir):
        """Create a PaperService instance for testing."""
        with patch("agents.api.services.paper_service.settings") as mock_settings:
            mock_settings.PAPERS_DIR = str(temp_dir / "papers")
            service = PaperService()
            # Replace agents with mocks
            service.workflow_agent = AsyncMock()
            service.batch_agent = AsyncMock()
            service.heartfelt_agent = AsyncMock()
            yield service

    @pytest.fixture
    def mock_upload_file(self, sample_pdf_content):
        """Create a mock upload file."""
        file = MagicMock(spec=UploadFile)
        file.filename = "test_paper.pdf"
        file.file = io.BytesIO(sample_pdf_content)
        file.content_type = "application/pdf"
        return file

    @pytest.mark.asyncio
    async def test_upload_paper_success(
        self, paper_service, mock_upload_file, temp_dir
    ):
        """Test successful paper upload."""
        # Setup mocks
        papers_dir = temp_dir / "papers"
        with patch_file_operations():
            mock_file_manager.add_file(
                str(papers_dir / "source/llm-agents/test_paper.pdf"),
                mock_upload_file.file.getvalue(),
            )
            mock_file_manager.mkdir(
                str(papers_dir / "source/llm-agents"), parents=True, exist_ok=True
            )

            with patch("agents.api.services.paper_service.datetime") as mock_datetime:
                mock_datetime.now.return_value.strftime.return_value = "20240115_143022"

                # Mock metadata saving
                with patch.object(
                    paper_service, "_save_metadata", new_callable=AsyncMock
                ):
                    result = await paper_service.upload_paper(
                        mock_upload_file, "llm-agents"
                    )

                    # Assert result
                    assert (
                        result["paper_id"]
                        == "llm-agents_20240115_143022_test_paper.pdf"
                    )
                    assert result["filename"] == "test_paper.pdf"
                    assert result["category"] == "llm-agents"
                    assert result["size"] == len(mock_upload_file.file.getvalue())

    @pytest.mark.asyncio
    async def test_upload_paper_invalid_filename(self, paper_service):
        """Test paper upload with invalid filename."""
        mock_file = MagicMock(spec=UploadFile)
        mock_file.filename = "../../../etc/passwd"
        mock_file.file = io.BytesIO(b"fake content")

        with patch.object(paper_service, "_save_metadata", new_callable=AsyncMock):
            result = await paper_service.upload_paper(mock_file, "test")

            # Should sanitize filename
            assert "etc_passwd" in result["paper_id"]
            assert result["category"] == "test"

    @pytest.mark.asyncio
    async def test_upload_paper_file_save_error(self, paper_service, mock_upload_file):
        """Test paper upload when file save fails."""
        with patch("builtins.open", side_effect=OSError("Disk full")):
            with pytest.raises(IOError):
                await paper_service.upload_paper(mock_upload_file, "test")

    @pytest.mark.asyncio
    async def test_process_paper_full_workflow(self, paper_service, temp_dir):
        """Test paper processing with full workflow."""
        paper_id = "test_paper_123"
        workflow = "full"

        # Setup mocks
        papers_dir = temp_dir / "papers"
        source_path = papers_dir / "source/test/test_paper_123.pdf"

        with patch.object(paper_service, "_get_source_path", return_value=source_path):
            with patch.object(
                paper_service, "_get_metadata", new_callable=AsyncMock
            ) as mock_get_meta:
                mock_get_meta.return_value = {"workflows": {}}

                with patch_file_operations():
                    mock_file_manager.add_file(str(source_path), b"PDF content")
                    mock_file_manager.exists(str(source_path))
                    source_path.exists = lambda: True  # Mock path.exists() check

                    # Mock workflow agent
                    paper_service.workflow_agent.process.return_value = {
                        "task_id": "task_123",
                        "status": "processing",
                    }

                    result = await paper_service.process_paper(paper_id, workflow)

                    assert result["task_id"] == "task_123"
                    assert result["status"] == "processing"
                    paper_service.workflow_agent.process.assert_called_once_with(
                        {
                            "source_path": str(source_path),
                            "workflow": workflow,
                            "paper_id": paper_id,
                            "options": None,
                        }
                    )

    @pytest.mark.asyncio
    async def test_process_paper_not_found(self, paper_service, temp_dir):
        """Test processing non-existent paper."""
        paper_id = "nonexistent_paper"

        papers_dir = temp_dir / "papers"
        source_path = papers_dir / "source/test/nonexistent_paper"

        with patch.object(paper_service, "_get_source_path", return_value=source_path):
            with patch.object(
                paper_service, "_get_metadata", new_callable=AsyncMock
            ) as mock_get_meta:
                mock_get_meta.return_value = (
                    None  # No metadata means paper doesn't exist
                )

                with patch_file_operations():
                    # File doesn't exist
                    mock_file_manager.files = {}
                    source_path.exists = (
                        lambda: False
                    )  # Mock path.exists() to return False

                    with pytest.raises(ValueError, match="Paper not found"):
                        await paper_service.process_paper(paper_id, "full")

    @pytest.mark.asyncio
    async def test_process_paper_with_options(self, paper_service, temp_dir):
        """Test paper processing with custom options."""
        paper_id = "test_paper_123"
        workflow = "translate"
        options = {"preserve_format": True, "translation_style": "academic"}

        papers_dir = temp_dir / "papers"
        source_path = papers_dir / "source/test/test_paper_123.pdf"
        with patch.object(paper_service, "_get_source_path", return_value=source_path):
            with patch.object(
                paper_service, "_get_metadata", new_callable=AsyncMock
            ) as mock_get_meta:
                mock_get_meta.return_value = {"workflows": {}}

                with patch_file_operations():
                    mock_file_manager.add_file(str(source_path), b"PDF content")
                    source_path.exists = lambda: True  # Mock path.exists() check

                    paper_service.workflow_agent.process.return_value = {
                        "task_id": "task_456",
                        "status": "processing",
                    }

                    result = await paper_service.process_paper(
                        paper_id, workflow, options
                    )

                    paper_service.workflow_agent.process.assert_called_once_with(
                        {
                            "source_path": str(source_path),
                            "workflow": workflow,
                            "paper_id": paper_id,
                            "options": options,
                        }
                    )
                assert result["task_id"] == "task_456"

    @pytest.mark.asyncio
    async def test_get_paper_status(self, paper_service):
        """Test getting paper status."""
        paper_id = "test_paper_123"
        metadata = {
            "paper_id": paper_id,
            "status": "processing",
            "workflows": {
                "extract": {"status": "completed", "progress": 100},
                "translate": {"status": "processing", "progress": 50},
            },
        }

        with patch.object(
            paper_service, "_get_metadata", new_callable=AsyncMock
        ) as mock_get_meta:
            mock_get_meta.return_value = metadata

            result = await paper_service.get_paper_status(paper_id)

            assert result["paper_id"] == paper_id
            assert result["status"] == "processing"
            assert result["workflows"]["extract"]["status"] == "completed"
            assert result["workflows"]["translate"]["progress"] == 50

    @pytest.mark.asyncio
    async def test_get_paper_status_not_found(self, paper_service):
        """Test getting status of non-existent paper."""
        paper_id = "nonexistent"

        with patch.object(
            paper_service, "_load_metadata", new_callable=AsyncMock
        ) as mock_load:
            mock_load.return_value = None

            result = await paper_service.get_paper_status(paper_id)

            assert result is None

    @pytest.mark.asyncio
    async def test_list_papers(self, paper_service):
        """Test listing papers."""
        papers = [
            {"paper_id": "paper_1", "category": "llm-agents", "status": "completed"},
            {"paper_id": "paper_2", "category": "rl", "status": "processing"},
            {"paper_id": "paper_3", "category": "llm-agents", "status": "uploaded"},
        ]

        with patch.object(
            paper_service, "_list_all_metadata", new_callable=AsyncMock
        ) as mock_list:
            mock_list.return_value = papers

            # Test without filter
            result = await paper_service.list_papers()
            assert len(result["papers"]) == 3

            # Test with category filter
            result = await paper_service.list_papers(category="llm-agents")
            assert len(result["papers"]) == 2
            assert all(p["category"] == "llm-agents" for p in result["papers"])

            # Test with status filter
            result = await paper_service.list_papers(status="processing")
            assert len(result["papers"]) == 1
            assert result["papers"][0]["status"] == "processing"

    @pytest.mark.asyncio
    async def test_list_papers_empty(self, paper_service):
        """Test listing papers when none exist."""
        with patch.object(
            paper_service, "_list_all_metadata", new_callable=AsyncMock
        ) as mock_list:
            mock_list.return_value = []

            result = await paper_service.list_papers()
            assert result["papers"] == []

    @pytest.mark.asyncio
    async def test_delete_paper(self, paper_service, temp_dir):
        """Test deleting a paper."""
        paper_id = "test_paper_123"

        papers_dir = temp_dir / "papers"
        source_path = papers_dir / "source/test/test_paper_123.pdf"
        metadata_path = papers_dir / ".metadata/test_paper_123.json"

        with patch.object(paper_service, "_get_source_path", return_value=source_path):
            with patch.object(
                paper_service, "_get_metadata_path", return_value=metadata_path
            ):
                with patch.object(
                    paper_service, "_get_metadata", new_callable=AsyncMock
                ) as mock_get_meta:
                    mock_get_meta.return_value = {
                        "paper_id": paper_id,
                        "status": "uploaded",
                    }

                    with patch_file_operations():
                        mock_file_manager.add_file(str(source_path), b"PDF content")
                        mock_file_manager.add_file(
                            str(metadata_path), b'{"paper_id": "test"}'
                        )

                        result = await paper_service.delete_paper(paper_id)

                        assert result is True

    @pytest.mark.asyncio
    async def test_delete_paper_not_found(self, paper_service):
        """Test deleting non-existent paper."""
        paper_id = "nonexistent"

        with patch.object(
            paper_service, "_get_metadata", new_callable=AsyncMock
        ) as mock_get_meta:
            mock_get_meta.return_value = None

            with pytest.raises(ValueError, match="Paper not found"):
                await paper_service.delete_paper(paper_id)

    @pytest.mark.asyncio
    async def test_get_paper_content(self, paper_service):
        """Test getting paper content."""
        paper_id = "test_paper_123"
        content = "Extracted PDF content..."

        with patch.object(
            paper_service, "_get_output_path", return_value=Path("/test/output.json")
        ):
            with patch_file_operations():
                mock_file_manager.add_file("/test/output.json", content)

                result = await paper_service.get_paper_content(paper_id, "extracted")

                assert result == content

    @pytest.mark.asyncio
    async def test_get_paper_content_not_found(self, paper_service):
        """Test getting content for non-existent output."""
        paper_id = "test_paper_123"

        with patch.object(
            paper_service, "_get_output_path", return_value=Path("/test/output.json")
        ):
            with patch_file_operations():
                # File doesn't exist
                result = await paper_service.get_paper_content(paper_id, "extracted")

                assert result is None

    @pytest.mark.asyncio
    async def test_batch_translate(self, paper_service, temp_dir):
        """Test batch translation of papers."""
        paper_ids = ["paper_1", "paper_2", "paper_3"]
        papers_dir = temp_dir / "papers"

        # Mock _get_source_path to return paths that exist
        def mock_get_source_path(paper_id):
            path = papers_dir / "source/test" / f"{paper_id}.pdf"
            path.exists = lambda: True  # Mock exists() to return True
            return path

        with patch.object(
            paper_service, "_get_source_path", side_effect=mock_get_source_path
        ):
            paper_service.batch_agent.batch_translate.return_value = {
                "batch_id": "batch_123",
                "total": 3,
                "status": "processing",
            }

            result = await paper_service.batch_translate(paper_ids)

            assert result["batch_id"] == "batch_123"
            assert result["total"] == 3
            paper_service.batch_agent.batch_translate.assert_called_once_with(paper_ids)

    def test_sanitize_filename(self, paper_service):
        """Test filename sanitization."""
        # Test normal filename
        assert paper_service._sanitize_filename("normal.pdf") == "normal.pdf"

        # Test filename with path
        assert (
            paper_service._sanitize_filename("path/to/file.pdf") == "path_to_file.pdf"
        )

        # Test filename with special characters
        assert paper_service._sanitize_filename("file@#$%.pdf") == "file____.pdf"

        # Test empty filename
        assert paper_service._sanitize_filename("") == "unnamed"

    @pytest.mark.asyncio
    async def test_heartfelt_analysis(self, paper_service, temp_dir):
        """Test heartfelt analysis of paper."""
        paper_id = "test_paper_123"
        papers_dir = temp_dir / "papers"
        source_path = papers_dir / "source/test/test_paper_123.pdf"
        source_path.exists = lambda: True  # Mock exists() to return True

        with patch.object(paper_service, "_get_source_path", return_value=source_path):
            with patch.object(
                paper_service, "_get_metadata", new_callable=AsyncMock
            ) as mock_get_meta:
                mock_get_meta.return_value = {"workflows": {}}

                paper_service.heartfelt_agent.analyze.return_value = {
                    "analysis_id": "analysis_123",
                    "status": "processing",
                }

                result = await paper_service.analyze_paper(paper_id)

                assert result["analysis_id"] == "analysis_123"
                paper_service.heartfelt_agent.analyze.assert_called_once_with(paper_id)

    @pytest.mark.asyncio
    async def test_get_paper_info(self, paper_service, temp_dir):
        """Test getting complete paper info."""
        paper_id = "test_paper_123"
        metadata = {
            "paper_id": paper_id,
            "filename": "test.pdf",
            "category": "llm-agents",
            "status": "completed",
            "upload_time": "2024-01-15T14:30:22Z",
            "workflows": {
                "extract": {"status": "completed"},
                "translate": {"status": "completed"},
                "heartfelt": {"status": "completed"},
            },
        }

        papers_dir = temp_dir / "papers"
        source_path = papers_dir / "source/test/test.pdf"
        source_path.exists = lambda: True
        # Mock stat().st_size
        source_path.stat = lambda: type("stat", (), {"st_size": 1024000})()

        with patch.object(paper_service, "_get_source_path", return_value=source_path):
            with patch.object(
                paper_service, "_get_metadata", new_callable=AsyncMock
            ) as mock_get_meta:
                mock_get_meta.return_value = metadata

                result = await paper_service.get_paper_info(paper_id)

                assert isinstance(result, dict)
                assert result["paper_id"] == paper_id
                assert result["filename"] == "test.pdf"
                assert result["size"] == 1024000
                assert result["category"] == "llm-agents"
                assert result["status"] == "completed"

    @pytest.mark.asyncio
    async def test_update_paper_metadata(self, paper_service):
        """Test updating paper metadata."""
        paper_id = "test_paper_123"
        updates = {
            "status": "completed",
            "workflows": {
                "extract": {"status": "completed", "progress": 100},
                "translate": {"status": "completed", "progress": 100},
            },
        }

        with patch.object(
            paper_service, "_load_metadata", new_callable=AsyncMock
        ) as mock_load:
            mock_load.return_value = {
                "paper_id": paper_id,
                "status": "processing",
                "workflows": {},
            }

            with patch.object(paper_service, "_save_metadata", new_callable=AsyncMock):
                result = await paper_service.update_paper_metadata(paper_id, updates)

                assert result is True
