#!/usr/bin/env python3
"""commander-git.py — 维护自定义 claude command 执行后的 git 版本记录。

用法:
    uv run commander-git.py --workspace=/path/to/ws --commander=my-command [--sub-path=src/views]

功能:
    1. 从 <workspace>/.claude/log-commander-git.md 读取该 commander 上次记录的 git 版本
    2. 获取当前 git HEAD 版本号
    3. 计算两次版本间的文件变更 diff（首次执行则列出当前所有文件）
    4. 更新记录文件，写入最新的 git 版本号

记录格式: <commander>=<git-hash>
"""

import argparse
import subprocess
import sys
from pathlib import Path


LOG_FILENAME = "log-commander-git.md"


def get_log_path(workspace: str) -> Path:
    """返回日志文件的完整路径。"""
    return Path(workspace) / ".claude" / "logs" / LOG_FILENAME


def run_git(cwd: str, args: list[str]) -> str:
    """执行 git 命令并返回标准输出，失败则终止脚本。"""
    result = subprocess.run(
        ["git", "-c", "core.quotePath=false"] + args,
        cwd=cwd,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"Git error: {result.stderr.strip()}", file=sys.stderr)
        sys.exit(1)
    return result.stdout.strip()


def get_current_hash(workspace: str) -> str:
    """获取当前 git HEAD 的完整哈希值。"""
    return run_git(workspace, ["rev-parse", "HEAD"])


def read_recorded_hash(log_path: Path, commander: str) -> str | None:
    """从记录文件中读取指定 commander 上次记录的 git hash。"""
    if not log_path.exists():
        return None

    with open(log_path) as f:
        for line in f:
            line = line.strip()
            if line.startswith(f"{commander}="):
                parts = line.split("=", 1)
                if len(parts) == 2:
                    return parts[1]
    return None


def update_record(log_path: Path, commander: str, new_hash: str) -> None:
    """更新记录文件：替换已有行或追加新行。"""
    log_path.parent.mkdir(parents=True, exist_ok=True)

    lines = []
    updated = False
    if log_path.exists():
        with open(log_path) as f:
            for line in f:
                stripped = line.rstrip("\n")
                if stripped.startswith(f"{commander}=") and not updated:
                    lines.append(f"{commander}={new_hash}")
                    updated = True
                else:
                    lines.append(stripped)

    if not updated:
        lines.append(f"{commander}={new_hash}")

    with open(log_path, "w") as f:
        f.write("\n".join(lines) + "\n")


def compute_diff(workspace: str, old_hash: str | None, current_hash: str, sub_path: str | None) -> str:
    """计算两次 git 版本间的 diff。

    首次执行（old_hash 为空）时：
        - sub-path 指定：列出该路径下所有 tracked 文件
        - sub-path 为空：列出仓库所有 tracked 文件
    否则：
        - 使用 git diff 计算 old_hash 到 current_hash 的差异
    """
    if old_hash is None:
        # 首次执行：列出当前 tracked 文件
        diff_args = ["ls-files"]
        if sub_path:
            diff_args += ["--", sub_path]
        result = run_git(workspace, diff_args)
        if result:
            return f"[首次执行] 当前 tracked 文件列表:\n{result}"
        return "[首次执行] 暂无 tracked 文件"
    elif old_hash == current_hash:
        return "无变更（git 版本未变化）"
    else:
        diff_args = ["diff", "--stat", f"{old_hash}..{current_hash}"]
        if sub_path:
            diff_args += ["--", sub_path]
        result = run_git(workspace, diff_args)
        if result:
            return result
        return f"版本 {old_hash[:7]} → {current_hash[:7]} 无文件变更（在指定 sub-path 下）"


def main() -> None:
    parser = argparse.ArgumentParser(description="维护自定义 claude command 执行后的 git 版本记录")
    parser.add_argument("--workspace", required=True, help="项目 workspace 目录（必选）")
    parser.add_argument("--commander", required=True, help="自定义 claude commander 名称（必选）")
    parser.add_argument("--sub-path", default=None, help="git diff 的限定路径（可选）")

    args = parser.parse_args()

    # 确保 workspace 目录存在
    workspace = Path(args.workspace).resolve()
    if not workspace.is_dir():
        print(f"Error: workspace 目录不存在: {workspace}", file=sys.stderr)
        sys.exit(1)

    log_path = get_log_path(str(workspace))
    commander = args.commander
    sub_path = args.sub_path

    # 1. 获取当前 git HEAD
    current_hash = get_current_hash(str(workspace))

    # 2. 读取之前记录的版本号
    old_hash = read_recorded_hash(log_path, commander)

    # 3. 计算 diff
    diff_output = compute_diff(str(workspace), old_hash, current_hash, sub_path)

    # 4. 更新记录文件
    update_record(log_path, commander, current_hash)

    # 5. 输出结果
    old_display = old_hash[:7] if old_hash else "(首次)"
    print(f"Commander: {commander}")
    print(f"Git 版本: {old_display} → {current_hash[:7]}")
    if sub_path:
        print(f"Sub-path: {sub_path}")
    print(f"日志文件: {log_path}")
    print(f"--- 变更摘要 ---")
    print(diff_output)


if __name__ == "__main__":
    main()
