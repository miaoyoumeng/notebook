# java-tdd

基于 JUnit 5 + Mockito + Spring Boot Test 的 Java TDD 单元测试技能。

## 何时使用

用户要求编写单元测试、实践 TDD、修复 bug、提升测试覆盖率或生成 mock/stub 时使用，例如：

- `给 PriceCalculator 写单元测试，用 TDD`
- `这是个 bug，先写个失败测试再修`
- `CompanyService 覆盖率太低了，补一下 mock 测试`
- `用 Mockito mock 掉用户仓库`

TDD 铁律：没有失败测试之前禁止写产品代码。

不要用于集成测试、端到端测试、性能压测或非 Java 项目。

## 目录结构

```text
java-tdd/
├── SKILL.md          # frontmatter + 指令正文
├── README.md         # 本文件
├── scripts/          # 确定性脚本
├── references/       # 按需加载的参考文档
├── assets/           # 模板与资源
└── evals/
    └── evals.json    # 测试用例
```

## 使用方式

在 Claude Code 中直接提出 Java 单元测试或 TDD 需求即可触发。指令正文见 `SKILL.md`。
