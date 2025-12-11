# 架构设计方案

## 项目概述

Agentic AI Papers Collection & Translation Platform 是一个专注于 Agentic AI 研究的学术论文收集、翻译和管理平台，致力于为中文读者提供高质量的人工智能智能体领域技术资源。

### 核心目标

- 📚 **系统性收集**: 全面收集 Agentic AI 领域的重要研究论文
- 🔄 **智能翻译**: 基于 AI 的高质量中文学术翻译
- 🤖 **智能处理**: 使用专门的 Agent 处理学术论文
- 📊 **深度分析**: 提供论文的深度解读和分析

## 仓库结构

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

## 核心功能

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

## 架构设计

### 系统架构总览

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

### Agent 层架构

#### Agent 继承关系

```mermaid
classDiagram
    class BaseAgent {
        <<abstract>>
        +config: Config
        +skill_registry: SkillRegistry
        +process(input) Promise~Result~
        +validate_input(input) bool
        +log_processing(message) void
        #call_skill(name, params) Promise~SkillResult~
        #batch_call_skill(calls) Promise~SkillResult[]~
    }

    class PDFProcessingAgent {
        +process_pdf(file_path) Promise~PDFResult~
        +extract_metadata() Promise~Metadata~
        -handle_images() Promise~Image[]~
    }

    class TranslationAgent {
        +translate_to_chinese(content) Promise~Translation~
        +preserve_formatting(content) string
        -handle_technical_terms(terms) string[]
    }

    class HeartfeltAgent {
        +generate_insights(content) Promise~Insights~
        +extract_contributions(content) Contribution[]
        -compare_with_research(content) Comparison[]
    }

    class BatchProcessingAgent {
        +process_batch(items) Promise~BatchResult~
        +configure_concurrency(max_workers) void
        -schedule_tasks() Task[]
    }

    class WorkflowAgent {
        +execute_pipeline(input) Promise~PipelineResult~
        +coordinate_agents(agents) Promise~Result~
        -monitor_progress() Progress
    }

    BaseAgent <|-- PDFProcessingAgent
    BaseAgent <|-- TranslationAgent
    BaseAgent <|-- HeartfeltAgent
    BaseAgent <|-- BatchProcessingAgent
    BaseAgent <|-- WorkflowAgent

    PDFProcessingAgent --> "uses" PDFReaderSkill
    TranslationAgent --> "uses" ZhTranslatorSkill
    HeartfeltAgent --> "uses" HeartfeltSkill
    BatchProcessingAgent --> "uses" BatchProcessorSkill
    WorkflowAgent --> "orchestrates" PDFProcessingAgent
    WorkflowAgent --> "orchestrates" TranslationAgent
    WorkflowAgent --> "orchestrates" HeartfeltAgent
```

### Agent 交互模式

```mermaid
sequenceDiagram
    participant Client
    participant API as FastAPI
    participant Workflow as WorkflowAgent
    participant PDF as PDFProcessingAgent
    participant Trans as TranslationAgent
    participant Heartfelt as HeartfeltAgent
    participant Storage as File System

    Client->>API: 上传论文
    API->>Workflow: 创建处理任务

    par PDF 处理
        Workflow->>PDF: 处理 PDF
        PDF->>Storage: 提取图片到 images/
        PDF->>Storage: 保存元数据
        PDF-->>Workflow: 返回提取结果
    end

    opt 翻译流程
        Workflow->>Trans: 翻译内容
        Trans->>Storage: 保存翻译结果
        Trans-->>Workflow: 返回翻译结果
    end

    opt 深度分析
        Workflow->>Heartfelt: 生成深度分析
        Heartfelt->>Storage: 保存分析结果
        Heartfelt-->>Workflow: 返回分析结果
    end

    Workflow-->>API: 返回处理状态
    API-->>Client: 返回结果链接
```

### 文档处理流水线

