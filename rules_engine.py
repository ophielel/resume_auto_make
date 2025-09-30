import re
from typing import Dict, List, Any, Set


METRIC_PATTERN = re.compile(r"(\d+\.?\d*%?|\b(万|千|百|倍)\b)")


def _word_count(text: str) -> int:
    if not text:
        return 0
    # 粗略计数：中文字符+空格分词
    return len(re.findall(r"\w+|[\u4e00-\u9fa5]", text))


def _contains_metric(text: str) -> bool:
    if not text:
        return False
    return bool(METRIC_PATTERN.search(text))


def _extract_keywords(text: str) -> Set[str]:
    if not text:
        return set()
    # 非严格关键词抽取：按非字母数字中文分割，过滤过短token
    tokens = re.split(r"[^\w\u4e00-\u9fa5\+\-\.]+", text)
    tokens = [t.strip() for t in tokens if len(t.strip()) >= 2]
    return set(tokens)


def validate_resume_structured(resume: Dict[str, Any], job_description: str) -> List[str]:
    """对结构化简历字典进行基础质量校验，返回错误/改进建议列表。"""
    errors: List[str] = []

    required_sections = ["contact", "summary", "experience", "education", "skills"]
    for sec in required_sections:
        if sec not in resume or not resume.get(sec):
            errors.append(f"缺少必要模块: {sec}")

    for exp in resume.get("experience", []):
        desc = exp.get("description") or exp.get("achievements") or ""
        if not _contains_metric(desc):
            title = exp.get("title") or exp.get("position") or "某项经历"
            errors.append(f"经历 '{title}' 缺少量化结果")

    jd_keywords = _extract_keywords(job_description)
    resume_skills = set(resume.get("skills", [])) if isinstance(resume.get("skills"), list) else set()
    missing = jd_keywords - resume_skills
    if missing:
        # 仅提示前若干个，避免噪音
        hints = list(missing)[:8]
        errors.append(f"建议补充JD关键词: {', '.join(hints)}")

    # 长度估计：拼接主要文本字段后计数
    text_fields: List[str] = []
    text_fields.append(str(resume.get("summary", "")))
    for exp in resume.get("experience", []):
        text_fields.append(str(exp.get("description", "")))
        text_fields.append(str(exp.get("achievements", "")))
    for proj in resume.get("projects", []):
        text_fields.append(str(proj.get("description", "")))
        text_fields.append(str(proj.get("results", "")))
    length = _word_count("\n".join(text_fields))
    if length > 700:
        errors.append("简历过长，建议精简至1页")

    return errors


def validate_resume_markdown(markdown_text: str, job_description: str) -> List[str]:
    """对Markdown简历进行启发式质量校验。"""
    errors: List[str] = []

    required_heads = ["个人信息", "个人摘要", "工作经历", "教育", "教育背景", "技能"]
    if not any(h in markdown_text for h in ["## 个人信息", "### 个人信息"]):
        errors.append("缺少必要模块: 个人信息")
    if not any(h in markdown_text for h in ["## 个人摘要", "### 个人摘要"]):
        errors.append("缺少必要模块: 个人摘要")
    if not any(h in markdown_text for h in ["## 工作经历", "### 工作经历"]):
        errors.append("缺少必要模块: 工作经历")
    if not any(h in markdown_text for h in ["## 教育背景", "### 教育背景", "## 教育", "### 教育"]):
        errors.append("缺少必要模块: 教育背景")
    if not any(h in markdown_text for h in ["## 技能", "### 技能"]):
        errors.append("缺少必要模块: 技能")

    # 量化成果：检查项目符号行是否包含数字/百分号
    bullet_lines = [ln.strip() for ln in markdown_text.splitlines() if ln.strip().startswith("-")]
    if bullet_lines:
        ratio_with_metric = sum(1 for ln in bullet_lines if _contains_metric(ln)) / max(len(bullet_lines), 1)
        if ratio_with_metric < 0.5:
            errors.append("量化成果不足：请在要点中加入明确的数字或百分比")

    # JD关键词覆盖
    jd_keywords = _extract_keywords(job_description)
    present = _extract_keywords(markdown_text)
    missing = jd_keywords - present
    if missing:
        hints = list(missing)[:8]
        errors.append(f"建议补充JD关键词: {', '.join(hints)}")

    # 长度控制
    if _word_count(markdown_text) > 900:  # Markdown符号会带来噪声，阈值略高
        errors.append("简历过长，建议精简至1页")

    return errors


