---
name: "tdd-java"
description: "Java TDD 单元测试 skill，基于 JUnit 5 + Mockito + Spring Boot Test。严格遵循 TDD 铁律：没有失败测试之前禁止写产品代码。当用户要求编写单元测试、实践 TDD、修复 bug、提升测试覆盖率、生成 mock/stub 时使用此 skill。"
---

# TDD Java

Java + Spring Boot + Redis + MySQL 项目的严格 TDD 工作流，基于 JUnit 5 + Mockito。

---

## 铁律

```
没有失败的测试之前，禁止写产品代码, 参考 `references/tdd-best-practices.md` 中 `铁律`。
```
```
从测试出发重新实现。参考 `references/testing-anti-patterns.md`。
```

## 核心原则

> 如果你没有亲眼看到测试失败，你就不知道它测的是不是对的东西。

> 违反规则的字面意思，就是违反规则的精神。

---

## 何时使用

**始终：**
- 新功能
- Bug 修复
- 重构
- 行为变更

**例外（必须问用户）：**
- 一次性原型
- 生成的代码
- 配置文件

想"就这一次跳过 TDD"？停下。这是合理化借口。

---

## Red-Green-Refactor 纪律

```
RED ──→ 验证失败 ──→ GREEN ──→ 验证通过 ──→ REFACTOR ──→ 验证通过 ──→ 下一个
   ↑                                                           │
   └───────────────────────────────────────────────────────────┘
```

### RED — 写失败测试

写一个最小的测试，描述**期望的行为**。

**好：**
```java
// CartTest.java
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class CartTest {

    @Test
    void shouldRejectZeroQuantity() {
        Cart cart = new Cart();
        assertThrows(IllegalArgumentException.class, () ->
            cart.addItem(new CartItem("sku-1", "Widget", 9.99, 0))
        );
    }
}
```
- 清晰的名称
- 测真实行为
- 一个测试一个行为
- 真实代码（非 mock，除非不可避免）

**坏：**
```java
// ❌ 模糊的名字，测试的是 mock 而不是代码
@Test
void testAddItem() {
    CartItem mockItem = mock(CartItem.class);
    cart.addItem(mockItem);
    verify(mockItem, times(1)).getId();
}
```

**要求：**
- 一个行为
- 清晰的名称（`should<行为>_when<条件>`）
- 真实代码（mock 只在不可避免时使用）

### 验证 RED — 必须看它失败

**强制。永不跳过。**

```bash
mvn test -Dtest=CartTest
```

确认：
- 测试**失败**（不是报错）
- 失败信息**符合预期**
- 失败原因**是功能缺失**（不是编译错误或语法错误）

**测试通过了？** 你测的是已存在的行为。修测试。

**测试编译报错？** 修错误，重新运行，直到它**正确地失败**。

> 编译失败也是测试失败。不要先创建类来避免编译错误 — 类型从测试中流出。

### GREEN — 最小实现

写能让测试通过的**最简代码**。

**好：**
```java
// Cart.java
public class Cart {
    public void addItem(CartItem item) {
        if (item.qty() <= 0) {
            throw new IllegalArgumentException("Quantity must be positive");
        }
        this.items.add(item);
    }
}
```
仅仅足够让测试通过。

**坏：**
```java
// ❌ 过度工程 YAGNI
public class Cart {
    public void addItem(CartItem item, AddOptions options) {
        // maxQty, onAdd callback, retry policy...
    }
}
```

**不要：**
- 添加功能
- 重构其他代码
- 超出测试范围的"改进"

### 验证 GREEN — 必须看它通过

**强制。**

```bash
mvn test -Dtest=CartTest
```

确认：
- 测试**通过**
- **其他测试依然通过**
- **输出干净**（无 error、无 warning）

**测试失败？** 修代码，不要修测试。

**其他测试失败？** 立即修复。

### REFACTOR — 清理

通过后才：
- 消除重复
- 改进命名
- 提取 helper

**保持测试绿色。不要添加行为。**

### 循环

下一个失败测试 → 下一个功能。

---

## 好测试的特征

| 质量 | 好 | 坏 |
|------|----|----|
| **最小** | 一个行为。名字有"and"就拆开 | `shouldValidateEmailAndDomainAndWhitespace()` |
| **清晰** | 名字描述行为 | `test1()` |
| **体现意图** | 展示期望的 API | 掩盖代码应该做什么 |

