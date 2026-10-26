# typescript-clean

基于 Robert C. Martin《Clean Code》原则，把能运行的 TypeScript 代码整理为整洁代码，覆盖命名、函数、注释、格式化、对象、错误处理、测试、类与代码臭味。

## 何时使用

用户要求清理、重构、审查或整理 TypeScript 代码时使用，例如：

- `审查 src/services/order-service.ts，按 Clean Code 原则给出修改建议`
- `重构这个 60 行的 TypeScript 函数`
- `这段代码的命名有什么问题？帮我改进`
- `清理这个文件里的代码臭味`

不用于改变功能行为、修复业务缺陷或处理生成代码。

## 核心维度

| 维度 | 覆盖内容 |
|------|---------|
| 命名 | 揭示意图、可搜索、避免误导 |
| 函数 | 短小、单一职责、单一抽象层级、无副作用、参数 ≤ 2 |
| 注释 | 用代码表达意图，删除坏注释 |
| 格式化 | 报纸隐喻、垂直密度、声明靠近使用 |
| 对象 | 数据抽象、得墨忒耳法则、DTO |
| 错误处理 | 异常替代返回码、不返回 null、不传入 null |
| 测试 | TDD 定律、FIRST 原则、测试行为而非实现 |
| 类 | 单一职责、按职责拆分大类 |
| 代码臭味 | 僵硬性、脆弱性、不可移植性、粘滞性、不必要的复杂性、重复 |

## 目录结构

```text
typescript-clean/
├── SKILL.md          # frontmatter + 指令正文
├── README.md         # 本文件
├── scripts/          # 确定性可执行脚本（当前为空）
├── references/       # 按需加载的参考文档
│   ├── naming-conventions.md
│   ├── functions-and-comments.md
│   ├── error-handling-and-testing.md
│   └── code-smells.md
├── assets/           # 模板与资源文件（当前为空）
└── evals/
    └── evals.json    # 测试用例
```

## 使用方式

在 Claude Code 中提出 TypeScript 代码整理需求即可触发。执行流程、验证命令与检查表见 `SKILL.md`；按需加载 `references/` 中的参考文档。
