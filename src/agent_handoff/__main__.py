if __name__ == "__main__":
    # 检测运行模式
    import sys
    import asyncio
    
    if len(sys.argv) > 1 and sys.argv[1] == "init":
        from agent_handoff.cli import cli
        cli()
    else:
        # 默认启动 MCP 服务器
        from agent_handoff.server import main
        asyncio.run(main())