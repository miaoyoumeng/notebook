# TDD Java — Java + Spring Boot 严格 TDD Skill

**版本**: 1.0.0
**更新日期**: 2026-05-29

**严格遵循 TDD 铁律的 Java 单元测试 skill。** 针对 Java 17 + Spring Boot + Redis + MySQL 技术栈，基于 JUnit 5 + Mockito。

> **铁律：** 没有失败的测试之前，禁止写产品代码。
> 已经写了？删掉。从头开始。

## 目录

- [概述](#概述)
- [铁律](#铁律)
- [安装](#安装)
- [快速开始](#快速开始)
- [脚本模块](#脚本模块)
- [配置](#配置)
- [技术栈](#技术栈)
- [测试质量标准](#测试质量标准)
- [故障排除](#故障排除)
- [测试反模式](#测试反模式)

## 概述

TDD Java skill 将**严格的 TDD 纪律**集成到 Java 17 + Spring Boot + Redis + MySQL 项目中：

- **铁律约束**: 没有失败测试之前禁止写产品代码
- **强制验证**: RED 必须亲眼看到失败，GREEN 必须亲眼看到通过
- **AIR 原则**: 单元测试全自动、独立、可重复
- **BCDE 原则**: 边界值、正确输入、设计文档、错误输入全覆盖
- **反模式门控**: 防止测试 mock 行为、生产类污染等常见错误
- **智能测试桩生成**: 从代码或需求生成测试桩
- **覆盖率分析**: 解析 JaCoCo XML/CSV 覆盖率报告，识别缺口

## 铁律

```
没有失败的测试之前，禁止写产品代码
```

**违反铁律的惩罚：**
- 已经写了产品代码？**删掉**。从头开始。
- 不要保留"作为参考"
- 不要在写测试时"适配"它
- **删除就是删除**

**强制验证：**
- RED：必须**亲眼看到测试失败**
- GREEN：必须**亲眼看到测试通过**，且其他测试依然通过，输出干净
- REFACTOR：每次小重构后**必须重新运行测试**

详见 `references/tdd-best-practices.md` 和 `references/testing-anti-patterns.md`。

## 安装

```bash
# 项目级别安装
cp -r tdd-java /path/to/your/project/.claude/skills/

# 用户级别安装
cp -r tdd-java ~/.claude/skills/
```

## 快速开始

### 1. 从代码生成测试

```
@tdd-java

为以下 Java Service 生成测试：
@Service
public class UserService {
    private final UserMapper userMapper;

    public UserDTO getById(Long id) {
        UserDO user = userMapper.selectById(id);
        if (user == null) {
            throw new NotFoundException("User not found: " + id);
        }
        return UserConverter.toDTO(user);
    }
}
```

### 2. 分析覆盖率

```
@tdd-java

分析覆盖率报告：target/site/jacoco/jacoco.xml
源代码目录：src/main/java
目标：80% 覆盖率
按优先级推荐
```

### 3. TDD 工作流引导

```
@tdd-java

引导我完成用户管理模块的 TDD 实现。

需求：
- 用户CRUD操作（增删改查）
- 分页查询用户列表
- 删除时清除Redis缓存
- 邮箱唯一性校验

技术栈：Java 17 + Spring Boot + MyBatis-Plus + Redis + MySQL
```

## 脚本模块

### test_generator.py
从 Java 源码生成测试用例：
- 解析 Java 源码结构
- 生成 @Test 方法代码
- 支持 Service、Controller、Mapper、Utils 等层级
- 覆盖 happy path、错误、边界场景（BCDE）

### coverage_analyzer.py
解析和分拆覆盖率报告：
- 支持 JaCoCo XML 和 CSV 格式
- 按优先级分类缺口（P0/P1/P2）
- 生成可操作的改进建议

### tdd_workflow.py
引导 Red-Green-Refactor 工作流：
- 验证每个阶段的完成条件
- 重构建议
- 工作流状态追踪

### fixture_generator.py
生成测试夹具和 mock 数据：
- 从 Java entity/DTO 生成 mock 对象
- 边界值生成
- 边缘场景数据

## 配置

### .tdd-java.json（可选，项目根目录）

```json
{
  "coverage_threshold": 80,
  "test_directory": "src/test/java/",
  "quality_rules": {
    "max_assertions_per_test": 3,
    "require_descriptive_names": true,
    "enforce_isolation": true,
    "follow_air_principles": true,
    "follow_bcde_principles": true
  }
}
```

## 技术栈

### 测试框架
- **JUnit 5** (Jupiter) — Java 标准测试框架
- **Mockito** 5+ — Mock 框架
- **AssertJ** — 流式断言库（推荐）

### 集成测试
- **Spring Boot Test** — Spring 容器集成测试
- **@SpringBootTest** — 完整容器测试
- **@WebMvcTest** / **@DataJpaTest** — 分层切片测试
- **Testcontainers** — Redis/MySQL 容器化测试
- **H2** — 内存数据库（测试替身）

### 构建与覆盖率
- **Maven** 3.8+ — 构建工具
- **maven-surefire-plugin** — 单元测试执行（`*Test.java`）
- **maven-failsafe-plugin** — 集成测试执行（`*IT.java`）
- **JaCoCo** — 代码覆盖率

### 项目基础设施
- **Java** 17+
- **Spring Boot** 3+
- **Redis** (Jedis / Lettuce)
- **MySQL** 8+
- **MyBatis** / **MyBatis-Plus**

## 测试质量标准

| 指标 | 目标 |
|------|------|
| 行覆盖率 | 80%+ |
| 分支覆盖率 | 75%+ |
| 方法覆盖率 | 90%+ |
| 核心模块语句/分支 | 100% |
| 单次测试耗时 | < 500ms |
| 每测试断言数 | 1-3 |

## 故障排除

**问题：测试编译失败 "cannot find symbol"**
```
解决：确认目标类已存在（即使是空的）。如果是 RED 阶段，编译失败也是测试失败
— 确认后进入 GREEN 创建实现类。
```

**问题：JaCoCo 报告未生成**
```
解决：检查 pom.xml 中 jacoco-maven-plugin 配置
运行 mvn clean test jacoco:report
```

**问题：Spring Boot 集成测试启动慢**
```
解决：使用 @WebMvcTest 或 @DataJpaTest 切片测试
或用 @SpringBootTest(classes = {OnlyNeeded.class}) 缩小加载范围
```

**问题：Mockito mock 返回 null**
```
解决：确认 @ExtendWith(MockitoExtension.class) 或 MockitoAnnotations.openMocks(this)
检查 when().thenReturn() 参数匹配
```

**问题：Redis 测试找不到连接**
```
解决：集成测试使用 Testcontainers 或 @DataRedisTest
单元测试 mock RedisTemplate
```

## 测试反模式

**写 mock 或添加测试工具时，必读 `references/testing-anti-patterns.md`。**

**铁律：**
1. 永不测试 mock 行为
2. 永不在生产类上添加仅测试用方法
3. 永不在未理解依赖的情况下使用 mock

**常见违规：**
- 断言 mock 对象被调用 → 测试的是 mock 而不是业务逻辑
- 类的方法只在测试文件中调用 → 移到测试工具
- Mock 设置占测试 >50% → 考虑集成测试
- Mock "保险起见" → 先理解依赖再 mock

**单元测试禁止事项（来自单元测试.md）：**
- 不准使用 System.out 进行人肉验证，必须使用 assert
- 不能假设数据库里数据存在
- 不要直接操作数据库插入数据，用程序插入
- 数据库测试不设回滚导致脏数据
- 构造方法中不要做过多事情
- 避免过多全局变量和静态方法

---

## 目录结构

```
tdd-java/
├── SKILL.md                       # Skill 定义（含铁律）
├── README.md                      # 本文件
├── pyproject.toml                 # Python 依赖
├── references/
│   ├── tdd-best-practices.md      # TDD 纪律（含铁律、AIR、BCDE、红旗）
│   ├── testing-anti-patterns.md   # 测试反模式与门控函数
│   ├── framework-guide.md         # Java + Spring Boot 测试指南
│   └── ci-integration.md          # CI 集成指南（GitHub Actions + Maven）
├── scripts/
│   ├── test_generator.py          # 测试桩生成（桩 ≠ 测试，仍须走 TDD）
│   ├── coverage_analyzer.py       # 覆盖率分析（JaCoCo）
│   ├── tdd_workflow.py            # TDD 工作流引导
│   └── fixture_generator.py       # 夹具生成
└── assets/
    └── sample_input.json          # 示例输入
```

## 版本历史

### v1.0.0 (2026-05-29)
- 初始版本
- **严格遵循 TDD 铁律**：没有失败测试之前禁止写产品代码
- 专注于 Java 17 + Spring Boot + Redis + MySQL 技术栈
- 基于 JUnit 5 + Mockito + AssertJ 测试框架
- 强制 RED/GREEN 验证步骤
- AIR + BCDE 单元测试原则
- 5 大测试反模式门控
- JaCoCo XML/CSV 覆盖率分析
- 测试夹具生成
- CI 集成指南（GitHub Actions + Maven）
