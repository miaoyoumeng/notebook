# prd-ui-validator

校验 PRD 与 UI 设计稿、界面截图的一致性，输出差异清单。

## 使用方式

在对话中同时提供 PRD 文档和 UI 截图或设计稿，并说明需要核对的内容，例如：

```text
帮我核对这份 PRD 和 UI 截图，看看页面有没有漏掉需求。
```

技能触发后，会逐条比对功能点、页面状态、文案与交互，按严重程度输出差异清单。

## 目录结构

```text
prd-ui-validator/
├── SKILL.md        # 技能指令
├── README.md       # 使用说明
├── scripts/        # 可执行脚本
├── references/     # 参考文档
├── assets/         # 模板与资源
└── evals/
    └── evals.json  # 测试用例
```
