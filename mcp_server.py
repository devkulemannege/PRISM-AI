# Minimal MCP server with a simple example tool using FastAPI, LangChain, Groq LLM, and Tavily search tool
#STILL IN  DEVELOPMENT NOT INCLUDED IN THE MVP######
##########################################################################3333
from fastapi import FastAPI, Request
from langchain_groq import ChatGroq
from langchain.tools.tavily_search import TavilySearchResults
from langchain.agents import initialize_agent, AgentType
import os
from dotenv import load_dotenv

load_dotenv(os.path.abspath(os.path.join(os.path.dirname(__file__), "credentials.env")))
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

app = FastAPI()

@app.post("/mcp")
async def mcp_endpoint(request: Request):
    data = await request.json()
    user_message = data.get("input", "")

    llm = ChatGroq(api_key=GROQ_API_KEY, model="llama3-8b-8192")
    search = TavilySearchResults(api_key=TAVILY_API_KEY)
    tools = [search]

    prompt = (
        "You are PRISM-AI, a friendly WhatsApp sales agent. Reply to the user message below in a helpful, concise, and conversational way (max 3 sentences, under 100 words). "
        "If you need to answer questions about the web, you can use the search tool.\n"
        "User Message: {input}\n"
        "Your reply:"
    )

    agent = initialize_agent(
        tools,
        llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
        agent_kwargs={"system_message": prompt}
    )

    response = agent.run(user_message)
    return {"response": response}


