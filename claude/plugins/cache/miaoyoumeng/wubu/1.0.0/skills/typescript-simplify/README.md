# typescript-simplify

在不改变行为的前提下简化和清理已有 TypeScript 代码。

## 何时使用

用户明确要求简化、清理、降低复杂度或去嵌套 TypeScript/JavaScript 代码时使用，例如：

- `简化 src/auth/session.ts`
- `这段嵌套太深，帮我清理一下`
- `reduce complexity in this file`

不要用于修改行为、修复缺陷或处理生成代码。

## 目录结构

```text
typescript-simplify/
├── SKILL.md          # frontmatter + 指令正文
├── README.md         # 本文件
├── references/       # 按需加载的参考文档
└── evals/
    ├── evals.json    # 测试用例
    └── fixtures/     # 用例输入文件
```

## 使用方式

在 Claude Code 中直接提出简化需求即可触发。指令正文见 `SKILL.md`，模式与风险参考见 `references/simplification-patterns.md`。
