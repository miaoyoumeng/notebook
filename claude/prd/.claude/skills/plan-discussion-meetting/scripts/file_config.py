from pathlib import Path
from datetime import datetime, timezone


ROOT_DIR = Path(__file__).resolve().parent.parent

PROJECT_ROOT_DIR = ROOT_DIR.parent.parent.parent

REFERENCES_DIR = Path(ROOT_DIR / "references")

THINKING_DIR = Path(PROJECT_ROOT_DIR / "tingking")

OUTPUT_DIR = Path(PROJECT_ROOT_DIR / "output")


# 以下是时间
TIMEZONE = "Asia/Shanghai"

def now_iso() -> str:
    """Current time in ISO 8601 format."""
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")

def today_iso() -> str:
    """Current date in ISO 8601 format."""
    return datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d")