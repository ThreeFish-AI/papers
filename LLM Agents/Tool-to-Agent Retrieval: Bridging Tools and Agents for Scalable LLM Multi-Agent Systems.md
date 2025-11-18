# 工具到智能体检索：连接工具与智能体的可扩展 LLM 多智能体系统

Elias Lumer, Faheem Nizar, Anmol Gulati, Pradeep Honaganahalli Basavaraju, Vamse Kumar Subbiah

普华永道美国

---

**摘要**。大语言模型（LLM）多智能体系统的最新进展使得子智能体的可扩展编排成为可能，每个子智能体协调数百或数千个工具或模型上下文协议（MCP）服务器。然而，现有的检索方法通常在路由前将查询与粗粒度的智能体级描述进行匹配，这掩盖了细粒度的工具功能，并经常导致次优的智能体选择。我们引入**工具到智能体检索**（Tool-to-Agent Retrieval），这是一个统一的框架，将工具及其父智能体嵌入到共享向量空间中，并通过元数据关系连接它们。通过显式表示工具能力并将元数据遍历到智能体级别，工具到智能体检索实现了细粒度的工具级或智能体级检索，确保智能体及其底层工具或 MCP 服务器得到平等表示，避免了将许多工具分块在一起时产生的上下文稀释。在八个嵌入模型上评估工具到智能体检索，我们的方法在 LiveMCPBench 基准测试上相比之前最先进的智能体检索器，实现了 Recall@5 一致提升 19.4%，nDCG@5 提升 17.7%。

**关键词**：大语言模型 · 工具检索 · 智能体路由 · 多智能体系统 · 模型上下文协议（MCP）

---

## 1 引言

大语言模型（LLM）智能体和模型上下文协议（MCP）的最新进展使得助手能够在推理时发现、装备和使用大量外部工具和 MCP 服务器 [6, 20]。在实践中，单个助手可能会委托给专门的子智能体进行代码分析、数据库或网络搜索，每个子智能体在单个界面后捆绑数十个工具 [5]。一个核心挑战是路由：给定用户查询，系统应该选择特定工具还是利用整个智能体（例如 MCP 服务器），后者提供一组协调的工具？将所有工具描述转发给模型是不切实际的，例如，一个包含 26 个工具的 MCP 服务器可能消耗超过 4,600 个 token，使得高效检索对可扩展性至关重要 [35, 38]。

现有策略通常分为两类。智能体优先的管道将查询与简短的智能体描述匹配，然后仅在该智能体内操作，这可能隐藏高度相关的工具，其父描述与查询明显不一致。相反，仅工具检索独立处理每个工具，并忽略周围工具包在多步骤任务中的互补好处 [22]。最近的基准测试突出了在多步骤工具选择中的这些挑战，评估了跨不同工具存储库的智能体 [10, 15, 29]。在实践中，当工作流程受益于协调的工具集时，单工具匹配可能表现不佳，而智能体优先路由可能 overlook 细粒度能力。需要的是一个能够在两个级别操作的检索机制，当查询具体时返回专注的工具，或者当更广泛的能力有益时返回整个智能体，而不承诺脆弱的两阶段管道。

**图 1**。仅智能体检索（左）与提出的工具到智能体检索（右）的比较，后者将工具和智能体嵌入共享向量空间以支持联合检索和遍历。

我们引入**工具到智能体检索**（Tool-to-Agent Retrieval），它将工具及其父智能体表示在同一向量空间中，并通过显式元数据链接它们（图 1）。在查询时，检索在联合索引上运行，根据哪个更适合查询返回单个工具或智能体包。通过建模细粒度工具语义同时通过工具→智能体链接保留智能体上下文（并在检索时遍历这些链接），该方法避免了当许多工具折叠成单个粗略描述时产生的上下文稀释。这使得能够一次性决定要装备什么（工具 vs. 智能体），改善了专注和多步查询的路由。