---

## 单元测试 AIR 原则

参考 `references/tdd-best-practices.md` 中 `AIR 原则`。
---

## 单元测试 BCDE 原则

参考 `references/tdd-best-practices.md` 中 `BCDE 原则`。

---

## 测试文件命名规范

```
src/
├── main/java/com/example/
│   ├── controller/
│   │   └── UserController.java
│   ├── service/
│   │   ├── IUserService.java
│   │   └── impl/
│   │       └── UserServiceImpl.java
│   ├── mapper/
│   │   └── UserMapper.java
│   └── entity/
│       └── UserDO.java
└── test/java/com/example/
    ├── controller/
    │   ├── UserControllerTest.java    ← 单元测试（Mock）
    │   └── UserControllerIT.java     ← 集成测试
    ├── service/impl/
    │   ├── UserServiceImplTest.java   ← 单元测试（Mock）
    │   └── UserServiceImplIT.java    ← 集成测试
    ├── mapper/
    │   └── UserMapperIT.java         ← 数据层测试（集成）
    └── utils/
        └── DateUtilsTest.java        ← 工具类测试
```

**命名规则：**
- 单元测试（mock 外部依赖）：`xxxTest.java`
- 集成测试（真实 Spring 容器）：`xxxIT.java`
- 测试类放在 `src/test/java` 下，目录结构镜像业务代码

---

## Spring Boot 测试模式

- 参考：`references/framework-guide.md`

---

## Mock 策略

### Mockito Mock

```java
// Mock 外部依赖
@Mock
private UserMapper userMapper;

@Mock
private RedisTemplate<String, Object> redisTemplate;

// 在 setUp 中确保 mock 干净
@BeforeEach
void setUp() {
    reset(userMapper, redisTemplate);
}
```

### 门控：使用 mock 之前

**写 mock 之前必须问：**
1. 真实方法有什么**副作用**？
2. 这个测试是否**依赖**这些副作用？
3. 我是否**完全理解**这个测试需要什么？

**如果依赖副作用：**
- 在更低层 mock（真正慢/外部的操作）
- 而不是测试依赖的高层方法

**不确定：**
- 先用真实实现跑测试
- 观察实际需要发生什么
- 然后在**正确层级**加最小 mock

### 红色警告

- "我保险起见 mock 这个"
- "这个可能慢，最好 mock"
- 不理解依赖链就 mock

---

## 覆盖率阈值

| 类型 | 阈值 | 说明 |
|------|------|------|
| 行覆盖率 | 80%+ | 项目基线（JaCoCo） |
| 分支覆盖率 | 75%+ | 比行覆盖率更有意义 |
| 方法覆盖率 | 90%+ | 公共 API 应被测试 |
| 关键路径 | 100% | auth、支付、数据校验 |

> 核心模块的语句覆盖率和分支覆盖率都要达到 100%（来自 单元测试.md）

---

## 测试质量标准

| 原则 | 来源 | 强制 |
|------|------|------|
| 测试全自动执行，非交互式，用 assert | AIR-A | 强制 |
| 测试之间不能互相调用，不依赖执行顺序 | AIR-I | 强制 |
| 边界值 + 正确输入 + 设计文档 + 错误输入 | BCDE | 推荐 |
| DAO 层、Manager 层、可重用 Service 必须测试 | 单元测试.md | 推荐 |
| 测试数据用程序插入，不假设数据库已有数据 | 单元测试.md | 推荐 |
| 数据库测试设自动回滚或明确前缀标识 | 单元测试.md | 推荐 |

---

## 测试反模式（必读）

写 mock 或添加测试工具时，参考 `references/testing-anti-patterns.md`。

参考 `references/testing-anti-patterns.md` 中`铁律`

**常见反模式：**
- 断言 mock 元素存在 → 测试的是 mock 而不是组件
- 类的方法只在测试文件中调用 → 放到测试工具里
- Mock 设置超过测试逻辑的一半 → 考虑集成测试
- Mock "保险起见" → 先理解依赖再 mock

**详细门控函数见 `references/testing-anti-patterns.md`。**

---

## 为什么顺序重要

> "我先写代码再补测试验证它有效"

写完代码再补的测试立即通过。**立即通过什么都证明不了：**
- 可能测的是错误的东西
- 可能测的是实现而不是行为
- 可能遗漏了你没想到的边界
- 你从来没看到它捕获 bug

