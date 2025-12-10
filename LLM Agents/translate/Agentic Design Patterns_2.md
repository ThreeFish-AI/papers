# 第1章：提示链（续）

### 上下文工程和提示工程

上下文工程（见图1）是在令牌生成之前设计、构建和向AI模型交付完整信息环境的系统性学科。该方法断言，模型输出的质量较少依赖于模型架构本身，而更多地依赖于所提供上下文的丰富性。

![img_30_0_20251210_191647.png](images/Agentic%20Design%20Patterns/img_30_0_20251210_191647.png)

图1：上下文工程是为AI构建丰富、全面的信息环境的学科，因为这个上下文的质量是实现高级智能体性能的主要因素。

它代表了从传统提示工程的重大演进，后者主要专注于优化用户即时查询的措辞。上下文工程将这个范围扩展到包括几个信息层，如系统提示，这是一组定义AI操作参数的基础指令——例如，"你是一名技术作家；你的语调必须正式和精确。"

上下文通过外部数据进一步丰富。这包括检索文档，AI主动从知识库中获取信息以通知其响应，例如为项目提取技术规格。它还包含工具输出，这些是AI使用外部API获取实时数据的结果，如查询日历以确定用户的可用性。这种明确的数据与关键的隐性数据相结合，如用户身份、交互历史和环境状态。

核心原则是，即使是高级模型，在提供有限或构建不良的操作环境视图时也会表现不佳。因此，这种实践将任务从仅仅回答问题重新定义为为智能体构建全面的操作图。例如，一个经过上下文工程的智能体不会仅仅响应查询，而是首先整合用户的日历可用性（工具输出）、与邮件收件人的专业关系（隐性数据）以及先前会议的笔记（检索文档）。这使得模型能够生成高度相关、个性化和实用有用的输出。"工程"组件涉及创建健壮的管道以在运行时获取和转换这些数据，并建立反馈循环以持续改进上下文质量。

为了实施这一点，可以使用专门的调优系统来大规模自动化改进过程。例如，谷歌Vertex AI提示优化器等工具可以通过系统地评估针对一组样本输入和预定义评估指标的响应来增强模型性能。这种方法对于适应不同模型的提示和系统指令是有效的，无需大量手动重写。通过向优化器提供样本提示、系统指令和模板，它可以以编程方式优化上下文输入，为实现复杂的上下文工程所需的反馈循环提供了结构化方法。

这种结构化方法是将基本AI工具与更复杂的、上下文感知的系统区分开来的方法。它将上下文本身视为主要组件，对智能体知道什么、何时知道以及如何使用这些信息给予关键重要性。该实践确保模型对用户的意图、历史和当前环境有全面的了解。最终，上下文工程是将无状态聊天机器人推进到高度能力强、情境感知系统的关键方法。

### 一览表

**内容**：当在单个提示中处理时，复杂任务经常让LLMs不堪重负，导致显著的性能问题。模型的认知负荷增加了忽视指令、丢失上下文和生成错误信息等错误的可能性。单体提示难以有效管理多个约束和顺序推理步骤。这导致不可靠和不准确的输出，因为LLM未能处理多方面请求的所有方面。

**原因**：提示链通过将复杂问题分解为一系列更小的、相互关联的子任务提供标准化解决方案。链中的每个步骤使用专注的提示来执行特定操作，显著提高了可靠性和控制性。一个提示的输出作为下一个提示的输入传递，创建逻辑工作流，逐步朝向最终解决方案前进。这种模块化的、分而治之的策略使过程更易管理、更容易调试，并允许在步骤之间集成外部工具或结构化数据格式。

这种模式是开发复杂的、多步骤智能体系统的基础，这些系统能够规划、推理和执行复杂的工作流。

**经验法则**：当任务过于复杂无法在单个提示中处理、涉及多个不同的处理阶段、需要在步骤之间与外部工具交互，或构建需要执行多步推理和维护状态的智能体系统时，使用此模式。

### 视觉摘要

![img_33_0_20251210_191647.png](images/Agentic%20Design%20Patterns/img_33_0_20251210_191647.png)

图2：提示链模式：智能体从用户那里接收一系列提示，每个智能体的输出作为链中下一个的输入。

### 关键要点

以下是一些关键要点：

● 提示链将复杂任务分解为一系列更小、专注的步骤。这有时被称为管道模式。
● 链中的每个步骤涉及LLM调用或处理逻辑，使用前一步的输出作为输入。
● 此模式提高了与语言模型复杂交互的可靠性和可管理性。
● LangChain/LangGraph和Google ADK等框架提供了强大的工具来定义、管理和执行这些多步骤序列。

### 结论

通过将复杂问题分解为一系列更简单、更易管理的子任务，提示链为引导大型语言模型提供了健壮的框架。这种"分而治之"策略通过一次专注于模型一个特定操作，显著增强了输出的可靠性和控制性。作为一种基础模式，它使能够开发复杂的AI智能体，这些智能体能够执行多步推理、工具集成和状态管理。最终，掌握提示链对于构建健壮的、上下文感知的系统至关重要，这些系统能够执行远远超出单个提示能力的复杂工作流。

### 参考文献