**相关工作**。越来越多的工作通过将工具描述和元数据嵌入工具知识库并为每个查询选择 top-k 工具来构建 LLM 智能体的工具检索 [19, 21, 22, 37]。**检索增强生成**（RAG）使 LLM 智能体能够通过语义搜索访问外部知识和工具 [7]，最近的混合方法结合知识图谱和向量检索以提高工具选择准确性 [32]。诸如 PLUTO 和 Re-Invoke 系统细化了工具选择的密集检索，并在规模上展示了强大的单次通过性能 [4, 9]。**基于图的方法**已经出现以构建工具关系，包括 ToolNet 和 ControlLLM，它们通过图结构组织工具以实现更复杂的导航 [16, 17]。诸如 ToolReAGT 等**迭代方法**分解复杂任务并逐步检索工具，提高了多步问题的召回率 [2, 3]。**多跳推理框架**通过链接中间步骤进一步增强检索 [34, 36]。同时，**分层管道**首先选择 MCP 服务器，然后选择其中的工具以控制提示成本，但这种智能体优先路由可能抑制细粒度匹配 [6, 39]。我们的方法通过联合表示工具和智能体并在单个链接空间上检索而有所不同，因此系统不必预先承诺仅工具或智能体优先选择。

**贡献**。我们通过这项工作做出以下贡献：

1. **统一检索框架**：我们引入了一种新颖的工具检索策略，将工具及其父智能体嵌入共享向量空间，通过工具到智能体元数据遍历链接，实现统一检索并达到最先进的性能。

2. **细粒度路由机制**：我们提出了一种检索过程，保留细粒度工具级细节同时保留智能体级上下文，减轻来自粗略摘要的上下文稀释，并提高多步查询的鲁棒性。

3. **全面评估**：我们在 LiveMCPBench 上跨八个嵌入模型评估该方法，展示了相比之前最先进方法 17.7%（recall@5）和 19.4%（nDCG@5）的改进。

---

## 2 方法：工具到智能体检索

如图 1 所示，工具到智能体检索将工具及其父智能体嵌入到统一向量空间中，通过元数据关系显式链接每个工具到其父智能体。我们考虑一个包含相应智能体的 MCP 服务器目录，表示为 a ∈ A。每个智能体 a 拥有一组工具 Ta，由智能体暴露的 API 调用、函数或操作组成。组合系统被建模为二分图 G = (A, T, E)，其中边 E 表示工具和智能体之间的所有权关系。工具关系的基于图建模实现了结构化导航和对工具能力的推理 [11, 33]。这种统一表示直接解决了单级检索的局限性。仅通过智能体描述检索可能会掩盖工具级别的细粒度功能能力，而独立检索工具会丢弃重要的执行上下文，如在智能体级别维护的身份验证、参数推断或访问策略。通过集成两个级别，检索器可以显示相关工具而不丢失周围的智能体上下文。此外，每个查询或子查询最终解析为可执行智能体，确保检索的实体能够响应用户请求。

**索引**。我们构建了一个统一的工具-智能体目录 C，集成了工具和智能体进行检索。目录由两个语料库组成：工具语料库 CT 和智能体语料库 CA。

工具语料库 CT ⊂ C 包含直接为检索索引的工具名称和描述。每个工具条目包括显式链接到其父 MCP 服务器或智能体的元数据，表示为 owner(T) = A。此映射支持在查询解析期间从检索的工具遍历到相应的可执行智能体，借鉴了用于知识集成的基于图的表示技术 [27, 28]。

智能体语料库 CA ⊂ C 类似地包含智能体名称和描述，表示更高级别的能力并在检索图中作为父节点。

**检索**。检索过程修改了标准的 top-K 排序过程。目标是为给定查询或子查询识别 top-K 最相关的智能体。为实现这一点，我们首先从统一的工具-智能体目录 C 中检索 top N ≫ K 个实体，按与查询的语义相似性排序。这种方法结合了语义和词汇匹配策略以提高召回率 [14]，利用 BM25 [30] 以及密集向量检索。然后聚合相应的父智能体，并选择 top-K 唯一智能体。

完整的检索过程在算法 1 中详细说明。

**算法 1** 组合工具-智能体 Top-K 检索（工具到智能体检索）

```
输入：查询 q，语料库 C（智能体 ∪ 工具），类型 τ(·) ∈{agent, tool}，所有者映射 own(·)，相似度 s(q, ·)，截断值 N, K
输出：智能体集合 A⋆，|A⋆|= K
1: L ← TopN(q, C, N)                    # 按 s 排序并返回有序 [e(1), . . . , e(N)]
2: A ← ∅; i ← 1
3: while |A| < K and i ≤ N do
4:     e ← L[i]
5:     if τ(e) = agent then
6:         a ← e
7:     else if τ(e) = tool and own(e) 已定义 then
8:         a ← own(e)
9:     else
10:        i ← i + 1; continue          # 如果所有者缺失/未定义则跳过
11:    if a ∉ A then
12:        A ← A ∪ {a}
13:    i ← i + 1
14: return A⋆ ← A
```

