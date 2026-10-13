#!/usr/bin/env python3
"""
console.py — 批量提问的统一入口：按 --model 转发到对应平台的脚本

用法（在插件根目录执行）：

    uv run python scripts/console.py \
        --model=kimi --prompt="问题一" --prompt="问题二" --dir=out

`--model` 之外的参数**原样交给**平台脚本，所以各平台支持什么参数，
看它自己的帮助就是准的：

    uv run python scripts/console.py --model=qwen --help

可用平台 = 同目录下的 `chat-<平台>.py`（清单来自 config.py）。目前：

    doubao   deepseek   kimi   qwen   yuanbao

为什么要有这一层：5 个平台的脚本名和参数各有一点差异，记「哪个平台用哪个开关」
比记参数烦。这里只做「选谁」这一件事——不解释参数、不改写参数、不给参数补默认值。
多解析一层就多一处会和平台脚本对不上的地方，透传才是能长期对得上的做法。

与直接跑平台脚本的关系：完全等价。退出码照原样传出去，stdout / stderr 都继承，
进度日志和最终结果跟直接跑一模一样。
"""

from __future__ import annotations

import importlib
import subprocess
import sys
from pathlib import Path

# 同目录的公共层：先把本目录放到 sys.path 最前面，再按名字加载
sys.path.insert(0, str(Path(__file__).resolve().parent))
config = importlib.import_module("config")

HERE = Path(__file__).resolve().parent
LOG_PREFIX = "[console]"


def split_model(argv: list[str]) -> tuple[str | None, list[str]]:
    """摘出 --model 的值，其余参数原样返回（顺序不动）。

    认三种写法：`--model=kimi`、`--model kimi`、`-m kimi`。
    摘完就交出去，不做二次解析——这是「参数能完整交给平台脚本」的前提。
    """
    model: str | None = None
    rest: list[str] = []
    i = 0
    while i < len(argv):
        arg = argv[i]
        if arg in ("--model", "-m"):
            if i + 1 >= len(argv):
                sys.exit(f"{LOG_PREFIX} --model 后面要跟平台名，比如 --model=kimi")
            model = argv[i + 1]
            i += 2
            continue
        if arg.startswith("--model="):
            model = arg[len("--model=") :]
            i += 1
            continue
        if arg.startswith("-m") and not arg.startswith("--"):
            model = arg[2:]  # -mkimi 这种粘连写法
            i += 1
            continue
        rest.append(arg)
        i += 1
    return model, rest


def script_for(model: str) -> Path:
    """平台名 → 同目录下的 chat-<平台>.py；认不出就报错退出。"""
    if model not in config.PLATFORM_KEYS:
        sys.exit(
            f"{LOG_PREFIX} 不认识这个平台：{model}\n"
            f"  可用平台：{'、'.join(config.PLATFORM_KEYS)}（对应同目录的 chat-<平台>.py）"
        )
    path = HERE / f"chat-{model}.py"
    if not path.exists():
        sys.exit(f"{LOG_PREFIX} 找不到平台脚本：{path}")
    return path


def main() -> None:
    model, rest = split_model(sys.argv[1:])
    if model is None:
        sys.exit(
            f"{LOG_PREFIX} 要用 --model 指定平台，比如 --model=kimi\n"
            f"  可用平台：{'、'.join(config.PLATFORM_KEYS)}\n"
            f"  看某个平台的参数：console.py --model=<平台> --help"
        )

    path = script_for(model)
    # 用同一个解释器（uv run 之下就是 .venv 里那个）跑平台脚本，
    # 参数原样透传、标准输入输出全继承——本层不加任何包装
    proc = subprocess.run([sys.executable, str(path), *rest])
    sys.exit(proc.returncode)


if __name__ == "__main__":
    main()
