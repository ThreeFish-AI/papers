# AI Agents Papers Collection 🔬

这是一个专注于 AI 智能体研究的学术论文仓库，收集和翻译了人工智能智能体领域的重要研究论文，为中文读者提供高质量的技术资源。

## 📋 项目概览

本仓库致力于收集、翻译和分享 AI 智能体领域的最新研究成果，特别关注以下方向：

- 🤖 **LLM 智能体架构与评估**
- 🔧 **上下文工程与检索增强生成 (RAG)**
- 📊 **智能体质量评估与观测性**
- 🧠 **强化学习在智能体搜索中的应用**
- 🔗 **知识图谱与图神经网络**
- 👁️ **OCR 与多模态智能体技术**

## 🎯 核心资源

### 📚 精选论文翻译

#### [Google Agent Quality 白皮书](./LLM%20Agents/Google/Agent%20Quality.md)
**[原始 PDF](./LLM%20Agents/Google/Agent%20Quality.pdf) | [中文翻译](./LLM%20Agents/Google/Agent%20Quality.md)**

Google 内部关于 AI 智能体质量评估的权威白皮书，提供了全面的智能体评估框架：

- **🎯 Outside-In 评估层次**：从黑盒到白盒的评估方法
- **📊 质量四大支柱**：有效性、效率、鲁棒性、安全性和对齐
- **🔍 观测性三大支柱**：日志记录、追踪、指标收集
- **⚖️ LLM-as-a-Judge** 和 **Agent-as-a-Judge** 评估范式
- **🧑‍💻 Human-in-the-Loop (HITL)** 评估流程

#### [Context Engineering 2.0](./Context%20Engineering/Context%20Engineering%202.0:%20The%20Context%20of%20Context%20Engineering.md)
**[原始 PDF](./Context%20Engineering/Context%20Engineering%202.0:%20The%20Context%20of%20Context%20Engineering.pdf)**

上下文工程的全面演进指南，从 1.0 到 4.0 时代的技术发展历程。

#### [DeepSeek OCR 研究](./DeepSeek%20OCR/DeepSeek_OCR_paper_中文版.md.md)
**[原始 PDF](./DeepSeek%20OCR/DeepSeek%20OCR:%20Contexts%20Optical%20Compression.pdf)**

DeepSeek OCR 技术的详细分析，涵盖上下文光学压缩技术。

### 📊 专项研究主题

#### GraphRAG 研究
- [Knowledge Graphs 综述](./Knowledge%20Graphs/愫读.md)
- [Graph-Guided Retrieval-Augmented Generation](./Knowledge%20Graphs/Graph-Guided%20Concept%20Selection%20For%20Efficient%20Retrieval-Augmented%20Generation.md)

#### 强化学习智能体搜索
- [基于强化学习的智能体搜索综合调研](./LLM%20Agents/A%20Comprehensive%20Survey%20on%20Reinforcement%20Learning-based%20Agentic%20Search.md)

#### 多模态智能体
- [LLaVA: Large Language and Vision Assistant](./LLM%20Agents/LLaVA.md)

## 🏗️ 仓库结构

```
papers/
├── Context Engineering/          # 上下文工程研究
├── DeepSeek OCR/                 # OCR 技术研究
├── GraphRAG/                     # GraphRAG 相关论文
├── Knowledge Graphs/             # 知识图谱研究
├── LLM Agents/                   # LLM 智能体论文
│   ├── Google/                   # Google 智能体研究
│   ├── LLaVA/                    # 多模态智能体
│   └── ...                       # 其他 LLM 智能体研究
├── Research Agents/              # 自主研究智能体
├── Tool-to-Agent Retrieval/      # 工具到智能体检索
├── .assets/                      # 静态资源与图表
├── .claude/                      # Claude Code 配置
├── AGENTS.md                     # 翻译指南与标准
└── README.md                     # 本文档
```

## 🌟 特色功能

### 📝 高质量翻译标准
- **逐字翻译**：保持原文技术准确性和完整性
- **格式保留**：完整保留图表、公式、参考文献格式
- **术语统一**：确保中文技术术语的一致性
- **结构完整**：维护学术论文的原始结构

### 🔍 完整性验证
每篇翻译都经过严格的完整性检查：
- ✅ 对照原文 PDF 验证内容完整性
- ✅ 确保章节、图表、公式无遗漏
- ✅ 保持引用和参考文献格式规范

### 📖 使用指南

#### 阅读论文
1. 浏览 [`LLM Agents/`](./LLM%20Agents/) 目录查看智能体相关论文
2. 查看 [`Context Engineering/`](./Context%20Engineering/) 了解上下文工程
3. 访问 [`GraphRAG/`](./GraphRAG/) 研究图检索增强生成

#### 贡献翻译
遵循 [`AGENTS.md`](./AGENTS.md) 中的翻译指南：
- 保持学术论文的专业性和准确性
- 统一技术术语的中文翻译
- 维护原文档的结构和格式

## 🤝 贡献方式

我们欢迎社区贡献！您可以：

- 📝 **提交新的论文翻译**
- 🔄 **改进现有翻译质量**
- 📚 **推荐重要研究方向**
- 🐛 **报告翻译错误或遗漏**

## 📜 许可证

本仓库遵循开源许可证，所有翻译内容仅供学术研究使用。原始论文的版权属于相应的出版机构和作者。

## 🔗 相关链接

- [微软 GraphRAG 框架源码解读](https://www.cnblogs.com/fanzhidongyzby/p/18294348/ms-graphrag)
- [Tongyi DeepResearch](https://mp.weixin.qq.com/s/SbPF7zAulPok2Xz3wU2ncw)
- [Claude Code](https://claude.ai/code) - 本项目使用的 AI 辅助开发工具

## 📊 统计信息

- 📄 **论文总数**: 15+ 篇
- 🌐 **翻译完成**: 12+ 篇
- 📂 **研究领域**: 6 个主要方向
- 🔄 **持续更新**: 定期添加新的研究内容

---

**注意**: 本仓库的内容仅供学术研究和教育目的使用。在使用翻译内容时，请引用原始论文的完整来源信息。