1. LangChain LCEL文档：https://python.langchain.com/v0.2/docs/core_modules/expression_language/
2. LangGraph文档：https://langchain-ai.github.io/langgraph/
3. 提示工程指南 - 链接提示：https://www.promptingguide.ai/techniques/chaining
4. OpenAI API文档（一般提示概念）：https://platform.openai.com/docs/guides/gpt/prompting
5. Crew AI文档（任务和流程）：https://docs.crewai.com/
6. 谷歌AI开发者（提示指南）：https://cloud.google.com/discover/what-is-prompt-engineering?hl=en
7. Vertex提示优化器https://cloud.google.com/vertex-ai/generative-ai/docs/learn/prompts/prompt-optimizer

---

## 第2章：路由

### 路由模式概述

虽然通过提示链进行顺序处理是执行确定性、线性语言模型工作流的基础技术，但它在需要自适应响应的场景中的适用性是有限的。现实世界的智能体系统通常必须基于偶然因素（如环境状态、用户输入或先前操作的结果）在多个潜在行动之间进行仲裁。

这种动态决策能力，它控制着流向不同专门功能、工具或子过程的流程，是通过称为路由的机制实现的。

路由将条件逻辑引入智能体的操作框架中，使得能够从固定执行路径转变为模型，在该模型中，智能体动态评估特定标准以从一组可能的后续行动中选择。这允许更灵活和上下文感知的系统行为。

例如，一个设计用于客户咨询的智能体，当配备路由功能时，可以首先分类传入查询以确定用户的意图。基于此分类，然后它可以将查询导向专门智能体进行直接问答、数据库检索工具获取账户信息，或针对复杂问题的升级程序，而不是默认单一、预定的响应路径。

因此，使用路由的更复杂的智能体可以：
1. 分析用户的查询。
2. 基于其意图路由查询：
   - 如果意图是"检查订单状态"，路由到与订单数据库交互的子智能体或工具链。
   - 如果意图是"产品信息"，路由到搜索产品目录的子智能体或链。
   - 如果意图是"技术支持"，路由到访问故障排除指南或升级到人的不同链。
   - 如果意图不明确，路由到澄清子智能体或提示链。

路由模式的核心组件是执行评估并指导流程的机制。这个机制可以通过几种方式实现：

● **基于LLM的路由**：语言模型本身可以被提示来分析输入并输出特定的标识符或指令，指示下一步或目的地。例如，提示可能要求LLM"分析以下用户查询并仅输出类别：'订单状态'、'产品信息'、'技术支持'或'其他'。"然后智能体系统读取此输出并相应地指导工作流。

● **基于嵌入的路由**：输入查询可以转换为向量嵌入（见RAG，第14章）。然后这个嵌入与代表不同路由或能力的嵌入进行比较。查询被路由到其嵌入最相似的路由。这对于语义路由很有用，其中决策基于输入的含义而不仅仅是关键词。

● **基于规则的路由**：这涉及使用预定义的规则或逻辑（例如，if-else语句，switch cases），基于从输入中提取的关键词、模式或结构化数据。这可以比基于LLM的路由更快和更确定，但对于处理细致或新颖的输入灵活性较低。

● **基于机器学习模型的路由**：它采用判别模型，如分类器，该模型已在小的标记数据语料库上进行专门训练以执行路由任务。虽然它与基于嵌入的方法共享概念相似性，但其关键特征是监督微调过程，该过程调整模型的参数以创建专门的路由功能。这种技术与基于LLM的路由不同，因为决策组件不是在推理时执行提示的生成模型。相反，路由逻辑编码在微调模型的学习权重中。虽然LLMs可能在预处理步骤中使用以生成用于增强训练集的合成数据，但它们不参与实时的路由决策本身。

路由机制可以在智能体操作周期的多个节点实施。它们可以在开始时应用以分类主要任务，在处理链中的中间点以确定后续行动，或在子例程期间从给定集合中选择最合适的工具。

LangChain、LangGraph和谷歌智能体开发工具包（Google ADK）等计算框架提供了明确定义和管理这种条件逻辑的构造。LangGraph以其基于状态的图架构，特别适用于复杂路由场景，其中决策取决于整个系统的累积状态。同样，谷歌的ADK提供了构建智能体能力和交互模型的基础组件，这些组件作为实施路由逻辑的基础。在这些框架提供的执行环境中，开发人员定义可能的操作路径以及在计算图中指导节点之间转换的函数或基于模型的评估。

路由的实施使得系统能够超越确定性顺序处理。它促进了更具自适应性的执行流的开发，这些流能够动态和适当地响应更广泛的输入和状态变化。

### 实际应用和用例

路由模式是设计自适应智能体系统的关键控制机制，使它们能够根据变量输入和内部状态动态改变其执行路径。它的实用性通过提供必要的条件逻辑层跨越多个领域。

在人机交互中，如虚拟助手或AI驱动的导师，路由用于解释用户意图。对自然语言查询的初步分析确定最合适的后续行动，无论是调用特定的信息检索工具、升级到人工操作员，还是基于用户表现选择课程中的下一个模块。这允许系统超越线性对话流并上下文地响应。

在自动化数据和文档处理管道中，路由充当分类和分发功能。传入数据，如电子邮件、支持票据或API负载，基于内容、元数据或格式进行分析。然后系统将每个项目导向相应的工作流，如销售潜在客户摄取过程、JSON或CSV格式的特定数据转换功能，或紧急问题升级路径。

在涉及多个专门工具或智能体的复杂系统中，路由充当高级调度器。由用于搜索、总结和分析信息的不同智能体组成的研究系统将使用路由器基于当前目标将任务分配给最合适的智能体。同样，AI编码助手使用路由来识别编程语言和用户的意图——调试、解释或翻译——然后将代码片段传递给正确的专门工具。

