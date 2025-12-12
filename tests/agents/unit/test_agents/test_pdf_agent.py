"""Unit tests for PDFProcessingAgent."""

import os
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from agents.claude.pdf_agent import PDFProcessingAgent


@pytest.mark.unit
class TestPDFProcessingAgent:
    """Test cases for PDFProcessingAgent."""

    @pytest.fixture
    def pdf_agent(self):
        """Create a PDFProcessingAgent instance for testing."""
        return PDFProcessingAgent()

    def test_pdf_agent_initialization(self):
        """Test PDFProcessingAgent initialization."""
        agent = PDFProcessingAgent()
        assert agent.name == "pdf_processor"
        assert agent.config == {}
        assert agent.default_options["extract_images"] is True
        assert agent.default_options["extract_tables"] is True
        assert agent.default_options["extract_formulas"] is True
        assert agent.default_options["output_format"] == "markdown"

    def test_pdf_agent_initialization_with_config(self):
        """Test PDFProcessingAgent initialization with config."""
        config = {"timeout": 60, "max_retries": 5}
        agent = PDFProcessingAgent(config)
        assert agent.name == "pdf_processor"
        assert agent.config == config

    @pytest.mark.asyncio
    async def test_process_no_file_path(self, pdf_agent):
        """Test process without file path."""
        input_data = {"options": {"extract_images": False}}

        result = await pdf_agent.process(input_data)

        assert result["success"] is False
        assert result["error"] == "No file path provided"

    @pytest.mark.asyncio
    async def test_process_file_not_found(self, pdf_agent):
        """Test process with nonexistent file."""
        input_data = {"file_path": "/nonexistent/file.pdf"}

        result = await pdf_agent.process(input_data)

        assert result["success"] is False
        assert "File not found:" in result["error"]

    @pytest.mark.asyncio
    async def test_process_success(self, pdf_agent, temp_dir):
        """Test successful PDF processing."""
        # Create a mock PDF file
        pdf_file = temp_dir / "test.pdf"
        pdf_file.write_bytes(b"%PDF-1.4\nmock pdf content")

        input_data = {"file_path": str(pdf_file)}

        # Mock the extract_content method
        mock_result = {
            "success": True,
            "data": {"content": "Extracted PDF content", "metadata": {"pages": 10}},
        }
        pdf_agent.extract_content = AsyncMock(return_value=mock_result)

        result = await pdf_agent.process(input_data)

        assert result["success"] is True
        assert result["data"] == mock_result["data"]
        pdf_agent.extract_content.assert_called_once()

    @pytest.mark.asyncio
    async def test_process_with_custom_options(self, pdf_agent, temp_dir):
        """Test process with custom options."""
        # Create a mock PDF file
        pdf_file = temp_dir / "test.pdf"
        pdf_file.write_bytes(b"%PDF-1.4\nmock pdf content")

        input_data = {
            "file_path": str(pdf_file),
            "options": {"extract_images": False, "output_format": "json"},
        }

        # Mock the extract_content method
        pdf_agent.extract_content = AsyncMock(
            return_value={"success": True, "data": {}}
        )

        await pdf_agent.process(input_data)

        # Check that options were merged correctly
        call_args = pdf_agent.extract_content.call_args[0][0]
        assert call_args["file_path"] == str(pdf_file)
        assert call_args["options"]["extract_images"] is False  # Custom option
        assert call_args["options"]["extract_tables"] is True  # Default option
        assert call_args["options"]["output_format"] == "json"  # Custom option

    @pytest.mark.asyncio
    async def test_extract_content_file_not_found(self, pdf_agent):
        """Test extract_content with nonexistent file."""
        params = {"file_path": "/nonexistent/file.pdf"}

        # Mock the pdf-reader skill to handle file not found
        with patch.object(pdf_agent, "call_skill") as mock_call_skill:
            mock_call_skill.return_value = {"success": False, "error": "File not found"}

            result = await pdf_agent.extract_content(params)

            assert result["success"] is False
            assert "File not found" in result["error"]

    # @pytest.mark.asyncio
    # async def test_extract_content_success(self, pdf_agent, temp_dir):
    #     """Test successful content extraction."""
    #     # Create a mock PDF file
    #     pdf_file = temp_dir / "test.pdf"
    #     pdf_file.write_bytes(b"%PDF-1.4\nmock pdf content")

    #     params = {
    #         "file_path": str(pdf_file),
    #         "options": {
    #             "extract_images": True,
    #             "extract_tables": True,
    #             "extract_formulas": True,
    #             "output_format": "markdown"
    #         }
    #     }

    #     # Mock the pdf-reader skill
    #     with patch.object(pdf_agent, 'call_skill') as mock_call_skill:
    #         mock_call_skill.return_value = {
    #             "success": True,
    #             "data": {
    #                 "content": "# Extracted Content\n\nThis is the PDF content.",
    #                 "metadata": {
    #                     "title": "Test PDF",
    #                     "author": "Test Author",
    #                     "pages": 10,
    #                     "word_count": 500
    #                 },
    #                 "images": [],
    #                 "tables": [],
    #                 "formulas": []
    #             }
    #         }

    #         result = await pdf_agent.extract_content(params)

    #         assert result["success"] is True
    #         assert "content" in result["data"]
    #         assert "metadata" in result["data"]
    #         assert result["data"]["metadata"]["pages"] == 10

    #         mock_call_skill.assert_called_once_with("pdf-reader", {
    #             "pdf_source": str(pdf_file),
    #             "method": "auto",
    #             "include_metadata": True,
    #             "extract_images": True,
    #             "extract_tables": True,
    #             "extract_formulas": True,
    #             "output_format": "markdown",
    #             "page_range": None
    #         })

    @pytest.mark.asyncio
    async def test_extract_content_skill_failure(self, pdf_agent, temp_dir):
        """Test content extraction when skill call fails."""
        # Create a mock PDF file
        pdf_file = temp_dir / "test.pdf"
        pdf_file.write_bytes(b"%PDF-1.4\nmock pdf content")

        params = {"file_path": str(pdf_file), "options": {"output_format": "markdown"}}

        # Mock failed skill call
        with patch.object(pdf_agent, "call_skill") as mock_call_skill:
            mock_call_skill.return_value = {
                "success": False,
                "error": "PDF processing failed",
            }

            result = await pdf_agent.extract_content(params)

            assert result["success"] is False
            assert "PDF processing failed" in result["error"]

    @pytest.mark.asyncio
    async def test_extract_content_with_partial_options(self, pdf_agent, temp_dir):
        """Test content extraction with partial options."""
        # Create a mock PDF file
        pdf_file = temp_dir / "test.pdf"
        pdf_file.write_bytes(b"%PDF-1.4\nmock pdf content")

        params = {
            "file_path": str(pdf_file),
            "options": {
                "extract_images": False,
                # Other options should use defaults
            },
        }

        # Mock the data extractor skill
        with patch.object(pdf_agent, "call_skill") as mock_call_skill:
            mock_call_skill.return_value = {"success": True, "data": {}}

            await pdf_agent.extract_content(params)

            # Check the call parameters
            call_args = mock_call_skill.call_args[0][1]
            assert call_args["extract_images"] is False
            assert call_args["extract_tables"] is True  # Default
            assert call_args["extract_formulas"] is True  # Default
            assert call_args["output_format"] == "markdown"  # Default

    @pytest.mark.asyncio
    async def test_validate_input(self, pdf_agent):
        """Test input validation."""
        # Valid input
        valid_input = {"file_path": "/path/to/file.pdf", "options": {}}
        assert await pdf_agent.validate_input(valid_input) is True

        # Invalid input (not a dict)
        assert await pdf_agent.validate_input("not a dict") is False
        assert await pdf_agent.validate_input(None) is False
        assert await pdf_agent.validate_input(123) is False

    # @pytest.mark.asyncio
    # async def test_log_processing(self, pdf_agent):
    #     """Test processing log logging."""
    #     input_data = {"file_path": "/test/file.pdf"}
    #     output_data = {"success": True, "data": {"content": "extracted"}}

    #     with patch("agents.claude.pdf_agent.logger") as mock_logger:
    #         await pdf_agent.log_processing(input_data, output_data)

    #         mock_logger.info.assert_called_once()
    #         log_message = mock_logger.info.call_args[0][0]
    #         assert "pdf_processor processed:" in log_message
    #         assert "/test/file.pdf" in log_message
    #         assert "True" in log_message

    @pytest.mark.asyncio
    async def test_batch_call_skill(self, pdf_agent):
        """Test batch skill calls."""
        calls = [
            {"skill": "skill1", "params": {}},
            {"skill": "skill2", "params": {}},
        ]

        # Mock the skill calls
        pdf_agent.call_skill = AsyncMock(
            side_effect=[
                {"success": True, "data": "result1"},
                {"success": True, "data": "result2"},
            ]
        )

        results = await pdf_agent.batch_call_skill(calls)

        assert len(results) == 2
        assert results[0]["success"] is True
        assert results[1]["success"] is True
        assert results[0]["data"] == "result1"
        assert results[1]["data"] == "result2"

    # @pytest.mark.asyncio
    # async def test_extract_content_with_url(self, pdf_agent):
    #     """Test content extraction with URL."""
    #     params = {
    #         "file_path": "https://example.com/document.pdf",
    #         "options": {"output_format": "markdown"}
    #     }

    #     # Mock the data extractor skill
    #     with patch.object(pdf_agent, 'call_skill') as mock_call_skill:
    #         mock_call_skill.return_value = {
    #             "success": True,
    #             "data": {"content": "Extracted from URL", "metadata": {}}
    #         }

    #         result = await pdf_agent.extract_content(params)

    #         assert result["success"] is True
    #         mock_call_skill.assert_called_once_with("data-extractor", {
    #             "action": "convert_pdf_to_markdown",
    #             "pdf_source": "https://example.com/document.pdf",
    #             "extract_images": True,
    #             "extract_tables": True,
    #             "extract_formulas": True,
    #             "output_format": "markdown"
    #         })

    @pytest.mark.asyncio
    async def test_process_preserves_default_options(self, pdf_agent, temp_dir):
        """Test that process preserves default options when not overridden."""
        # Create a mock PDF file
        pdf_file = temp_dir / "test.pdf"
        pdf_file.write_bytes(b"%PDF-1.4\nmock pdf content")

        input_data = {"file_path": str(pdf_file)}

        # Mock the extract_content method
        pdf_agent.extract_content = AsyncMock(
            return_value={"success": True, "data": {}}
        )

        await pdf_agent.process(input_data)

        # Check that default options were preserved
        call_args = pdf_agent.extract_content.call_args[0][0]
        options = call_args["options"]
        assert options["extract_images"] is True
        assert options["extract_tables"] is True
        assert options["extract_formulas"] is True
        assert options["output_format"] == "markdown"
