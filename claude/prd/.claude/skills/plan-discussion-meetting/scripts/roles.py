#!/usr/bin/env python3
#-*- coding:utf-8 -*-

__author__ = 'miaoyoumeng'

import json
from file_config import PROJECT_ROOT_DIR, REFERENCES_DIR
from markdown import parse_role_md

def role(role_name: str):

    # 1. 配置 Skill 路径
    # 替换为你的 Skill 文件夹路径
    metadata = parse_role_md(str(REFERENCES_DIR) + "/" + role_name)

    name = metadata['name'] if ("name" in metadata) else role_name
    instructions = metadata['markdown'] if ("markdown" in metadata) else ""
    description = metadata['description'] if ("description" in metadata) else ""
    max_turns = metadata['max_turns'] if ("max_turns" in metadata) else 10
    system_prompt = metadata['system_prompt'] if ("system_prompt" in metadata) else {"type": "preset", "preset": "claude_code"}
    
    tools = metadata['tools'] if ("tools" in metadata) else ["Read", "Grep", "Glob"]
    cwd = str(PROJECT_ROOT_DIR)

    prompt_parts = []
    if role_name:
        prompt_parts.append(f"# Skill: {name}\n")
    if description:
        prompt_parts.append(f"## Description\n{description}\n")
    if instructions:
        prompt_parts.append(f"## Instructions\n{instructions}\n")

    return {
        "name": name,
        "cwd": str(PROJECT_ROOT_DIR),
        "system_prompt": system_prompt,
        "allowed_tools": tools,
        "permission_mode": "acceptEdits",
        "max_turns": max_turns,
        "description":description,
        "prompt_parts":prompt_parts
    }
    

ZhongShuLing = role('Role_中书省.md')
MenXiaShiZhong = role('Role_门下省.md')
ShangShuLing = role('Role_尚书省.md')

HrShangShu = role('Role_吏部.md')
HuBuShangShu = role('Role_户部.md')
GongBuShangShu = role('Role_工部.md')
XingBuShangShu = role('Role_刑部.md')
BingBuShangShu = role('Role_兵部.md')
LiBuShangShu = role('Role_礼部.md')



