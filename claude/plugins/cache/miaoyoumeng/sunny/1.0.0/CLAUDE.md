# CLAUDE.md

## 项目定位

Claude Code 插件 **wubu**：只编辑插件资产（skills、commands、hooks、agents、knowledges、scripts）。

## 关键目录说明

各目录在插件中的用途：

```
.
├── commands/                 # 斜杠命令
├── agents/                   # Claude 代理
├── skills/                   # 技能
│   └── [skill-name]/
│       └── SKILL.md          # 每个技能必需
├── hooks/
│   └── hooks.json            # 事件钩子配置
├── knowledges/               # 知识库
├── scripts/                  # 辅助脚本与工具
└── pyproject.toml            # 只声明 Python 依赖
```

- `skills/`、`commands/`、`agents/`、`hooks/` 由 Claude Code 直接加载；
- `knowledges/`、`scripts/` 不被直接加载，生效依赖上面 4 类对它们的引用；
- `pyproject.toml` 只用于声明 Python 工具链依赖，即 `scripts/`、`skills/[skill-name]/` 下 Python 脚本的依赖清单。
- `knowledges` 是提供给 `skills/`、`commands/`、`agents/` 描述需要共享的知识 。