最终，路由提供了逻辑仲裁能力，这对于创建功能多样和上下文感知的系统是必不可少的。它将智能体从预定义序列的静态执行器转变为能够在变化的条件下决定完成任务的最有效方法的动态系统。

### 动手代码示例（LangChain）

在代码中实施路由涉及定义可能的路径和决定采用哪条路径的逻辑。LangChain和LangGraph等框架为此提供了特定的组件和结构。LangGraph的基于状态的图结构对于可视化和实施路由逻辑特别直观。

这段代码演示了使用LangChain和谷歌生成AI的简单智能体类系统。它设置了一个"协调器"，根据请求的意图（预订、信息或不明确）将用户请求路由到不同的模拟"子智能体"处理程序。系统使用语言模型对请求进行分类，然后将其委托给适当的处理程序函数，模拟了多智能体架构中常见的基本委托模式。

首先，确保安装了必要的库：

```bash
pip install langchain langgraph google-cloud-aiplatform langchain-google-genai google-adk deprecated pydantic
```

你还需要为你选择的语言模型（例如，OpenAI、谷歌Gemini、Anthropic）设置你的API密钥环境。

```python
# 版权所有 (c) 2025 Marco Fago
# https://www.linkedin.com/in/marco-fago/
#
# 此代码根据MIT许可证授权。
# 有关完整许可证文本，请参见存储库中的LICENSE文件。

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableBranch

# --- 配置 ---

# 确保设置了你的API密钥环境变量（例如，GOOGLE_API_KEY）
try:
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
    print(f"语言模型已初始化: {llm.model}")
except Exception as e:
    print(f"语言模型初始化错误: {e}")
    llm = None

# --- 定义模拟子智能体处理程序（等同于ADK sub_agents） ---

def booking_handler(request: str) -> str:
    """模拟预订智能体处理请求。"""
    print("\n--- 委托给预订处理程序 ---")
    return f"预订处理程序已处理请求: '{request}'。结果: 模拟预订操作。"

def info_handler(request: str) -> str:
    """模拟信息智能体处理请求。"""
    print("\n--- 委托给信息处理程序 ---")
    return f"信息处理程序已处理请求: '{request}'。结果: 模拟信息检索。"

def unclear_handler(request: str) -> str:
    """处理无法委托的请求。"""
    print("\n--- 处理不明确的请求 ---")
    return f"协调器无法委托请求: '{request}'。请澄清。"

# --- 定义协调器路由链（等同于ADK协调器的指令） ---

# 此链决定委托给哪个处理程序。
coordinator_router_prompt = ChatPromptTemplate.from_messages([
    ("system", """分析用户的请求并确定应该由哪个专门处理程序处理它。
- 如果请求与预订航班或酒店相关，输出 'booker'。
- 对于所有其他一般信息问题，输出 'info'。
- 如果请求不明确或不符合任一类别，输出 'unclear'。
仅输出一个词：'booker'、'info' 或 'unclear'。"""),
    ("user", "{request}")
])

if llm:
    coordinator_router_chain = coordinator_router_prompt | llm | StrOutputParser()

# --- 定义委托逻辑（等同于ADK基于sub_agents的自动流程） ---

# 使用RunnableBranch基于路由链的输出进行路由。

# 为RunnableBranch定义分支
branches = {
    "booker": RunnablePassthrough.assign(output=lambda x: booking_handler(x['request']['request'])),
    "info": RunnablePassthrough.assign(output=lambda x: info_handler(x['request']['request'])),
    "unclear": RunnablePassthrough.assign(output=lambda x: unclear_handler(x['request']['request'])),
}

# 创建RunnableBranch。它接收路由链的输出
# 并将原始输入（'request'）路由到相应的处理程序。
delegation_branch = RunnableBranch(
    (lambda x: x['decision'].strip() == 'booker', branches["booker"]),  # 添加.strip()
    (lambda x: x['decision'].strip() == 'info', branches["info"]),       # 添加.strip()
    branches["unclear"]  # 'unclear'或任何其他输出的默认分支
)

# 将路由链和委托分支组合成单个可运行对象
# 路由链的输出（'decision'）与原始输入（'request'）一起传递
# 给委托分支。
coordinator_agent = {
    "decision": coordinator_router_chain,
    "request": RunnablePassthrough()
} | delegation_branch | (lambda x: x['output'])  # 提取最终输出

# --- 示例用法 ---

def main():
    if not llm:
        print("\n由于LLM初始化失败跳过执行。")
        return
        
    print("--- 运行预订请求 ---")
    request_a = "为我预订去伦敦的航班。"
    result_a = coordinator_agent.invoke({"request": request_a})
    print(f"最终结果A: {result_a}")
    
    print("\n--- 运行信息请求 ---")
    request_b = "意大利的首都是什么？"
    result_b = coordinator_agent.invoke({"request": request_b})
    print(f"最终结果B: {result_b}")
    
    print("\n--- 运行不明确的请求 ---")
    request_c = "告诉我关于量子物理学的知识。"
    result_c = coordinator_agent.invoke({"request": request_c})
    print(f"最终结果C: {result_c}")

if __name__ == "__main__":
    main()
```

如前所述，此Python代码使用LangChain库和谷歌的生成AI模型（特别是gemini-2.5-flash）构建了一个简单的智能体类系统。详细来说，它定义了三个模拟的子智能体处理程序：booking_handler、info_handler和unclear_handler，每个都设计用于处理特定类型的请求。

