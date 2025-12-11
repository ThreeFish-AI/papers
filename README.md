# Agentic AI Papers Collection & Translation Platform 🔬

这是一个专注于 Agentic AI 研究的学术论文收集、翻译和管理平台，致力于为中文读者提供高质量的人工智能智能体领域技术资源。

## 📋 项目概览

本平台提供：

- 📚 **论文收集**: 系统性收集 Agentic AI 领域重要研究论文
- 🔄 **智能翻译**: 基于 AI 的高质量中文翻译
- 🤖 **Agent 工具**: 专门用于处理学术论文的智能代理
- 🖥️ **管理界面**: Web UI 用于管理论文和翻译流程

## 🏗️ 仓库结构

```bash
agentic-ai-papers/
├── agents/             # AI 代理实现
│   └── claude/         # 基于 Claude Agent SDK 的代理
│       ├── __init__.py
│       ├── base.py           # Agent 基类
│       ├── workflow_agent.py # 工作流协调器
│       ├── pdf_agent.py      # PDF 处理代理
│       ├── translation_agent.py # 翻译代理
│       ├── heartfelt_agent.py # 深度分析代理
│       └── batch_agent.py    # 批处理代理
├── api/                # FastAPI 服务层
│   ├── main.py        # 应用入口
│   ├── routes/        # API 路由
│   │   ├── papers.py  # 论文管理接口
│   │   ├── tasks.py   # 任务管理接口
│   │   └── websocket.py # WebSocket 接口
│   ├── services/      # 业务逻辑层
│   │   ├── paper_service.py # 论文处理服务
│   │   ├── task_service.py  # 任务管理服务
│   │   └── websocket_service.py # WebSocket 服务
│   └── models/        # 数据模型
│       ├── paper.py   # 论文相关模型
│       └── task.py    # 任务相关模型
├── core/              # 核心配置和工具
│   ├── config.py      # 应用配置
│   ├── exceptions.py  # 异常定义
│   └── utils.py       # 工具函数
├── ui/                # Web UI（可选）
│   ├── index.html     # 主页面
│   └── nginx.conf     # Nginx 配置
├── papers/            # 论文存储
│   ├── source/        # 原始文档 (PDF)
│   ├── images/        # 提取的图片
│   ├── translation/   # 中文翻译 (Markdown)
│   └── heartfelt/     # 深度分析 (Markdown)
├── .claude/           # Claude 配置和 Skills
│   └── skills/        # Claude Skills (7个)
├── logs/              # 日志文件
├── docker-compose.yml # 容器编排配置
├── Dockerfile         # 容器镜像配置
└── pyproject.toml     # 项目依赖配置
```

## 🎯 核心功能

### 智能论文处理

- 解析和提取 PDF/Web Page 内容
- 识别和提取数学公式和表格
- 提取图像和图表
- 自动分类和标签

### 高质量翻译

- 保持技术术语准确性
- 保留数学公式格式
- 适应中文表达习惯
- 翻译质量评估

### 深度解读

- 核心贡献总结
- 技术要点分析
- 相关研究对比
- 实践应用建议

## 📋 工程实施计划方案

### 📊 项目现状

#### ✅ 已完成的核心功能

1. **完整的 Claude Skills 生态系统** (7 个技能):

   - `doc-translator`: 文档翻译工作流协调器
   - `pdf-reader`: PDF 内容提取(支持图片/表格/公式)
   - `web-translator`: 网页内容提取和转换
   - `zh-translator`: 中文翻译(保持格式)
   - `markdown-formatter`: Markdown 格式优化
   - `batch-processor`: 大文档批处理
   - `heartfelt`: 深度阅读和摘要生成

2. **丰富的论文库**:
   - 20+ 篇分类整理的 PDF 论文
   - 15+ 篇已完成中文翻译
   - 清晰的目录结构 (source/, translation/, heartfelt/, images/)

#### ✅ 最新实现状态 (v1.0.0)

1. **完整的混合架构实现**:
   - Claude Agent SDK 标准化 Agent 层
   - FastAPI 异步 API 服务层
   - 保留现有 Claude Skills 生态
   - 精简部署配置

2. **已实现的核心组件**:
   - BaseAgent 基类和 5 个专用 Agent
   - 完整的 RESTful API 接口
   - WebSocket 实时通信
   - 任务管理和进度追踪
   - Docker 容器化部署

