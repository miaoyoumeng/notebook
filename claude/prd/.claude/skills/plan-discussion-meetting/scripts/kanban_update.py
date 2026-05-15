#!/usr/bin/env python3
"""
看板任务更新工具 - 供各省部 Agent 调用

本工具操作 data/tasks_source.json（JSON 看板模式）。
如果您已部署 edict/backend（Postgres + Redis 事件总线模式），
请使用 edict/backend API 端点代替本脚本，或运行迁移脚本：
  python3 edict/migration/migrate_json_to_pg.py

两种模式互相独立，数据不会自动同步。

用法:
  # 新建任务（收旨时）
  uv run python .claude/skills/plan-discussion-meetting/scripts/kanban_update.py create JJC-20260223-012 "任务标题" Zhongshu 中书省 中书令

  # 更新状态
  uv run python .claude/skills/plan-discussion-meetting/scripts/kanban_update.py state JJC-20260223-012 Menxia "规划方案已提交门下省"

  # 添加流转记录
  uv run python .claude/skills/plan-discussion-meetting/scripts/kanban_update.py flow JJC-20260223-012 "中书省" "门下省" "规划方案提交审核"

  # 完成任务
  uv run python .claude/skills/plan-discussion-meetting/scripts/kanban_update.py done JJC-20260223-012 "/path/to/output" "任务完成摘要"

  # 添加/更新子任务 todo
  uv run python .claude/skills/plan-discussion-meetting/scripts/kanban_update.py todo JJC-20260223-012 1 "实现API接口" in-progress
  uv run python .claude/skills/plan-discussion-meetting/scripts/kanban_update.py todo JJC-20260223-012 1 "" completed

  # 🔥 实时进展汇报（Agent 主动调用，频率不限）
  python3 kanban_update.py progress JJC-20260223-012 "正在分析需求，拟定3个子方案" "1.调研技术选型|2.撰写设计文档|3.实现原型"
"""
import datetime
import json, pathlib, sys, subprocess, logging, os, re
from file_config import PROJECT_ROOT_DIR, now_iso

# 每个命令对应的参数个数 105607.50     66.93 
_CMD_MIN_ARGS = {
    'create': 6, 
    'state': 3, 
    'flow': 5, 
    'done': 2, 
    'block': 3, 
    'confirm': 3,
    'todo': 4, 
    'progress': 3,
    'memory': 4, 
    'task-memo': 4, 
    'shared-memo': 3,
    'delegate': 5, 
    'delegate-result': 3,
}

if __name__ == '__main__':
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(0)
    cmd = args[0]
    if cmd in _CMD_MIN_ARGS and len(args) < _CMD_MIN_ARGS[cmd]:
        print(f'错误："{cmd}" 命令至少需要 {_CMD_MIN_ARGS[cmd]} 个参数，实际 {len(args)} 个')
        print(__doc__)
        sys.exit(1)
    # 越权检测：推断当前 Agent 身份，校验是否有权执行该命令
    _check_permission(_infer_agent_id_from_runtime(), cmd)
    if cmd == 'create':
        cmd_create(args[1], args[2], args[3], args[4], args[5], args[6] if len(args)>6 else None)
    
    else:
        print(__doc__)
        sys.exit(1)
