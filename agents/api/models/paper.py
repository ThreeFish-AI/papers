"""Paper related data models."""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class PaperUploadResponse(BaseModel):
    """论文上传响应模型."""
    paper_id: str = Field(..., description="论文ID")
    filename: str = Field(..., description="原始文件名")
    category: str = Field(..., description="论文分类")
    size: int = Field(..., description="文件大小（字节）")
    upload_time: str = Field(..., description="上传时间")


class PaperProcessRequest(BaseModel):
    """论文处理请求模型."""
    workflow: str = Field(default="full", description="处理工作流类型")
    options: Optional[Dict[str, Any]] = Field(default=None, description="处理选项")

    class Config:
        schema_extra = {
            "example": {
                "workflow": "full",
                "options": {
                    "extract_images": True,
                    "preserve_format": True
                }
            }
        }


class PaperStatus(BaseModel):
    """论文状态模型."""
    paper_id: str = Field(..., description="论文ID")
    status: str = Field(..., description="当前状态")
    workflows: Dict[str, Dict[str, Any]] = Field(default_factory=dict, description="各工作流状态")
    upload_time: Optional[str] = Field(None, description="上传时间")
    updated_at: Optional[str] = Field(None, description="更新时间")
    category: Optional[str] = Field(None, description="论文分类")
    filename: Optional[str] = Field(None, description="文件名")

    class Config:
        schema_extra = {
            "example": {
                "paper_id": "llm-agents_20240115_143022_example.pdf",
                "status": "completed",
                "workflows": {
                    "extract": {
                        "status": "completed",
                        "updated_at": "2024-01-15T14:35:00"
                    },
                    "translate": {
                        "status": "processing",
                        "progress": 75
                    }
                }
            }
        }


class PaperContent(BaseModel):
    """论文内容模型."""
    paper_id: str = Field(..., description="论文ID")
    content_type: str = Field(..., description="内容类型")
    format: str = Field(..., description="内容格式")
    content: Optional[str] = Field(None, description="内容文本")
    file_path: Optional[str] = Field(None, description="文件路径")
    word_count: Optional[int] = Field(None, description="字数")
    size: Optional[int] = Field(None, description="文件大小")
    metadata: Optional[Dict[str, Any]] = Field(None, description="元数据")


class PaperInfo(BaseModel):
    """论文信息模型."""
    paper_id: str = Field(..., description="论文ID")
    filename: str = Field(..., description="文件名")
    category: str = Field(..., description="分类")
    status: str = Field(..., description="状态")
    upload_time: str = Field(..., description="上传时间")
    updated_at: Optional[str] = Field(None, description="更新时间")
    size: int = Field(..., description="文件大小")


class PaperListResponse(BaseModel):
    """论文列表响应模型."""
    papers: List[PaperInfo] = Field(..., description="论文列表")
    total: int = Field(..., description="总数")
    offset: int = Field(..., description="偏移量")
    limit: int = Field(..., description="限制数")


class BatchProcessRequest(BaseModel):
    """批量处理请求模型."""
    batch_id: str = Field(..., description="批次ID")
    total_requested: int = Field(..., description="请求数量")
    total_files: int = Field(..., description="实际文件数")
    workflow: str = Field(..., description="工作流类型")
    stats: Dict[str, Any] = Field(..., description="处理统计")
    results: List[Dict[str, Any]] = Field(..., description="处理结果")


class PaperReport(BaseModel):
    """论文报告模型."""
    paper_id: str = Field(..., description="论文ID")
    report: Dict[str, Any] = Field(..., description="报告内容")