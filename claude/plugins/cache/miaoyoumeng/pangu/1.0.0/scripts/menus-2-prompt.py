#!/usr/bin/env python3
#-*- coding:utf-8 -*-
import re
import json
import os
import sys
from pathlib import Path
import argparse

from config import prompts_dir, outputs_dir

def parse_menu_tree(lines):
    """
    解析 markdown 菜单树
    """

    tree = []
    stack = []

    # 菜单节点格式
    node_pattern = re.compile(
        r'^(?P<prefix>[│ ]*)(├──|└──)\s*(?P<icon>\S+)\s*(?P<name>.+)$'
    )

    for raw_line in lines:
        line = raw_line.rstrip()

        m = node_pattern.match(line)
        if not m:
            continue

        prefix = m.group("prefix")
        icon = m.group("icon")
        name = m.group("name").strip()

        # 去掉序号
        name = re.sub(r'^\d+\.\s*', '', name)

        # 缩进层级
        level = len(prefix) // 4

        node = {
            "type": icon,
            "name": name,
            "children": []
        }
        # 只取前两层菜单
        if level == 0:
            tree.append(node)
            stack = [node]
        # elif level == 1: 
        else: 
            while len(stack) > level:
                stack.pop()

            parent = stack[-1]
            parent["children"].append(node)

            stack.append(node)

    return tree
def build_unique_names(nodes, sep="-"):
    result = []

    for node in nodes:
        parent_name = node.get("name", "")

        children = node.get("children", [])

        if not children or len(children) == 0:
            result.append({
                "name": parent_name,
                "function": [],
                "tab": []
                })
            # print(parent_name)
            continue
        
        for child in children:
            child_name = child.get("name", "")
            funcs = []
            tabs = []
            if child.get("children", []):
                tabs, funcs = build_functions_tabs(child.get("children"), sep)

            result.append({
                "name": f"{parent_name}{sep}{child_name}",
                "function": funcs,
                "tab": tabs
            })
    return list(result)

def build_functions_tabs(nodes, sep="-"):
    funcs = []
    tabs = []

    for node in nodes:

        node_type = node.get("type", "")
        node_name = node.get("name", "")
        
        children = node.get("children", [])
        if not children:
            continue

        if "💠" == node_type or "🗂️" == node_type:
            if not children:
                tabs.append(node_name)
                continue
            else:
                for child in children:
                    child_name = child.get("name", "")
                    tabs.append(f"{node_name}{sep}{child_name}")
        else:
            funcs.append(node_name)

        
        
    return tabs, funcs

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description = "根据指定目录下的包含菜单 markdown 文件，为菜单生成对应的prd文档",
        formatter_class = argparse.RawDescriptionHelpFormatter,
        epilog = "示例: %(prog)s --workspace=<workspace>  --name=<name> --pages=<pages>"
    )
    parser.add_argument('--workspace', required = False,
         help = '工作目录目录的路径（非必需）')
    parser.add_argument('--name', required = True,
          help = '系统名称（必需）')
    parser.add_argument('--pages', required = True,
          help = '页面结构内容')
    parser.add_argument('--context', required = False,
         help = '生成 prd 的 context')
    
    args = parser.parse_args()
    
    workspace: Path = Path(args.workspace if args.workspace else str(Path.cwd()))
    name:str = args.name if args.name else "default"

    # input_dir: Path = inputs_dir(workspace)

    # if not input_dir.exists() or not input_dir.is_dir():
    #     print(f"目录：{input_dir} 不存在...")
    #     sys.exit()  # 退出程序

    pages = args.pages if args.pages else ""
    context = args.context if args.context else ""
    menu_tree = parse_menu_tree(pages.splitlines())
    
    values = build_unique_names(menu_tree)
    # print(values)
    output_dir: Path = outputs_dir(workspace)
    if not output_dir.exists():
        output_dir.mkdir(parents=True, exist_ok=True)

    for item in values:
        page_name = item["name"].replace("/", "-")
        page_function = item["function"]
        page_tab = item["tab"]
        
        prompt_dir = prompts_dir(workspace)
        prompt_file = Path(prompt_dir / f"prd-{page_name}.prompt.md")

        prompt = f"""
调用 skill `/solo:prd-writer`，请为管理系统页面 "{page_name}" 生成 prd 文档。
- 禁止自己手写 prd 文档，必须通过 `/solo:prd-writer` skill 执行生成。
- 将生成的 prd 文档保存在 {output_dir}/prds/{name}/{page_name}.prd.md，如果 prd 文档已存在，则重新生成并直接覆盖。
{"- prd 包含tab：" + json.dumps(page_tab, ensure_ascii=False) if len(page_tab) > 0 else ""}
{"- prd 包含功能点：" + json.dumps(page_function, ensure_ascii=False) if len(page_function) > 0 else ""}

{context}
"""
        # prompt_file.write_text(prompt, encoding='utf-8')

        print(prompt)
        # break
    # print(
    #     json.dumps(
    #         values,
    #         ensure_ascii=False,
    #         indent=2
    #     )
    # )

    