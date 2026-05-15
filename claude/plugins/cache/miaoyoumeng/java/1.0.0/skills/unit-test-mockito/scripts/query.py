
from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path

from config import SKILL_ROOT_DIR, PROJECT_ROOT_DIR, SCRIPTS_DIR, REFERENCES_DIR, now_iso
from markdown import get_skill_meta_data, get_skill_markdown


async def run_query(java_file: Path, meta_data: dict, markdown: str, file_back: bool) -> str:

    from claude_agent_sdk import (
        AssistantMessage,
        ClaudeAgentOptions,
        ResultMessage,
        TextBlock,
        query,
    )
    # print(f"编写单元测试: {java_file}")

    name = meta_data['name'] if ("name" in meta_data) else "java_unit_test"
    model = meta_data['model'] if ("model" in meta_data) else "sonnet"
    max_turns = meta_data['max_turns'] if ("max_turns" in meta_data) else 10
    system_prompt = meta_data['system_prompt'] if ("system_prompt" in meta_data) else {"type": "preset", "preset": "claude_code"}
    
    tools = meta_data['tools'] if ("tools" in meta_data) else ["Read", "Grep", "Glob"]
    cwd = str(PROJECT_ROOT_DIR)


# """
    test_path_str = str(java_file).replace('src/main/java', 'src/test/java').replace('.java', 'Test.java')
    # 创建目录
    Path(test_path_str).parent.mkdir(parents=True, exist_ok=True)
    prompt = f"""
## 生成 mockito 单元测试步骤，**不能跳步执行**

1. 读取源码文件路径: `{java_file}`。
2. 写入单元测试文件路径: `{test_path_str}`。
3. 写入之前，需要判断已有的单元测试内容，尽量少修改原有的单元测试。
4. 生成后，执行命令 `mvn clean test-compile` 验证语法是否正确。
5. 如果第4步执行错误，请重复执行第3、4步，直到编译成功。

## 实施规则如下：

{markdown}


"""
    print(prompt, flush=True)

    answer = ""
    try:
        async for message in query(
            prompt = prompt,
            options = ClaudeAgentOptions(
                cwd = cwd,
                model= model,
                system_prompt = system_prompt,
                allowed_tools = tools,
                permission_mode = "acceptEdits",
                max_turns = max_turns,
                # verbose = True
            ),
            # stream = True
        ):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        answer += block.text
                        print(block.text, flush=True)
            elif isinstance(message, ResultMessage):
                print(f"\n\n✅ 生成完成。结果: {message.result}", flush=True)

    except Exception as e:
        answer = f"Error querying knowledge base: {e}"

    return answer
