import asyncio
import os
import json
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI
from langchain_mcp_adapters.sse import SseServerParameters
from dotenv import load_dotenv

load_dotenv
memory = ChatMessageHistory()

async def llm_client():
    return ChatOpenAI(
            model="deepseek-chat",
            temperature=0.2,
            api_key=os.getenv('API_KEY'),
            base_url="https://api.deepseek.com",
            system=system_prompt,
            response_format={"type":"json_object"}
            )

async def mcp_client():
    server_configs = {
        "thinking-sse":{
            "url":"ttps://mcp.api-inference.modelscope.net/3263ca4515d34c/sse",
            "transport":"sse"
                },

        "bing-sse":{
            "url":"https://mcp.api-inference.modelscope.net/9b8518aab38346/sse",
            "transport":"sse"
            }
        }

    client = MultiServerMCPClient()
    for server_name,config in server_config.items():
        if config["type"] == "sse":
            server_params = SseServerParameters(url=config["url"])
            await client.add_sse_server(server_name,server_params)
    return client


async def get_tools():
    tools = await client.get_tools()
    return tools

async def agent():
    client = await mcp_client()
    tools = await get_tools(client)
    llm = llm_client()
    agent = create_react_agent(llm,tools)

    result = await agent.invoke({
        "messages":[HumanMessage(content=user_query)]
        })

    last_message = result['message'][-1]
    return last_message

async def read_info(filename):
    user_data = {}

    try:
        with open(filename,'r',encoding='utf-8') as file:
            for line in file:
                if line.strip() == "":
                    continue

                if '：' in line:
                    key,value = line.split('：',1)
                    user_data[key.strip()] = value.strip()
    except:
        pass

async def save_text(data,filename="resume.txt"):
    try:
        with open(filename,'w',encoding='utf-8') as file:
            file.write(str(data))
    except Exception as e:
        pass

async def main():
    user_info = read_info(user_info.txt)
    answer = agent(user_info)
    save_text(answer)

if __name__ == "__main__":
    asyncio.run(main())
