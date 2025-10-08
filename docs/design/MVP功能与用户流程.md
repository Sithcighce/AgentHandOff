2. MVP 功能与用户流程
版本: v5.0.0 (Final)
状态: 最终设计

2.1 核心功能清单 (MVP 范围)
1. 项目初始化 (init)
功能描述: 提供一个命令行工具 agent-handoff init，它会在项目中创建一套推荐的 (非强制) docs/ 目录结构和 agentreadme.md 模板。

推荐目录结构:

docs/01_Goals_and_Status/: 存放整体目标、开发现状、开发规范。

docs/02_Architecture_and_Usage/: 存放架构设计、API 或组件的使用方式。

docs/03_History_and_Lessons/: 存放开发历史、决策记录和经验教训。

docs/04_User_Facing/: 存放面向最终用户的 README 和使用方法。

2. 标准 MCP 服务器 (serve)
功能描述: 一个通过标准 MCP 协议（基于 stdio）将项目知识库和工作流作为工具暴露给 Agent 的子进程。

核心特性:

本地优先: 所有数据和计算都在本地进行。

无网络端口: 每个项目窗口启动独立的服务器进程，天然隔离。

3. 强制工作流 (Strict Workflow)
功能描述: Agent 必须遵循 start_work -> plan_setup -> proceed -> end_job 的结构化流程。任何试图绕过流程的工具调用都将被服务器拒绝。

实现方式:

服务器在内存中为每个任务维护一个严格的状态机。

只有当任务处于正确的状态时，相应的工具才能被成功调用。

4. 受控的知识库操作
功能描述: MCP 服务器提供一套完备的原子文件操作工具，专门用于对 docs/ 目录进行增删改查。

Git 集成: 无内置 Git 功能。docs/ 目录作为项目的一部分，由开发者像对待其他代码文件一样，手动通过 Git进行版本控制和提交。

5. 智能知识库维护建议
功能描述: 服务器在执行文件操作后，会基于预设规则对知识库的“健康度”进行检查，并通过工具的返回信息向 Agent 提供主动的优化建议。

2.2 典型用户流程 (修正后)
场景 1: 为新项目启用 Agent-Handoff
开发者 在项目根目录运行 pip install agent-handoff && agent-handoff init，生成了推荐的 docs/ 目录。

开发者 在 IDE (如 VS Code) 的 settings.json 中配置 Agent-Handoff MCP 服务器的启动命令。

IDE 启动时，自动根据配置运行 MCP 服务器子进程。

开发者 在 Copilot Chat 中输入：“开始开发用户注册功能”。

Agent (Copilot) 判断需要上下文，于是调用了 start_work 工具，开启了被严格监管的任务。