核心组件是coordinator_router_chain，它利用ChatPromptTemplate指示语言模型将传入的用户请求分类为三个类别之一：'booker'、'info'或'unclear'。然后这个路由链的输出被RunnableBranch使用，将原始请求委托给相应的处理程序函数。RunnableBranch检查来自语言模型的决策，并将请求数据导向booking_handler、info_handler或unclear_handler。

coordinator_agent结合了这些组件，首先路由请求以进行决策，然后将请求传递给选定的处理程序。最终输出从处理程序的响应中提取。main函数演示了系统如何处理三个示例请求，展示了不同的输入如何被模拟智能体路由和处理。包含语言模型初始化的错误处理以确保健壮性。代码结构模拟了一个基本的多智能体框架，其中中央协调器基于意图将任务委托给专门的智能体。

### 动手代码示例（Google ADK）

智能体开发工具包（ADK）是一个用于工程智能体系统的框架，提供了定义智能体能力和行为的结构化环境。与基于显式计算图的架构相比，ADK范式中的路由通常通过定义代表智能体功能的离散"工具"集来实现。响应于用户查询选择合适工具由框架的内部逻辑管理，该逻辑利用底层模型将用户意图与正确的功能处理程序匹配。

此Python代码演示了使用谷歌ADK库的智能体开发工具包（ADK）应用程序示例。它设置了一个"协调器"智能体，根据定义的指令将用户请求路由到专门的子智能体（"Booker"用于预订，"Info"用于一般信息）。然后子智能体使用特定工具模拟处理请求，展示了智能体系统内的基本委托模式。

```python
# 版权所有 (c) 2025 Marco Fago
#
# 此代码根据MIT许可证授权。
# 有关完整许可证文本，请参见存储库中的LICENSE文件。

import uuid
from typing import Dict, Any, Optional
from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner
from google.adk.tools import FunctionTool
from google.genai import types
from google.adk.events import Event

# --- 定义工具函数 ---

# 这些函数模拟专门智能体的操作。

def booking_handler(request: str) -> str:
    """
    处理航班和酒店的预订请求。
    参数:
        request: 用户的预订请求。
    返回:
        确认已处理预订的消息。
    """
    print("-------------------------- 预订处理程序被调用 ---------------------------")
    return f"已模拟对 '{request}' 的预订操作。"

def info_handler(request: str) -> str:
    """
    处理一般信息请求。
    参数:
        request: 用户的问题。
    返回:
        表示已处理信息请求的消息。
    """
    print("-------------------------- 信息处理程序被调用 ---------------------------")
    return f"已处理对 '{request}' 的信息请求。结果：模拟信息检索。"

def unclear_handler(request: str) -> str:
    """处理无法委托的请求。"""
    return f"协调器无法委托请求: '{request}'。请澄清。"

# --- 从函数创建工具 ---

booking_tool = FunctionTool(booking_handler)
info_tool = FunctionTool(info_handler)

# 定义配备各自工具的专门子智能体
booking_agent = Agent(
    name="Booker",
    model="gemini-2.0-flash",
    description="通过调用预订工具处理所有航班和酒店预订请求的专门智能体。",
    tools=[booking_tool]
)

info_agent = Agent(
    name="Info",
    model="gemini-2.0-flash",
    description="通过调用信息工具提供一般信息并回答用户问题的专门智能体。",
    tools=[info_tool]
)

# 使用显式委托指令定义父智能体
coordinator = Agent(
    name="Coordinator",
    model="gemini-2.0-flash",
    instruction=(
        "你是主协调器。你的唯一任务是分析传入的用户请求 "
        "并将它们委托给适当的专门智能体。不要尝试直接回答用户。\n"
        "- 对于与预订航班或酒店相关的任何请求，委托给'Booker'智能体。\n"
        "- 对于所有其他一般信息问题，委托给'Info'智能体。"
    ),
    description="将用户请求路由到正确专门智能体的协调器。",
    
    # sub_agents的存在启用了LLM驱动的委托（自动流程）默认。
    sub_agents=[booking_agent, info_agent]
)

# --- 执行逻辑 ---

async def run_coordinator(runner: InMemoryRunner, request: str):
    """使用给定请求运行协调器智能体并委托。"""
    print(f"\n--- 使用请求运行协调器: '{request}' ---")
    final_result = ""
    try:
        user_id = "user_123"
        session_id = str(uuid.uuid4())
        await runner.session_service.create_session(
            app_name=runner.app_name,
            user_id=user_id,
            session_id=session_id
        )
        
        for event in runner.run(
            user_id=user_id,
            session_id=session_id,
            new_message=types.Content(
                role='user',
                parts=[types.Part(text=request)]
            ),
        ):
            if event.is_final_response() and event.content:
                # 尝试直接从event.content获取文本
                # 以避免迭代部分
                if hasattr(event.content, 'text') and event.content.text:
                    final_result = event.content.text
                elif event.content.parts:
                    # 回退：迭代部分并提取文本（可能触发警告）
                    text_parts = [part.text for part in event.content.parts if part.text]
                    final_result = "".join(text_parts)
                
                # 假设循环应该在最终响应后中断
                break
                
        print(f"协调器最终响应: {final_result}")
        return final_result
    except Exception as e:
        print(f"处理你的请求时发生错误: {e}")
        return f"处理你的请求时发生错误: {e}"

async def main():
    """运行ADK示例的主函数。"""
    print("--- 谷歌ADK路由示例（ADK自动流程风格） ---")
    print("注意：这需要安装和验证谷歌ADK。")
    runner = InMemoryRunner(coordinator)
    
    # 示例用法
    result_a = await run_coordinator(runner, "为我在巴黎预订酒店。")
    print(f"最终输出A: {result_a}")
    
    result_b = await run_coordinator(runner, "世界上最高的山是什么？")
    print(f"最终输出B: {result_b}")
    
    result_c = await run_coordinator(runner, "告诉我一个随机的事实。")  # 应该去Info
    print(f"最终输出C: {result_c}")
    
    result_d = await run_coordinator(runner, "查找下个月去东京的航班。")  # 应该去Booker
    print(f"最终输出D: {result_d}")

if __name__ == "__main__":
    import nest_asyncio
    nest_asyncio.apply()
    await main()
```

