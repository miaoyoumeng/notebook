#!/usr/bin/env python3

"""
从数据存储目录读取图片地址，提交给 claude_agent_sdk 识别成 markdown 文件，
输出到 markdowns/${md5(url)}.md。

目录约定（--dir 为数据存储根目录）：
    {dir}/markdowns/    — 输入的 markdown 文件
    {dir}/logs/         — 运行日志

用法:
    uv run python scripts/uri_2_markdown.py --dir /path/to/data
"""

import json
import time
import random
import sys
import csv
import argparse
import asyncio
import os
import logging

from config import setup_logger

import hashlib
from pathlib import Path

from typing import Any, Dict, Iterable, List, Optional, Tuple, Union

def parse_row(row: str):
    """
    将 csv.reader 解析出的列表转换为 (year, region, url)
    年份转换为整数，区域和地址去除两端空白
    """
    # csv.reader 会自动去除引号，但可能保留字段前后的空格
    year_str, region, url = [field.strip() for field in row]
    year = int(year_str)  # 转为整数，若可能包含其他字符可先用正则提取
    return year, region, url
def process_todo_list(file_path: str):
    data = []
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, skipinitialspace=True)
        for row in reader:
            if not row:
                continue
            year, region, url = parse_row(row)

            data.append({
                "time": year,
                "region": region,
                "url": url
                })
    return data

async def claudeQueryURI(data: Dict, project_dir: str):
    from claude_agent_sdk import (
        AssistantMessage,
        ClaudeAgentOptions,
        ResultMessage,
        TextBlock,
        query,
    )

    if not data or not data['url'] or not data['time'] or not data['region']:
        return ""

    tools = ["Read", "Glob", "Grep", "WebFetch", "Bash"]
    prompt = f"""
## 识别图片内容

- 图片地址：{data['url']}。
- 图片地址可能是一个url，也有可能是本地磁盘地址，根据具体url情况字段识别。
- 识别远程url 图片过程中，如果需要下载图片，请把图片下载到 `/tmp/images/` 目录下。

## 识别规则

如果识别不出有效内容，就直接输出空字符串，不要靠联想内容。
如果图片中的文字上下行之间内容明显是树形的，则输出对应数量的空格，保证树形关系成立，如下面情况。
```
就业人数       18034
   第一产业    800
   第二产业    500
   第三产业    534
```

## 内容输出

- 以 markdown 格式输出。
- 仅输出识别出来的内容，禁止添加而外的话语。
- 识别不出内容，直接输出空字符串
    """
    answer = ""
    total_cost = 0.0
    try:
        async for message in query(
            prompt = prompt,
            options = ClaudeAgentOptions(
                cwd = project_dir,
                system_prompt = {"type": "preset", "preset": "claude_code"},
                allowed_tools = tools,
                permission_mode = "bypassPermissions",
                max_turns = 15,
            ),
        ):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        answer += block.text
            elif isinstance(message, ResultMessage):
                total_cost = message.total_cost_usd or 0.0
    except Exception as e:
        logger.error(f"Error claude querying base: {e}")
        answer = ""
    markdown = ""
    if answer and answer.strip():
        markdown = f"""
    
{answer}

# 上面内容是 `{data['region']} `地区 `{data['time']}` 的统计年鉴。
- 这是 `{data['region']} `地区 `{data['time']}` 的数据。
- 数据来源地址：{data['url']}

        """
    return markdown, total_cost

def markdown_writer(content: str, file_path: Union[str, Path]) -> None:
    """
    将 Markdown 内容写入磁盘文件。
    
    参数:
        content: Markdown 字符串内容
        file_path: 输出文件路径（可以是字符串或 Path 对象）
    
    异常:
        OSError: 如果无法创建目录或写入文件
    """
    dir_path = Path(file_path).parent
    if not dir_path.exists():
        logger.warning(f"{dir_path} 不存在, exit...")
        sys.exit(0)
    # 以 UTF-8 编码写入
    file_path.write_text(content, encoding='utf-8')


