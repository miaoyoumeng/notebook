import re
import yaml

"""
    解析 Markdown 文件中的 YAML front matter
    Args:
        content: Markdown 文件内容
    Returns:
        (meta_data, markdown_content) 元组
"""
def parse_front_matter(content: str) -> tuple[dict, str]:
    
    pattern = r'^---\s*\n(.*?)\n---\s*\n(.*)'
    match = re.match(pattern, content, re.DOTALL)

    if not match:
        return {}, content

    yaml_content = match.group(1)
    markdown_content = match.group(2)

    try:
        meta_data = yaml.safe_load(yaml_content)
    except yaml.YAMLError as e:
        print(f"YAML 解析错误：{e}", file=sys.stderr)
        meta_data = {}

    return meta_data, markdown_content

# 获取
def get_skill_meta_data(content: str) -> tuple[dict, str]:
    meta_data, markdown_content = parse_front_matter(content)
    return meta_data


def get_skill_markdown(content: str) -> tuple[dict, str]:

    meta_data, markdown_content = parse_front_matter(content)
    name = meta_data['name'] if ("name" in meta_data) else "java_unit_test"
    description = meta_data['description'] if ("description" in meta_data) else ""

    prompt_parts = []
    if name:
        prompt_parts.append(f"# Skill: {name}\n")
    if description:
        prompt_parts.append(f"## Description: {description}\n")
    if markdown_content:
        prompt_parts.append(f"## Instructions: \n{markdown_content}\n")
    
    # 可选：添加额外的引导语，确保 Agent 遵循 Skill
    prompt_parts.append("\n **您现在是使用上述技能的单元测试专家了。严格按照说明进行操作。** \n")

    instructions = "\n".join(prompt_parts)
    return markdown_content