此脚本由一个主协调器智能体和两个专门的子智能体组成：Booker和Info。每个专门智能体都配备了一个FunctionTool，它包装了一个模拟操作的Python函数。booking_handler函数模拟处理航班和酒店预订，而info_handler函数模拟检索一般信息。虽然当前的协调器逻辑在main run_coordinator函数中没有明确使用unclear_handler进行委托失败，但它作为协调器无法委托的请求的回退包含在内。

协调器智能体的主要角色，如其指令中所定义的，是分析传入的用户消息并将它们委托给Booker或Info智能体。由于协调器定义了sub_agents，这种委托由ADK的自动流程机制自动处理。run_coordinator函数设置一个InMemoryRunner，创建用户和会话ID，然后使用runner通过协调器智能体处理用户的请求。runner.run方法处理请求并产生事件，代码从event.content中提取最终响应文本。

main函数通过使用不同的请求运行协调器来演示系统的用法，展示了它如何将预订请求委托给Booker，将信息请求委托给Info智能体。

### 一览表

**内容**：智能体系统通常必须响应各种无法由单一、线性过程处理的输入和情况。简单的顺序工作流缺乏基于上下文做出决策的能力。没有机制为特定任务选择正确的工具或子过程，系统保持刚性和非适应性。这种限制使得构建能够管理现实世界用户请求的复杂性和可变性的复杂应用程序变得困难。

**原因**：路由模式通过将条件逻辑引入智能体的操作框架提供标准化解决方案。它使系统能够首先分析传入查询以确定其意图或性质。基于此分析，智能体动态地将控制流引导到最合适的专门工具、函数或子智能体。这个决策可以由各种方法驱动，包括提示LLMs、应用预定义规则或使用基于嵌入的语义相似性。

最终，路由将静态、预定的执行路径转变为能够选择最佳可能的行动的灵活和上下文感知的工作流。

**经验法则**：当智能体必须基于用户输入或当前状态在多个不同的工作流、工具或子智能体之间做出决定时，使用路由模式。对于需要分类或分类传入请求以处理不同类型任务的应用程序（如区分销售咨询、技术支持和账户管理问题的客户支持机器人）来说，它是必不可少的。

### 视觉摘要：

![img_47_0_20251210_191647.png](images/Agentic%20Design%20Patterns/img_47_0_20251210_191647.png)

图1：路由器模式，使用LLM作为路由器

### 关键要点

● 路由使智能体能够基于条件做出关于工作流中下一步的动态决策。
● 它允许智能体处理多样化输入并调整其行为，超越线性执行。
● 路由逻辑可以使用LLMs、基于规则的系统或嵌入相似性来实施。
● LangGraph和谷歌ADK等框架提供了在智能体工作流内定义和管理路由的结构化方法，尽管采用不同的架构方法。

### 结论

路由模式是构建真正动态和响应式智能体系统的关键步骤。通过实施路由，我们超越了简单的线性执行流，并使我们的智能体能够就如何处理信息、响应用户输入以及利用可用工具或子智能体做出智能决策。

我们已经看到路由如何应用于各个领域，从客户服务聊天机器人到复杂的数据处理管道。分析输入并有条件地指导工作流的能力是创建能够处理现实世界任务固有可变性的智能体的基础。

使用LangChain和谷歌ADK的代码示例展示了两种不同但有效的路由实施方法。LangGraph的基于图的结构提供了定义状态和转换的视觉化和显式方式，使其成为具有复杂路由逻辑的复杂、多步骤工作流的理想选择。另一方面，谷歌ADK通常专注于定义不同的能力（工具），并依赖框架将用户请求路由到适当的工具处理程序，这对于具有明确定义的离散操作集的智能体来说可能更简单。

掌握路由模式对于构建能够智能地导航不同场景并基于上下文提供定制响应或行动的智能体至关重要。它是创建多功能和健壮的智能体应用程序的关键组成部分。

### 参考文献

1. LangGraph文档：https://www.langchain.com/
2. 谷歌智能体开发工具包文档：https://google.github.io/adk-docs/

---

## 第3章：并行化

### 并行化模式概述

在之前的章节中，我们探讨了用于顺序工作流的提示链和用于动态决策以及在不同路径之间转换的路由。虽然这些模式是必不可少的，但许多复杂的智能体任务涉及可以同时而不是一个接一个地执行的多个子任务。这就是并行化模式变得至关重要的地方。

并行化涉及并发执行多个组件，如LLM调用、工具使用，甚至整个子智能体（见图1）。而不是等待一个步骤完成后再开始下一个，并行执行允许独立任务同时运行，显著减少了可以分解为独立部分的任务的总体执行时间。