**查询**。工具到智能体检索器的输入可以是原始用户查询、从中分解的子步骤，或两者的组合。我们评估两种查询范式。

第一种，**直接查询**（Direct Querying），直接使用用户的高级问题作为检索查询，无需任何预处理。这种方法为整体任务检索 top-K 最相关的智能体或工具。

第二种，**逐步查询**（Step-wise Querying），将原始查询分解为一系列较小的子任务。然后每个步骤独立提交给检索器，允许系统在多步工作流程中根据需要识别不同的智能体。这种分解策略与基于推理的检索规划方法一致，后者将复杂查询分解为可管理的子目标 [12, 13]。查询重写技术通过重构查询以改进语义匹配进一步增强检索 [23]。这种逐步过程是我们评估中使用的主要设置。

---

## 3 实验与评估

我们评估了所提出的工具到智能体检索器的有效性，与仅智能体检索方法进行比较。我们的主要假设是，在工具和智能体上操作的统一检索器将优于仅检索智能体的方法。在 MCP 环境中，特别是在分层查询下 [6, 21]，这种改进扩展到路由的初始阶段，其中识别正确的 MCP 服务器能够访问其相关工具进行跨连接操作。最近的基准测试工作突出了在多轮交互中有状态、对话式工具使用的挑战 [18, 40]。

实验设置评估在为每个查询识别正确智能体或 MCP 服务器的检索准确性。我们报告标准信息检索指标，包括召回率（Recall）、平均精度均值（mAP）和标准化折扣累积增益（nDCG），以量化所提出方法的性能改进。

**数据集和评估协议**。我们在 LiveMCPBench 数据集 [24, 25] 上评估我们的方法，该数据集包括 70 个 MCP 服务器和 527 个工具，以及 95 个带逐步分解和相关工具-智能体映射的真实问题。这种结构支持检索性能的细粒度、步骤级评估。平均而言，每个问题跨越 2.68 个步骤，涉及 2.82 个工具和 1.40 个 MCP 智能体。

为了隔离工具级信息的贡献，我们还构建了一个仅智能体的基线数据集，仅包含 MCP 服务器名称和描述。在推理期间，我们采用逐步查询，并将工具到智能体检索与 BM25 [31]、ScaleMCP [21] 和 MCPZero [6] 进行比较。

**检索器设置**。我们在几个嵌入模型上评估检索性能。具体来说，我们使用了 8 个嵌入模型，包括闭源和开源 [1, 8, 26]。使用每个模型对数据集进行嵌入，并执行语义相似性搜索以检索相关实体。我们首先从工具-智能体目录中检索 top N ≫ K 个实体，然后使用算法 1 选择 top-K 唯一智能体。通过将检索的智能体与评估集中每个查询相关的真实智能体进行比较来计算检索准确性。

**结果**。表 1 和 2 显示工具到智能体检索在召回率、mAP 和 nDCG 指标上始终优于先前方法。我们的方法在所有基线上实现了优越性能，在多个嵌入系列中观察到增益，包括 Vertex AI、Gemini、Titan、OpenAI 和 MiniLM。

这些改进主要来自更丰富的检索语料库，该语料库联合索引工具和智能体，实现更细粒度的语义对齐。重要的是，性能提升不能仅归因于工具级检索。联合索引支持细致的匹配同时保留智能体上下文，如 39.13% 的检索 top-K 项目源自智能体语料库 CA 和 34.44% 的匹配 top-K 工具也追溯到 CA 所证明。总之，这些结果证明显式链接工具到其父智能体减轻了上下文稀释并改善了多步路由，而不牺牲细粒度精度。

在所有八个嵌入模型中，工具到智能体检索表现出显著稳定的改进，相对于 MCPZero，Recall@5 的标准偏差为 0.02，nDCG@5 的标准偏差为 0.01。这种一致性表明增益是架构无关的，主要由统一索引设计驱动，而不是嵌入特定行为。最强的相对改进在 Amazon Titan v2 上观察到（Recall@5 从 0.66 提高到 0.85，相对增益 +28%），而即使是紧凑的 All-MiniLM-L6-v2 模型也实现了 +13% 的改进，确认了在专有和开源嵌入中的普遍性。

**表 1** LiveMCPBench 基准测试结果

比较工具到智能体检索与基线（BM25、Q.Retrieval、ScaleMCP 和 MCPZero）。指标为 K ∈{1, 5, 10} 的 Recall@K、mAP@K 和 nDCG@K。