```mermaid
flowchart LR
    A[输入源] --> B{类型判断}

    B -->|PDF| C[PDFProcessingAgent]
    B -->|Web| D[WebTranslationAgent]

    C --> E[pdf-reader 技能]
    D --> F[web-translator 技能]

    E --> G[内容提取]
    F --> G

    G --> H{处理模式}

    H -->|翻译| I[TranslationAgent]
    H -->|批处理| J[BatchProcessingAgent]
    H -->|深度分析| K[HeartfeltAgent]

    I --> L[zh-translator 技能]
    J --> M[batch-processor 技能]
    K --> N[heartfelt 技能]

    L --> O[中文翻译]
    M --> P[批量处理]
    N --> Q[深度解读]

    O --> R[markdown-formatter 技能]
    P --> R
    Q --> R

    R --> S[输出结果]

    subgraph 输出存储
        T[papers/source/]
        U[papers/translation/]
        V[papers/heartfelt/]
        W[papers/images/]
    end

    S --> T
    S --> U
    S --> V
    S --> W

    classDef input fill:#E3F2FD,stroke:#1976D2
    classDef agent fill:#F3E5F5,stroke:#7B1FA2
    classDef skill fill:#E8F5E9,stroke:#388E3C
    classDef output fill:#FFF3E0,stroke:#F57C00

    class A input
    class C,D,I,J,K agent
    class E,F,L,M,N,R skill
    class T,U,V,W output
```

## 技术栈

### 后端技术

- **Python 3.12+**: 主要编程语言
- **FastAPI**: 高性能异步 Web 框架
- **Claude Agent SDK**: Agent 开发框架
- **Pydantic**: 数据验证和序列化
- **Uvicorn**: ASGI 服务器

### AI 集成

- **Claude API**: 大语言模型服务
- **MCP (Model Context Protocol)**: 模型上下文协议
- **7 个专用 Claude Skills**: 文档处理能力

### 数据处理

- **PDF 处理**: pypdf2, pdfplumber
- **图像处理**: Pillow
- **Markdown**: markdown 库
- **Web 抓取**: beautifulsoup4, lxml

### 部署技术

- **Docker**: 容器化部署
- **Docker Compose**: 服务编排
- **Nginx**: 反向代理（可选）

## 设计原则

### 1. 最小化架构

- 避免过度工程化
- 优先使用现有工具和服务
- 保持架构简单可维护

### 2. 异步优先

- 全异步架构设计
- 非阻塞 I/O 操作
- 高并发处理能力

### 3. 可扩展性

- 模块化的 Agent 设计
- 插件式的 Skill 系统
- 清晰的接口定义

### 4. 容错性

- 优雅的错误处理
- 重试机制
- 详细的日志记录

## 部署架构

### 开发环境

```mermaid
flowchart TB
    subgraph LocalDev [本地开发环境]
        A[代码仓库] --> B[Python 3.12+]
        B --> C[venv 虚拟环境]
        C --> D[uvicorn 开发服务器]
        D --> E[本地文件系统]
    end

    F[Claude API] --> D
    G[MCP Services] --> D
```

### 生产环境

```mermaid
flowchart TB
    subgraph Docker [Docker 环境]
        A[API 容器] --> B[FastAPI 应用]
        C[Nginx 容器] --> D[静态文件服务]
        E[MCP 服务容器] --> F[外部工具]
    end

    G[用户] --> C
    C --> A
    A --> E

    subgraph Storage [持久化存储]
        H[papers/ 目录]
        I[logs/ 目录]
    end

    A --> H
    A --> I
    B --> I
```

## 工程实施策略

### 精简实施原则

1. **利用现有生态**: 充分利用 Claude Skills 的现有能力
2. **渐进式开发**: 从核心功能开始，逐步扩展
3. **本地优先**: 优先支持本地开发和部署
4. **文件系统存储**: 避免引入重型数据库依赖

### 实施阶段

1. **Agent SDK 集成**: 封装现有 Skills 为标准化 Agent
2. **API 服务构建**: 实现轻量级 RESTful API
3. **UI 界面**: 可选的简单 Web 界面
4. **部署优化**: 精简的容器化部署方案

## 性能考虑

### 并发处理

- 使用异步 I/O 提高并发能力
- 批处理 Agent 支持多任务并行
- 合理的资源限制和队列管理

### 缓存策略

- 技能调用结果缓存
- 文件处理状态缓存
- API 响应缓存

### 资源管理

- 内存使用优化
- 临时文件清理
- 长时间任务的资源释放
