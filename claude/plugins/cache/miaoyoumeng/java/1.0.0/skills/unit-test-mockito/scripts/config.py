from pathlib import Path
from datetime import datetime, timezone

SCRIPTS_DIR = Path(__file__).resolve().parent

SKILL_ROOT_DIR = SCRIPTS_DIR.parent

PROJECT_ROOT_DIR = SKILL_ROOT_DIR.parent.parent.parent

REFERENCES_DIR = Path(SKILL_ROOT_DIR / "references")



# 以下是时间
TIMEZONE = "Asia/Shanghai"

def now_iso() -> str:
    """Current time in ISO 8601 format."""
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")

def today_iso() -> str:
    """Current date in ISO 8601 format."""
    return datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d")