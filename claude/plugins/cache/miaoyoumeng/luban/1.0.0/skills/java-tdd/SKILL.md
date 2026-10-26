---
name: java-tdd
description: "基于 JUnit 5、Mockito 与 Spring Boot Test 的 Java TDD 单元测试：先写失败测试，再写最小实现，最后重构，覆盖 mock/stub 设计、测试命名与断言、覆盖率提升与缺陷修复。当用户要求编写单元测试、实践测试驱动开发、为新功能或缺陷补测试、提升测试覆盖率、生成 mock/stub 时使用，包括「写个单元测试」「先写测试再实现」「TDD 一下」「提高覆盖率」「mock 掉这个依赖」等说法；不要用于集成测试、端到端测试、性能压测或非 Java 项目。"
---

# java-tdd

## 概述

Java 17 + Spring Boot 项目的 TDD 工作流，基于 JUnit 5、Mockito、AssertJ 与 Spring Boot Test。

铁律：没有失败的测试之前，禁止写产品代码。已经写了产品代码，删除后从测试重新开始。

本技能处理单元测试与 TDD 流程。

## 上下文层级

- 本文件常驻上下文，包含工作流、判定标准与脚本用法。
- `references/tdd-best-practices.md`：RED/GREEN 验证细节、AIR 与 BCDE 原则、验证清单、合理化借口、红旗、Maven 命令。进入任一阶段前按需加载。
- `references/testing-anti-patterns.md`：写或改测试、添加 mock、在生产类上添加方法时加载。
- `references/framework-guide.md`：编写 Service、Controller、Mapper、Redis、Testcontainers 测试时加载。
- `assets/sample_input.json`：脚本输入的字段示例。

## 使用时机

适用于新功能、Bug 修复、重构、行为变更。

一次性原型、生成的代码、配置文件不进入 TDD 流程。用户明确要求跳过 TDD 时，说明未走 TDD 流程，并停止使用本技能。

不适用于集成测试、端到端测试、性能压测、非 Java 项目。

## 编码四原则

1. 测试先行：先写能失败的测试，再确认它因功能缺失而失败。
2. 最小实现：只写让当前测试通过的最少代码。
3. 验证真实行为：断言业务结果，不断言 mock 是否被调用。
4. 保持绿色：每次改动后全部测试通过且输出干净。

## 流程

### 1. RED：写失败测试

写一个最小的测试，描述期望行为。

- 一个测试一个行为；名称包含 "and" 时拆开。
- 测试名描述预期行为：`should<行为>_when<条件>`。
- 优先使用真实代码，mock 只在不可避免时使用。
- 单元测试放在 `src/test/java`，目录镜像生产代码，命名 `XxxTest.java`。

```java
@Test
void shouldRejectZeroQuantity_whenAddItem() {
    Cart cart = new Cart();

    assertThrows(IllegalArgumentException.class,
        () -> cart.addItem(new CartItem("sku-1", 0)));
}
```

完整规则见 `references/tdd-best-practices.md` 的 `RED 阶段`。

### 2. 验证 RED

运行目标测试：

```bash
mvn test -Dtest=CartTest
```

确认：

- 测试失败，而不是意外通过；编译失败也属于测试失败。
- 失败信息符合预期。
- 失败原因是功能缺失，而不是拼写或语法错误。

测试通过说明测的是已存在行为，修改测试。编译失败时先确认由功能缺失导致，再进入 GREEN。

### 3. GREEN：最小实现

写能让测试通过的最少代码。不添加功能，不重构其他代码，不引入超出测试范围的改进。临时重复代码可以接受。

详细规则见 `references/tdd-best-practices.md` 的 `GREEN 阶段`。

### 4. 验证 GREEN

再次运行目标测试，确认：

- 测试通过。
- 其他测试依然通过。
- 输出干净，无 error、无 warning。

测试失败时修改代码，不修改测试。其他测试失败时立即修复。

### 5. REFACTOR：清理

测试通过后消除重复、改进命名、提取 helper。每次小重构后重新运行测试。

保持测试绿色，不添加行为。

### 6. 循环

完成一个 RED-GREEN-REFACTOR 循环再开始下一个。每次 GREEN 后提交。

## 代码分析

### 测试质量

| 质量 | 合格 | 不合格 |
|------|------|--------|
| 最小 | 一个测试一个行为 | 名称含多个 and 的复合测试 |
| 清晰 | 名称描述行为 | `test1()` |
| 体现意图 | 展示期望的 API | 掩盖代码应该做什么 |

### 目录与命名

测试类放在 `src/test/java`，包路径镜像 `src/main/java`。单元测试（mock 外部依赖）命名 `XxxTest.java`，集成测试命名 `XxxIT.java`。Mapper 等数据层测试是否需要编写，按项目约定判断。

### 覆盖率阈值

| 类型 | 阈值 |
|------|------|
| 行覆盖率 | 80%+ |
| 分支覆盖率 | 75%+ |
| 方法覆盖率 | 90%+ |
| 关键路径（认证、支付、数据校验） | 100% |

核心模块的语句覆盖率与分支覆盖率均需达到 100%。

### Mock 策略

写 mock 之前回答三个问题：

1. 真实方法有什么副作用？
2. 测试是否依赖这些副作用？
3. 是否完全理解测试需要什么？

依赖副作用时，在更低层 mock 真正慢或外部的操作。不确定时，先用真实实现运行测试，观察实际需要，再在正确层级添加最小 mock。

Mock 的完整门控函数与五种反模式见 `references/testing-anti-patterns.md`。Mockito 的 stubbing、ArgumentCaptor、InOrder、Spy 用法见 `references/framework-guide.md` 的 `常用 Mockito 模式`。

## 验证清单

完成工作前逐项确认：

