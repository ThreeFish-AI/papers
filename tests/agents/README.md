# Backend Tests

This directory contains the backend test suite for the Agentic AI Papers Collection & Translation Platform.

## 测试结构

```
tests/agents/
├── conftest.py              # 全局测试配置和fixtures
├── unit/                    # 单元测试
│   ├── agents/             # Agent层测试
│   │   └── test_workflow_agent.py
│   └── api/                # API层测试
│       ├── services/       # 服务层测试
│       │   └── test_paper_service.py
│       └── routes/         # 路由测试
│           └── test_papers_routes.py
├── integration/             # 集成测试
│   └── test_api_integration.py
├── fixtures/               # 测试工具和数据
│   ├── factories/          # 数据工厂
│   │   ├── paper_factory.py
│   │   └── task_factory.py
│   └── mocks/              # Mock配置
│       ├── mock_claude_api.py
│       ├── mock_file_operations.py
│       └── mock_websocket.py
└── data/                  # 测试数据
    └── sample_papers/
        └── sample.pdf
```

## 运行测试

### 安装测试依赖

```bash
pip install -e ".[dev]"
```

### 运行所有测试

```bash
# 使用项目提供的测试脚本 (从tests/agents目录)
python run_tests.py

# 或者从项目根目录运行
python tests/agents/run_tests.py

# 或者直接使用pytest
pytest tests/agents -v
```

### 运行特定类型的测试

```bash
# 只运行单元测试
pytest tests/agents/unit -v

# 只运行集成测试
pytest tests/agents/integration -v

# 运行特定测试文件
pytest tests/agents/unit/api/services/test_paper_service.py -v
```

### 生成覆盖率报告

```bash
pytest tests/agents --cov=agents --cov-report=html
# 报告将生成在 htmlcov/index.html
```

### 运行带标记的测试

```bash
# 跳过慢速测试
pytest tests/agents -m "not slow"

# 只运行集成测试
pytest tests/agents -m integration

# 运行WebSocket相关测试
pytest tests/agents -m websocket
```

## 测试重点

### 已实现的测试覆盖

1. **PaperService 测试**
   - 文件上传流程
   - 论文处理工作流
   - 状态跟踪
   - 批量处理
   - 错误处理

2. **API路由测试**
   - 所有API端点
   - 请求/响应验证
   - 错误状态码
   - 参数验证
   - 分页功能

3. **WorkflowAgent测试**
   - 完整处理流程
   - 各种工作流类型
   - 子Agent协调
   - 错误恢复

4. **集成测试**
   - 端到端处理流程
   - WebSocket通信
   - 并发请求处理
   - 批量操作

## Mock策略

### 外部依赖Mock

- **Claude API**: 使用 `mock_claude_api.py` 模拟所有Claude API调用
- **文件系统**: 使用 `mock_file_operations.py` 模拟文件读写操作
- **WebSocket**: 使用 `mock_websocket.py` 模拟实时通信

### 数据生成

使用 `factory-boy` 生成测试数据：
- `PaperFactory`: 生成论文相关数据
- `TaskFactory`: 生成任务相关数据

## 测试配置

### pytest配置 (pyproject.toml)

```toml
[tool.pytest.ini_options]
addopts = [
    "-ra",
    "-q",
    "--strict-markers",
    "--strict-config",
    "--cov=agents",
    "--cov-report=term-missing",
    "--cov-report=html:htmlcov",
    "--cov-fail-under=80",
    "-p no:warnings",
]
asyncio_mode = "auto"
markers = [
    "slow: marks tests as slow",
    "integration: marks tests as integration tests",
    "unit: marks tests as unit tests",
    "e2e: marks tests as end-to-end tests",
    "performance: marks tests as performance tests",
    "websocket: marks tests that require WebSocket",
]
```

## 最佳实践

1. **测试隔离**: 每个测试使用独立的临时目录和数据
2. **Mock使用**: 对外部依赖使用Mock避免实际调用
3. **异步测试**: 使用 `pytest-asyncio` 处理异步代码
4. **覆盖率目标**: 保持 >80% 的代码覆盖率
5. **清晰命名**: 测试名称应该清楚描述测试的场景和期望

## 添加新测试

1. 单元测试放在 `tests/agents/unit/` 对应模块下
2. 集成测试放在 `tests/agents/integration/`
3. 使用现有的fixtures和mocks
4. 确保测试标记正确（unit, integration等）
5. 运行所有测试确保没有破坏现有功能

## 故障排除

### 常见问题

1. **导入错误**: 确保在测试中正确设置Python路径
2. **AsyncMock问题**: 检查异步方法是否正确mock
3. **临时文件清理**: 使用pytest的tmp_path fixture自动清理
4. **覆盖率不正确**: 检查cov配置是否包含正确的路径

### 调试技巧

```bash
# 显示详细的测试输出
pytest -v -s tests/agents

# 只运行失败的测试
pytest --lf

# 在第一个失败时停止
pytest -x

# 显示本地变量
pytest --tb=long
```