# Minimal MCP server with a simple example tool using FastMCP
from fastmcp.server import FastMCP
from fastmcp.tools import FunctionTool

# Example tool: returns a static list of leads
def get_leads():
    """Return a static list of leads for demonstration purposes."""
    return [
        {"name": "Alice", "email": "alice@example.com"},
        {"name": "Bob", "email": "bob@example.com"}
    ]

# Register the tool with MCP
mcp = FastMCP()
mcp.add_tool(FunctionTool.from_function(get_leads))

if __name__ == "__main__":
    # Run the MCP server on the default port (3333)
    mcp.run()


