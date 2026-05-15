---

name: unit-test-mockito
description: 为 Java 项目生成自动化单元测试（JUnit 4 + Mockito）。当用户要求编写单元测试、生成测试用例或提升测试覆盖率时使用。
paths:
  - "**/*/src/test/java/**/*/*Test.java"
tools: ["Read", "Grep", "Glob", "Write", "Edit"]
model: opus
system_prompt: 你是单元测试专家。
max_turns: 3

---

### Java 单元测试规则

#### 前置检查清单

在生成测试代码前，必须完成以下检查与信息收集（缺失则先补齐）：

1. 识别被测系统（SUT， System Under Test）

- 读取被测类源文件与其直接依赖（构造参数、字段注入、静态依赖）
- 记录包名、类名、可见性、构造方法、所有 public 方法签名

2. 分析类结构与行为

- 逐个梳理 public 方法：
  - 入参、返回值、抛出异常
  - 分支条件与边界值（null/空集合/0/负数/超长字符串等）
  - 外部交互：数据库/缓存/HTTP/RPC/文件/时间/随机数等

3. 识别依赖与可 Mock 点

- 识别可替换依赖（接口/组件/DAO/Client），明确 Mock/Spy 的对象
- 标记不可 Mock 或较难 Mock 的点（static/final/private/new 出来的对象）

4. 确认测试工程与框架约束

- 确认项目使用的测试框架与版本（JUnit 4，Mockito，Spring Test 等）
- 确认测试源码目录结构（例如：src/test/java 与包路径对齐）
- 确认断言库与风格（JUnit Assertions / AssertJ / Hamcrest 等，优先跟随项目现状）

5. 【强制】单元测试是可以重复执行的，不能受到外界环境的影响。 

**说明**：单元测试通常会被放到持续集成中，每次有代码check in时单元测试都会被执行。如果单测对外部环境（网络、服务、中间件等）有依赖，容易导致持续集成机制的不可用。 
**正例**：为了不受外界环境影响，要求设计代码时就把SUT的依赖改成注入，在测试时用spring 这样的DI框架注入一个本地（内存）实现或者Mock实现。 

6. 执行单元测试需要追加 `-Dmaven.test.skip=false`


#### 测试代码生成规范

1. 单元测试框架依赖 jar 包 

- org.springframework.boot:spring-boot-starter-test
- org.junit.jupiter:junit-jupiter
- org.mockito:mockito-core

2. 测试类命名规范

- 测试类名：{被测类名}Test。
- 用 @org.junit.jupiter.api.Nested，清晰的测试方法名定义内部类，禁止用中文命名。
- 在内部类中按照场景实现单元测试的方法逻辑，禁止用中文命名。

3. 测试类结构模板

- 统一结构：
  - Mock 声明区
  - 被测对象构建区（如 @InjectMocks 或手动 new）
  - 通用测试数据构建方法（可选）
  - 用例区：按被测方法分组

推荐的骨架（根据项目框架选择其一）：

1)  如果测试类是springboot 框架对应的，必须与 Spring 参与：（优先）
   - @ExtendWith(SpringExtension.class)
   - @MockBean 替换外部依赖
   - @InjectMocks 被测对象

2) 纯 Mockito：
   - @ExtendWith(MockitoExtension.class)
   - @Mock 依赖
   - @InjectMocks 被测对象（或构造注入手动 new）

4. Mock 对象配置规范

- Mock 行为遵循 “最小必要” 原则：只 stub 当前用例需要的调用
- 对外部依赖交互必须验证（verify）：
  - 是否被调用
  - 调用次数（times / never）
  - 关键入参（ArgumentCaptor 或 eq）
- 不要过度验证实现细节（避免脆弱测试）

5. 测试数据构建规范

- 优先使用 Builder/Factory 方法构建测试数据（若项目已有）
- 没有 Builder 时，使用专用的私有方法构造常见对象：
  - buildValidXxx()
  - buildXxxWithBoundary()
- 避免在单个测试方法内堆叠大量对象构建逻辑

6. 断言规范

- 每个测试只断言该场景的关键输出与关键副作用
- 断言优先级：
  - 业务返回值/状态
  - 对外部依赖的交互（verify）
  - 产生的持久化/事件（如有）

7. 异常与边界用例规范

- 对非法参数、依赖异常、返回空值/空集合的场景必须覆盖
- 异常断言使用 assertThrows，并校验异常信息或错误码（若稳定）

8. 参数化测试（可选）

- 当存在多个等价输入组合且断言相同，优先使用参数化测试

9. 参考示例 `mockito-demo.md`

#### 测试用例设计原则

1. 覆盖策略

- 覆盖 public 方法的：
  - 正常流程（Happy Path）
  - 关键分支（if/else、switch、early return）
  - 边界条件（边界值、空值、极端值）
  - 异常流程（依赖抛错、业务校验失败）
汽车运输运达买方指定 工地。外观质量以及包装 完好，符合各项技术指 标，随车附带出场资料以 及质量证明文件

2. 测试金字塔

- 单元测试优先覆盖纯业务逻辑与边界条件
- 集成测试只覆盖关键链路与契约（本技能重点在单元测试）

3. 覆盖率目标（按团队要求调整）


- 以可维护性优先，覆盖关键逻辑与高风险模块
- 对“薄封装/纯转发”代码不过度追求覆盖率

#### 最佳实践清单

1. 命名清单

- 测试方法名包含：方法名 + 场景 + 预期结果
- 命名风格统一（可选其一并保持一致）：
  - shouldXxxWhenYyy
  - givenYyyWhenXxxThenZzz

2. 结构清单

- Arrange / Act / Assert 三段式清晰
- 单测不依赖执行顺序，可重复执行
- 单测不依赖真实时间/随机数（必要时注入 Clock/Random 或封装）

3. 断言清单

- 断言尽量具体，避免 “只 assertNotNull” 的弱断言
- 对集合/对象断言关注关键字段，避免断言全量对象导致脆弱

4. Mock 清单

- 避免 deep stubs
- 避免对私有方法做测试（测试对外可观察行为）

5. 性能清单

- 单测应快速（通常毫秒级）
- 避免线程 sleep、真实 IO、网络请求

#### 常见问题与解决方案

1. 静态方法难以 Mock

- 优先重构：用可注入的依赖封装静态调用
- 若项目已启用 Mockito inline 等能力，再考虑静态 Mock（谨慎使用）

2. final 类/方法 Mock 问题

- 优先遵循项目现有 Mockito 配置；必要时使用 Mockito inline

3. 私有方法怎么测

- 不直接测试私有方法；通过 public 方法的输入输出与副作用覆盖其逻辑