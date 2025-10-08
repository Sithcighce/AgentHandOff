if __name__ == "__main__":
    # 检测运行模式
    import sys
    import asyncio
    
    if len(sys.argv) > 1 and sys.argv[1] in ["init", "status", "--version", "--help"]:
        # CLI 模式
        from agent_handoff.cli import cli
        cli()
    else:
        # 默认启动 MCP 服务器
        try:
            from agent_handoff.server import main
            asyncio.run(main())
        except ImportError as e:
            print(f"无法启动MCP服务器: {e}", file=sys.stderr)
            print("请确保agent-handoff已正确安装", file=sys.stderr)
            sys.exit(1)