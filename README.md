# Agent-Handoff

> 项目级 AI 协作记忆与工作流系统

**一句话**├── .agent-handoff/
    ├── agentreadme.md             # Agent 交接文档
    ├── config.yaml                # 配置文件
    ├── mcp_server.py              # 独立MCP服务器（无需安装）
    └── history/                   # 会话历史AI Agent 像有经验的团队成员一样，理解项目上下文、遵循工作流程，而不是每次对话都从零开始。

## 核心问题

当前 AI 辅助开发的痛点：
- 🔴 **上下文耗尽**: 复杂项目超出 LLM 的 token 限制
- 🔴 **知识断层**: 切换对话 = 重新解释项目
- 🔴 **准则失控**: Agent 难以持续遵守开发规范
- 🔴 **成本失控**: 按次计费模型下，短任务成本高

## 解决方案

Agent-Handoff 提供：
1. **项目记忆系统** - 结构化的文档管理（`docs/`）
2. **强制工作流** - 引导 Agent 遵循"规划→执行→汇报"流程
3. **任务交接机制** - Agent 之间通过 `agentreadme.md` 传递知识
4. **本地优先** - 所有数据在本地，完全可控

## 快速开始

### 1. 安装

```bash
# 从 GitHub 安装（MVP 阶段）
pip install git+https://github.com/Sithcighce/AgentHandOff.git#egg=agent-handoff

# 未来会发布到 PyPI
# pip install agent-handoff
```

### 2. 初始化项目

```bash
cd your-project
agent-handoff init
```

这会创建完整的项目结构和**独立的MCP服务器脚本**：
```
your-project/
├── docs/
│   ├── 01_Goals_and_Status/      # 目标、进度、规范
│   ├── 02_Architecture_and_Usage/ # 架构、API 文档
│   ├── 03_History_and_Lessons/    # 历史记录、教训
│   └── 04_User_Facing/            # 用户文档
└── .agent-handoff/
    ├── agentreadme.md             # Agent 交接文档
    ├── config.yaml                # 配置文件
    └── history/                   # 会话历史
```

### 3. 配置 IDE

**重要**: `agent-handoff init` 会在项目中创建独立的 `mcp_server.py` 脚本，这样即使在没有安装 `agent-handoff` 的其他项目中也可以使用 MCP 功能。

**VSCode / Cursor (推荐使用配置助手)**:

运行配置助手获取准确的配置：
```bash
python tools/setup_helper.py
```

**或手动配置**:

打开 `settings.json`，添加（使用你的实际Python路径）：

```json
{
  "mcp": {
    "servers": {
      "agent-handoff": {
        "command": "python",
        "args": ["-m", "agent_handoff.server"],
        "cwd": "${workspaceFolder}"
      }
    }
  }
}
```

**⚠️ 重要配置说明**:
- 如果使用虚拟环境，请将 `"command"` 设为虚拟环境中的python路径
- 确保 `agent-handoff` 已安装到对应的Python环境中
- 配置后需要重启VSCode

**配置诊断**:
如果遇到问题，运行诊断命令：
```bash
agent-handoff diagnose
```

**Claude Desktop**:

编辑 `~/Library/Application Support/Claude/claude_desktop_config.json`：

```json
{
  "mcpServers": {
    "agent-handoff": {
      "command": "python",
      "args": ["-m", "agent_handoff.server"],
      "cwd": "/path/to/your/project"
    }
  }
}
```

### 4. 开始使用

在 Copilot/Claude 中：

```
你：开始工作，我要实现用户登录功能

Agent：(自动调用 start_work)
📋 任务已启动！
我已阅读项目交接文档...
接下来我会制定详细计划...

Agent：(自动调用 plan_setup)
计划已提交：
1. 创建 Login 组件
2. 实现 API 调用
3. 添加错误处理
4. 编写测试

开始执行第 1 步...
```

## 工作流程

```
start_work
   ↓
   读取 agentreadme.md（了解项目现状）
   ↓
plan_setup
   ↓
   提交详细计划
   ↓
proceed → proceed → proceed
   ↓
   逐步完成任务
   ↓
end_job
   ↓
   Agent 生成新的 agentreadme.md
   保存会话历史
```

### 为什么这样设计？

**传统方式**（失控）:
```
你: 实现登录
Agent: 好的 [直接写代码]
你: 等等，这不符合我们的架构
Agent: 抱歉，我重写 [又写错了]
你: 💢💢💢
```

