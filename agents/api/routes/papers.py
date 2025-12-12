"""Papers management routes."""

import logging
from typing import Any

from fastapi import (
    APIRouter,
    Body,
    Depends,
    File,
    HTTPException,
    Path,
    Query,
    UploadFile,
)

from agents.api.models.paper import (
    BatchProcessRequest,
    PaperListResponse,
    PaperProcessRequest,
    PaperStatus,
    PaperUploadResponse,
)
from agents.api.services.paper_service import PaperService

logger = logging.getLogger(__name__)
router = APIRouter()


# 依赖注入
async def get_paper_service() -> PaperService:
    """获取 PaperService 实例."""
    return PaperService()


@router.post("/upload", response_model=PaperUploadResponse)
async def upload_paper(
    file: UploadFile = File(...),
    category: str = Query("general", description="论文分类"),
    service: PaperService = Depends(get_paper_service),
) -> PaperUploadResponse:
    """
    上传论文文件.

    - **file**: PDF 文件
    - **category**: 论文分类（可选）
    """
    if not (file.filename and file.filename.lower().endswith(".pdf")):
        raise HTTPException(status_code=400, detail="只支持 PDF 文件")

    if file.size and file.size > 50 * 1024 * 1024:  # 50MB 限制
        raise HTTPException(status_code=400, detail="文件大小不能超过 50MB")

    try:
        result = await service.upload_paper(file, category)
        return PaperUploadResponse(**result)
    except Exception as e:
        logger.error(f"Error uploading paper: {str(e)}")
        raise HTTPException(status_code=500, detail=f"上传失败: {str(e)}") from e


@router.post("/{paper_id}/process")
async def process_paper(
    paper_id: str = Path(..., description="论文 ID"),
    request: PaperProcessRequest = Body(...),
    service: PaperService = Depends(get_paper_service),
) -> dict[str, Any]:
    """
    处理论文（提取/翻译/分析）.

    - **paper_id**: 论文 ID
    - **workflow**: 处理工作流类型
    """
    try:
        result = await service.process_paper(paper_id, request.workflow)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except Exception as e:
        logger.error(f"Error processing paper {paper_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"处理失败: {str(e)}") from e


@router.get("/{paper_id}/status", response_model=PaperStatus)
async def get_paper_status(
    paper_id: str = Path(..., description="论文 ID"),
    service: PaperService = Depends(get_paper_service),
) -> dict[str, Any]:
    """
    获取论文处理状态.

    - **paper_id**: 论文 ID
    """
    try:
        status = await service.get_status(paper_id)
        return status
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except Exception as e:
        logger.error(f"Error getting paper status {paper_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取状态失败: {str(e)}") from e


@router.get("/{paper_id}/content")
async def get_paper_content(
    paper_id: str = Path(..., description="论文 ID"),
    content_type: str = Query(
        "translation", description="内容类型: source, translation, heartfelt"
    ),
    service: PaperService = Depends(get_paper_service),
) -> dict[str, Any]:
    """
    获取论文内容.

    - **paper_id**: 论文 ID
    - **content_type**: 内容类型
    """
    if content_type not in ["source", "translation", "heartfelt"]:
        raise HTTPException(status_code=400, detail="无效的内容类型")

    try:
        content = await service.get_content(paper_id, content_type)
        return content
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except Exception as e:
        logger.error(f"Error getting paper content {paper_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取内容失败: {str(e)}") from e


@router.get("/", response_model=PaperListResponse)
async def list_papers(
    category: str | None = Query(None, description="按分类筛选"),
    status: str | None = Query(None, description="按状态筛选"),
    limit: int = Query(20, ge=1, le=100, description="返回数量限制"),
    offset: int = Query(0, ge=0, description="偏移量"),
    service: PaperService = Depends(get_paper_service),
) -> dict[str, Any]:
    """
    获取论文列表.

    - **category**: 分类筛选
    - **status**: 状态筛选
    - **limit**: 返回数量限制
    - **offset**: 偏移量
    """
    try:
        papers = await service.list_papers(
            category=category, status=status, limit=limit, offset=offset
        )
        return papers
    except Exception as e:
        logger.error(f"Error listing papers: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取列表失败: {str(e)}") from e


@router.delete("/{paper_id}")
async def delete_paper(
    paper_id: str = Path(..., description="论文 ID"),
    service: PaperService = Depends(get_paper_service),
) -> dict[str, Any]:
    """
    删除论文及其相关数据.

    - **paper_id**: 论文 ID
    """
    try:
        result = await service.delete_paper(paper_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except Exception as e:
        logger.error(f"Error deleting paper {paper_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}") from e


@router.post("/batch", response_model=BatchProcessRequest)
async def batch_process_papers(
    paper_ids: list[str] = Body(...),
    workflow: str = Query("full", description="处理工作流"),
    service: PaperService = Depends(get_paper_service),
) -> dict[str, Any]:
    """
    批量处理论文.

    - **paper_ids**: 论文 ID 列表
    - **workflow**: 处理工作流
    """
    if len(paper_ids) > 50:
        raise HTTPException(status_code=400, detail="批量处理最多支持 50 个文件")

    try:
        result = await service.batch_process_papers(paper_ids, workflow)
        return result
    except Exception as e:
        logger.error(f"Error in batch processing: {str(e)}")
        raise HTTPException(status_code=500, detail=f"批量处理失败: {str(e)}") from e


@router.get("/{paper_id}/report")
async def get_paper_report(
    paper_id: str = Path(..., description="论文 ID"),
    service: PaperService = Depends(get_paper_service),
) -> dict[str, Any]:
    """
    获取论文的深度阅读报告.

    - **paper_id**: 论文 ID
    """
    try:
        report = await service.get_paper_report(paper_id)
        return report
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except Exception as e:
        logger.error(f"Error getting paper report {paper_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取报告失败: {str(e)}") from e
