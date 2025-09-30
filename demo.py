import asyncio
import json
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv
import os

# 加载环境变量
load_dotenv()

async def create_llm():
    """创建阿里云百炼平台的LLM客户端"""
    llm = ChatOpenAI(
        model="qwen-plus",  # 或者使用 qwen-turbo, qwen-max 等
        temperature=0.3,
        api_key=os.getenv("DASHSCOPE_API_KEY", "sk-1d878ae8655d43aa9b1b65ec100f6aa7"),
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
    )
    return llm

async def optimize_resume_with_llm(user_info):
    """使用LLM优化简历信息"""
    llm = await create_llm()
    
    system_prompt = """
    你是一个专业的简历优化专家。请根据用户提供的基本信息，帮助用户完善和优化简历内容。
    
    重要要求：
    1. 严格基于用户提供的真实信息，不得编造任何信息
    2. 如果用户没有提供某些信息，请在相应字段中填写"用户未提供"或留空
    3. 只能对用户提供的信息进行语言优化和格式整理，不得添加虚假内容
    4. 保持原有信息的真实性，不得夸大或虚构任何经历、技能、成就等
    5. 优化语言表达，使其更加专业和规范
    6. 按照标准简历格式输出
    7. 严格按照以下JSON格式输出，不要添加其他内容：
    
    {
        "个人信息": {
            "姓名": "string",
            "年龄": "string",
            "联系方式": "string",
            "邮箱": "string"
        },
        "教育背景": {
            "学历": "string",
            "学校": "string",
            "专业": "string",
            "毕业年份": "string",
            "GPA": "string"
        },
        "工作经历": [
            {
                "公司": "string",
                "职位": "string",
                "时间": "string",
                "工作内容": "string",
                "成就": "string"
            }
        ],
        "技能专长": {
            "编程技能": ["string"],
            "技术技能": ["string"],
            "软技能": ["string"]
        },
        "获奖情况": [
            {
                "奖项名称": "string",
                "颁发机构": "string",
                "获奖时间": "string",
                "排名": "string"
            }
        ],
        "职业证书": [
            {
                "证书名称": "string",
                "颁发机构": "string",
                "获得时间": "string",
                "等级": "string"
            }
        ],
        "项目经验": [
            {
                "项目名称": "string",
                "项目时间": "string",
                "角色": "string",
                "技术栈": "string",
                "项目描述": "string",
                "成果": "string"
            }
        ],
        "自我评价": "string",
        "求职意向": {
            "目标职位": "string",
            "期望薪资": "string",
            "期望地点": "string"
        }
    }
    
    请记住：绝对不能编造任何信息！如果用户没有提供某些信息，请如实反映。
    """

    user_prompt = f"""
    请根据以下用户提供的详细信息，帮我优化简历：
    
    用户提供的原始信息：
    {json.dumps(user_info, ensure_ascii=False, indent=2)}
    
    请严格按照以下要求处理：
    1. 只使用用户提供的信息，不得编造任何内容
    2. 对现有信息进行语言优化，使其更加专业
    3. 如果某些字段用户没有填写，请填写"用户未提供"
    4. 保持信息的真实性和准确性
    5. 按照标准格式输出完整的简历JSON
    
    请特别注意：
    - 工作经历部分要基于用户提供的workExperience信息
    - 教育背景要基于用户提供的school、major、graduationYear等信息
    - 技能部分要基于用户提供的programmingSkills、technicalSkills、softSkills
    - 获奖情况要基于用户提供的awards信息
    - 职业证书要基于用户提供的certificates信息
    - 项目经验要基于用户提供的projects信息
    """

    try:
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        response = await llm.ainvoke(messages)
        return response.content
    except Exception as e:
        print(f"调用LLM时出错: {e}")
        return None

async def read_user_info(filename):
    """读取用户基本信息文件"""
    user_data = {}
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                if line == "":
                    continue
                if '：' in line:
                    key, value = line.split('：', 1)
                    user_data[key.strip()] = value.strip()
        return user_data
    except FileNotFoundError:
        print(f"文件 {filename} 不存在，请创建用户信息文件")
        return {}
    except Exception as e:
        print(f"读取文件错误: {e}")
        return {}

async def save_resume(data, filename="optimized_resume.json"):
    """保存优化后的简历"""
    try:
        # 如果返回的是字符串，尝试解析为JSON
        if isinstance(data, str):
            try:
                # 清理可能的markdown格式
                clean_data = data.replace("```json", "").replace("```", "").strip()
                parsed_data = json.loads(clean_data)
                with open(filename, 'w', encoding='utf-8') as file:
                    json.dump(parsed_data, file, ensure_ascii=False, indent=2)
            except json.JSONDecodeError:
                # 如果解析失败，保存原始文本
                with open(f"{filename}.txt", 'w', encoding='utf-8') as file:
                    file.write(data)
        else:
            with open(filename, 'w', encoding='utf-8') as file:
                json.dump(data, file, ensure_ascii=False, indent=2)
        
        print(f"简历已保存到 {filename}")
        return True
    except Exception as e:
        print(f"保存简历错误: {e}")
        return False

async def interactive_resume_builder():
    """交互式简历构建器"""
    print("=== 简历智能优化助手 ===")
    print("请输入您的基本信息，我会帮您完善简历")
    
    user_info = {}
    
    # 收集基本信息
    user_info["姓名"] = input("姓名：") or "未提供"
    user_info["年龄"] = input("年龄：") or "未提供"
    user_info["学历"] = input("学历：") or "未提供"
    user_info["工作经验"] = input("工作经验：") or "未提供"
    user_info["技能"] = input("技能：") or "未提供"
    user_info["自我介绍"] = input("自我介绍：") or "未提供"
    
    print("\n正在为您优化简历...")
    
    # 调用LLM优化简历
    optimized_resume = await optimize_resume_with_llm(user_info)
    
    if optimized_resume:
        print("\n=== 优化后的简历 ===")
        print(optimized_resume)
        
        # 保存简历
        await save_resume(optimized_resume)
    else:
        print("简历优化失败")

async def main():
    """主函数"""
    # 首先尝试从文件读取用户信息
    user_info = await read_user_info("user_info.txt")
    
    if user_info:
        print("检测到用户信息文件，正在处理...")
        print(f"原始信息: {user_info}")
        
        optimized_resume = await optimize_resume_with_llm(user_info)
        
        if optimized_resume:
            print("\n=== 优化后的简历 ===")
            print(optimized_resume)
            await save_resume(optimized_resume, "optimized_resume.json")
        else:
            print("简历优化失败")
    else:
        print("未找到用户信息文件，启动交互模式...")
        await interactive_resume_builder()

if __name__ == "__main__":
    asyncio.run(main())