考虑一个设计用于研究主题并总结其发现的智能体。顺序方法可能：
1. 搜索来源A。
2. 总结来源A。
3. 搜索来源B。
4. 总结来源B。
5. 根据总结A和B综合最终答案。

并行方法可以：
1. 同时搜索来源A和来源B。
2. 两个搜索完成后，同时总结来源A和来源B。
3. 根据总结A和B综合最终答案（此步骤通常是顺序的，等待并行步骤完成）。

核心思想是识别工作流中不依赖于其他部分输出的部分并并行执行它们。这在处理具有延迟的外部服务（如API或数据库）时特别有效，因为你可以并发发出多个请求。

实施并行化通常需要支持异步执行或多线程/多处理的框架。现代智能体框架在设计时就考虑了异步操作，允许你轻松定义可以并行运行的步骤。

![img_50_0_20251210_191647.png](images/Agentic%20Design%20Patterns/img_50_0_20251210_191647.png)

图1. 与子智能体并行化的示例

LangChain、LangGraph和谷歌ADK等框架提供了并行执行的机制。在LangChain表达式语言（LCEL）中，你可以通过使用|（用于顺序）等运算符组合可运行对象，以及构建具有并发执行分支的链或图来实现并行执行。

LangGraph凭借其图结构，允许你定义可以从单个状态转换执行的多个节点，有效地在工作流中启用并行分支。谷歌ADK提供了强大、原生的机制来促进和管理智能体的并行执行，显著增强了复杂、多智能体系统的效率和可扩展性。ADK框架内的这种固有能力使开发人员能够设计和实现多个智能体可以并发而不是顺序操作的解决方案。

并行化模式对于提高智能体系统的效率和响应性至关重要，特别是在涉及多个独立查找、计算或与外部服务交互的任务中。它是优化复杂智能体工作流性能的关键技术。

### 实际应用和用例

并行化是跨各种应用程序优化智能体性能的强大模式：

1. **信息收集和研究**：
   同时从多个源收集信息是经典用例。
   - **用例**：研究公司的智能体。
   - **并行任务**：同时搜索新闻文章、提取股票数据、检查社交媒体提及和查询公司数据库。
   - **好处**：比顺序查找更快地收集全面视图。

2. **数据处理和分析**：
   并发应用不同的分析技术或处理不同的数据段。
   - **用例**：分析客户反馈的智能体。
   - **并行任务**：对一批反馈条目同时运行情感分析、提取关键词、分类反馈和识别紧急问题。
   - **好处**：快速提供多方面分析。

3. **多API或工具交互**：
   调用多个独立的API或工具以收集不同类型的信息或执行不同的操作。
   - **用例**：旅行规划智能体。
   - **并行任务**：同时检查航班价格、搜索酒店可用性、查找当地事件和寻找餐厅推荐。
   - **好处**：更快地呈现完整的旅行计划。

4. **多组件内容生成**：
   并行生成复杂内容的不同部分。
   - **用例**：创建营销电子邮件的智能体。
   - **并行任务**：同时生成主题行、起草电子邮件正文、查找相关图像和创建行动号召按钮文本。
   - **好处**：更高效地组装最终电子邮件。

5. **验证和验证**：
   并发执行多个独立的检查或验证。
   - **用例**：验证用户输入的智能体。
   - **并行任务**：同时检查电子邮件格式、验证电话号码、对照数据库验证地址和检查亵渎内容。
   - **好处**：提供关于输入有效性的更快反馈。

6. **多模态处理**：
   并发处理相同输入的不同模态（文本、图像、音频）。
   - **用例**：分析带有文本和图像的社交媒体帖子的智能体。
   - **并行任务**：同时分析文本的情感和关键词，以及分析图像的对象和场景描述。
   - **好处**：更快地整合来自不同模态的洞察。

7. **A/B测试或多选项生成**：
   并行生成响应或输出的多个变体以选择最佳的一个。
   - **用例**：生成不同创意文本选项的智能体。
   - **并行任务**：使用略有不同的提示或模型同时为一篇文章生成三个不同的标题。
   - **好处**：允许快速比较和选择最佳选项。

并行化是智能体设计中的基本优化技术，使开发人员能够通过利用独立任务的并发执行来构建更高性能和响应能力的应用程序。

### 动手代码示例（LangChain）

LangChain框架内的并行执行由LangChain表达式语言（LCEL）促进。主要方法涉及在字典或列表构造中构建多个可运行组件。当此集合作为输入传递给链中的后续组件时，LCEL运行时并发执行包含的可运行对象。

在LangGraph的上下文中，此原则应用于图的拓扑结构。通过构建图使得多个节点在缺乏直接顺序依赖性的情况下可以从单个公共节点启动来定义并行工作流。这些并行路径在它们的结果可以在图中后续汇聚点聚合之前独立执行。

以下实现演示了使用LangChain框架构建的并行处理工作流。此工作流设计为响应单个用户查询并发执行两个独立操作。这些并行过程被实例化为不同的链或函数，它们各自的输出随后被聚合成统一的结果。

此实现的先决条件包括安装必需的Python包，如langchain、langchain-community和模型提供程序库（如langchain-openai）。此外，必须在本地环境中配置所选语言模型的有效API密钥以进行身份验证。

