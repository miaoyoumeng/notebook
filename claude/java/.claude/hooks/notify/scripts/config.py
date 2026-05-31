from pathlib import Path

# 结果目录
HOOK_DIR = Path(__file__).resolve().parent.parent

# 日志文件
LOG = HOOK_DIR / "logs" / "hook.log"

# 任务元数据文件
META_FILE = HOOK_DIR / "outputs" / "task-meta.json"

# 最新结果输出
LATEST_JSON = HOOK_DIR / "outputs" / "latest.json"

# 唤醒标记文件
WAKE_FILE = HOOK_DIR / "outputs" / "pending-wake.json"

# openclaw 命令 CLI 路径
OPENCLAW_COMMAND = "openclaw"

# ---- 去重锁 ----
LOCK_FILE = HOOK_DIR / ".hook-lock"

LOCK_AGE_LIMIT = 10  # 秒，同一任务在该时间内重复触发视为重复

# ---- Claude 输出来源 ----
TASK_OUTPUT = HOOK_DIR / "output" / "task-output.txt"

FALLBACK_OUTPUT = Path("/tmp/claude-code-output.txt")

# ---- 输出长度限制 ----
MAX_OUTPUT_CHARS = 4000       # 读取的最大输出字符数
MSG_MAX_LENGTH = 800        # 消息中摘要的最大长度
WAKE_SUMMARY_CHARS = 500      # wake 文件中摘要的最大长度
