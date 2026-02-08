from mcp.server.fastmcp import FastMCP
import sys

# Create an MCP server instance.
# The name "HelloWorldServer" will be exposed to clients.
mcp = FastMCP("HelloWorldServer")


@mcp.tool()
def say_hello(name: str = "World") -> str:
    """
    Greets the given name.

    Args:
        name: The name to greet. Defaults to "World".

    Returns:
        A greeting string.
    """
    return f"Hello, {name}!"


if __name__ == "__main__":
    print("Starting MCP 'Hello World' Server...", file=sys.stderr)
    print("This server exposes a 'say_hello' tool.", file=sys.stderr)
    print("Press Ctrl+C to stop the server.", file=sys.stderr)
    mcp.run(transport="stdio")


"""
{"jsonrpc": "2.0","id": 1,"method": "tools/call","params": {"name": "say_hello","arguments": {"name": "Marcelo"}}}
"""
