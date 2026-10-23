#!/usr/bin/env python3
"""Claude Code Stop Hook: 任务完成后通知 AGI。

触发时机: Stop (生成停止) + SessionEnd (会话结束)
支持 Agent Teams: lead 完成后自动触发
"""

import json
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from config import (
    FALLBACK_OUTPUT,
    LATEST_JSON,
    LOCK_AGE_LIMIT,
    LOCK_FILE,
    LOG,
    MAX_OUTPUT_CHARS,
    META_FILE,
    OPENCLAW_COMMAND,

    TASK_OUTPUT,
    MSG_MAX_LENGTH,
    WAKE_FILE,
    WAKE_SUMMARY_CHARS,
)


def log(msg: str) -> None:
    ts = datetime.now(timezone.utc).isoformat()
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG, "a") as f:
        f.write(f"[{ts}] {msg}\n")


def read_stdin() -> str:
    """读取 stdin 中的 JSON 数据。"""
    if sys.stdin.isatty():
        log("stdin is tty, skip")
        return ""
    try:
        return sys.stdin.read()
    except Exception:
        return ""


def parse_input(raw: str) -> dict:
    """解析 stdin JSON，提取 session_id / cwd / hook_event_name。"""
    try:
        data = json.loads(raw) if raw else {}
    except json.JSONDecodeError:
        data = {}
    return {
        "session_id": data.get("session_id", "unknown"),
        "cwd": data.get("cwd", ""),
        "event": data.get("hook_event_name", "unknown"),
    }


def is_duplicate() -> bool:
    """防重复：LOCK_AGE_LIMIT 秒内的重复触发跳过。"""
    if not LOCK_FILE.exists():
        return False
    lock_time = LOCK_FILE.stat().st_mtime
    age = time.time() - lock_time
    if age < LOCK_AGE_LIMIT:
        log(f"Duplicate hook within {int(age)}s, skipping")
        return True
    return False


def acquire_lock() -> None:
    LOCK_FILE.parent.mkdir(parents=True, exist_ok=True)
    LOCK_FILE.touch()


def read_output(cwd: str) -> str:
    """按优先级读取 Claude Code 输出。"""
    # 等待 tee 管道 flush
    time.sleep(1)

    # 来源1: task-output.txt
    if TASK_OUTPUT.exists() and TASK_OUTPUT.stat().st_size > 0:
        content = TASK_OUTPUT.read_text(errors="replace")[-MAX_OUTPUT_CHARS:]
        log(f"Output from task-output.txt ({len(content)} chars)")
        return content

    # 来源2: /tmp/claude-code-output.txt
    if FALLBACK_OUTPUT.exists() and FALLBACK_OUTPUT.stat().st_size > 0:
        content = FALLBACK_OUTPUT.read_text(errors="replace")[-MAX_OUTPUT_CHARS:]
        log(f"Output from /tmp fallback ({len(content)} chars)")
        return content

    # 来源3: 工作目录文件列表
    if cwd:
        cwd_path = Path(cwd)
        if cwd_path.is_dir():
            try:
                files = sorted(cwd_path.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True)
                names = [f.name for f in files[:20]]
                content = f"Working dir: {cwd}\nFiles: {', '.join(names)}"
                log("Output from dir listing")
                return content
            except Exception:
                pass

    log("No output source available")
    return ""


def read_metadata() -> dict:
    """读取任务元数据。"""
    if not META_FILE.exists():
        return {"task_name": "unknown", "feishu_bot": ""}
    try:
        data = json.loads(META_FILE.read_text())
        return {
            "task_name": data.get("task_name", "unknown"),
            "feishu_bot": data.get("feishu_bot", ""),
        }
    except Exception:
        return {"task_name": "unknown", "feishu_bot": ""}


def write_latest(session_id: str, cwd: str, event: str, output: str, meta: dict) -> None:
    """写入 latest.json 结果文件。"""
    result = {
        "session_id": session_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "cwd": cwd,
        "event": event,
        "output": output,
        "task_name": meta["task_name"],
        "feishu_bot": meta.get("feishu_bot", ""),
        "status": "done",
    }
    LATEST_JSON.parent.mkdir(parents=True, exist_ok=True)
    LATEST_JSON.write_text(json.dumps(result, ensure_ascii=False))
    log("Wrote latest.json")


def send_feishu(task_name: str, feishu_bot: str, output: str) -> None:
    """通过 openclaw CLI 发送 feishu 通知。"""
    if not feishu_bot or not shutil.which(OPENCLAW_COMMAND):
        return

    summary = output[-MSG_MAX_LENGTH:].replace("\n", " ")
    msg = (
        f"🤖 *Claude Code 任务完成*\n"
        f"📋 任务: {task_name}\n"
        f"📝 结果摘要:\n"
        f"```\n"
        f"{summary[:MSG_MAX_LENGTH]}\n"
        f"```"
    )

    try:

        subprocess.run(
            [
                OPENCLAW_COMMAND, "message", "send",
                "--channel", "feishu",
                "--target", feishu_bot,
                "--message", msg,
            ],
            capture_output=True,
            timeout=120,
        )
        log(f"Sent Feishu message to {feishu_bot}")
    except Exception as e:
        log(f"Feishu send failed: {e}")


def write_wake_file(task_name: str, feishu_bot: str, output: str) -> None:
    """写入 pending-wake.json 唤醒标记文件。"""
    summary = output[:WAKE_SUMMARY_CHARS].replace("\n", " ")
    wake = {
        "task_name": task_name,
        "feishu_bot": feishu_bot,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "summary": summary,
        "processed": False,
    }
    WAKE_FILE.parent.mkdir(parents=True, exist_ok=True)
    WAKE_FILE.write_text(json.dumps(wake, ensure_ascii=False))
    log("Wrote pending-wake.json")


def main() -> None:
    log("=== Notify Hook fired ===")

    # 1. 读取 stdin
    raw = read_stdin()
    info = parse_input(raw)
    log(f"session={info['session_id']} cwd={info['cwd']} event={info['event']}")

    # 2. 防重复
    if is_duplicate():
        sys.exit(0)
    acquire_lock()

    # 3. 读取输出
    output = read_output(info["cwd"])

    # 4. 读取任务元数据
    meta = read_metadata()
    log(f"Meta: task={meta['task_name']} group={meta['feishu_bot']}")

    # 5. 写入结果 JSON
    write_latest(info["session_id"], info["cwd"], info["event"], output, meta)

    # 6. 发送 Feishu 通知
    send_feishu(meta["task_name"], meta["feishu_bot"], output)

    # 7. 写入 wake 标记
    write_wake_file(meta["task_name"], meta["feishu_bot"], output)

    log("=== Notify Hook completed ===")
    sys.exit(0)


if __name__ == "__main__":
    main()
