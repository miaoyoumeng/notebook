#!/usr/bin/env python3
#-*- coding:utf-8 -*-
import re
import json
import os
import sys
from pathlib import Path
import argparse
from config import KNOWLEDGES_DIR, outputs_dir, inputs_dir

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description = "初始化项目 CLAUDE 工作环境",
        formatter_class = argparse.RawDescriptionHelpFormatter,
        epilog = "示例: %(prog)s --workspace=<workspace>  --name=<name>"
    )
    parser.add_argument('--workspace', required = False,
         help = '工作目录目录的路径（非必需）')

    args = parser.parse_args()
    workspace:Path = Path(args.workspace if args.workspace else str(Path.cwd()))

    """复制 CLAUDE.md 文件"""

    source_claude = Path(KNOWLEDGES_DIR / "CLAUDE.md")

    if not source_claude.is_file(): 
        print(f"{source_claude} 文件不存在...")
        sys.exit(1)
    target_claude = Path(workspace / "CLAUDE.md")
    if not target_claude.is_file():
        print("复制 CLAUDE.md 文件")
        source_claude.copy(target_claude, preserve_metadata=True)

    """构建工作需要的目录结果"""

    input_dir: Path = inputs_dir(workspace)
    if not input_dir.exists():
        print(f"创建 {input_dir} 目录")
        input_dir.mkdir(parents=True, exist_ok=True)

    output_dir: Path = outputs_dir(workspace)
    if not output_dir.exists():
        print(f"创建 {output_dir} 目录")
        output_dir.mkdir(parents=True, exist_ok=True)
