#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Java 单元测试生成脚本 (JUnit 4 + Mockito)
使用 claude-agent-sdk 调用 Claude 生成单元测试

操作步骤:
1. 扫描 Maven 项目下的各个模块
2. 逐个模块扫描 Java 文件
3. 为每个 Java 类生成对应的单元测试（枚举类和常量类除外）
"""

import os
from pathlib import Path

from config import PROJECT_ROOT_DIR, REFERENCES_DIR
from markdown import get_skill_meta_data, get_skill_markdown
from query import run_query

def load_references_template(file_name: str)-> str:
    if not os.path.isabs(file_name):
        file_path = REFERENCES_DIR / file_name
    content = ""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    return str(content)

async def java_unit_test(java_file: str):
    # print(json.dumps(meta_data, ensure_ascii=False))
    """主函数"""
    # 获取项目根目录（默认为当前工作目录或通过参数指定）
    java_file_path = Path(str(PROJECT_ROOT_DIR) + "/" + java_file)
    if (not java_file_path.exists()):
        print(f"file: {java_file} not exists. ")
        return

    print(f"文件：{java_file} 的单元测试")
    skill_content = load_references_template("mockito-template.md")
    meta_data = get_skill_meta_data(skill_content)
    markdown = get_skill_markdown(skill_content)
    answer = await run_query(java_file, meta_data, markdown, False)
    
    print(answer)

