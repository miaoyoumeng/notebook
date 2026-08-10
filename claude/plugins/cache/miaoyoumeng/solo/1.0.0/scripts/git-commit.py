#!/usr/bin/env python3
#-*- coding:utf-8 -*-
import sys
import json
import argparse
import asyncio
from pathlib import Path
import os
import subprocess

def find_git_root(workspace: Path) -> str:
    """向下查找包含 .git 的目录，找到第一个匹配项即返回，最多搜索 3 层"""
    base_depth = len(workspace.parts)
    for git_dir in workspace.rglob('.git'):
        if git_dir.is_dir() and len(git_dir.parent.parts) - base_depth <= 3:
            return git_dir.parent
    return None

async def run_query(git_msg: str) -> str:
    from claude_agent_sdk import (
        AssistantMessage,
        ClaudeAgentOptions,
        ResultMessage,
        TextBlock,
        query,
    )
    prompt = f"""请这下面的内容整理适合git commit 的信息。内容如下：
{git_msg}
git commit模板整理后的模板如下：
```
- 实现了 xxx 功能
- ……
- 实现了 yyy 功能
```
最终以markdown方式输出，最多3行。
    """
    answer = ""
    try:
        async for message in query(
            prompt = prompt,
            options = ClaudeAgentOptions(
                cwd=str(Path.cwd()),
                system_prompt = {"type": "preset", "preset": "claude_code"},
                allowed_tools = ["Read", "Glob", "Grep"],
                permission_mode="acceptEdits",
                max_turns = 30,
            ),
        ):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        answer += block.text
            elif isinstance(message, ResultMessage):
                cost = message.total_cost_usd or 0.0
    except Exception as e:
        print(f"Error querying knowledge base: {e}")
        answer = ""

    return answer

def get_commit_message(workspace: Path):
    """
    生成 commit message。
    注意：在 Stop hook 中，Claude 刚刚完成了任务。
    这里我们利用一个巧妙的机制：让脚本提示 Claude 需要补充信息，
    或者你可以通过读取上一步的对话历史来提取。
    为了简单可靠，这里我们让脚本自动生成一个基础信息，
    或者你可以在此处调用大模型 API 总结 git diff。
    这里演示直接读取 git diff 的简略信息作为 commit message。
    .claude/logs/develop_command_git.md
    """
    # 创建一个 Path 对象
    git_commit_message_file = workspace / ".claude" / "logs"/ "develop_command_git.md"

    # 判断文件是否存在
    git_commit_message = False
    if git_commit_message_file.exists():
        file_content = git_commit_message_file.read_text().strip()
        if file_content:
            git_commit_message = True

    if git_commit_message:
        message = git_commit_message_file.read_text().strip()
        return message
    else:
        try:
            # 获取暂存区或工作区的变更简述
            result = subprocess.run(['git', 'diff', '--cached', '--stat'], capture_output=True, text=True)
            if result.stdout:
                return f"feat: auto commit after commander-admin develop\n\n{result.stdout}"
            
            # 如果暂存区为空，说明还没 add，先获取工作区的变更
            result = subprocess.run(['git', 'diff', '--stat'], capture_output=True, text=True)
            return f"feat: auto commit after commander-admin develop\n\n{result.stdout}"
        except Exception as e:
            return "feat: auto commit after commander-admin develop"

def main(workspace: Path):
    # 1. 校验目录参数
    if not workspace:
        print(" --dir params has not valid value...")
        return
    if not workspace.is_dir():
        print(f"dir {workspace} not exist...")
        return

    # 2. 向下查找 .git 目录
    git_root = find_git_root(workspace)
    if not git_root:
        print(f"git .git dir not found under {workspace}...")
        return

    # 3. 检查是否有变更
    os.chdir(git_root)
    result = subprocess.run(['git', 'status', '-s'], capture_output=True, text=True)
    if not result.stdout.strip():
        print("git nothing to commit ....")
        return

    # 获取 commit message
    command_msg = get_commit_message(workspace)
    # print(f"command_msg:\n{command_msg}")
    # commit_msg = asyncio.run(run_query(command_msg))

    print(f"git commit_msg:\n{command_msg}")

    # 4. 提交变更
    print("git commit task...")
    subprocess.run(['git', 'add', '-A'])
    subprocess.run(['git', 'commit', '-m', command_msg], stderr=subprocess.DEVNULL)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description = "处理指定 bugs 目录下的包含菜单 markdown 文件",
        formatter_class = argparse.RawDescriptionHelpFormatter,
        epilog = "示例: %(prog)s --workspace=<workspace>"
    )
    parser.add_argument('--workspace', required = True,
         help = '工作目录目录的路径（非必需）')
    args = parser.parse_args()

    workspace: Path = Path(args.workspace if args.workspace else str(Path.cwd()))
    print("---------git commit excute---------")
    main(workspace)
    print("---------git commit done---------")