| 方法                   | Recall |        |        | mAP    |        |        | nDCG   |        |        |
|------------------------|--------|--------|--------|--------|--------|--------|--------|--------|--------|
|                        | @1     | @3     | @5     | @1     | @3     | @5     | @1     | @3     | @5     |
| BM25                   | 0.20   | 0.20   | 0.20   | 0.12   | 0.12   | 0.12   | 0.14   | 0.14   | 0.14   |
| Q.Retrieval            | 0.31   | 0.47   | 0.56   | 0.31   | 0.31   | 0.24   | 0.31   | 0.35   | 0.32   |
| MCPZero                | 0.44   | 0.66   | 0.70   | 0.45   | 0.39   | 0.31   | 0.45   | 0.46   | 0.41   |
| ScaleMCP               | 0.49   | 0.68   | 0.74   | 0.49   | 0.40   | 0.29   | 0.49   | 0.48   | 0.40   |
| **工具到智能体检索**   | **0.61** | **0.77** | **0.83** | **0.61** | **0.49** | **0.34** | **0.61** | **0.56** | **0.46** |

**表 2** 与 MCPZero 的各嵌入模型比较

| 检索器模型                  | Recall@5 |        | nDCG@5 |        | mAP@5 |        |
|----------------------------|----------|--------|--------|--------|-------|--------|
|                            | **Ours** | MCPZero | **Ours** | MCPZero | **Ours** | MCPZero |
| Vertex AI text embedding 005 | 0.87     | 0.74   | 0.48   | 0.42   | 0.36   | 0.32   |
| Gemini Embedding 001       | 0.86     | 0.74   | 0.49   | 0.44   | 0.37   | 0.34   |
| Amazon titan embed text v2 | 0.85     | 0.66   | 0.47   | 0.37   | 0.35   | 0.28   |
| Amazon titan embed text v1 | 0.85     | 0.65   | 0.48   | 0.39   | 0.36   | 0.30   |
| OpenAI text embedding ada 002 | 0.83     | 0.70   | 0.50   | 0.40   | 0.39   | 0.30   |
| OpenAI text embedding 3 small | 0.87     | 0.72   | 0.49   | 0.41   | 0.36   | 0.31   |
| OpenAI text embedding 3 large | 0.87     | 0.74   | 0.50   | 0.42   | 0.38   | 0.32   |
| All MiniLM L6 v2          | 0.80     | 0.67   | 0.45   | 0.39   | 0.33   | 0.29   |

---

## 4 结论

大语言模型（LLM）多智能体系统的最新进展使得子智能体的可扩展编排成为可能，这些子智能体协调数百或数千个工具或模型上下文协议（MCP）服务器。我们引入了**工具到智能体检索**（Tool-to-Agent Retrieval），这是一个用于大语言模型（LLM）多智能体系统的统一框架，将工具及其父智能体嵌入到共享向量空间中，通过元数据关系链接。通过显式建模工具能力并支持工具级和智能体级表示之间的遍历，我们的方法支持细粒度检索决策，保留细粒度上下文而不引入粗略智能体摘要的稀释。在 LiveMCPBench 基准上跨八个嵌入模型的实验证明了相比先前智能体检索器的实质性改进，Recall@5 增益 19.4%，nDCG@5 增益 17.7%。这些结果突出了统一工具和智能体选择的有希望方向，激励了未来对跨越来越复杂的智能体网络扩展的检索架构的研究。

---

## 参考文献

