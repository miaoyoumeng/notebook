# clean-typescript

基于 Robert C. Martin《Clean Code》原则，将"能运行的代码"转化为"整洁的代码"。开发语言：TypeScript。

> "代码如果可以被除原作者之外的开发者阅读和改进，那它就是整洁的。" — Grady Booch

## 使用示例

```
审查这段 TypeScript 代码并提出改进建议
```

```
重构这个 60 行的 TypeScript 函数
```

```
这段代码的命名有什么问题？帮我改进
```

## 核心维度

| 维度 | 覆盖内容 |
|------|---------|
| 命名 | 揭示意图、可搜索、避免误导 |
| 函数 | 短小、单一职责、无副作用、参数 ≤ 2 |
| 注释 | 用代码表达意图、删除坏注释 |
| 格式化 | 报纸隐喻、垂直密度 |
| 对象 | 数据抽象、得墨忒耳法则 |
| 错误处理 | 异常替代返回码、不返回 null |
| 测试 | TDD 三定律、FIRST 原则 |
| 代码臭味 | 僵硬性、脆弱性、复杂性、重复 |

## 参考资料

- [naming-conventions.md](references/naming-conventions.md) — TypeScript 命名规范
- [functions-and-comments.md](references/functions-and-comments.md) — 函数设计与注释
- [error-handling-and-testing.md](references/error-handling-and-testing.md) — 错误处理与测试
- [code-smells.md](references/code-smells.md) — 代码臭味与重构
