"""Unit tests for WorkflowAgent."""

import asyncio
from unittest.mock import AsyncMock, patch

import pytest

from agents.claude.base import BaseAgent
from agents.claude.workflow_agent import WorkflowAgent
from tests.agents.fixtures.mocks.mock_file_operations import (
    mock_file_manager,
    patch_file_operations,
)


@pytest.mark.unit
class TestWorkflowAgent:
    """Test cases for WorkflowAgent."""

    @pytest.fixture
    def workflow_agent(self, temp_dir):
        """Create a WorkflowAgent instance for testing."""
        config = {
            "papers_dir": str(temp_dir / "papers"),
            "max_retries": 3,
            "timeout": 30,
        }
        agent = WorkflowAgent(config)

        # Replace sub-agents with mocks
        agent.pdf_agent = AsyncMock()
        agent.translation_agent = AsyncMock()
        agent.heartfelt_agent = AsyncMock()

        # Mock save methods
        agent._save_workflow_results = AsyncMock()
        agent._save_extract_result = AsyncMock()
        agent._save_translate_result = AsyncMock()
        agent._save_heartfelt_result = AsyncMock()
        # Note: Don't mock _async_heartfelt_analysis as we need to test the real method

        return agent

    @pytest.fixture
    def test_paper_path(self, temp_dir):
        """Create a test paper file."""
        pdf_path = temp_dir / "test_paper.pdf"
        pdf_path.write_bytes(b"%PDF-1.4\nTest PDF content")
        return pdf_path

    @pytest.mark.asyncio
    @patch.object(BaseAgent, "call_skill", return_value={"success": True, "data": {}})
    async def test_full_workflow_success(
        self, mock_call_skill, workflow_agent, test_paper_path
    ):
        """Test successful full workflow execution."""
        paper_id = "test_paper_123"
        input_data = {
            "source_path": str(test_paper_path),
            "workflow": "full",
            "paper_id": paper_id,
        }

        # Setup mocks
        workflow_agent.pdf_agent.extract_content.return_value = {
            "success": True,
            "data": {
                "content": "Extracted PDF content...",
                "metadata": {"pages": 10},
                "images": [],
                "formulas": [],
            },
        }

        workflow_agent.translation_agent.translate.return_value = {
            "success": True,
            "data": {"translated_content": "翻译后的内容...", "quality_score": 0.95},
        }

        # Mock heartfelt agent analyze method to avoid ImportError
        workflow_agent.heartfelt_agent.analyze.return_value = {
            "success": True,
            "data": {"analysis": "Deep analysis complete..."},
        }

        with patch_file_operations():
            mock_file_manager.add_file(str(test_paper_path), b"PDF content")
            mock_file_manager.exists(str(test_paper_path))

            result = await workflow_agent.process(input_data)

            # Give a moment for the async heartfelt analysis to complete
            await asyncio.sleep(0.1)

            assert result["success"] is True
            assert result["workflow"] == "full"
            assert result["status"] == "completed"
            assert "extract_result" in result
            assert "translate_result" in result

            # Verify sub-agents were called
            workflow_agent.pdf_agent.extract_content.assert_called_once()
            workflow_agent.translation_agent.translate.assert_called_once()
            workflow_agent.heartfelt_agent.analyze.assert_called_once()
            workflow_agent._save_workflow_results.assert_called_once()

    @pytest.mark.asyncio
    async def test_extract_workflow_success(self, workflow_agent, test_paper_path):
        """Test successful extract-only workflow."""
        paper_id = "test_paper_123"
        input_data = {
            "source_path": str(test_paper_path),
            "workflow": "extract_only",
            "paper_id": paper_id,
        }

        workflow_agent.pdf_agent.extract_content.return_value = {
            "success": True,
            "data": {"content": "Extracted content...", "metadata": {"pages": 10}},
        }

        with patch_file_operations():
            mock_file_manager.add_file(str(test_paper_path), b"PDF content")
            mock_file_manager.exists(str(test_paper_path))

            result = await workflow_agent.process(input_data)

            assert result["success"] is True
            assert result["workflow"] == "extract_only"
            assert result["status"] == "completed"
            assert "data" in result
            assert result["data"]["content"] == "Extracted content..."

            workflow_agent.pdf_agent.extract_content.assert_called_once_with(
                {
                    "file_path": str(test_paper_path),
                    "options": {
                        "extract_images": True,
                        "extract_tables": True,
                        "extract_formulas": True,
                    },
                }
            )
            workflow_agent._save_extract_result.assert_called_once_with(
                paper_id, result["data"]
            )

    @pytest.mark.asyncio
    async def test_translate_workflow_success(self, workflow_agent, test_paper_path):
        """Test successful translate-only workflow."""
        paper_id = "test_paper_123"
        input_data = {
            "source_path": str(test_paper_path),
            "workflow": "translate_only",
            "paper_id": paper_id,
        }

        # Setup mocks for extract and translate
        workflow_agent.pdf_agent.extract_content.return_value = {
            "success": True,
            "data": {"content": "Original content...", "metadata": {"pages": 10}},
        }

        workflow_agent.translation_agent.translate.return_value = {
            "success": True,
            "data": {"translated_content": "翻译后的内容...", "quality_score": 0.95},
        }

        with patch_file_operations():
            mock_file_manager.add_file(str(test_paper_path), b"PDF content")
            mock_file_manager.exists(str(test_paper_path))

            result = await workflow_agent.process(input_data)

            assert result["success"] is True
            assert result["workflow"] == "translate_only"
            assert result["status"] == "completed"

            # Verify both agents were called
            workflow_agent.pdf_agent.extract_content.assert_called_once()
            workflow_agent.translation_agent.translate.assert_called_once()
            workflow_agent._save_translate_result.assert_called_once()

    @pytest.mark.asyncio
    async def test_heartfelt_workflow_success(self, workflow_agent, test_paper_path):
        """Test successful heartfelt-only workflow."""
        paper_id = "test_paper_123"
        input_data = {
            "source_path": str(test_paper_path),
            "workflow": "heartfelt_only",
            "paper_id": paper_id,
        }

        workflow_agent.pdf_agent.extract_content.return_value = {
            "success": True,
            "data": {"content": "Content for analysis...", "metadata": {"pages": 10}},
        }

        workflow_agent.heartfelt_agent.analyze.return_value = {
            "success": True,
            "data": {"summary": "论文摘要...", "insights": ["洞见1", "洞见2"]},
        }

        with patch_file_operations():
            mock_file_manager.add_file(str(test_paper_path), b"PDF content")
            mock_file_manager.exists(str(test_paper_path))

            result = await workflow_agent.process(input_data)

            assert result["success"] is True
            assert result["workflow"] == "heartfelt_only"
            assert result["status"] == "completed"

            workflow_agent.pdf_agent.extract_content.assert_called_once()
            workflow_agent.heartfelt_agent.analyze.assert_called_once()
            workflow_agent._save_heartfelt_result.assert_called_once()

    @pytest.mark.asyncio
    async def test_invalid_workflow(self, workflow_agent, test_paper_path):
        """Test handling of invalid workflow type."""
        input_data = {
            "source_path": str(test_paper_path),
            "workflow": "invalid_workflow",
        }

        with patch_file_operations():
            mock_file_manager.add_file(str(test_paper_path), b"PDF content")
            mock_file_manager.exists(str(test_paper_path))

            result = await workflow_agent.process(input_data)

            assert result["success"] is False
            assert "Unsupported workflow" in result["error"]

    @pytest.mark.asyncio
    async def test_file_not_found(self, workflow_agent, temp_dir):
        """Test handling of non-existent file."""
        input_data = {
            "source_path": "/nonexistent/file.pdf",
            "workflow": "extract_only",
        }

        with patch_file_operations():
            result = await workflow_agent.process(input_data)

            assert result["success"] is False
            assert "Source file not found" in result["error"]

    @pytest.mark.asyncio
    async def test_extract_failure(self, workflow_agent, test_paper_path):
        """Test handling of extraction failure."""
        input_data = {"source_path": str(test_paper_path), "workflow": "extract_only"}

        # Mock extraction failure
        workflow_agent.pdf_agent.extract_content.return_value = {
            "success": False,
            "error": "Extraction failed",
        }

        with patch_file_operations():
            mock_file_manager.add_file(str(test_paper_path), b"PDF content")
            mock_file_manager.exists(str(test_paper_path))

            result = await workflow_agent.process(input_data)

            assert result["success"] is False
            assert result["error"] == "Extraction failed"

    @pytest.mark.asyncio
    async def test_translate_failure(self, workflow_agent, test_paper_path):
        """Test handling of translation failure in translate workflow."""
        input_data = {"source_path": str(test_paper_path), "workflow": "translate_only"}

        workflow_agent.pdf_agent.extract_content.return_value = {
            "success": True,
            "data": {"content": "Content..."},
        }

        # Mock translation failure
        workflow_agent.translation_agent.translate.return_value = {
            "success": False,
            "error": "Translation failed",
        }

        with patch_file_operations():
            mock_file_manager.add_file(str(test_paper_path), b"PDF content")
            mock_file_manager.exists(str(test_paper_path))

            result = await workflow_agent.process(input_data)

            assert result["success"] is False
            assert result["error"] == "Translation failed"

    @pytest.mark.asyncio
    async def test_validation_failure(self, workflow_agent, temp_dir):
        """Test input validation failure."""
        # Missing required fields
        input_data = {
            "source_path": "",  # Empty path
            "workflow": "full",
        }

        result = await workflow_agent.process(input_data)

        assert result["success"] is False
        assert result["error"] == "Invalid input data"

    @pytest.mark.asyncio
    async def test_workflow_with_options(self, workflow_agent, test_paper_path):
        """Test workflow execution with custom options."""
        paper_id = "test_paper_123"
        options = {
            "extract_images": False,
            "translation_style": "casual",
            "analysis_depth": "brief",
        }

        input_data = {
            "source_path": str(test_paper_path),
            "workflow": "full",
            "paper_id": paper_id,
            "options": options,
        }

        workflow_agent.pdf_agent.extract_content.return_value = {
            "success": True,
            "data": {"content": "Content..."},
        }

        workflow_agent.translation_agent.translate.return_value = {
            "success": True,
            "data": {"translated_content": "Translated..."},
        }

        with patch_file_operations():
            mock_file_manager.add_file(str(test_paper_path), b"PDF content")
            mock_file_manager.exists(str(test_paper_path))

            result = await workflow_agent.process(input_data)

            assert result["success"] is True

            # Verify options were passed correctly
            workflow_agent.pdf_agent.extract_content.assert_called_once()
            call_args = workflow_agent.pdf_agent.extract_content.call_args[0][0]
            assert call_args["file_path"] == str(test_paper_path)
            assert "options" in call_args

    @pytest.mark.asyncio
    async def test_async_heartfelt_analysis(self, workflow_agent, temp_dir):
        """Test async heartfelt analysis task creation."""
        source_path = "/test/paper.pdf"
        extract_data = {"content": "Content..."}
        translate_data = {"content": "Translated..."}
        paper_id = "test_paper"

        # Mock the heartfelt analysis - it's an async method
        workflow_agent.heartfelt_agent.analyze = AsyncMock(
            return_value={
                "success": True,
                "data": {"summary": "Analysis..."},
            }
        )

        # Mock saving result
        workflow_agent._save_heartfelt_result = AsyncMock()

        # Call the method directly
        await workflow_agent._async_heartfelt_analysis(
            source_path, extract_data, translate_data, paper_id
        )

        # Verify the analysis was called
        workflow_agent.heartfelt_agent.analyze.assert_called_once_with(
            {
                "content": "Content...",
                "translation": "Translated...",
                "paper_id": "test_paper",
            }
        )
        workflow_agent._save_heartfelt_result.assert_called_once()

    def test_validate_input_success(self, workflow_agent, temp_dir):
        """Test successful input validation."""
        valid_input = {"source_path": "/test/paper.pdf", "workflow": "full"}

        result = asyncio.run(workflow_agent.validate_input(valid_input))
        assert result is True

    def test_validate_input_failure(self, workflow_agent, temp_dir):
        """Test input validation failure."""
        invalid_input = {
            "source_path": "",  # Missing or empty
            "workflow": "full",
        }

        result = asyncio.run(workflow_agent.validate_input(invalid_input))
        assert result is False

    @pytest.mark.asyncio
    async def test_save_workflow_results(self, workflow_agent, temp_dir):
        """Test saving workflow results."""
        paper_id = "test_paper"
        extract_result = {"content": "Extracted...", "metadata": {"pages": 10}}
        translate_result = {
            "translated_content": "Translated...",
            "quality_score": 0.95,
        }

        with patch_file_operations():
            output_dir = temp_dir / paper_id
            mock_file_manager.mkdir(str(output_dir), parents=True, exist_ok=True)

            await workflow_agent._save_workflow_results(
                paper_id, extract_result, translate_result
            )

            # Verify files were created (mocked)
            assert mock_file_manager.exists(f"{output_dir}/extracted.json")
            assert mock_file_manager.exists(f"{output_dir}/translated.md")

    @pytest.mark.asyncio
    async def test_batch_process_papers(self, workflow_agent, temp_dir):
        """Test batch processing of multiple papers."""
        if not hasattr(workflow_agent, "batch_process_papers"):
            pytest.skip("batch_process_papers method not implemented")

        paper_paths = ["/test/paper1.pdf", "/test/paper2.pdf", "/test/paper3.pdf"]

        # Mock individual processing
        with patch.object(workflow_agent, "process") as mock_process:
            mock_process.side_effect = [
                {"success": True, "paper_id": "paper1"},
                {"success": True, "paper_id": "paper2"},
                {"success": False, "error": "Processing failed"},
            ]

            with patch_file_operations():
                # Add files to mock file system
                for path in paper_paths[:2]:
                    mock_file_manager.add_file(path, b"PDF content")
                    mock_file_manager.exists(path)

                result = await workflow_agent.batch_process_papers(
                    paper_paths, "extract_only"
                )

                assert len(result["results"]) == 3
                assert result["success_count"] == 2
                assert result["failure_count"] == 1

    @pytest.mark.asyncio
    async def test_get_workflow_status(self, workflow_agent, temp_dir):
        """Test getting workflow status."""
        if not hasattr(workflow_agent, "get_workflow_status"):
            pytest.skip("get_workflow_status method not implemented")

        paper_id = "test_paper"

        with patch.object(
            workflow_agent, "_load_metadata", new_callable=AsyncMock
        ) as mock_load:
            mock_load.return_value = {
                "status": "processing",
                "progress": 50,
                "current_stage": "translation",
            }

            status = await workflow_agent.get_workflow_status(paper_id)

            assert status["status"] == "processing"
            assert status["progress"] == 50
            assert status["current_stage"] == "translation"