- [ ] 每个新方法都有测试
- [ ] 亲眼看过每个测试失败
- [ ] 每个测试因预期原因失败（功能缺失，不是笔误）
- [ ] 每个测试用最小代码通过
- [ ] 全部测试通过
- [ ] 输出干净，无 error、无 warning
- [ ] 测试使用真实代码，mock 只在不可避免时使用
- [ ] 边界场景与错误输入已覆盖（BCDE）
- [ ] 测试自动、独立、可重复（AIR）

任一项未完成，视为未完成 TDD，回到 RED。

完整清单见 `references/tdd-best-practices.md` 的 `验证清单`。

## 危险信号

出现以下任一情况，删除产品代码，从 RED 重新开始：

- 在测试之前写产品代码。
- 实现之后补测试。
- 测试立即通过。
- 说不清测试为什么失败。
- 说“以后再补测试”。
- 保留已写代码“作参考”，或让测试适配已有实现。
- 在生产类上添加仅测试使用的方法。
- 只验证 mock 调用，没有真实业务结果断言。
- 用 `System.out` 代替 assert 做验收。
- 测试之间互相调用或依赖执行顺序。
- 以“就这一次”“这次不一样”为由跳过 TDD。

完整红旗清单见 `references/tdd-best-practices.md` 的 `红旗`，mock 相关红旗见 `references/testing-anti-patterns.md` 的 `红旗`。

## 理由辩解

| 常见理由 | 判断 |
|----------|------|
| 太简单，不需要测试 | 简单代码也会出错，写测试只需几十秒。 |
| 之后补测试 | 立即通过的测试无法证明它测的是正确行为。 |
| 已经手动测试过 | 手动验证无记录、不可重跑，也证明不了边界。 |
| 删除已写代码太浪费 | 保留未验证代码是技术债，沉没成本不构成保留理由。 |
| 保留代码作参考，先写测试 | 实际会去适配已有实现，等于后补测试。删除就是删除。 |
| 需要先探索方案 | 探索完成后丢弃探索代码，用 TDD 重新实现。 |
| 测试很难写 | 难测试通常意味着接口难使用，简化接口。 |
| TDD 太慢 | 测试先行比事后调试快；捷径会把成本转移到生产环境。 |
| 现有代码没有测试 | 为现有代码补测试，再修改行为。 |

完整列表见 `references/tdd-best-practices.md` 的 `常见合理化借口`。

## 验证

按以下顺序执行，使用项目已有命令：

```bash
# 运行单个测试类
mvn test -Dtest=UserServiceTest

# 运行单个测试方法
mvn test -Dtest=UserServiceTest#shouldReturnUser_whenIdExists

# 运行全部单元测试
mvn test

# 运行集成测试
mvn verify

# 生成覆盖率报告
mvn clean test jacoco:report
```

判定标准：

- RED 阶段：测试必须失败，且失败原因符合预期。
- GREEN 阶段：目标测试通过，其他测试通过，输出干净。
- REFACTOR 阶段：重构后所有测试保持通过。

发现 bug 时，先写一个失败测试复现它，再走 TDD 循环。不在没有测试的情况下修复 bug。

测试命令速查见 `references/framework-guide.md` 的 `测试命令速查`。

## 实现检查表

- 测试类位于 `src/test/java`，包路径镜像生产代码。
- 单元测试命名 `XxxTest.java`。
- Service 单元测试使用 `@ExtendWith(MockitoExtension.class)` 与 `@Mock`、`@InjectMocks`。
- Controller 单元测试使用 `@WebMvcTest` 与 `@MockBean`。
- 集成测试、切片测试与 Testcontainers 配置见 `references/framework-guide.md`。
- mock 数据使用 Builder 填充全部必填字段，避免部分 mock 导致 NPE。
- 测试数据由程序插入，不依赖数据库已有数据；数据库测试使用事务回滚或明确前缀标识。

## 参考资料

| 文件 | 内容 |
|------|------|
| `references/tdd-best-practices.md` | TDD 纪律、AIR/BCDE、验证清单、借口与红旗、Maven 命令 |
| `references/testing-anti-patterns.md` | 测试反模式、mock 门控函数、快速参考 |
| `references/framework-guide.md` | Service/Controller/Mapper/Redis/Testcontainers 测试示例、Mockito 模式、命令速查 |
| `assets/sample_input.json` | 脚本输入的字段示例 |

脚本依赖 `typer` 与 `rich`，统一使用以下前缀运行：

```bash
uv run --with typer --with rich python scripts/<script>.py <子命令> [参数]
```

| 脚本 | 用途 | 调用示例 |
|------|------|----------|
| `test_generator.py` | 从 Java 源码生成 JUnit 5 测试桩 | `uv run --with typer --with rich python scripts/test_generator.py generate --file src/main/java/com/example/UserService.java` |
| `coverage_analyzer.py` | 解析 JaCoCo XML/CSV，按 P0/P1/P2 排列缺口 | `uv run --with typer --with rich python scripts/coverage_analyzer.py analyze --report target/site/jacoco/jacoco.xml --threshold 80` |
| `tdd_workflow.py` | 引导并验证 RED/GREEN/REFACTOR 阶段 | `uv run --with typer --with rich python scripts/tdd_workflow.py phase red --test UserServiceImplTest` |
| `fixture_generator.py` | 从 Entity/DTO 生成完整测试夹具 | `uv run --with typer --with rich python scripts/fixture_generator.py generate --file src/main/java/com/example/UserDO.java --count 5` |

`tdd_workflow.py` 还提供 `verify <阶段> --test <测试类>`、`full-cycle --test <测试类>` 与 `checklist` 子命令。

脚本生成的是测试桩，不等于测试。真正编写测试必须走本文的 TDD 流程。
