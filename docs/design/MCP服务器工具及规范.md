4. MCP 服务器工具集规范
版本: v7.0.0 (最终蓝图)
状态: 定稿

本文档定义了 Agent-Handoff MCP 服务器向 Agent 暴露的所有工具的技术规格。

4.1 工具调用原则
Agent-Handoff 提供的工具分为两类，它们遵循不同的调用规则：

1. 工作流工具 (Workflow Tools)
工具列表: start_work, plan_setup, proceed, report_issue, end_job。

规则: 必须拥有一个活跃的会话，并且严格按预设顺序调用。服务器内部维护一个状态机，任何不符合当前状态的调用都将被拒绝，并返回 WORKFLOW_VIOLATION 错误。

2. 实用工具 (Utility Tools)
工具列表: read_file, write_file, list_files, search_files。

规则: 可以随时调用，不需要活跃的会话。这些工具是无状态的，用于让 Agent 自由地查询和操作 docs/ 知识库。

4.2 状态化工作流工具
start_work
描述: 启动一个新任务，获取初始上下文。

输出: 包含 session_id, agent_readme_content, instruction (指示 Agent 下一步调用 plan_setup)。

plan_setup
描述: 提交一个开发计划以供服务器记录。

前置条件: 必须已调用 start_work。

proceed
描述: 汇报上一步的完成情况，并获取下一步的任务指令。

前置条件: 必须已调用 plan_setup 或上一步 proceed。

report_issue
描述: 当计划执行失败时调用，进入结构化的调试流程。

前置条件: 必须处于一个活跃的会话中。

end_job
描述: 完成所有工作，提交由 Agent 自己总结生成的、用于交接的 agentreadme.md，正式结束任务。

前置条件: 必须处于一个活跃的会话中。

4.3 受控的知识库操作工具
这些工具专门用于操作 docs/ 目录，并会进行严格的路径检查。

read_file, write_file, list_files, search_files
核心约束: 所有路径参数 (path) 必须指向 docs/ 目录或其子目录。任何试图访问 docs/ 目录之外的路径（如 ../）的操作都将被拒绝，并返回 INVALID_PATH 错误。

4.4 错误响应格式
当工具调用失败时，服务器将返回统一格式的错误信息，以指导 Agent 进行修正。

{
  "error": {
    "code": "WORKFLOW_VIOLATION" | "INVALID_PATH" | "FILE_NOT_FOUND",
    "message": "一段人类可读的、清晰的错误描述。",
    "suggestion": "（可选）一段建议 Agent 下一步应该如何操作的提示。"
  }
}
