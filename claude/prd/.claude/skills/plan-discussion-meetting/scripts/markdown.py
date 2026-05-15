import re
import yaml

# 解析 markdown 内容，按照 --- 分隔符解析成对应的 claude code 需要的属性
def parse_role_md(file_path: Path) -> Tuple[Dict, str]:
    """
    解析 SKILL.md 文件，返回 (metadata, instructions)
    
    metadata: 包含 name, description 等 YAML frontmatter 字段
    instructions: Markdown 正文部分
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 正则匹配 YAML frontmatter
    frontmatter_pattern = r'^---\s*\n(.*?)\n---\s*\n(.*)$'
    match = re.search(frontmatter_pattern, content, re.DOTALL)
    
    if match:
        yaml_text = match.group(1)
        markdown_text = match.group(2).strip()
        try:
            metadata = yaml.safe_load(yaml_text) or {}
        except yaml.YAMLError as e:
            raise ValueError(f"YAML 解析失败: {e}")
    else:
        # 没有 frontmatter 时，整个文件视为 instructions
        metadata = {}
        markdown_text = content.strip()
    
    metadata['markdown'] = markdown_text
    return metadata



# def load_skill(skill_dir: Path) -> str:
#     """
#     从 skill 目录加载 SKILL.md，并生成适用于 Agent 的 system_prompt
#     """
#     skill_md_path = skill_dir / "SKILL.md"
#     if not skill_md_path.exists():
#         raise FileNotFoundError(f"未找到 SKILL.md: {skill_md_path}")
    
#     metadata, instructions = parse_skill_md(skill_md_path)
    
#     # 构建 system prompt
#     name = metadata.get('name', 'Unnamed Skill')
#     description = metadata.get('description', '')
    
#     prompt_parts = []
#     if name:
#         prompt_parts.append(f"# Skill: {name}\n")
#     if description:
#         prompt_parts.append(f"## Description\n{description}\n")
#     if instructions:
#         prompt_parts.append(f"## Instructions\n{instructions}\n")
    
#     # 可选：添加额外的引导语，确保 Agent 遵循 Skill
#     prompt_parts.append("You are now an expert using the above skill. Follow the instructions precisely.")
    
#     return "\n".join(prompt_parts)

# def create_agent_options(skill_dir: Path, **extra_options) -> ClaudeAgentOptions:
#     """
#     根据 Skill 目录创建 ClaudeAgentOptions 对象
    
#     extra_options: 可覆盖或添加其他选项，如 allowed_tools, model 等
#     """
#     system_prompt = load_skill(skill_dir)
    
#     # 默认配置（可根据需要调整）
#     default_options = {
#         "system_prompt": system_prompt,
#         "allowed_tools": ["Read", "Write", "Bash"],   # 根据 skill 实际需求授权
#         "permission_mode": "acceptEdits",
#     }
#     default_options.update(extra_options)
    
#     return ClaudeAgentOptions(**default_options)