1. Amazon: Amazon titan 文本嵌入模型。https://docs.aws.amazon.com/bedrock/latest/userguide/titan-embedding-models.html (2025)
2. Anantha, R., Bandyopadhyay, B., Kashi, A., Mahinder, S., Hill, A.W., Chappidi, S.: Protip: 渐进式工具检索改进规划 (2023), https://arxiv.org/abs/2312.10332
3. Braunschweiler, N., Doddipatla, R., ZORILA, T.C.: ToolreAGt: 通过检索增强生成为基于 LLM 的复杂任务解决方案进行工具检索。在：ACL 2025 的知识基础模型 (2025), https://openreview.net/forum?id=LTeBIM1rJL
4. Chen, Y., Yoon, J., Sachan, D.S., Wang, Q., Cohen-Addad, V., Bateni, M., Lee, C.Y., Pfister, T.: Re-invoke: 零样本工具检索的工具调用重写 (2024), https://arxiv.org/abs/2408.01875
5. Du, Y., Wei, F., Zhang, H.: AnyTool: 用于大规模 API 调用的自反思、分层智能体 (2024), arXiv preprint arXiv:2402.04253
6. Fei, X., Zheng, X., Feng, H.: Mcp-zero: 自主 LLM 智能体的主动工具发现 (2025), https://arxiv.org/abs/2506.01056
7. Gao, Y., Xiong, Y., Gao, X., Jia, K., Pan, J., Bi, Y., Dai, Y., Sun, J., Wang, M., Wang, H.: 大语言模型的检索增强生成：综述 (2024), arXiv preprint arXiv:2312.10997
8. Google: Vertex AI 文本嵌入模型。https://cloud.google.com/vertex-ai/generative-ai/docs/embeddings/get-text-embeddings (2025)
9. Huang, T., Jung, D., Chen, M.: 规划和编辑检索内容以增强工具学习 (2024), https://arxiv.org/abs/2404.00450
10. Huang, Y., Shi, J., Li, Y., Fan, C., Wu, S., Zhang, Q., Liu, Y., Zhou, P., Wan, Y., Gong, N.Z., Sun, L.: 大语言模型的元工具基准：决定是否使用工具以及使用哪些工具 (2024), arXiv preprint arXiv:2310.03128
11. Jin, B., Xie, C., Zhang, J., Roy, K.K., Zhang, Y., Li, Z., Li, R., Tang, X., Wang, S., Meng, Y., Han, J.: 图思维链：通过图推理增强大语言模型 (2024), arXiv preprint arXiv:2404.07103
12. Joshi, A., Sarwar, S.M., Varshney, S., Nag, S., Agrawal, S., Naik, J.: REAPER: 复杂 RAG 系统的基于推理的检索规划 (2024), arXiv preprint arXiv:2407.18553
13. Khattab, O., Santhanam, K., Li, X.L., Hall, D., Liang, P., Potts, C., Zaharia, M.: Demonstrate-Search-Predict: 组合检索和语言模型进行知识密集型 NLP (2023), arXiv preprint arXiv:2212.14024
14. Kuzi, S., Zhang, M., Li, C., Bendersky, M., Najork, M.: 利用语义和词汇匹配提高文档检索系统的召回率：混合方法 (2020), arXiv preprint arXiv:2010.01195
15. Li, M., Zhao, Y., Yu, B., Song, F., Li, H., Yu, H., Li, Z., Huang, F., Li, Y.: API-Bank: 工具增强 LLM 的综合基准 (2023), arXiv preprint arXiv:2304.08244
16. Liu, X., Peng, Z., Yi, X., Xie, X., Xiang, L., Liu, Y., Xu, D.: Toolnet: 通过工具图将大语言模型与大量工具连接 (2024), arXiv preprint arXiv:2403.00839
17. Liu, Z., Lai, Z., Gao, Z., Cui, E., Li, Z., Zhu, X., Lu, L., Chen, Q., Qiao, Y., Dai, J., Wang, W.: Controlllm: 通过图搜索用工具增强语言模型 (2023), arXiv preprint arXiv:2310.17796
18. Lu, J., Holleis, T., Zhang, Y., Aumayer, B., Nan, F., Bai, F., Ma, S., Ma, S., Li, M., Yin, G., Wang, Z., Pang, R.: Toolsandbox: LLM 工具使用能力的有状态、对话式、交互式评估基准 (2024), arXiv preprint arXiv:2408.04682
19. Lumer, E., Basavaraju, P.H., Mason, M., Burke, J.A., Subbiah, V.K.: Graph rag-tool fusion (2025), https://arxiv.org/abs/2502.07223
20. Lumer, E., Gulati, A., Subbiah, V.K., Basavaraju, P.H., Burke, J.A.: Memtool: 优化 LLM 智能体多轮对话中动态工具调用的短期记忆管理 (2025), https://arxiv.org/abs/2507.21428
21. Lumer, E., Gulati, A., Subbiah, V.K., Basavaraju, P.H., Burke, J.A.: Scalemcp: LLM 智能体的动态和自动同步模型上下文协议工具 (2025), https://arxiv.org/abs/2505.06416
22. Lumer, E., Subbiah, V.K., Burke, J.A., Basavaraju, P.H., Huber, A.: Toolshed: 使用高级 RAG-工具融合和工具知识库扩展工具装备智能体 (2024), https://arxiv.org/abs/2410.14594
23. Ma, X., Gong, Y., He, P., Zhao, H., Duan, N.: 检索增强大语言模型的查询重写 (2023), arXiv preprint arXiv:2305.14283
24. Mo, G., Zhong, W., Chen, J., Chen, X., Lu, Y., Lin, H., He, B., Han, X., Sun, L.: Livemcpbench: 智能体能航行在 MCP 工具的海洋中吗？(2025), https://arxiv.org/abs/2508.01780
25. Mo, G., Zhong, W., Chen, J., Chen, X., Lu, Y., Lin, H., He, B., Han, X., Sun, L.: Livemcpbench: 智能体能航行在 MCP 工具的海洋中吗？https://github.com/icip-cas/LiveMCPBench/blob/main/annotated_data/all_annotations.json (2025)
26. OpenAI: 向量嵌入文档。https://platform.openai.com/docs/guides/embeddings/embedding-models (2025)
27. Pan, S., Luo, L., Wang, Y., Chen, C., Wang, J., Wu, X.: 统一大语言模型和知识图谱：路线图。IEEE Transactions on Knowledge and Data Engineering 36(7), 3580–3599 (2024年7月)。https://doi.org/10.1109/tkde.2024.3352100, http://dx.doi.org/10.1109/TKDE.2024.3352100
28. Peng, B., Zhu, Y., Liu, Y., Bo, X., Shi, H., Hong, C., Zhang, Y., Tang, S.: 图检索增强生成：综述 (2024), arXiv preprint arXiv:2408.08921
29. Qin, Y., Liang, S., Ye, Y., Zhu, K., Yan, L., Lu, Y., Lin, Y., Cong, X., Tang, X., Qian, B., Zhao, S., Hong, L., Tian, R., Xie, R., Zhou, J., Gerstein, M., Li, D., Liu, Z., Sun, M.: Toolllm: 帮助大语言模型掌握 16000+ 真实世界 API (2023), arXiv preprint arXiv:2307.16789
30. Robertson, S., Zaragoza, H.: 概率相关性框架：BM25 及超越 (2009)。https://doi.org/10.1561/1500000019, http://dx.doi.org/10.1561/1500000019
31. Robertson, S., Zaragoza, H.: 概率相关性框架：BM25 及超越。信息检索基础与趋势 3(4), 333–389 (2009)。https://doi.org/10.1561/1500000019, http://dx.doi.org/10.1561/1500000019
32. Sarmah, B., Hall, B., Rao, R., Patel, S., Pasquali, S., Mehta, D.: Hybridrag: 整合知识图谱和向量检索增强生成以实现高效信息提取 (2024), arXiv preprint arXiv:2408.04948
33. Sun, J., Xu, C., Tang, L., Wang, S., Lin, C., Gong, Y., Ni, L.M., Shum, H.Y., Guo, J.: Think-on-graph: 大语言模型在知识图谱上的深度和负责任推理 (2024), arXiv preprint arXiv:2307.07697
34. Trivedi, H., Balasubramanian, N., Khot, T., Sabharwal, A.: 知识密集型多步问题的检索与思维链推理交错 (2023), arXiv preprint arXiv:2212.10509
35. Wu, M., Zhu, T., Han, H., Tan, C., Zhang, X., Chen, W.: Seal-tools: 用于智能体调优和详细基准的自指导工具学习数据集 (2024), arXiv preprint arXiv:2405.08355
36. Yao, S., Zhao, J., Yu, D., Du, N., Shafran, I., Narasimhan, K., Cao, Y.: ReAct: 在语言模型中协同推理和行动 (2023), arXiv preprint arXiv:2210.03629
37. Yuan, L., Chen, Y., Wang, X., Fung, Y.R., Peng, H., Ji, H.: Craft: 通过创建和从专用工具集中检索来定制 LLM (2024), https://arxiv.org/abs/2309.17428
38. Yuan, S., Song, K., Chen, J., Tan, X., Shen, Y., Kan, R., Li, D., Yang, D.: EASY-TOOL: 用简洁工具指令增强基于 LLM 的智能体 (2024), arXiv preprint arXiv:2401.06201
39. Zheng, Y., Li, P., Liu, W., Liu, Y., Luan, J., Wang, B.: Toolrerank: 工具检索的自适应和层次感知重排序 (2024), https://arxiv.org/abs/2403.06551
40. Zhong, L., Du, Z., Zhang, X., Hu, H., Tang, J.: Complexfuncbench: 在长上下文场景下探索多步和约束函数调用 (2025), arXiv preprint arXiv:2501.10132

---

**图表说明**：

**图 1**：仅智能体检索（左）与提出的工具到智能体检索（右）的比较，后者将工具和智能体嵌入共享向量空间以支持联合检索和遍历。