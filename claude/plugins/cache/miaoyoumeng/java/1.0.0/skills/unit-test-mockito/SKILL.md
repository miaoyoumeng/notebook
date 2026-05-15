---
name: unit-test-mockito
description: 为 Java 项目生成自动化单元测试（JUnit 4 + Mockito）。当用户要求编写单元测试、生成测试用例或提升测试覆盖率时使用。
paths:
  - "**/*/src/test/java/**/*/*Test.java"
---


# Java Unit Test Skill

## 触发条件

当用户提出以下需求时激活本技能（包含同义表达）：

- 帮我写单元测试 / 为这个类写测试 / 生成测试用例
- 提升测试覆盖率 / 补齐测试 / 覆盖率不达标
- junit test / mockito test / unit test


### 🧠 使用规则
scope=file → 必须提供 path
scope=dir → 必须提供 path

### 执行规则

1. 单文件生成单元测试，根据指定的单个 java，执行如下脚本
```shell
uv run python .claude/skills/unit-test-mockito/scripts/main.py --scope file --path /xxx/yyy/zzz.java
```
2. 根据指定的 maven 模块生成对应模块下所有 java 源码的的单元测试，执行如下脚本
```shell
uv run python .claude/skills/unit-test-mockito/scripts/main.py --scope dir  --path /xxx/yyy/
```

3. **严格遵守“只处理一个文件”的原则**。完成后，明确告知结果，再处理下一个文件，**禁止**在主 Agent 启动 subgent 去执行单元测试。

4. 写完单元测试，离开执行单元测试 `mvn test ……`，验证编写结果。

5. 验证通过后，再继续编写下一个文件的单元测试。