# 开发与维护手册

## 开发环境设置

### 环境要求

- Python 3.12 或更高版本
- Git
- Docker & Docker Compose（可选，用于容器化开发）
- Claude API Key
- 代码编辑器（推荐 VS Code）

### 本地开发设置

#### 1. 克隆仓库

```bash
git clone https://github.com/ThreeFish-AI/agentic-ai-papers.git
cd agentic-ai-papers
```

#### 2. 创建虚拟环境

```bash
# 使用 venv
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 或使用 conda
conda create -n agentic-papers python=3.12
conda activate agentic-papers
```

#### 3. 安装依赖

```bash
# 安装核心依赖
pip install -e .

# 安装开发依赖
pip install -e ".[dev]"

# 或使用 uv（更快的包管理器）
uv pip install -e ".[dev]"
```

#### 4. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件
nano .env
```

必要的环境变量：

```env
ANTHROPIC_API_KEY=your_claude_api_key_here
# 可选配置
LOG_LEVEL=INFO
MAX_CONCURRENT_TASKS=5
PAPERS_DIR=./papers
```

#### 5. 启动开发服务器

```bash
# 启动 API 服务器
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# 或使用 Make 命令（如果存在）
make dev
```

### Docker 开发环境

#### 使用 Docker Compose

```bash
# 启动开发环境
docker-compose -f docker-compose.dev.yml up

# 后台运行
docker-compose -f docker-compose.dev.yml up -d

# 查看日志
docker-compose -f docker-compose.dev.yml logs -f
```

## 代码组织原则

### 目录结构规范

```
agents/
├── claude/              # Claude Agent 实现
│   ├── __init__.py     # 包初始化
│   ├── base.py         # 基础 Agent 类
│   ├── *.py            # 具体实现
├── api/                # FastAPI 服务
│   ├── __init__.py
│   ├── main.py         # 应用入口
│   ├── routes/         # 路由模块
│   ├── services/       # 业务逻辑
│   └── models/         # 数据模型
└── core/               # 核心工具
    ├── config.py       # 配置管理
    ├── exceptions.py   # 异常定义
    └── utils.py        # 通用工具
```

### 命名规范

- **文件名**: 使用小写字母和下划线 (`snake_case`)
- **类名**: 使用大驼峰命名 (`PascalCase`)
- **函数/变量**: 使用小写字母和下划线 (`snake_case`)
- **常量**: 使用大写字母和下划线 (`UPPER_CASE`)
- **私有成员**: 前缀单下划线 (`_private`)

### 导入规范

```python
# 标准库导入
import os
import asyncio
from pathlib import Path
from typing import Optional, Dict, List

# 第三方库导入
import aiofiles
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# 本地模块导入
from agents.claude.base import BaseAgent
from core.config import settings
from api.models.paper import Paper
```

## Agent 开发指南

### 创建新 Agent

#### 1. 继承 BaseAgent

```python
from agents.claude.base import BaseAgent
from typing import Dict, Any

class CustomAgent(BaseAgent):
    """自定义 Agent 实现"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.agent_name = "custom"
        self.required_skills = ["skill1", "skill2"]

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理输入数据"""
        # 验证输入
        if not self.validate_input(input_data):
            raise ValueError("Invalid input")

        # 调用技能
        result = await self.call_skill("skill1", input_data)

        # 处理结果
        processed = self._process_result(result)

        return {"success": True, "data": processed}

    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """验证输入数据"""
        required_fields = ["field1", "field2"]
        return all(field in input_data for field in required_fields)

    def _process_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """处理技能结果"""
        # 自定义处理逻辑
        return result
```

#### 2. Agent 配置

```python
# 在 core/config.py 中添加配置
class CustomAgentConfig(BaseSettings):
    enabled: bool = True
    max_retries: int = 3
    timeout: int = 30

    class Config:
        env_prefix = "CUSTOM_AGENT_"
```

#### 3. 注册 Agent

```python
# 在 agents/claude/__init__.py 中注册
from .custom_agent import CustomAgent

AVAILABLE_AGENTS = {
    "custom": CustomAgent,
    # ... 其他 agents
}
```

### 最佳实践

#### 1. 错误处理

```python
async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
    try:
        # 处理逻辑
        result = await self.call_skill("skill", input_data)
        return {"success": True, "data": result}

    except SkillTimeoutError as e:
        self.log_processing(f"Skill timeout: {e}")
        return {"success": False, "error": "Processing timeout"}

    except ValidationError as e:
        self.log_processing(f"Validation error: {e}")
        raise

    except Exception as e:
        self.log_processing(f"Unexpected error: {e}")
        raise ProcessingError(f"Failed to process: {e}")
```

#### 2. 日志记录

```python
import logging

logger = logging.getLogger(__name__)

