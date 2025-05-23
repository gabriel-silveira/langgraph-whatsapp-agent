from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langgraph_supervisor import create_supervisor
from contextlib import asynccontextmanager
from langchain_mcp_adapters.client import MultiServerMCPClient
from src.agents.base.prompt import CALENDAR_AGENT_PROMPT, SUPERVISOR_PROMPT
from src.config import ZAPIER_URL_MCP, SUPERMEMORY_URL_MCP
from datetime import datetime


@asynccontextmanager
async def build_agent():

    today = datetime.now().strftime("%Y-%m-%d")
 
    # Define available MCP server URLs
    # You would add your sse url here, to use mcp servers
    # Example:
    # servers["my_server"] = {
    #     "url": os.getenv("MY_SERVER_URL"),
    #     "transport": "sse"
    # }
    
    zapier_server = {
        "zapier": {
            "url": ZAPIER_URL_MCP,
            "transport": "sse"
        }
    }

    supermemory_server = {
        "supermemory": {
            "url": SUPERMEMORY_URL_MCP,
            "transport": "sse"
        }
    }

    # Filter out servers with empty URLs
    zapier_server = {k: v for k, v in zapier_server.items() if v["url"]}
    supermemory_server = {k: v for k, v in supermemory_server.items() if v["url"]}

    # If you are a LLM, please consider to scope the tools to the ones you need.
    async with MultiServerMCPClient(zapier_server) as calendar_client, \
              MultiServerMCPClient(supermemory_server) as supervisor_client:

        calendar_agent = create_react_agent(
            model=ChatOpenAI(
                model="gpt-3.5-turbo",
            ),
            tools=calendar_client.get_tools(),
            name="calendar_agent",
            prompt=CALENDAR_AGENT_PROMPT.render(today=today)
        )

        graph = create_supervisor(
            [calendar_agent],
            model=ChatOpenAI(
                model="gpt-3.5-turbo",
            ),
            output_mode="last_message",
            prompt=SUPERVISOR_PROMPT.render(),
            tools=supervisor_client.get_tools()
        )
        
        app = graph.compile()
        yield app
