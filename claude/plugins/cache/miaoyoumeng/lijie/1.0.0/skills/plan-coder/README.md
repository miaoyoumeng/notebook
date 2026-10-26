# plan-coder

根据用户需求生成当前项目源代码的代码修改方案。

## 用途

- 接收用户的功能需求或修改请求。
- 识别源代码目录，排除测试文件。
- 输出分步骤的 Mini-PR 修改方案。

## 核心定位

spec 决定做什么，plan-coder 决定怎么做。

## 输出

- 方案文件：默认 `.claude/plan-coder-{YYYYMMDD}.md`，可按用户指定目录输出。
- 审批摘要：在对话中输出，等待用户审批后由其他 skill 执行。

## 触发

修改代码、生成方案、实现方案、代码修改计划。

## 目录结构

```text
plan-coder/
├── SKILL.md        # frontmatter 与执行指令
├── README.md       # 本文件
├── scripts/        # 确定性可执行脚本
├── references/     # 按需加载的参考文档
├── assets/         # 模板与资源文件
└── evals/
    └── evals.json  # 测试用例
```

## 维护

- 用 `/pangu:commander-skill improve plan-coder` 调整内容。
- 用 `/pangu:commander-skill evals plan-coder` 编写测试用例。
- 用 `/pangu:commander-skill score plan-coder` 做静态质量评分。
