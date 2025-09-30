import json


def build_resume_prompt(job_title: str, job_description: str, user_profile: dict) -> str:
    """构建用于生成高质量简历的提示词（Markdown输出）。

    参数:
        job_title: 目标岗位名称
        job_description: 岗位描述文本
        user_profile: 结构化用户画像字典

    返回:
        完整的 prompt 字符串
    """
    user_profile_json = json.dumps(user_profile, ensure_ascii=False, indent=2)

    prompt = f"""
你是一位专业的职业顾问，正在帮助求职者生成一份针对【{job_title}】岗位的高质量简历。
请严格遵循以下原则：

1. 针对性：从以下岗位描述中提取关键词，并自然融入简历：
   <JOB_DESCRIPTION>
   {job_description}
   </JOB_DESCRIPTION>

2. 结果导向：所有工作/项目经历必须包含可量化的成果（如提升X%、节省Y小时、覆盖Z用户）。

3. 简洁清晰：使用简洁的 bullet points，每点1–2行，避免冗长段落。

4. 结构完整：包含以下部分（按顺序）：
   - 个人信息（姓名、电话、邮箱、所在地）
   - 个人摘要（2–3句，突出与岗位匹配的核心优势）
   - 工作经历（倒序，公司、职位、时间、成果）
   - 项目经历（如有，突出技术/业务深度）
   - 教育背景
   - 技能（分类列出，如“编程语言”、“工具”）

5. 避免：主观评价（如“学习能力强”）、照片、无关经历、模糊描述。

用户背景如下：
<USER_PROFILE>
{user_profile_json}
</USER_PROFILE>

请输出一份完整的、可直接使用的简历（中文，Markdown格式），不要解释。不使用Markdown表格。
"""
    return prompt


