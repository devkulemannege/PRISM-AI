from llm_chain import test_agent_with_mcp_tool
# Import or define get_leads_tool_schema and llm before use
from llm_chain import get_leads_tool_schema  # Replace 'my_tools_module' with the actual module name
from llm_chain import llm  # Replace 'my_llm_module' with the actual module name



from langgraph.prebuilt import create_react_agent
tools = [get_leads_tool_schema]
agent = create_react_agent(tools=tools, model=llm)
result = agent.invoke({"input": "Show me the leads"})
print(result)

# Connect to your MCP server (default port 3333)
mcp_client = Client("http://localhost:3333")

# Fetch and call the tool from the MCP server by name
def get_leads_from_mcp():
    """Get leads from the MCP server's get_leads tool."""
    tool_fn = mcp_client.tool("get_leads")
    return tool_fn()

# Optionally, wrap as a LangChain tool for agent use
@tool
def get_leads_tool_lc():
    """Get leads from MCP server (LangChain tool wrapper)."""
    return get_leads_from_mcp()

# Define a schema for the tool input (can be empty for no input)
class GetLeadsInput(BaseModel):
    query: Optional[str] = None  # Optionally allow a query string

def get_leads_from_mcp_with_schema(input: GetLeadsInput) -> str:
    """Get leads from MCP server (LangGraph tool schema version)."""
    leads = get_leads_from_mcp()
    return str(leads)

get_leads_tool_schema = Tool(
    name="get_leads",
    description="Get leads from MCP server. Optionally provide a query string.",
    args_schema=GetLeadsInput,
    func=get_leads_from_mcp_with_schema,
)


def test_agent_with_mcp_tool():
    """Test the agent with the MCP get_leads tool."""
    # List of tools for the agent
    tools = [get_leads_tool_lc]

    # Initialize your LLM (already in your code)
    llm = ChatGroq(api_key=GROQ_API_KEY, model="llama3-8b-8192")

    # Create the agent with the tools
    agent = initialize_agent(
        tools,
        llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True
    )

    # Example usage: ask for leads
    result = agent.run("Show me the leads")
    print("Agent result:", result)