"""Workflow Agent - 负责任务分解和流程编排."""

import asyncio
import logging
import os
from pathlib import Path
from typing import Any

from .base import BaseAgent
from .heartfelt_agent import HeartfeltAgent
from .pdf_agent import PDFProcessingAgent
from .translation_agent import TranslationAgent

logger = logging.getLogger(__name__)


class WorkflowAgent(BaseAgent):
    """工作流协调 Agent - 负责任务分解和流程编排."""

    def __init__(self, config: dict[str, Any] | None = None):
        """初始化 WorkflowAgent.

        Args:
            config: 配置参数
        """
        super().__init__("workflow", config)
        self.papers_dir = Path(config.get("papers_dir", "papers"))
        self.pdf_agent = PDFProcessingAgent(config)
        self.translation_agent = TranslationAgent(config)
        self.heartfelt_agent = HeartfeltAgent(config)

    async def process(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """处理文档的主入口.

        Args:
            input_data: 包含 source_path 和 workflow 字段

        Returns:
            处理结果
        """
        # 验证输入
        if not await self.validate_input(input_data):
            return {"success": False, "error": "Invalid input data"}

        source_path = input_data.get("source_path")
        workflow = input_data.get("workflow", "full")
        paper_id = input_data.get("paper_id")

        if not source_path or not os.path.exists(source_path):
            return {"success": False, "error": f"Source file not found: {source_path}"}

        try:
            if workflow == "full":
                return await self._full_workflow(source_path, paper_id)
            elif workflow == "extract_only":
                return await self._extract_workflow(source_path, paper_id)
            elif workflow == "translate_only":
                return await self._translate_workflow(source_path, paper_id)
            elif workflow == "heartfelt_only":
                return await self._heartfelt_workflow(source_path, paper_id)
            else:
                return {"success": False, "error": f"Unsupported workflow: {workflow}"}
        except Exception as e:
            logger.error(f"Error in workflow processing: {str(e)}")
            return {"success": False, "error": str(e)}

    async def _full_workflow(
        self, source_path: str, paper_id: str | None = None
    ) -> dict[str, Any]:
        """完整处理流程：提取 -> 翻译 -> 分析.

        Args:
            source_path: 源文件路径
            paper_id: 论文ID

        Returns:
            处理结果
        """
        logger.info(f"Starting full workflow for {source_path}")

        # 1. 内容提取
        extract_result = await self.pdf_agent.extract_content(
            {
                "file_path": source_path,
                "options": {
                    "extract_images": True,
                    "extract_tables": True,
                    "extract_formulas": True,
                },
            }
        )

        if not extract_result["success"]:
            return extract_result

        # 2. 翻译
        translate_result = await self.translation_agent.translate(
            {
                "content": extract_result["data"]["content"],
                "preserve_format": True,
                "paper_id": paper_id,
            }
        )

        # 3. 深度分析（异步，不阻塞返回）
        asyncio.create_task(
            self._async_heartfelt_analysis(
                source_path,
                extract_result["data"],
                translate_result.get("data"),
                paper_id,
            )
        )

        # 4. 保存结果
        if paper_id:
            await self._save_workflow_results(
                paper_id, extract_result, translate_result
            )

        return {
            "success": True,
            "extract_result": extract_result["data"],
            "translate_result": translate_result.get("data"),
            "status": "completed",
            "workflow": "full",
        }

    async def _extract_workflow(
        self, source_path: str, paper_id: str | None = None
    ) -> dict[str, Any]:
        """仅提取内容流程.

        Args:
            source_path: 源文件路径
            paper_id: 论文ID

        Returns:
            提取结果
        """
        logger.info(f"Starting extract workflow for {source_path}")

        result = await self.pdf_agent.extract_content(
            {
                "file_path": source_path,
                "options": {
                    "extract_images": True,
                    "extract_tables": True,
                    "extract_formulas": True,
                },
            }
        )

        if result["success"] and paper_id:
            await self._save_extract_result(paper_id, result["data"])

        return {
            "success": result["success"],
            "data": result.get("data"),
            "status": "completed" if result["success"] else "failed",
            "workflow": "extract_only",
        }

    async def _translate_workflow(
        self, source_path: str, paper_id: str | None = None
    ) -> dict[str, Any]:
        """仅翻译流程.

        Args:
            source_path: 源文件路径
            paper_id: 论文ID

        Returns:
            翻译结果
        """
        logger.info(f"Starting translate workflow for {source_path}")

        # 首先提取内容
        extract_result = await self.pdf_agent.extract_content(
            {"file_path": source_path, "options": {"extract_images": False}}
        )

        if not extract_result["success"]:
            return extract_result

        # 然后翻译
        translate_result = await self.translation_agent.translate(
            {
                "content": extract_result["data"]["content"],
                "preserve_format": True,
                "paper_id": paper_id,
            }
        )

        if translate_result["success"] and paper_id:
            await self._save_translate_result(paper_id, translate_result["data"])

        return {
            "success": translate_result["success"],
            "data": translate_result.get("data"),
            "status": "completed" if translate_result["success"] else "failed",
            "workflow": "translate_only",
        }

    async def _heartfelt_workflow(
        self, source_path: str, paper_id: str | None = None
    ) -> dict[str, Any]:
        """仅深度分析流程.

        Args:
            source_path: 源文件路径
            paper_id: 论文ID

        Returns:
            分析结果
        """
        logger.info(f"Starting heartfelt workflow for {source_path}")

        # 首先提取内容
        extract_result = await self.pdf_agent.extract_content(
            {"file_path": source_path, "options": {"extract_images": False}}
        )

        if not extract_result["success"]:
            return extract_result

        # 进行深度分析
        heartfelt_result = await self.heartfelt_agent.analyze(
            {"content": extract_result["data"]["content"], "paper_id": paper_id}
        )

        if heartfelt_result["success"] and paper_id:
            await self._save_heartfelt_result(paper_id, heartfelt_result["data"])

        return {
            "success": heartfelt_result["success"],
            "data": heartfelt_result.get("data"),
            "status": "completed" if heartfelt_result["success"] else "failed",
            "workflow": "heartfelt_only",
        }

    async def _async_heartfelt_analysis(
        self,
        source_path: str,
        extract_data: dict[str, Any],
        translate_data: dict[str, Any] | None,
        paper_id: str | None = None,
    ):
        """异步进行深度分析.

        Args:
            source_path: 源文件路径
            extract_data: 提取的数据
            translate_data: 翻译数据
            paper_id: 论文ID
        """
        try:
            result = await self.heartfelt_agent.analyze(
                {
                    "content": extract_data["content"],
                    "translation": translate_data.get("content")
                    if translate_data
                    else None,
                    "paper_id": paper_id,
                }
            )

            if result["success"] and paper_id:
                await self._save_heartfelt_result(paper_id, result["data"])

            logger.info(f"Heartfelt analysis completed for {paper_id}")
        except Exception as e:
            logger.error(f"Error in heartfelt analysis: {str(e)}")

    async def _save_workflow_results(
        self,
        paper_id: str,
        extract_result: dict[str, Any],
        translate_result: dict[str, Any],
    ):
        """保存工作流结果.

        Args:
            paper_id: 论文ID
            extract_result: 提取结果
            translate_result: 翻译结果
        """
        try:
            # 保存提取结果
            await self._save_extract_result(paper_id, extract_result)

            # 保存翻译结果
            if translate_result:
                await self._save_translate_result(paper_id, translate_result)

        except Exception as e:
            logger.error(f"Error saving workflow results: {str(e)}")

    async def _save_extract_result(self, paper_id: str, data: dict[str, Any]):
        """保存提取结果.

        Args:
            paper_id: 论文ID
            data: 提取数据
        """
        # 构建文件路径
        category = paper_id.split("_")[0] if "_" in paper_id else "general"
        output_dir = self.papers_dir / "translation" / category
        output_dir.mkdir(parents=True, exist_ok=True)

        # 保存 Markdown 内容
        output_file = output_dir / f"{paper_id}.md"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(data.get("content", ""))

        # 保存图片（如果有）
        if "images" in data:
            images_dir = self.papers_dir / "images" / category
            images_dir.mkdir(parents=True, exist_ok=True)
            # 这里应该处理图片保存逻辑

        logger.info(f"Extract result saved to {output_file}")

    async def _save_translate_result(self, paper_id: str, data: dict[str, Any]):
        """保存翻译结果.

        Args:
            paper_id: 论文ID
            data: 翻译数据
        """
        # 默认与提取结果保存在同一文件
        # 实际实现中可能需要区分源文件和翻译文件
        logger.info(f"Translate result saved for {paper_id}")

    async def _save_heartfelt_result(self, paper_id: str, data: dict[str, Any]):
        """保存深度分析结果.

        Args:
            paper_id: 论文ID
            data: 分析数据
        """
        category = paper_id.split("_")[0] if "_" in paper_id else "general"
        output_dir = self.papers_dir / "heartfelt" / category
        output_dir.mkdir(parents=True, exist_ok=True)

        output_file = output_dir / f"{paper_id}.md"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(data.get("content", ""))

        logger.info(f"Heartfelt result saved to {output_file}")

    async def batch_process(self, documents: list[str]) -> dict[str, Any]:
        """批量处理多个文档.

        Args:
            documents: 文档路径列表

        Returns:
            批量处理结果
        """
        logger.info(f"Starting batch processing for {len(documents)} documents")

        tasks = []
        for doc_path in documents:
            task = self.process({"source_path": doc_path, "workflow": "full"})
            tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 统计结果
        successful = sum(1 for r in results if isinstance(r, dict) and r.get("success"))
        failed = len(results) - successful

        return {
            "success": True,
            "total": len(documents),
            "successful": successful,
            "failed": failed,
            "results": results,
        }
