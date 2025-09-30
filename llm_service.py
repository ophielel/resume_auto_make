import asyncio
from typing import Optional
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv
import os

load_dotenv()


async def create_llm(model: str = "qwen-plus", temperature: float = 0.3) -> ChatOpenAI:
    return ChatOpenAI(
        model=model,
        temperature=temperature,
        api_key=os.getenv("DASHSCOPE_API_KEY", ""),
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )


async def generate_markdown_resume(prompt: str, *, model: str = "qwen-plus", temperature: float = 0.3) -> Optional[str]:
    llm = await create_llm(model=model, temperature=temperature)
    system = SystemMessage(content="你是资深HR与职业顾问，严谨、客观、结果导向，输出中文Markdown。")
    user = HumanMessage(content=prompt)
    try:
        resp = await llm.ainvoke([system, user])
        return resp.content
    except Exception as e:
        print(f"LLM生成失败: {e}")
        return None


