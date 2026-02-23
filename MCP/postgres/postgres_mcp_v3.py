import asyncio
import os
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
from langchain_google_genai import ChatGoogleGenerativeAI


load_dotenv('E:\jupyter_notebook\sqlite_mcp_langchain_gemini\.env')
print("Environment variables loaded from .env file")

# Initialize model
model = ChatGoogleGenerativeAI(model="gemini-2.0-flash-lite", api_key=os.environ["GOOGLE_API_KEY"])

# Postgres connection string
POSTGRES_CONNECTION_STRING = "postgresql://postgres:12345678@localhost:5432/tagminds_poc"

# MCP server parameters
server_params = StdioServerParameters(
    command="npx",
    args=[
        "-y",
        "@modelcontextprotocol/server-postgres",
        POSTGRES_CONNECTION_STRING,
    ],
)


async def process_query(agent, query):
    response = await agent.ainvoke({"messages": query})
    return response["messages"][-1].content


async def main():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await load_mcp_tools(session)

            # ✅ langgraph's create_react_agent — no hub.pull prompt needed
            agent = create_react_agent(model, tools)

            print("PostgreSQL Assistant - tagminds_poc (type 'exit' to quit)")

            while True:
                query = input("\nEnter your query: ").strip()
                if query.lower() == 'exit':
                    break
                if not query:
                    continue

                print("\nProcessing...\n")
                response = await process_query(agent, query)
                print(f"\nAnswer: {response}")


if __name__ == "__main__":
    asyncio.run(main())