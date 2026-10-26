# java-it

为 Java 项目编写、运行与维护集成测试。

## 何时使用

用户要求给 Java 服务或模块补集成测试、搭建集成测试环境、排查集成测试失败时使用，例如：

- `给 UserService 写个集成测试`
- `这个 Spring Boot 接口的集成测试一直失败，帮我看看`
- `用 Testcontainers 跑一下订单流程的 integration test`

不要用于纯单元测试、性能压测或非 Java 项目。

## 目录结构

```text
java-it/
├── SKILL.md          # frontmatter + 指令正文
├── README.md         # 本文件
├── scripts/          # 确定性脚本
├── references/       # 按需加载的参考文档
├── assets/           # 模板与资源
└── evals/
    └── evals.json    # 测试用例
```

## 使用方式

在 Claude Code 中直接提出 Java 集成测试需求即可触发。指令正文见 `SKILL.md`。
