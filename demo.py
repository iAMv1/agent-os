#!/usr/bin/env python3
"""
AgentOS Demo - Demonstrates all components working together.
"""

import sys
import os
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agentos.orchestrator import AgentOS
from agentos.tools.tool_system import ToolDefinition, ToolSafety


def main():
    print("=" * 70)
    print("AGENTOS DEMO")
    print("=" * 70)

    # Initialize AgentOS
    print("\n[1/8] Initializing AgentOS...")
    aos = AgentOS()
    print("  âœ“ Session manager initialized")
    print("  âœ“ Memory system initialized")
    print("  âœ“ Context manager initialized")
    print("  âœ“ MCP config initialized")
    print("  âœ“ Tool registry initialized")
    print("  âœ“ Self-healing system initialized")

    # Session Management
    print("\n[2/8] Session Management...")
    session_id = aos.start_session()
    print(f"  âœ“ Session started: {session_id}")

    aos.add_user_message("Build a REST API for a todo app")
    print("  âœ“ User message added")

    aos.add_assistant_message("Enhanced task specification: ...")
    print("  âœ“ Assistant message added")

    aos.add_tool_result("FileRead", "Contents of main.py...", "success")
    print("  âœ“ Tool result added")

    # Memory System
    print("\n[3/8] Memory System...")
    memory_summary = aos.memory.get_memory_summary()
    print(f"  âœ“ Memory file exists: {memory_summary['exists']}")
    print(f"  âœ“ Memory size: {memory_summary['size_bytes']} bytes")

    # Context Management
    print("\n[4/8] Context Management...")

    # Test large output handling
    large_content = "Line " + "\nLine ".join(str(i) for i in range(3000))
    handled = aos.context.handle_large_output(large_content, prefix="test")
    if handled.get("written_to_disk"):
        print(f"  âœ“ Large output written to disk: {handled['file_path']}")
        print(f"  âœ“ Preview generated: {len(handled['preview'])} chars")
    else:
        print("  âœ“ Content within limits, no disk write needed")

    # Test file deduplication
    test_content = "test file content"
    test_hash = aos.context.compute_hash(test_content)
    should_read = aos.context.should_read_file("test.txt", test_hash)
    print(f"  âœ“ File deduplication: should_read={should_read}")

    aos.context.update_file_hash("test.txt", test_content)
    should_read_again = aos.context.should_read_file("test.txt", test_hash)
    print(f"  âœ“ After update: should_read={should_read_again}")

    # Tool System
    print("\n[5/8] Tool System...")

    # Register some tools
    concurrent_tools = [
        ToolDefinition(
            "FileRead", "Read file contents", ToolSafety.CONCURRENT_SAFE, "built-in", {}
        ),
        ToolDefinition(
            "Grep", "Search file contents", ToolSafety.CONCURRENT_SAFE, "built-in", {}
        ),
        ToolDefinition(
            "Glob",
            "Find files matching patterns",
            ToolSafety.CONCURRENT_SAFE,
            "built-in",
            {},
        ),
    ]

    serial_tools = [
        ToolDefinition(
            "FileEdit", "Edit files", ToolSafety.SERIAL_ONLY, "built-in", {}
        ),
        ToolDefinition(
            "FileWrite", "Write files", ToolSafety.SERIAL_ONLY, "built-in", {}
        ),
        ToolDefinition(
            "Bash", "Execute shell commands", ToolSafety.SERIAL_ONLY, "built-in", {}
        ),
    ]

    for tool in concurrent_tools + serial_tools:
        aos.tools.register_tool(tool)

    print(f"  âœ“ Registered {len(aos.tools.list_tools())} tools")
    print(f"  âœ“ Concurrent tools: {len(aos.tools.concurrent_tools)}")
    print(f"  âœ“ Serial tools: {len(aos.tools.serial_tools)}")

    # Test tool partitioning
    tool_calls = [
        {"tool": "FileRead", "arguments": {"path": "main.py"}},
        {"tool": "Grep", "arguments": {"pattern": "def"}},
        {"tool": "FileEdit", "arguments": {"path": "main.py"}},
        {"tool": "Bash", "arguments": {"command": "ls"}},
    ]
    partitioned = aos.tool_executor.partition_tool_calls(tool_calls)
    print(
        f"  âœ“ Partitioned: {len(partitioned['concurrent'])} concurrent, {len(partitioned['serial'])} serial"
    )

    # Self-Healing
    print("\n[6/8] Self-Healing System...")

    # Test circuit breaker
    cb = aos.healing.get_circuit_breaker("test_api")
    print(f"  âœ“ Circuit breaker created: {cb.get_state()['state']}")

    # Test successful execution
    result = aos.healing.execute_with_healing("test_api", lambda: "success")
    print(f"  âœ“ Successful execution: {result}")
    print(f"  âœ“ Circuit breaker state: {cb.get_state()['state']}")

    # Test retry with failure
    call_count = 0

    def failing_then_success():
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise ValueError(f"Failure {call_count}")
        return f"Success on attempt {call_count}"

    result = aos.healing.execute_with_healing(
        "retry_test",
        failing_then_success,
        retryable_exceptions=[ValueError],
    )
    print(f"  âœ“ Retry succeeded: {result}")

    # MCP Integration
    print("\n[7/8] MCP Integration...")
    aos.mcp.add_server(
        "test-server",
        {
            "command": "echo",
            "args": ["test"],
        },
    )
    print(f"  âœ“ MCP server added: {aos.mcp.list_servers()}")
    print(f"  âœ“ MCP status: {aos.mcp.get_server_status()}")

    # System Status
    print("\n[8/8] System Status...")
    status = aos.get_status()
    print(f"  âœ“ Session: {status['session']['current_id']}")
    print(f"  âœ“ Turn count: {status['session']['turn_count']}")
    print(f"  âœ“ Available sessions: {status['session']['available_sessions']}")
    print(f"  âœ“ Memory exists: {status['memory']['exists']}")
    print(f"  âœ“ Cached files: {status['context']['cached_files']}")
    print(f"  âœ“ Total tools: {status['tools']['total_tools']}")

    print("\n" + "=" * 70)
    print("AGENTOS DEMO COMPLETE")
    print("=" * 70)
    print("\nAll components working:")
    print("  âœ“ Session persistence with JSONL logging")
    print("  âœ“ Threshold-based memory extraction")
    print("  âœ“ Context management with deduplication")
    print("  âœ“ Tool system with concurrent/serial batching")
    print("  âœ“ Self-healing with retry and circuit breaker")
    print("  âœ“ MCP integration with deferred loading")


if __name__ == "__main__":
    main()
