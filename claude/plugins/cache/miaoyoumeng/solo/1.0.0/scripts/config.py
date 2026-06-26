from pathlib import Path
import sys
from datetime import datetime, timezone


PLUTIN_ROOT_DIR = Path(__file__).resolve().parent.parent

KNOWLEDGES_DIR = Path(PLUTIN_ROOT_DIR / "knowledges")

HOOKS_DIR = Path(PLUTIN_ROOT_DIR / "hooks")

TEMPLATES_DIR = Path(PLUTIN_ROOT_DIR / "templates")

def inputs_dir(project_dir: Path) -> Path:
    """定义输入参数的文件目录路径
    Args:
        project_dir (Path): 项目目录。

    Returns:
        Path: 获取输入目录的路径
    """
    input_dir = Path(project_dir / "references")
    if not input_dir.exists() or not input_dir.is_dir():
        print(f"references 目录：{input_dir} 不存在...")
        """退出程序."""
        sys.exit()
    return input_dir

def user_story_dir(project_dir: Path,  sysName: str)-> Path:
    if not bool(sysName) or not bool(sysName.strip()):
        print(f"系统：{sysName} 不存在...")
        sys.exit()

    userstory_dir = Path(inputs_dir(project_dir) / "user-story" / sysName)
    if not userstory_dir.exists():
        userstory_dir.mkdir(parents=True, exist_ok=True)
    return userstory_dir

def outputs_dir(project_dir: Path) -> Path:

    output_dir = Path(project_dir / "outputs")
    if not output_dir.exists() or not output_dir.is_dir():
        print(f"outputs 目录：{output_dir} 不存在...")
        sys.exit()
    return output_dir

def logs_dir(project_dir: Path) -> Path:
    return Path(project_dir / "logs")

def prompts_dir(project_dir: Path) -> Path:
    prompt_dir = Path(outputs_dir(project_dir) / "prompts")
    if not prompt_dir.exists():
        prompt_dir.mkdir(parents=True, exist_ok=True)
    return prompt_dir

def prds_dir(project_dir: Path,  sysName: str) -> Path:
    """prd 路径"""
    if not bool(sysName) or not bool(sysName.strip()):
        print(f"系统：{sysName} 不存在...")
        sys.exit()

    prd_dir = Path(outputs_dir(project_dir) / "prds" / sysName)
    if not prd_dir.exists():
        prd_dir.mkdir(parents=True, exist_ok=True)
    return prd_dir

def bugs_dir(project_dir: Path,  sysName: str) -> Path:
    """prd 路径"""
    if not bool(sysName) or not bool(sysName.strip()):
        print(f"系统：{sysName} 不存在...")
        sys.exit()

    bug_dir = Path(outputs_dir(project_dir) / "bugs" / sysName)
    if not bug_dir.exists():
        bug_dir.mkdir(parents=True, exist_ok=True)
    return bug_dir