class CustomAgent(BaseAgent):
    async def process(self, input_data):
        logger.info(f"Processing {len(input_data)} items")

        try:
            result = await self._do_process(input_data)
            logger.info(f"Successfully processed {result['count']} items")
            return result
        except Exception as e:
            logger.error(f"Processing failed: {e}", exc_info=True)
            raise
```

#### 3. 异步编程

```python
# 使用 asyncio 进行并发处理
async def process_batch(self, items: List[Dict]) -> List[Dict]:
    """批量处理"""
    semaphore = asyncio.Semaphore(self.max_concurrent)

    async def process_with_limit(item):
        async with semaphore:
            return await self.process(item)

    tasks = [process_with_limit(item) for item in items]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    return results
```

## API 开发模式

### FastAPI 应用结构

#### 1. 路由定义

```python
# api/routes/custom.py
from fastapi import APIRouter, Depends, HTTPException
from api.services.custom_service import CustomService
from api.models.custom import CustomRequest, CustomResponse

router = APIRouter(prefix="/api/custom", tags=["custom"])

@router.post("/process", response_model=CustomResponse)
async def process_data(
    request: CustomRequest,
    service: CustomService = Depends()
) -> CustomResponse:
    """处理自定义数据"""
    try:
        result = await service.process(request.data)
        return CustomResponse(success=True, data=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

#### 2. 服务层

```python
# api/services/custom_service.py
from agents.claude.custom_agent import CustomAgent
from core.config import settings

class CustomService:
    def __init__(self):
        self.agent = CustomAgent(settings.custom_agent_config)

    async def process(self, data: Dict) -> Dict:
        """处理数据"""
        result = await self.agent.process(data)
        return result
```

#### 3. 数据模型

```python
# api/models/custom.py
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class CustomRequest(BaseModel):
    data: Dict[str, Any] = Field(..., description="处理数据")
    options: Optional[Dict[str, Any]] = Field(default=None, description="选项")

class CustomResponse(BaseModel):
    success: bool = Field(..., description="是否成功")
    data: Optional[Dict[str, Any]] = Field(default=None, description="结果数据")
    error: Optional[str] = Field(default=None, description="错误信息")
```

### API 最佳实践

#### 1. 依赖注入

```python
from fastapi import Depends

def get_current_user():
    """获取当前用户"""
    # 认证逻辑
    return user

@router.get("/protected")
async def protected_route(user=Depends(get_current_user)):
    return {"message": f"Hello {user}"}
```

#### 2. 中间件使用

```python
# api/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 自定义中间件
@app.middleware("http")
async def log_requests(request, call_next):
    logger.info(f"Request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Response: {response.status_code}")
    return response
```

## 测试策略

### 测试框架配置

项目使用 `pytest` 作为测试框架，配置如下：

```toml
# pyproject.toml
[tool.pytest.ini_options]
minversion = "7.0"
addopts = "-ra -q --strict-markers --strict-config"
testpaths = ["tests"]
markers = [
    "slow: marks tests as slow",
    "integration: marks tests as integration",
    "unit: marks tests as unit"
]
```

### 测试结构

```
tests/
├── unit/               # 单元测试
│   ├── test_agents/
│   ├── test_api/
│   └── test_core/
├── integration/        # 集成测试
│   ├── test_workflows/
│   └── test_endpoints/
├── fixtures/           # 测试数据
│   ├── sample_pdfs/
│   └── mock_responses/
└── conftest.py         # 测试配置
```

### 单元测试示例

```python
# tests/unit/test_agents/test_custom_agent.py
import pytest
from agents.claude.custom_agent import CustomAgent

@pytest.fixture
def custom_agent():
    config = {"max_retries": 3}
    return CustomAgent(config)

@pytest.mark.asyncio
async def test_process_success(custom_agent):
    """测试成功处理"""
    input_data = {"field1": "value1", "field2": "value2"}

    result = await custom_agent.process(input_data)

    assert result["success"] is True
    assert "data" in result

@pytest.mark.asyncio
async def test_process_invalid_input(custom_agent):
    """测试无效输入"""
    input_data = {"field1": "value1"}  # 缺少 field2

    with pytest.raises(ValueError):
        await custom_agent.process(input_data)
```

### Mock 策略

```python
# tests/conftest.py
import pytest
from unittest.mock import AsyncMock, patch

@pytest.fixture
def mock_skill():
    """Mock 技能调用"""
    async def mock_call(name, params):
        return {"result": f"mocked_{name}_result"}

    with patch("agents.claude.base.BaseAgent.call_skill", mock_call):
        yield

@pytest.fixture
def sample_pdf():
    """提供示例 PDF 文件路径"""
    return "tests/fixtures/sample_papers/sample.pdf"
```

## 调试和故障排除

### 日志配置

```python
# core/logging.py
import logging
import sys
from pathlib import Path

def setup_logging(log_level: str = "INFO", log_file: str = None):
    """配置日志"""
    # 创建格式化器
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    # 根日志器
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    root_logger.addHandler(console_handler)

    # 文件处理器（可选）
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
```

### 常见问题排查

#### 1. Agent 无法启动

```python
# 检查配置
def debug_agent_config(agent_class):
    """调试 Agent 配置"""
    print(f"Agent class: {agent_class.__name__}")
    print(f"Required skills: {agent_class.required_skills}")
    print(f"Config schema: {agent_class.config_schema}")
```

#### 2. 技能调用失败

```python
# 技能调用调试
async def debug_skill_call(agent, skill_name, params):
    """调试技能调用"""
    print(f"Calling skill: {skill_name}")
    print(f"Parameters: {params}")

    try:
        result = await agent.call_skill(skill_name, params)
        print(f"Result: {result}")
        return result
    except Exception as e:
        print(f"Error: {e}")
        print(f"Error type: {type(e)}")
        raise
```

#### 3. 性能问题

```python
# 性能分析
import time
from functools import wraps

def timing_decorator(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start = time.time()
        result = await func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} took {end - start:.2f} seconds")
        return result
    return wrapper
```

## 贡献指南

### 开发流程

```mermaid
flowchart LR
    A[Fork 仓库] --> B[创建功能分支]
    B --> C[编写代码]
    C --> D[编写测试]
    D --> E[运行测试]
    E --> F{测试通过?}
    F -->|否| C
    F -->|是| G[提交代码]
    G --> H[推送分支]
    H --> I[创建 PR]
    I --> J[代码审查]
    J --> K[合并主分支]
```

### 提交规范

使用 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

```
feat: 添加新功能
fix: 修复 bug
docs: 更新文档
style: 代码格式调整
refactor: 代码重构
test: 添加或修改测试
chore: 构建过程或辅助工具的变动
```

示例：

```bash
git commit -m "feat(agent): 添加新的翻译 Agent"
git commit -m "fix(api): 修复文件上传的内存泄漏问题"
```

### 代码审查清单

- [ ] 代码符合项目编码规范
- [ ] 包含必要的单元测试
- [ ] 文档已更新
- [ ] 没有硬编码的配置
- [ ] 错误处理完善
- [ ] 日志记录合理
- [ ] 性能影响已评估

## 发布流程

### 版本管理

使用语义化版本 (SemVer)：

- **主版本号**：不兼容的 API 修改
- **次版本号**：向下兼容的功能性新增
- **修订号**：向下兼容的问题修正

### 发布步骤

1. **更新版本号**

```bash
# 更新 pyproject.toml
version = "1.1.0"

# 更新 API 版本（如果需要）
```

2. **更新 CHANGELOG**

```markdown
# 更新日志

## [1.1.0] - 2024-01-15

### 新增

- 添加批量处理功能
- 支持更多文档格式

### 修复

- 修复 PDF 解码问题
```

3. **创建发布标签**

```bash
git tag -a v1.1.0 -m "Release version 1.1.0"
git push origin v1.1.0
```

4. **构建和发布**

```bash
# 构建 Docker 镜像
docker build -t agentic-ai-papers:v1.1.0 .

# 发布到 PyPI（可选）
python -m build
twine upload dist/*
```

## 性能优化

### Agent 优化

1. **并发处理**

```python
# 使用信号量限制并发
semaphore = asyncio.Semaphore(max_concurrent)

async def process_with_limit(item):
    async with semaphore:
        return await process(item)
```

2. **缓存策略**

```python
from functools import lru_cache

class CachedAgent(BaseAgent):
    @lru_cache(maxsize=128)
    async def get_cached_result(self, key):
        # 缓存结果
        pass
```

### API 优化

1. **异步数据库操作**

```python
async def get_papers_fast():
    """快速获取论文列表"""
    # 使用异步查询
    results = await db.fetch_all(query)
    return results
```

2. **响应压缩**

```python
from fastapi.middleware.gzip import GZipMiddleware

app.add_middleware(GZipMiddleware, minimum_size=1000)
```

## 维护任务

### 定期维护

- **每日**：检查错误日志
- **每周**：更新依赖包
- **每月**：清理临时文件和日志
- **每季度**：安全审计

### 监控指标

- API 响应时间
- 错误率
- 内存使用
- 磁盘空间
- 请求量

### 备份策略

```bash
# 备份脚本示例
#!/bin/bash
DATE=$(date +%Y%m%d)
tar -czf backup_${DATE}.tar.gz papers/ logs/
aws s3 cp backup_${DATE}.tar.gz s3://backup-bucket/
```

## 故障恢复

### 应急响应流程

1. **发现问题**

   - 监控告警
   - 用户反馈
   - 定期检查

2. **快速响应**

   - 定位问题
   - 评估影响
   - 通知相关人员

3. **问题解决**

   - 实施修复
   - 验证解决
   - 恢复服务

4. **事后分析**
   - 根因分析
   - 改进措施
   - 文档更新