```python
import os
import asyncio
from typing import Optional
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import Runnable, RunnableParallel, RunnablePassthrough

# --- 配置 ---

# 确保设置了你的API密钥环境变量（例如，OPENAI_API_KEY）
try:
    llm: Optional[ChatOpenAI] = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
except Exception as e:
    print(f"语言模型初始化错误: {e}")
    llm = None

# --- 定义独立链 ---

# 这三个链代表可以并行执行的不同任务。
summarize_chain: Runnable = (
    ChatPromptTemplate.from_messages([
        ("system", "简洁地总结以下主题:"),
        ("user", "{topic}")
    ])
    | llm
    | StrOutputParser()
)

questions_chain: Runnable = (
    ChatPromptTemplate.from_messages([
        ("system", "为以下主题生成三个有趣的问题:"),
        ("user", "{topic}")
    ])
    | llm
    | StrOutputParser()
)

terms_chain: Runnable = (
    ChatPromptTemplate.from_messages([
        ("system", "从以下主题中识别5-10个关键术语，用逗号分隔:"),
        ("user", "{topic}")
    ])
    | llm
    | StrOutputParser()
)

# --- 构建并行 + 综合链 ---

# 1. 定义要并行运行的任务块。这些的结果，
#    连同原始主题，将被馈送到下一步。
map_chain = RunnableParallel({
    "summary": summarize_chain,
    "questions": questions_chain,
    "key_terms": terms_chain,
    "topic": RunnablePassthrough(),  # 传递原始主题
})

# 2. 定义将结合并行结果的最终综合提示。
synthesis_prompt = ChatPromptTemplate.from_messages([
    ("system", """基于以下信息:
总结: {summary}
相关问题: {questions}
关键术语: {key_terms}
综合一个全面的答案。"""),
    ("user", "原始主题: {topic}")
])

# 3. 通过将并行结果直接管道传输
#    到综合提示，然后是LLM和输出解析器来构建完整链。
full_parallel_chain = map_chain | synthesis_prompt | llm | StrOutputParser()

# --- 运行链 ---

async def run_parallel_example(topic: str) -> None:
    """
    使用特定主题异步调用并行处理链并打印综合结果。
    参数:
        topic: 要由LangChain链处理的输入主题。
    """
    if not llm:
        print("LLM未初始化。无法运行示例。")
        return
        
    print(f"\n--- 主题的并行LangChain示例: '{topic}' ---")
    try:
        # `ainvoke`的输入是单个'topic'字符串，
        # 然后传递给`map_chain`中的每个可运行对象。
        response = await full_parallel_chain.ainvoke(topic)
        print("\n--- 最终响应 ---")
        print(response)
    except Exception as e:
        print(f"\n链执行期间发生错误: {e}")

if __name__ == "__main__":
    test_topic = "太空探索的历史"
    
    # 在Python 3.7+中，asyncio.run是运行异步函数的标准方式。
    asyncio.run(run_parallel_example(test_topic))
```

提供的Python代码实现了一个设计为通过利用并行执行来高效处理给定主题的LangChain应用程序。注意，asyncio提供并发性，而不是并行性。它通过使用事件循环在任务空闲时（例如，等待网络请求）智能地在任务之间切换来实现这一点。这产生了多个任务同时进行的效果，但代码本身仍然只由一个线程执行，受到Python的全局解释器锁（GIL）的限制。

代码通过导入langchain_openai和langchain_core中的基本模块开始，包括语言模型、提示、输出解析和可运行结构的组件。代码尝试初始化一个ChatOpenAI实例，特别是使用"gpt-4o-mini"模型，并指定温度来控制创造性。在语言模型初始化期间使用try-except块以确保健壮性。

然后定义了三个独立的LangChain"链"，每个都设计用于对输入主题执行不同的任务。第一个链用于简洁地总结主题，使用系统消息和包含主题占位符的用户消息。第二个链配置为生成与主题相关的三个有趣问题。第三个链设置为从输入主题中识别5到10个关键术语，要求它们用逗号分隔。

这些独立链中的每一个都包括为其特定任务定制的ChatPromptTemplate，后跟初始化的语言模型和StrOutputParser以将输出格式化为字符串。

然后构建一个RunnableParallel块来捆绑这三个链，允许它们同时执行。这个并行可运行对象还包括一个RunnablePassthrough，以确保原始输入主题可用于后续步骤。

为最终综合步骤定义了单独的ChatPromptTemplate，将总结、问题、关键术语和原始主题作为输入以生成全面的答案。

名为full_parallel_chain的端到端处理链通过将map_chain（并行块）排序到综合提示中，后跟语言模型和输出解析器来创建。提供了一个异步函数run_parallel_example来演示如何调用此full_parallel_chain。此函数接受主题作为输入并使用ainvoke来运行异步链。

最后，标准的Python if __name__ == "__main__":块显示如何使用asyncio.run执行带有样本主题的run_parallel_example，在本例中是"太空探索的历史"，以管理异步执行。

本质上，此代码设置了一个工作流，其中多个LLM调用（用于总结、问题和术语）针对给定主题同时发生，然后它们的结果由最终LLM调用组合。这展示了在智能体工作流中使用LangChain进行并行化的核心思想。

### 动手代码示例（Google ADK）

好的，现在让我们转向谷歌ADK框架内说明这些概念的具体示例。我们将研究如何应用ADK原语，如ParallelAgent和SequentialAgent，来构建利用并发执行以提高效率的智能体流。