3. **优化的部署方案**:
   - 单一 API 服务 + 可选 UI
   - 移除重型依赖 (PostgreSQL, Redis, MinIO)
   - 本地开发优先设计

### 🎯 精简实施策略

**核心理念**: 利用现有的 Claude Skills 生态，构建轻量级管理界面，避免过度工程化。

```mermaid
flowchart TD
    %% 用户交互层
    A[Web界面<br/>可选的静态页面] --> B[FastAPI 服务<br/>异步 API 服务]

    %% API路由层
    B --> C[论文路由<br/>/api/papers]
    B --> D[任务路由<br/>/api/tasks]

    %% 服务层
    C --> E[论文服务<br/>PaperService]
    D --> F[任务服务<br/>TaskService]

    %% Agent层
    E --> G[WorkflowAgent<br/>工作流协调]
    F --> G
    E --> H[PDFProcessingAgent<br/>PDF处理]
    E --> I[TranslationAgent<br/>翻译]
    E --> J[BatchProcessingAgent<br/>批处理]
    E --> K[HeartfeltAgent<br/>深度分析]

    %% Skills封装层
    subgraph Skills [Claude Skills - MCP工具]
        S1[pdf-reader<br/>内容提取]
        S2[zh-translator<br/>中文翻译]
        S3[markdown-formatter<br/>格式优化]
        S4[doc-translator<br/>工作流协调]
        S5[batch-processor<br/>批量处理]
        S6[heartfelt<br/>深度解读]
    end

    G --> S4
    H --> S1
    I --> S2
    J --> S5
    K --> S6

    %% 存储层
    subgraph Storage [文件系统存储]
        F1[source/<br/>原始文档]
        F2[translation/<br/>翻译文档]
        F3[heartfelt/<br/>深度摘要]
        F4[images/<br/>提取图片]
        F5[logs/<br/>处理日志]
    end

    E --> Storage
    F --> F5

    %% MCP服务层
    subgraph MCP [MCP服务器]
        M1[data-extractor<br/>PDF/Web提取]
        M2[filesystem<br/>文件操作]
        M3[time<br/>时间服务]
    end

    Skills --> MCP

    %% 样式
    classDef ui fill:#4CAF50,stroke:#388E3C,color:#fff
    classDef api fill:#2196F3,stroke:#1976D2,color:#fff
    classDef service fill:#00BCD4,stroke:#0097A7,color:#fff
    classDef agent fill:#9C27B0,stroke:#7B1FA2,color:#fff
    classDef skills fill:#673AB7,stroke:#512DA8,color:#fff
    classDef storage fill:#FF9800,stroke:#F57C00,color:#fff
    classDef mcp fill:#795548,stroke:#5D4037,color:#fff

    class A ui
    class B,C,D api
    class E,F service
    class G,H,I,J,K agent
    class S1,S2,S3,S4,S5,S6 skills
    class F1,F2,F3,F4,F5 storage
    class M1,M2,M3 mcp
```

### 🚀 基于 Claude Agent SDK 的实施阶段

#### Phase 1: Agent SDK 服务架构 (2.5 小时)

- 创建基于 Claude Agent SDK 的 Agent 服务
- 封装现有 Skills 为标准化 Agent
- 实现异步处理架构

#### Phase 2: FastAPI 服务实现 (1.5 小时)

- 构建轻量级 API 服务
- 实现论文和任务管理接口
- 集成 Agent SDK 调用

#### Phase 3: 简化 Web 界面 (可选，1 小时)

- 创建单页面应用（可选）
- 实现文件上传和进度展示
- 集成 API 调用

#### Phase 4: 极简部署配置 (30 分钟)

- 移除重型基础设施 (PostgreSQL, Redis, MinIO, Celery)
- 更新 docker-compose.yml 为单服务
- 创建最小化 Dockerfile

#### Phase 5: Agent 自动化工作流 (1 小时)

- 实现工作流协调 Agent
- 创建文件监控和自动处理
- 集成批处理和深度分析功能

### 📁 关键实施文件

**需要创建：**

1. **`/agents/claude/base.py`** - Agent SDK 基础类
2. **`/agents/claude/workflow_agent.py`** - 工作流协调 Agent
3. **`/agents/claude/pdf_agent.py`** - PDF 处理 Agent
4. **`/agents/claude/translation_agent.py`** - 翻译 Agent
5. **`/api/main.py`** - FastAPI 应用入口
6. **`/api/routes/papers.py`** - 论文管理接口
7. **`/api/services/paper_service.py`** - 业务逻辑层
8. **`Dockerfile`** - 应用容器化

