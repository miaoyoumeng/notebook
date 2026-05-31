# notify

Claude Code Stop Hook — 任务完成后通知 AGI，支持 Telegram 消息推送和 wake 标记。

## 使用

```bash
uv run python notify/scripts/run.py
```

该脚本从 stdin 读取 Claude Code hook 传入的 JSON 数据：

```json
{
  "session_id": "abc123",
  "cwd": "/path/to/project",
  "hook_event_name": "Stop"
}
```

## Claude Code 配置

在 Claude Code 的 `settings.json` 中配置 hooks：

```json
{
  "hooks": {
    "Stop": {
      "hooks": [
        {
          "type": "command",
          "command": "uv run python notify/scripts/run.py",
          "timeout": 15
        }
      ]
    },
    "SessionEnd": {
      "hooks": [
        {
          "type": "command",
          "command": "uv run python notify/scripts/run.py",
          "timeout": 15
        }
      ]
    }
  }
}
```

## 工作流程

1. 读取 stdin 中的 hook 事件数据（session_id / cwd / event）
2. 防重复：30 秒内同一任务只处理一次
3. 从多个来源读取 Claude Code 输出（task-output.txt → /tmp 备用 → 工作目录文件列表）
4. 读取任务元数据（task_name / telegram_group）
5. 写入 `latest.json` 结果文件
6. 若配置了 Telegram 群组，通过 `openclaw` 发送通知
7. 写入 `pending-wake.json` 唤醒标记文件

## 配置

所有可配置的路径和参数集中管理在 `notify/scripts/config.py` 中：

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `RESULT_DIR` | 结果存储目录 | `/home/ubuntu/clawd/data/claude-code-results` |
| `LOCK_AGE_LIMIT` | 防重复时间窗口（秒） | `30` |
| `MAX_OUTPUT_CHARS` | 读取的最大输出字符数 | `4000` |
| `TELEGRAM_MSG_MAX` | Telegram 消息摘要长度 | `800` |
| `WAKE_SUMMARY_CHARS` | wake 文件摘要长度 | `500` |
