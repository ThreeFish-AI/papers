"""WebSocket routes for real-time updates."""

import json
import logging
from datetime import datetime
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from agents.api.services.websocket_service import WebSocketService

logger = logging.getLogger(__name__)
router = APIRouter()


# WebSocket 连接管理器
class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections: dict[str, WebSocket] = {}
        self.client_subscriptions: dict[
            str, set[str]
        ] = {}  # client_id -> set of task_ids

    async def connect(self, websocket: WebSocket, client_id: str) -> None:
        """接受 WebSocket 连接."""
        await websocket.accept()
        self.active_connections[client_id] = websocket
        self.client_subscriptions[client_id] = set()
        logger.info(f"WebSocket client connected: {client_id}")

    def disconnect(self, client_id: str) -> None:
        """断开 WebSocket 连接."""
        if client_id in self.active_connections:
            del self.active_connections[client_id]
        if client_id in self.client_subscriptions:
            del self.client_subscriptions[client_id]
        logger.info(f"WebSocket client disconnected: {client_id}")

    async def send_personal_message(
        self, message: dict[str, Any], client_id: str
    ) -> None:
        """发送个人消息."""
        if client_id in self.active_connections:
            websocket = self.active_connections[client_id]
            try:
                await websocket.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Error sending message to {client_id}: {str(e)}")
                self.disconnect(client_id)

    async def broadcast_to_subscribers(
        self, message: dict[str, Any], task_id: str
    ) -> None:
        """向任务订阅者广播消息."""
        for client_id, subscriptions in self.client_subscriptions.items():
            if task_id in subscriptions:
                await self.send_personal_message(message, client_id)

    async def subscribe(self, client_id: str, task_id: str):
        """订阅任务更新."""
        if client_id in self.client_subscriptions:
            self.client_subscriptions[client_id].add(task_id)
            logger.info(f"Client {client_id} subscribed to task {task_id}")

    async def unsubscribe(self, client_id: str, task_id: str):
        """取消订阅任务更新."""
        if client_id in self.client_subscriptions:
            self.client_subscriptions[client_id].discard(task_id)
            logger.info(f"Client {client_id} unsubscribed from task {task_id}")


manager = ConnectionManager()


@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """WebSocket 连接端点."""
    await manager.connect(websocket, client_id)

    try:
        while True:
            # 接收客户端消息
            data = await websocket.receive_text()
            message = json.loads(data)

            # 处理不同类型的消息
            message_type = message.get("type")

            if message_type == "subscribe":
                task_id = message.get("task_id")
                if task_id:
                    await manager.subscribe(client_id, task_id)
                    # 发送订阅确认
                    await manager.send_personal_message(
                        {
                            "type": "subscription_confirmed",
                            "task_id": task_id,
                            "timestamp": datetime.now().isoformat(),
                        },
                        client_id,
                    )

            elif message_type == "unsubscribe":
                task_id = message.get("task_id")
                if task_id:
                    await manager.unsubscribe(client_id, task_id)
                    # 发送取消订阅确认
                    await manager.send_personal_message(
                        {
                            "type": "unsubscription_confirmed",
                            "task_id": task_id,
                            "timestamp": datetime.now().isoformat(),
                        },
                        client_id,
                    )

            elif message_type == "ping":
                # 心跳检测
                await manager.send_personal_message(
                    {"type": "pong", "timestamp": datetime.now().isoformat()}, client_id
                )

    except WebSocketDisconnect:
        manager.disconnect(client_id)
    except Exception as e:
        logger.error(f"WebSocket error for {client_id}: {str(e)}")
        manager.disconnect(client_id)


# WebSocket 服务依赖
async def get_websocket_service() -> WebSocketService:
    """获取 WebSocketService 实例."""
    return WebSocketService(manager)


# 发送任务更新的辅助函数
async def send_task_update(
    task_id: str, status: str, progress: float | None = None, message: str | None = None
) -> None:
    """发送任务更新给所有订阅者."""
    update_message = {
        "type": "task_update",
        "task_id": task_id,
        "status": status,
        "progress": progress,
        "message": message,
        "timestamp": datetime.now().isoformat(),
    }
    await manager.broadcast_to_subscribers(update_message, task_id)


# 发送任务完成通知
async def send_task_completion(
    task_id: str, result: dict[Any, Any] | None = None, error: str | None = None
) -> None:
    """发送任务完成通知."""
    completion_message = {
        "type": "task_completed",
        "task_id": task_id,
        "success": error is None,
        "result": result,
        "error": error,
        "timestamp": datetime.now().isoformat(),
    }
    await manager.broadcast_to_subscribers(completion_message, task_id)


# 发送批处理进度更新
async def send_batch_progress(
    batch_id: str, total: int, processed: int, current_file: str | None = None
) -> None:
    """发送批处理进度更新."""
    progress_message = {
        "type": "batch_progress",
        "batch_id": batch_id,
        "total": total,
        "processed": processed,
        "progress": processed / total * 100,
        "current_file": current_file,
        "timestamp": datetime.now().isoformat(),
    }

    # 向所有连接的客户端发送批处理更新
    for client_id in manager.active_connections:
        await manager.send_personal_message(progress_message, client_id)