**需要修改：**

1. **`pyproject.toml`** - 简化依赖，添加 claude-agent-sdk
2. **`docker-compose.yml`** - 精简服务配置
3. **`README.md`** - 更新部署和使用说明

### ✅ 优化后的优势

- **标准化架构**: 基于 Claude Agent SDK 的标准化 Agent 实现
- **异步处理**: 全异步架构，提高并发处理能力
- **清晰分层**: Agent -> Service -> API 的清晰分层
- **极简部署**: 单一 API 服务 + 可选 UI
- **易于扩展**: 每个 skill 对应一个 Agent，易于独立开发和测试

_完整实施计划详见: [工程实施计划详细方案](.claude/plans/joyful-mapping-gosling.md)_

## 🚀 快速开始

### 环境要求

- Python 3.12+
- Docker & Docker Compose (可选，用于容器化部署)
- Claude API Key

### 安装步骤

1. **克隆仓库**

```bash
git clone https://github.com/ThreeFish-AI/agentic-ai-papers.git
cd agentic-ai-papers
```

2. **配置环境变量**

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，添加必要的配置
# 必须设置 ANTHROPIC_API_KEY
```

3. **使用 Docker Compose 部署（推荐）**

```bash
# 启动 API 服务
docker-compose up -d

# 启动 Web UI（可选）
docker-compose --profile ui up -d

# 启动 MCP 服务（可选）
docker-compose --profile mcp up -d
```

4. **本地开发安装**

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -e .

# 启动 API 服务
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

## 📖 使用指南

### 添加新论文

#### 方式一：使用 API

```bash
# 上传论文
curl -X POST "http://localhost:8000/api/papers/upload" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@paper.pdf"

# 触发翻译
curl -X POST "http://localhost:8000/api/papers/{paper_id}/translate"

# 查询任务状态
curl "http://localhost:8000/api/tasks/{task_id}"
```

#### 方式二：使用 Web UI

1. 访问 `http://localhost:3000`（如启用 UI 服务）
2. 上传 PDF 文件
3. 选择处理流程（翻译、批处理、深度分析等）
4. 查看实时处理进度和结果

#### 方式三：直接使用文件系统

1. 将 PDF 文件放入 `papers/source/` 对应分类目录
2. 文件监控 Agent 会自动检测并处理
3. 处理结果保存至对应目录（translation/, heartfelt/）

## 🌟 研究领域

### LLM Agents

- Agent 架构设计
- Tool 使用和学习
- 多 Agent 协作
- 规划和推理

### Context Engineering

- 上下文管理策略
- 提示工程技术
- 记忆机制设计
- 会话状态维护

### Knowledge Graphs

- 知识表示方法
- 图神经网络
- 知识增强生成
- 推理和查询

### Multi-Agent Systems

- 协作机制
- 通信协议
- 任务分配
- 涌现行为

## 🤝 贡献方式

我们欢迎社区贡献！您可以：

- 📝 **提交新论文**: 添加重要的 Agentic AI 研究论文
- 🔄 **改进翻译**: 提升翻译质量和准确性
- 🛠️ **开发 Agent**: 贡献新的处理能力
- 🐛 **报告问题**: 帮助改进平台功能
- 📚 **完善文档**: 改进使用指南和说明

## 📊 项目统计

- 📄 **论文总数**: 20+ 篇
- 🌐 **翻译完成**: 15+ 篇
- 📂 **研究领域**: 6 个主要方向
- 🤖 **Agent 数量**: 10+ 个专用代理
- 🔄 **持续更新**: 每周添加新内容

## 📜 许可证

本项目采用 [MIT License](LICENSE)，所有翻译内容仅供学术研究使用。原始论文的版权属于相应的出版机构和作者。

## 🔗 相关链接

- [Claude Agent SDK](https://github.com/anthropics/claude-agent-sdk)
- [Google Agent Development Kit](https://developers.google.com/agent-kit)
- [Agentic AI Survey](https://arxiv.org/abs/2401.01268)
- [Agent Project](https://agent.supply/) - 中文 Agent 项目聚合

---

**注意**: 本项目的内容仅供学术研究和教育目的使用。在使用翻译内容时，请引用原始论文的完整来源信息。