测试先行强制你看到测试失败，证明它**确实在测某个东西**。

---

## 常见合理化借口

- 参考`references/tdd-best-practices.md` 中 `常见合理化借口`

---

## 红旗 — 立即停止，从头开始

- 参考`references/tdd-best-practices.md` 中 `红旗`

**以上任何一项都意味着：删除代码。用 TDD 重新开始。**

---

## 示例：Bug 修复

**Bug：** 空邮箱被接受

**RED**
```java
// UserServiceImplTest.java
@Test
void shouldRejectEmptyEmail() {
    UserDTO input = new UserDTO("", "password123");
    assertThrows(ValidationException.class, () ->
        userService.register(input)
    );
}
```

**验证 RED**
```bash
$ mvn test -Dtest=UserServiceImplTest
FAIL: Expected ValidationException to be thrown, but nothing was thrown
```
正确地失败 — 进入 GREEN。

**GREEN**
```java
// UserServiceImpl.java
public void register(UserDTO input) {
    if (input.getEmail() == null || input.getEmail().trim().isEmpty()) {
        throw new ValidationException("Email required");
    }
    // ...
}
```

**验证 GREEN**
```bash
$ mvn test -Dtest=UserServiceImplTest
PASS
```

**REFACTOR**
如果多个字段需要校验，提取 `Validator` 类。

---

## 验证清单

- 参考`references/tdd-best-practices.md` 中 `验证清单`

不能全打勾？你跳过了 TDD。**从头开始。**

---

## 调试集成

**发现 bug？写一个失败测试复现它。走 TDD 循环。**

测试既证明修复又防止回归。

**永不在没有测试的情况下修 bug。**

---

## 卡住时

- 参考`references/tdd-best-practices.md` 中 `卡住时`

---

## 关键工具

| 工具 | 用途 | 使用方式 |
|------|------|---------|
| `test_generator.py` | 分析源码生成测试桩 | `uv run python scripts/test_generator.py --input src.java` |
| `coverage_analyzer.py` | 解析 JaCoCo XML/CSV 覆盖率 | `uv run python scripts/coverage_analyzer.py --report jacoco.xml --threshold 80` |
| `tdd_workflow.py` | 引导 Red-Green-Refactor | `uv run python scripts/tdd_workflow.py --phase red --test UserServiceTest.java` |
| `fixture_generator.py` | 生成夹具和 mock | `uv run python scripts/fixture_generator.py --entity User --count 5` |

**注意：** 这些工具生成的是**测试桩**。真正写测试必须走 TDD 铁律流程。

---

## 输入要求

### 测试生成
- Java 源代码（文件路径或粘贴内容）
- 可选：覆盖范围（Service、Controller、Mapper、Utils）

### 覆盖率分析
- JaCoCo XML 报告文件
- 可选：源代码文件路径
- 可选：目标覆盖率阈值（默认 80%）

### TDD 工作流
- 功能需求或用户故事
- 当前阶段（RED / GREEN / REFACTOR）
- 测试代码和实现状态

---

## 限制

| 范围 | 细节 |
|------|------|
| 单元测试重点 | 集成和 E2E 测试需要不同模式 |
| 静态分析 | 不能运行测试或测量运行时行为 |
| 语言支持 | 专注于 Java 17 + Spring Boot |
| 测试框架 | JUnit 5 + Mockito + Spring Boot Test |
| 编译工具 | Maven |
| 覆盖率格式 | JaCoCo XML / CSV |
| 生成测试 | 提供桩，复杂逻辑需人工审核 |

---

## 技术栈

- **运行时**: Java 17+ (JDK 17)
- **编译工具**: Maven 3.8+
- **框架**: Spring Boot 3+
- **缓存**: Redis (Jedis / Lettuce)
- **数据库**: MySQL 8+
- **ORM**: MyBatis / MyBatis-Plus
- **测试框架**: JUnit 5 (Jupiter)
- **Mock 框架**: Mockito 5+
- **断言库**: AssertJ（推荐）/ JUnit Jupiter Assertions
- **覆盖率**: JaCoCo
- **测试数据库**: H2 In-Memory（集成测试）/ Testcontainers

---

## 最终规则

```
产品代码 → 必须存在测试且先失败
否则 → 不是 TDD
```

**无用户许可不得例外。**
