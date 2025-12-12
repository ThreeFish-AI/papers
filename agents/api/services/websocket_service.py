"""WebSocket service for real-time communication."""

import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class WebSocketService:
    """WebSocket 服务."""

    def __init__(self, connection_manager) -> None:
        """初始化 WebSocketService.

        Args:
            connection_manager: 连接管理器实例
        """
        self.manager = connection_manager

    async def send_task_update(
        self,
        task_id: str,
        status: str,
        progress: Optional[float] = None,
        message: Optional[str] = None,
    ) -> None:
        """发送任务更新.

        Args:
            task_id: 任务ID
            status: 状态
            progress: 进度
            message: 消息
        """
        from ..routes.websocket import send_task_update

        await send_task_update(task_id, status, progress, message)

    async def send_task_completion(
        self,
        task_id: str,
        result: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
    ) -> None:
        """发送任务完成通知.

        Args:
            task_id: 任务ID
            result: 结果
            error: 错误
        """
        from ..routes.websocket import send_task_completion

        await send_task_completion(task_id, result, error)

    async def send_batch_progress(
        self,
        batch_id: str,
        total: int,
        processed: int,
        current_file: Optional[str] = None,
    ) -> None:
        """发送批处理进度.

        Args:
            batch_id: 批次ID
            total: 总数
            processed: 已处理数
            current_file: 当前文件
        """
        from ..routes.websocket import send_batch_progress

        await send_batch_progress(batch_id, total, processed, current_file)
