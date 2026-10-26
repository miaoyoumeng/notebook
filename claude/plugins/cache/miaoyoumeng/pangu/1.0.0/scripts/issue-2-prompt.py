#!/usr/bin/env python3
#-*- coding:utf-8 -*-
import re
import os
import sys
from pathlib import Path
import argparse

from config import prds_dir, bugs_dir, logs_dir, prompts_dir

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description = "处理指定 bugs 目录下的包含菜单 markdown 文件",
        formatter_class = argparse.RawDescriptionHelpFormatter,
        epilog = "示例: %(prog)s --workspace=<workspace>  --name=<name>"
    )
    parser.add_argument('--workspace', required = False,
         help = '工作目录目录的路径（非必需）')
    parser.add_argument('--name', required = True,
          help = '系统名称（必需）')
    args = parser.parse_args()

    workspace: Path = Path(args.workspace if args.workspace else str(Path.cwd()))
    name:str = args.name if args.name else "default"
    
    bug_dir = bugs_dir(workspace, name)
    prd_dir = prds_dir(workspace, name)

    for markdown in bug_dir.glob('*.md'):
        try:
            content = markdown.read_text(encoding='utf-8')
        except Exception as e:
            print(f"读取 {markdown.name} 失败: {e}")

        type, name = markdown.name.split('-', 1) 
        if ("prd" == type):
            name, suffix = name.split('.', 1) 
            fix_path = Path(prd_dir / f"{name}.prd.md")
        if not fix_path.is_file():
        	continue

        prompt = f"""
1. 调用`/clear` 命令，清空当前context。 
2. 调用 Skill `/solo:prd-writer`，请修改 prd 文档：{fix_path}。
按要求如下进行修改：
{content}
"""
        prompt_dir = prompts_dir(workspace)
        prompt_md_path = Path(prompt_dir / f"bug-{name}.prompt.md")

        prompt_md_path.write_text(prompt, encoding='utf-8')

        markdown.unlink()