**Agent-Handoff 方式**（有序）:
```
你: 实现登录
Agent: [调用 start_work，读取项目文档]
Agent: 我看到项目使用 Supabase Auth，遵循 RBAC...
Agent: [调用 plan_setup] 我的计划是：1. 2. 3.
你: 好的，开始吧
Agent: [proceed] 步骤 1 完成...
Agent: [proceed] 步骤 2 完成...
Agent: [end_job] 任务完成，交接文档已更新
```

## MCP 工具集

### 文档操作

| 工具 | 描述 |
|------|------|
| `read_file` | 读取 docs/ 下的文件 |
| `write_file` | 写入文件（仅限 docs/） |
| `list_files` | 列出目录内容 |
| `search_files` | 搜索关键词 |

### 工作流

| 工具 | 描述 |
|------|------|
| `start_work` | 启动任务，获取项目上下文 |
| `plan_setup` | 提交开发计划 |
| `proceed` | 汇报进度，获取下一步 |
| `report_issue` | 报告问题，进入调试流程 |
| `end_job` | 结束任务，提交交接文档 |

## 设计哲学

### 1. 本地优先 (Local-First)

```
┌─────────────────────┐
│   开发者的机器       │
│                     │
│  ┌───────────────┐  │
│  │  项目代码     │  │
│  │  docs/        │  │
│  │  .git/        │  │
│  └───────────────┘  │
│         ↕           │
│  ┌───────────────┐  │
│  │ MCP 服务器    │  │
│  │ (Python 进程) │  │
│  └───────────────┘  │
│         ↕           │
│  ┌───────────────┐  │
│  │   AI Agent    │  │
│  └───────────────┘  │
└─────────────────────┘

✅ 所有数据在本地
✅ 不依赖云服务
✅ 完全可控
```

### 2. 非侵入式 (Non-Invasive)

```
Agent 的能力：

┌──────────────┐    ┌──────────────────┐
│ 原生能力     │    │ MCP 工具         │
│              │    │                  │
│ • 写代码     │    │ • 管理 docs/     │
│ • Git 操作   │    │ • 工作流引导     │
│ • 运行命令   │    │                  │
└──────────────┘    └──────────────────┘

MCP 只管文档，不干涉代码编辑
```

### 3. 强制工作流 (Strict Workflow)

不是"建议"，而是"必须"：
- 启动任务必须调用 `start_work`
- 必须提交计划才能执行
- 必须逐步汇报进度
- 必须提交交接文档才能结束

**为什么强制？**
- 确保 Agent 养成良好工程习惯
- 最大化按次计费模型的价值
- 便于审计和回溯

## 常见问题

### Q: Agent 不听话怎么办？

A: 通过提示词引导。在 IDE 配置中添加系统提示：

```markdown
本项目使用 Agent-Handoff 进行任务管理。
开始任何工作前，你必须调用 start_work 工具。
工作流程：start_work → plan_setup → proceed → end_job
这是强制的工程实践，不可跳过。
```

### Q: docs/ 结构必须按推荐的来吗？

A: 不是强制的。你可以完全自定义目录结构，MCP 工具不限制。推荐结构只是 `init` 命令创建的模板。

### Q: 可以在多个项目使用吗？

A: 可以。每个项目独立运行自己的 MCP 服务器实例，互不干扰。

### Q: 支持团队协作吗？

A: MVP 阶段通过 Git 协作（文档在 Git 中）。云端团队协作是 v2.0 的计划功能。

### Q: 会自动 Git commit 吗？

A: 不会。文档变更由开发者手动 commit，保持灵活性。

## 开发路线图

### v0.1 (当前) - MVP
- ✅ 基础 MCP 服务器
- ✅ 文档操作工具
- ✅ 强制工作流
- ✅ CLI init 命令

### v1.0 - 完善
- [ ] 语义搜索（向量数据库）
- [ ] 交互式 init（问答生成文档）
- [ ] VSCode 插件（可视化面板）

### v2.0 - 团队协作
- [ ] 云端同步
- [ ] 多人协作
- [ ] 代码准则检查

## 贡献

欢迎贡献！请查看 [CONTRIBUTING.md](CONTRIBUTING.md)

## 许可证

MIT License

## 致谢

- [MCP Protocol](https://modelcontextprotocol.io/) by Anthropic
- 灵感来源于 vibecoding 社区的实践

---

**Agent-Handoff = Git for AI Context**

让 AI 协作像代码协作一样规范、可追溯、高效。