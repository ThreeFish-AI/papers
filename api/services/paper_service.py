"""Paper service for managing papers."""

import os
import shutil
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path
from fastapi import UploadFile
import logging

from ..agents.workflow_agent import WorkflowAgent
from ..agents.batch_agent import BatchProcessingAgent
from ..agents.heartfelt_agent import HeartfeltAgent
from ..core.config import settings

logger = logging.getLogger(__name__)


class PaperService:
    """论文处理服务."""

    def __init__(self):
        """初始化 PaperService."""
        self.papers_dir = Path(settings.PAPERS_DIR)
        self.workflow_agent = WorkflowAgent({
            "papers_dir": str(self.papers_dir)
        })
        self.batch_agent = BatchProcessingAgent({
            "papers_dir": str(self.papers_dir)
        })
        self.heartfelt_agent = HeartfeltAgent({
            "papers_dir": str(self.papers_dir)
        })

    async def upload_paper(self, file: UploadFile, category: str) -> Dict[str, Any]:
        """处理文件上传.

        Args:
            file: 上传的文件
            category: 论文分类

        Returns:
            上传结果
        """
        # 生成唯一ID和文件路径
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_filename = self._sanitize_filename(file.filename)
        paper_id = f"{category}_{timestamp}_{safe_filename}"

        # 确保目录存在
        source_dir = self.papers_dir / "source" / category
        source_dir.mkdir(parents=True, exist_ok=True)

        # 保存文件
        source_path = source_dir / paper_id
        try:
            with open(source_path, "wb") as f:
                shutil.copyfileobj(file.file, f)

            file_size = os.path.getsize(source_path)

            # 保存元数据
            metadata = {
                "paper_id": paper_id,
                "filename": file.filename,
                "safe_filename": safe_filename,
                "category": category,
                "size": file_size,
                "upload_time": datetime.now().isoformat(),
                "status": "uploaded",
                "workflows": {}
            }

            await self._save_metadata(paper_id, metadata)

            logger.info(f"Paper uploaded successfully: {paper_id}")

            return {
                "paper_id": paper_id,
                "filename": file.filename,
                "category": category,
                "size": file_size,
                "upload_time": metadata["upload_time"]
            }

        except Exception as e:
            # 如果保存失败，删除可能已创建的文件
            if source_path.exists():
                source_path.unlink()
            logger.error(f"Error uploading paper: {str(e)}")
            raise

    async def process_paper(self, paper_id: str, workflow: str) -> Dict[str, Any]:
        """启动处理流程.

        Args:
            paper_id: 论文ID
            workflow: 工作流类型

        Returns:
            处理结果
        """
        source_path = self._get_source_path(paper_id)
        if not source_path.exists():
            raise ValueError(f"论文不存在: {paper_id}")

        # 更新状态
        await self._update_status(paper_id, "processing", workflow)

        try:
            # 启动处理
            result = await self.workflow_agent.process({
                "source_path": str(source_path),
                "workflow": workflow,
                "paper_id": paper_id,
            })

            if result["success"]:
                await self._update_status(paper_id, "completed", workflow)
            else:
                await self._update_status(paper_id, "failed", workflow, result.get("error"))

            # 创建任务记录
            task_id = f"task_{paper_id}_{workflow}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            await self._create_task_record(paper_id, task_id, workflow, result)

            return {
                "task_id": task_id,
                "paper_id": paper_id,
                "workflow": workflow,
                "status": "completed" if result["success"] else "failed",
                "result": result if result["success"] else None
            }

        except Exception as e:
            await self._update_status(paper_id, "failed", workflow, str(e))
            logger.error(f"Error processing paper {paper_id}: {str(e)}")
            raise

    async def get_status(self, paper_id: str) -> Dict[str, Any]:
        """获取论文处理状态.

        Args:
            paper_id: 论文ID

        Returns:
            状态信息
        """
        metadata = await self._get_metadata(paper_id)
        if not metadata:
            raise ValueError(f"论文不存在: {paper_id}")

        return {
            "paper_id": paper_id,
            "status": metadata.get("status", "unknown"),
            "workflows": metadata.get("workflows", {}),
            "upload_time": metadata.get("upload_time"),
            "updated_at": metadata.get("updated_at"),
            "category": metadata.get("category"),
            "filename": metadata.get("filename"),
        }

    async def get_content(self, paper_id: str, content_type: str) -> Dict[str, Any]:
        """获取论文内容.

        Args:
            paper_id: 论文ID
            content_type: 内容类型

        Returns:
            内容数据
        """
        # 根据内容类型构建文件路径
        category = await self._get_paper_category(paper_id)
        base_filename = paper_id

        if content_type == "source":
            # 源文件（PDF）
            source_path = self._get_source_path(paper_id)
            if not source_path.exists():
                raise ValueError(f"源文件不存在: {paper_id}")
            return {
                "paper_id": paper_id,
                "content_type": "source",
                "format": "pdf",
                "file_path": str(source_path),
                "size": source_path.stat().st_size
            }

        else:
            # Markdown 文件
            if content_type == "translation":
                content_dir = self.papers_dir / "translation" / category
            elif content_type == "heartfelt":
                content_dir = self.papers_dir / "heartfelt" / category
            else:
                raise ValueError(f"不支持的内容类型: {content_type}")

            content_path = content_dir / f"{base_filename}.md"
            if not content_path.exists():
                raise ValueError(f"{content_type}内容不存在: {paper_id}")

            with open(content_path, "r", encoding="utf-8") as f:
                content = f.read()

            return {
                "paper_id": paper_id,
                "content_type": content_type,
                "format": "markdown",
                "content": content,
                "word_count": len(content.split()),
                "file_path": str(content_path)
            }

    async def list_papers(
        self,
        category: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> Dict[str, Any]:
        """获取论文列表.

        Args:
            category: 分类筛选
            status: 状态筛选
            limit: 返回数量限制
            offset: 偏移量

        Returns:
            论文列表
        """
        papers = []
        source_dir = self.papers_dir / "source"

        # 遍历所有分类目录
        for cat_dir in source_dir.iterdir():
            if cat_dir.is_dir():
                current_category = cat_dir.name

                # 分类筛选
                if category and current_category != category:
                    continue

                # 遍历分类下的所有文件
                for file_path in cat_dir.iterdir():
                    if file_path.is_file() and file_path.suffix == '.pdf':
                        paper_id = file_path.name

                        # 获取元数据
                        metadata = await self._get_metadata(paper_id)
                        if metadata:
                            # 状态筛选
                            if status and metadata.get("status") != status:
                                continue

                            papers.append({
                                "paper_id": paper_id,
                                "filename": metadata.get("filename", paper_id),
                                "category": current_category,
                                "status": metadata.get("status", "unknown"),
                                "upload_time": metadata.get("upload_time"),
                                "updated_at": metadata.get("updated_at"),
                                "size": file_path.stat().st_size,
                            })

        # 排序（按上传时间倒序）
        papers.sort(key=lambda x: x["upload_time"], reverse=True)

        # 分页
        total = len(papers)
        papers = papers[offset:offset + limit]

        return {
            "papers": papers,
            "total": total,
            "offset": offset,
            "limit": limit
        }

    async def delete_paper(self, paper_id: str) -> Dict[str, Any]:
        """删除论文及其相关数据.

        Args:
            paper_id: 论文ID

        Returns:
            删除结果
        """
        try:
            # 获取分类
            category = await self._get_paper_category(paper_id)

            # 删除源文件
            source_path = self._get_source_path(paper_id)
            if source_path.exists():
                source_path.unlink()

            # 删除翻译文件
            translation_path = self.papers_dir / "translation" / category / f"{paper_id}.md"
            if translation_path.exists():
                translation_path.unlink()

            # 删除深度分析文件
            heartfelt_dir = self.papers_dir / "heartfelt" / category
            heartfelt_path = heartfelt_dir / f"{paper_id}.md"
            if heartfelt_path.exists():
                heartfelt_path.unlink()

            heartfelt_json_path = heartfelt_dir / f"{paper_id}_analysis.json"
            if heartfelt_json_path.exists():
                heartfelt_json_path.unlink()

            report_path = heartfelt_dir / f"{paper_id}_report.md"
            if report_path.exists():
                report_path.unlink()

            # 删除元数据
            await self._delete_metadata(paper_id)

            logger.info(f"Paper deleted successfully: {paper_id}")

            return {
                "paper_id": paper_id,
                "deleted": True
            }

        except Exception as e:
            logger.error(f"Error deleting paper {paper_id}: {str(e)}")
            raise

    async def batch_process_papers(self, paper_ids: List[str], workflow: str) -> Dict[str, Any]:
        """批量处理论文.

        Args:
            paper_ids: 论文ID列表
            workflow: 夥流类型

        Returns:
            批量处理结果
        """
        # 获取文件路径
        file_paths = []
        for paper_id in paper_ids:
            source_path = self._get_source_path(paper_id)
            if source_path.exists():
                file_paths.append(str(source_path))

        if not file_paths:
            raise ValueError("没有找到有效的论文文件")

        # 启动批处理
        result = await self.batch_agent.batch_process({
            "files": file_paths,
            "workflow": workflow,
            "options": {
                "batch_size": 5,
                "parallel_tasks": 3
            }
        })

        return {
            "batch_id": f"batch_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "total_requested": len(paper_ids),
            "total_files": len(file_paths),
            "workflow": workflow,
            "stats": result["stats"],
            "results": result["results"]
        }

    async def get_paper_report(self, paper_id: str) -> Dict[str, Any]:
        """获取论文的深度阅读报告.

        Args:
            paper_id: 论文ID

        Returns:
            阅读报告
        """
        result = await self.heartfelt_agent.generate_reading_report(paper_id)

        if not result["success"]:
            raise ValueError(result.get("error", "生成报告失败"))

        return {
            "paper_id": paper_id,
            "report": result["data"]
        }

    # 私有辅助方法

    def _sanitize_filename(self, filename: str) -> str:
        """清理文件名."""
        # 移除特殊字符，只保留字母、数字、下划线、连字符和点
        import re
        safe_name = re.sub(r'[^\w\-_\.]', '_', filename)
        return safe_name

    def _get_source_path(self, paper_id: str) -> Path:
        """获取源文件路径."""
        # 从 paper_id 提取分类
        if "_" in paper_id:
            category = paper_id.split("_")[0]
        else:
            category = "general"

        return self.papers_dir / "source" / category / paper_id

    async def _get_paper_category(self, paper_id: str) -> str:
        """获取论文分类."""
        metadata = await self._get_metadata(paper_id)
        if metadata and "category" in metadata:
            return metadata["category"]

        # 从 paper_id 提取
        if "_" in paper_id:
            return paper_id.split("_")[0]
        return "general"

    async def _save_metadata(self, paper_id: str, metadata: Dict[str, Any]):
        """保存元数据."""
        metadata_dir = self.papers_dir / ".metadata"
        metadata_dir.mkdir(exist_ok=True)

        metadata_file = metadata_dir / f"{paper_id}.json"
        import json
        with open(metadata_file, "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)

    async def _get_metadata(self, paper_id: str) -> Optional[Dict[str, Any]]:
        """获取元数据."""
        metadata_dir = self.papers_dir / ".metadata"
        metadata_file = metadata_dir / f"{paper_id}.json"

        if not metadata_file.exists():
            return None

        import json
        with open(metadata_file, "r", encoding="utf-8") as f:
            return json.load(f)

    async def _update_metadata(self, paper_id: str, updates: Dict[str, Any]):
        """更新元数据."""
        metadata = await self._get_metadata(paper_id) or {}
        metadata.update(updates)
        metadata["updated_at"] = datetime.now().isoformat()
        await self._save_metadata(paper_id, metadata)

    async def _delete_metadata(self, paper_id: str):
        """删除元数据."""
        metadata_dir = self.papers_dir / ".metadata"
        metadata_file = metadata_dir / f"{paper_id}.json"

        if metadata_file.exists():
            metadata_file.unlink()

    async def _update_status(self, paper_id: str, status: str, workflow: str = None, error: str = None):
        """更新状态."""
        updates = {"status": status}
        if workflow:
            workflows = (await self._get_metadata(paper_id) or {}).get("workflows", {})
            workflow_status = {"status": status, "updated_at": datetime.now().isoformat()}
            if error:
                workflow_status["error"] = error
            workflows[workflow] = workflow_status
            updates["workflows"] = workflows

        await self._update_metadata(paper_id, updates)

    async def _create_task_record(self, paper_id: str, task_id: str, workflow: str, result: Dict[str, Any]):
        """创建任务记录."""
        # 这里可以实现任务记录保存逻辑
        # 例如保存到数据库或文件
        pass