"""Skill implementation for Claude Agent Skills fallback."""

import logging
import os
import re
from pathlib import Path
from typing import Any

import anthropic
import httpx
import pdfplumber
from bs4 import BeautifulSoup

try:
    from marko.ext.gfm import GFM
except ImportError:
    GFM = None

logger = logging.getLogger(__name__)


class SkillInvoker:
    """Fallback skill implementation using available Python packages."""

    def __init__(self):
        """Initialize the skill invoker."""
        self.anthropic_client = None
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if api_key:
            self.anthropic_client = anthropic.Anthropic(api_key=api_key)

        # Registry of available skills
        self.skill_registry = {
            "pdf-reader": self._handle_pdf_reader,
            "web-translator": self._handle_web_translator,
            "zh-translator": self._handle_zh_translator,
            "doc-translator": self._handle_doc_translator,
            "markdown-formatter": self._handle_markdown_formatter,
            "heartfelt": self._handle_heartfelt,
            "batch-processor": self._handle_batch_processor,
        }

    async def call_skill(
        self, skill_name: str, params: dict[str, Any]
    ) -> dict[str, Any]:
        """Call a skill by name.

        Args:
            skill_name: Name of the skill to call
            params: Parameters to pass to the skill

        Returns:
            Skill execution result with success status and data or error
        """
        handler = self.skill_registry.get(skill_name)
        if not handler:
            return {
                "success": False,
                "error": f"Unknown skill: {skill_name}",
                "error_type": "SkillNotFoundError",
            }

        try:
            return await handler(params)
        except Exception as e:
            logger.error(f"Error executing skill {skill_name}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__,
            }

    async def _handle_pdf_reader(self, params: dict[str, Any]) -> dict[str, Any]:
        """Handle PDF reading and conversion to Markdown.

        Args:
            params: Dictionary containing:
                - file_path or url: Path or URL to PDF file
                - extract_images: Whether to extract images (default: True)
                - extract_tables: Whether to extract tables (default: True)
                - extract_formulas: Whether to extract formulas (default: True)
                - page_range: Optional [start, end] page range

        Returns:
            Dictionary with success status and extracted content
        """
        file_path = (
            params.get("file_path")
            or params.get("url")
            or params.get("pdf_path")
            or params.get("pdf_source")
        )
        if not file_path:
            return {
                "success": False,
                "error": "No file_path, url, or pdf_source provided",
                "error_type": "ValueError",
            }

        # Handle URLs by downloading first
        if file_path.startswith(("http://", "https://")):
            # Download PDF from URL
            async with httpx.AsyncClient() as client:
                response = await client.get(file_path)
                response.raise_for_status()
                # Save to temporary file
                temp_path = Path("/tmp") / f"temp_{os.getpid()}.pdf"
                with open(temp_path, "wb") as f:
                    f.write(response.content)
                file_path = str(temp_path)
                cleanup_temp = True
        else:
            # Convert relative to absolute path
            if not os.path.isabs(file_path):
                file_path = os.path.abspath(file_path)
            cleanup_temp = False

        try:
            # Extract content using pdfplumber for better text extraction
            content_parts = []
            metadata = {}
            assets = {"images": [], "tables": 0, "formulas": 0}

            with pdfplumber.open(file_path) as pdf:
                # Extract metadata
                if hasattr(pdf, "metadata") and pdf.metadata:
                    metadata = {
                        "title": pdf.metadata.get("Title", ""),
                        "author": pdf.metadata.get("Author", ""),
                        "creator": pdf.metadata.get("Creator", ""),
                        "producer": pdf.metadata.get("Producer", ""),
                        "creation_date": str(pdf.metadata.get("CreationDate", "")),
                        "modification_date": str(pdf.metadata.get("ModDate", "")),
                    }

                # Get page range
                page_range = params.get("page_range", [0, len(pdf.pages)])
                start_page = max(0, page_range[0] if page_range else 0)
                end_page = min(
                    len(pdf.pages), page_range[1] + 1 if page_range else len(pdf.pages)
                )

                total_words = 0
                for i, page in enumerate(pdf.pages[start_page:end_page]):
                    page_num = start_page + i + 1
                    text = page.extract_text() or ""

                    # Add page header
                    content_parts.append(f"\n\n## Page {page_num}\n\n")

                    # Add extracted text
                    if text.strip():
                        content_parts.append(text)
                        total_words += len(text.split())

                    # Extract tables if requested
                    if params.get("extract_tables", True):
                        tables = page.extract_tables()
                        for table in tables:
                            if table:
                                assets["tables"] += 1
                                # Convert table to markdown
                                markdown_table = self._convert_table_to_markdown(table)
                                content_parts.append(f"\n\n{markdown_table}\n")

                # Combine all content
                full_content = "\n".join(content_parts)

                # Add metadata header
                if metadata:
                    metadata_header = "\n## Document Metadata\n\n"
                    for key, value in metadata.items():
                        if value:
                            metadata_header += f"- **{key.title()}**: {value}\n"
                    full_content = metadata_header + "\n" + full_content

            # Cleanup temp file if downloaded from URL
            if cleanup_temp:
                os.unlink(file_path)

            return {
                "success": True,
                "data": {
                    "content": full_content,
                    "markdown": full_content,  # Alias for compatibility
                    "metadata": metadata,
                    "images": assets.get("images", []),
                    "tables": [
                        f"Table {i + 1}" for i in range(assets.get("tables", 0))
                    ],
                    "formulas": [
                        f"Formula {i + 1}" for i in range(assets.get("formulas", 0))
                    ],
                    "page_count": end_page - start_page,
                },
                "metadata": {
                    **metadata,
                    "page_count": end_page - start_page,
                    "total_words": total_words,
                },
                "assets": assets,
                "statistics": {
                    "total_words": total_words,
                    "total_paragraphs": len(
                        [p for p in full_content.split("\n\n") if p.strip()]
                    ),
                    "processing_time": "N/A",  # Could add timing if needed
                },
            }

        except Exception as e:
            if cleanup_temp and os.path.exists(file_path):
                os.unlink(file_path)
            raise e

    async def _handle_web_translator(self, params: dict[str, Any]) -> dict[str, Any]:
        """Handle web page content extraction and conversion to Markdown.

        Args:
            params: Dictionary containing:
                - url: URL of the web page

        Returns:
            Dictionary with success status and extracted content
        """
        url = params.get("url")
        if not url:
            return {
                "success": False,
                "error": "No url provided",
                "error_type": "ValueError",
            }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, follow_redirects=True)
                response.raise_for_status()
                html_content = response.text

            # Parse HTML and extract main content
            soup = BeautifulSoup(html_content, "html.parser")

            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()

            # Extract title
            title = soup.find("title")
            title = title.get_text().strip() if title else ""

            # Extract meta description
            description = soup.find("meta", attrs={"name": "description"})
            description = description.get("content", "") if description else ""

            # Extract main content
            # Try to find main content area
            main_content = (
                soup.find("main")
                or soup.find("article")
                or soup.find("div", class_=re.compile(r"content|main|article", re.I))
            )

            if not main_content:
                # Fallback to body
                main_content = soup.find("body") or soup

            # Convert to text while preserving some structure
            content_parts = []

            # Add metadata header
            if title:
                content_parts.append(f"# {title}\n")
            if description:
                content_parts.append(f"*{description}*\n\n")

            # Process content elements
            for element in main_content.find_all(
                [
                    "h1",
                    "h2",
                    "h3",
                    "h4",
                    "h5",
                    "h6",
                    "p",
                    "ul",
                    "ol",
                    "blockquote",
                    "pre",
                ]
            ):
                tag_name = element.name

                if tag_name in ["h1", "h2", "h3", "h4", "h5", "h6"]:
                    level = int(tag_name[1])
                    content_parts.append(
                        f"\n{'#' * level} {element.get_text().strip()}\n"
                    )
                elif tag_name == "p":
                    text = element.get_text().strip()
                    if text:
                        content_parts.append(f"{text}\n")
                elif tag_name in ["ul", "ol"]:
                    items = []
                    for li in element.find_all("li", recursive=False):
                        items.append(f"- {li.get_text().strip()}")
                    content_parts.append(f"\n{chr(10).join(items)}\n")
                elif tag_name == "blockquote":
                    text = element.get_text().strip()
                    if text:
                        content_parts.append(f"\n> {text}\n")
                elif tag_name == "pre":
                    text = element.get_text()
                    content_parts.append(f"\n```\n{text}\n```\n")

            # Extract links
            links = []
            for link in soup.find_all("a", href=True):
                href = link["href"]
                if href.startswith("http"):
                    links.append({"text": link.get_text().strip(), "url": href})

            full_content = "\n".join(content_parts)

            return {
                "success": True,
                "content": full_content,
                "metadata": {
                    "title": title,
                    "description": description,
                    "url": url,
                },
                "assets": {
                    "links": links[:10],  # Limit to first 10 links
                },
                "statistics": {
                    "total_words": len(full_content.split()),
                    "total_paragraphs": len(
                        [p for p in full_content.split("\n\n") if p.strip()]
                    ),
                },
            }

        except Exception as e:
            logger.error(f"Error processing web page {url}: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to process web page: {str(e)}",
                "error_type": type(e).__name__,
            }

    async def _handle_zh_translator(self, params: dict[str, Any]) -> dict[str, Any]:
        """Handle translation to Chinese using Claude API.

        Args:
            params: Dictionary containing:
                - content: Markdown content to translate
                - preserve_formatting: Whether to preserve formatting (default: True)

        Returns:
            Dictionary with success status and translated content
        """
        content = params.get("content")
        if not content:
            return {
                "success": False,
                "error": "No content provided",
                "error_type": "ValueError",
            }

        if not self.anthropic_client:
            return {
                "success": False,
                "error": "Anthropic API key not configured",
                "error_type": "ConfigurationError",
            }

        try:
            # Create translation prompt
            prompt = f"""Please translate the following Markdown content to Chinese while preserving:

1. All formatting (headers, lists, bold, italic, etc.)
2. Code blocks and inline code
3. URLs and file paths
4. LaTeX mathematical formulas
5. HTML tags
6. Special characters and emojis

Do not translate:
- Code blocks
- URLs
- File paths
- Technical terms that should remain in English

Here is the content to translate:

{content}

Please provide only the translated content without any explanations."""

            # Call Claude API
            response = self.anthropic_client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=4000,
                messages=[{"role": "user", "content": prompt}],
            )

            translated_content = response.content[0].text

            return {
                "success": True,
                "data": translated_content,  # Translation agent expects data field
                "content": translated_content,
                "metadata": {
                    "original_language": "auto-detected",
                    "target_language": "zh-CN",
                },
            }

        except Exception as e:
            logger.error(f"Translation error: {str(e)}")
            return {
                "success": False,
                "error": f"Translation failed: {str(e)}",
                "error_type": type(e).__name__,
            }

    async def _handle_doc_translator(self, params: dict[str, Any]) -> dict[str, Any]:
        """Handle document translation workflow.

        Args:
            params: Dictionary containing PDF file parameters

        Returns:
            Dictionary with success status and translated document
        """
        # First extract content from PDF
        pdf_result = await self._handle_pdf_reader(params)
        if not pdf_result["success"]:
            return pdf_result

        # Then translate the extracted content
        translate_params = {
            "content": pdf_result["content"],
            "preserve_formatting": True,
        }
        translate_result = await self._handle_zh_translator(translate_params)
        if not translate_result["success"]:
            return translate_result

        # Combine results
        return {
            "success": True,
            "content": translate_result["content"],
            "metadata": {
                **pdf_result.get("metadata", {}),
                **translate_result.get("metadata", {}),
                "original_content": pdf_result["content"],
            },
            "assets": pdf_result.get("assets", {}),
            "statistics": translate_result.get("statistics", {}),
        }

    async def _handle_markdown_formatter(
        self, params: dict[str, Any]
    ) -> dict[str, Any]:
        """Handle Markdown formatting.

        Args:
            params: Dictionary containing:
                - content: Raw content to format
                - options: Formatting options

        Returns:
            Dictionary with success status and formatted content
        """
        content = params.get("content", "")
        options = params.get("options", {})

        # Basic formatting - in a real implementation, this would be more sophisticated
        formatted_content = content

        # Apply basic formatting rules
        if options.get("fix_headers", True):
            # Ensure headers have proper spacing
            formatted_content = re.sub(
                r"([^\n])\n(#+\s)", r"\1\n\n\2", formatted_content
            )

        if options.get("fix_lists", True):
            # Ensure list items have proper spacing
            formatted_content = re.sub(
                r"([^\n])\n(-|\*|\d+\.)\s", r"\1\n\n\2 ", formatted_content
            )

        if options.get("fix_code_blocks", True):
            # Ensure code blocks are properly formatted
            formatted_content = re.sub(
                r"```(\w+)?\n", lambda m: f"```{m.group(1) or ''}\n", formatted_content
            )

        return {
            "success": True,
            "content": formatted_content,
            "metadata": {
                "original_length": len(content),
                "formatted_length": len(formatted_content),
            },
        }

    async def _handle_heartfelt(self, params: dict[str, Any]) -> dict[str, Any]:
        """Handle heartfelt analysis of documents.

        Args:
            params: Dictionary containing:
                - content: Document content to analyze
                - analysis_type: Type of analysis to perform

        Returns:
            Dictionary with success status and analysis results
        """
        content = params.get("content", "")
        analysis_type = params.get("analysis_type", "comprehensive")

        if not self.anthropic_client:
            return {
                "success": False,
                "error": "Anthropic API key not configured",
                "error_type": "ConfigurationError",
            }

        try:
            # Create analysis prompt
            if analysis_type == "comprehensive":
                prompt = f"""Please provide a heartfelt, comprehensive analysis of the following document content. Include:

1. Key themes and main ideas
2. Emotional tone and sentiment
3. Important insights and takeaways
4. Personal reflections and connections
5. Actionable conclusions

Content to analyze:

{content}

Please provide a thoughtful, human-like analysis that goes beyond simple summary."""
            else:
                prompt = f"""Please analyze the following document content from a heartfelt perspective:

{content}

Focus on the emotional and human aspects of the content."""

            # Call Claude API
            response = self.anthropic_client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}],
            )

            analysis = response.content[0].text

            return {
                "success": True,
                "content": analysis,
                "metadata": {
                    "analysis_type": analysis_type,
                    "original_length": len(content),
                },
            }

        except Exception as e:
            logger.error(f"Heartfelt analysis error: {str(e)}")
            return {
                "success": False,
                "error": f"Analysis failed: {str(e)}",
                "error_type": type(e).__name__,
            }

    async def _handle_batch_processor(self, params: dict[str, Any]) -> dict[str, Any]:
        """Handle batch processing of multiple items.

        Args:
            params: Dictionary containing:
                - items: List of items to process
                - skill: Skill to apply to each item
                - skill_params: Parameters for the skill

        Returns:
            Dictionary with success status and batch results
        """
        items = params.get("items", [])
        skill_name = params.get("skill")
        skill_params = params.get("skill_params", {})

        if not items:
            return {
                "success": False,
                "error": "No items provided for batch processing",
                "error_type": "ValueError",
            }

        if not skill_name:
            return {
                "success": False,
                "error": "No skill specified for batch processing",
                "error_type": "ValueError",
            }

        # Process items in batches
        batch_size = params.get("batch_size", 5)
        results = []

        for i in range(0, len(items), batch_size):
            batch = items[i : i + batch_size]
            batch_results = []

            for item in batch:
                # Prepare skill parameters with current item
                item_params = skill_params.copy()
                if isinstance(item, dict):
                    item_params.update(item)
                else:
                    item_params["content"] = str(item)

                # Call the skill
                result = await self.call_skill(skill_name, item_params)
                batch_results.append(result)

            results.extend(batch_results)

        # Count successes and failures
        success_count = sum(1 for r in results if r.get("success", False))
        error_count = len(results) - success_count

        return {
            "success": True,
            "results": results,
            "summary": {
                "total_items": len(items),
                "successful": success_count,
                "failed": error_count,
                "success_rate": success_count / len(results) if results else 0,
            },
        }

    def _convert_table_to_markdown(self, table: list[list[str]]) -> str:
        """Convert a table to Markdown format.

        Args:
            table: 2D list representing the table

        Returns:
            Markdown formatted table
        """
        if not table:
            return ""

        # Clean cell values
        cleaned_table = []
        for row in table:
            cleaned_row = [str(cell) if cell is not None else "" for cell in row]
            cleaned_table.append(cleaned_row)

        if not cleaned_table:
            return ""

        # Calculate column widths
        col_widths = []
        for col in range(len(cleaned_table[0])):
            max_width = max(len(str(row[col])) for row in cleaned_table)
            col_widths.append(max_width)

        # Build markdown table
        markdown_rows = []

        # Header row
        header = " | ".join(
            str(cell).ljust(col_widths[i]) for i, cell in enumerate(cleaned_table[0])
        )
        markdown_rows.append(f"| {header} |")

        # Separator row
        separator = " | ".join("-" * col_widths[i] for i in range(len(col_widths)))
        markdown_rows.append(f"| {separator} |")

        # Data rows
        for row in cleaned_table[1:]:
            data_row = " | ".join(
                str(cell).ljust(col_widths[i]) for i, cell in enumerate(row)
            )
            markdown_rows.append(f"| {data_row} |")

        return "\n".join(markdown_rows)