def log_writer(content: str, log_file: Union[str, Path]) -> None:
    """
    将 Markdown 内容写入磁盘文件。
    
    参数:
        content: Markdown 字符串内容
        file_path: 输出文件路径（可以是字符串或 Path 对象）
    
    异常:
        OSError: 如果无法创建目录或写入文件
    """
    log_path = Path(log_file)
    if not log_path.exists():
        log_path.touch(exist_ok=True)
    
    with log_path.open("a", encoding="utf-8") as f:
        print(content, file=f)


def is_line_match(file_path: str, match_str: str) -> bool:
    """
    读取文件，检查是否存在与 match_str 完全相同的行（整行匹配，非包含关系）

    参数:
        file_path: 文件路径
        match_str: 要匹配的字符串

    返回:
        True  - 存在某一行与 match_str 完全相同
        False - 不存在完全匹配的行，或文件读取失败
    """
    if not file_path.exists():
        return False
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                # 移除行尾的换行符（保留行内其他空白字符）
                stripped_line = line.rstrip('\n\r')
                if stripped_line == match_str:
                    return True
        return False
    except FileNotFoundError:
        logger.error(f"错误：文件 '{file_path}' 不存在")
        return False
    except PermissionError:
        logger.error(f"错误：没有权限读取文件 '{file_path}'")
        return False
    except Exception as e:
        logger.error(f"读取文件时发生未知错误: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(
        description = "处理指定目录下的文件/子目录列表",
        formatter_class = argparse.RawDescriptionHelpFormatter,
        epilog = "示例: %(prog)s --dir /tmp/myfolder"
    )
    parser.add_argument('--dir', required = False,
                        help = '目标目录的路径（必需）')
    
    # 支持 --dir=xx/yy 或 --dir xx/yy 两种写法
    args = parser.parse_args()

    ROOT_DIR: str = args.dir if args.dir else str(Path(os.getcwd()).resolve().parent)
    
    ROOT = Path(ROOT_DIR)
    if not ROOT.exists():
        logger.warning(f"{ROOT} 不存在,  exit...")
        sys.exit(0)
        
    MARKDOWNS_DIR:Path = Path(ROOT / "markdowns")
    if not MARKDOWNS_DIR.exists():
        MARKDOWNS_DIR.mkdir(parents=True)

    LOGS_DIR:Path = Path(ROOT / "logs")
    if not LOGS_DIR.exists():
        LOGS_DIR.mkdir(parents=True)

    TODO_LIST_FILE:Path = Path(ROOT / "todolist"/ "index.csv")
    if not TODO_LIST_FILE.exists():
        logger.warning(f'{ROOT_DIR}/todolist/index.txt 文件不存在, exit....' )
        sys.exit(0)

    todo_list = process_todo_list(str(TODO_LIST_FILE))

    total_cost = 0.0

    total = 0
    skipped = 0
    errors = 0

    logger.info(f"找到 {len(todo_list)} 个 URI 路径")

    for item in todo_list:
        md5_hash = hashlib.md5(json.dumps(item,ensure_ascii=True).encode('utf-8')).hexdigest()

        processed_urls_log = Path(LOGS_DIR / "processed_urls.log")
        if (is_line_match(processed_urls_log, md5_hash)):
            # logger.info(f'{md5_hash} 已处理， 跳过...')
            skipped += 1
            continue
        
        logger.info(f'处理文件 {md5_hash} ...')
        markdown, cost = asyncio.run(claudeQueryURI(item, ROOT_DIR))
        total_cost = total_cost + cost
        if not markdown:
            logger.warning(f'无法获取 markdown, exit....')
            errors += 1
            time.sleep(120)
            continue
        markdown_path = Path(MARKDOWNS_DIR / (md5_hash + ".md"))

        log_writer(md5_hash, processed_urls_log)
        markdown_writer(markdown, markdown_path)
        pause = random.randint(20, 25)
        time.sleep(pause)
        total += 1
        logger.info(f"\n完成: 总数{len(todo_list)}个, 处理 {total} 个, 跳过 {skipped} 个, 错误 {errors} 个, 剩余 {len(todo_list) - total - skipped - errors} 个")

    logger.info(f"\n完成: 总数{len(todo_list)}个, 成功处理处理 {total + skipped} 个, 错误 {errors} 个, 剩余 {len(todo_list) - total - skipped - errors} 个")



if __name__ == '__main__':
    logger = setup_logger(level = logging.INFO)
    main()