```python
from google.adk.agents import LlmAgent, ParallelAgent, SequentialAgent
from google.adk.tools import google_search

GEMINI_MODEL="gemini-2.0-flash"

# --- 1. 定义研究子智能体（并行运行） ---

# 研究员1：可再生能源
researcher_agent_1 = LlmAgent(
    name="RenewableEnergyResearcher",
    model=GEMINI_MODEL,
    instruction="""你是一个专门研究能源的AI研究助手。研究'可再生能源'的最新进展。使用提供的谷歌搜索工具。简洁地总结你的关键发现（1-2句话）。仅输出总结。""",
    description="研究可再生能源。",
    tools=[google_search],
    
    # 在状态中存储结果供合并智能体使用
    output_key="renewable_energy_result"
)

# 研究员2：电动汽车
researcher_agent_2 = LlmAgent(
    name="EVResearcher",
    model=GEMINI_MODEL,
    instruction="""你是一个专门研究交通的AI研究助手。研究'电动汽车技术'的最新发展。使用提供的谷歌搜索工具。简洁地总结你的关键发现（1-2句话）。仅输出总结。""",
    description="研究电动汽车技术。",
    tools=[google_search],
    
    # 在状态中存储结果供合并智能体使用
    output_key="ev_technology_result"
)

# 研究员3：碳捕获
researcher_agent_3 = LlmAgent(
    name="CarbonCaptureResearcher",
    model=GEMINI_MODEL,
    instruction="""你是一个专门研究气候解决方案的AI研究助手。研究'碳捕获方法'的现状。使用提供的谷歌搜索工具。简洁地总结你的关键发现（1-2句话）。仅输出总结。""",
    description="研究碳捕获方法。",
    tools=[google_search],
    
    # 在状态中存储结果供合并智能体使用
    output_key="carbon_capture_result"
)

# --- 2. 创建ParallelAgent（并发运行研究员） ---

# 此智能体协调研究员的并发执行。
# 一旦所有研究员完成并将结果存储在状态中，它就完成。
parallel_research_agent = ParallelAgent(
    name="ParallelWebResearchAgent",
    sub_agents=[researcher_agent_1, researcher_agent_2, researcher_agent_3],
    description="并行运行多个研究智能体以收集信息。"
)

# --- 3. 定义合并智能体（在并行智能体之后运行） ---

# 此智能体获取并行智能体存储在会话状态中的结果
# 并将它们合成为单个、结构化的响应，并注明出处。
merger_agent = LlmAgent(
    name="SynthesisAgent",
    model=GEMINI_MODEL,  # 或者如果需要更强大的模型用于综合
    instruction="""你是一个负责将研究结果组合成结构化报告的AI助手。你的主要任务是综合以下研究摘要，
明确地将发现归因于其源领域。使用每个主题的标题来构建你的响应。
确保报告连贯并平滑地整合关键点。

**关键：你的整个响应必须完全基于下面'输入摘要'中提供的信息。不要添加任何外部知识或进行超出所提供文本的综合。使用以下格式：
## 可再生能源
[来自renewable_energy_result的信息]

## 电动汽车
[来自ev_technology_result的信息]

## 碳捕获
[来自carbon_capture_result的信息]""",
    description="综合并行研究结果。",
    
    # 注意：这个智能体不需要工具，它只处理来自状态的信息
)

# --- 4. 创建SequentialAgent来组织整个工作流 ---

# 首先运行并行研究，然后运行合并智能体。
full_research_workflow = SequentialAgent(
    name="FullResearchWorkflow",
    sub_agents=[parallel_research_agent, merger_agent],
    description="运行并行研究，然后综合结果。"
)
```

这个ADK示例展示了如何通过并行执行来提高研究效率。系统创建三个专门的研究员，每个专注于不同的领域（可再生能源、电动汽车、碳捕获），并同时运行它们以收集信息。一旦所有研究员完成他们的搜索，合并智能体将他们的发现整合成一个连贯的报告。

这种方法展示了并行化的核心优势：通过让独立的研究任务同时运行，系统可以显著快于顺序执行每个任务的方式收集全面的信息。

### 一览表

**内容**：顺序处理可能效率低下，特别是当每个步骤都涉及等待外部系统（如API调用）时。当不同任务不依赖于彼此时，一个接一个地执行它们会浪费宝贵的时间和资源。这种线性方法限制了系统的吞吐量，使其在处理大量独立操作时表现不佳。

**原因**：并行化模式通过同时执行多个独立的任务来解决这个低效率问题。而不是等待一个任务完成后再开始下一个，系统启动多个任务，让它们并发运行。这显著减少了完成一组独立任务所需的总时间，因为等待时间被重叠和最小化。该模式在涉及网络请求、数据库查询或其他I/O密集型操作的场景中特别有效。

**经验法则**：当你有多个独立的任务可以同时执行而不会相互干扰时使用并行化。这对于信息收集、数据处理、多API调用或任何涉及等待外部响应的任务特别有用。

### 关键要点

● 并行化通过并发执行独立任务来显著减少总执行时间。
● 它在处理I/O密集型操作（如API调用、数据库查询）时特别有效。
● 现代智能体框架（LangChain、LangGraph、谷歌ADK）提供了内置的并行执行支持。
● 识别可以并行运行的任务部分是有效实施此模式的关键。

### 结论

并行化模式是优化智能体系统性能的基本技术。通过识别和并发执行独立任务，我们可以显著减少总体执行时间并提高系统效率。

该模式特别有价值，当处理涉及多个外部交互、数据处理或信息收集任务时。正如我们所见，现代智能体框架如LangChain和谷歌ADK提供了强大的原语来使并行化更容易实施。

在构建响应式和高效智能体时，掌握并行化对于创建能够在合理时间内处理复杂、多方面任务的系统至关重要。