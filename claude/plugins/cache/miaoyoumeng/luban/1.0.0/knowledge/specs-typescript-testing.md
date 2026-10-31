# TypeScript test 规范


- 禁止编写文件名为 `types.ts` 和 `index.ts` 对应的单元测试（它们只包含类型定义或 re-export，无可测试行为）。
- 禁止编写仅验证日志输出（`debug`/`info`/`warn`/`error` 调用次数、参数、颜色）的单元测试。日志是副作用，不是行为。测试应关注函数的返回值、状态变更或外部调用，而非日志是否被打印。如果一个测试的全部断言都是 `expect(mockLog).toHaveBeenCalled(...)`，则该测试无意义，应删除。
- 只 Mock 边界：网络、数据库、文件系统、时间、随机数、第三方 API 等外部依赖才 Mock；禁止 Mock 被测函数或类本身。
- 优先依赖注入：通过构造函数、参数或工厂注入接口依赖，优于 `vi.mock` 整个模块。
- Mock 必须遵守真实契约：返回值、异常、Promise、副作用须与真实依赖一致，用接口/类型约束，禁止「测试通过但生产失败」。
- 选最轻的替身：fake > stub > spy > 完整 mock；避免创建庞大万能 Mock。
- 类型安全创建 Mock：使用 `vi.mocked<T>`、`MockedFunction<T>`、`Partial<T>`；禁止强制类型断言。
- 只断言可观察行为：测试公共 API、返回值、状态变化和必要副作用；禁止断言私有方法、内部调用顺序或实现步骤。
- 交互断言要克制：只有副作用、命令、通知等真正重要时才验证调用参数和次数；查询/计算逻辑优先断言返回结果。
- 每个测试独立且可重复：`beforeEach` 新建 Mock，`afterEach` restore/reset/clear；禁止共享可变 Mock 状态。
- 封装第三方依赖为适配器：Mock 自己定义的适配器接口，不直接 Mock 第三方库内部 API。
- 保持确定、快速、可读：避免真实网络/时间/随机性；遵循 AAA（Arrange-Act-Assert）；命名说明行为而非实现。

## 测试原则

### TDD 三定律

1. 在写出失败的单元测试之前，不写生产代码。
2. 单元测试只写到刚好失败；编译失败也算失败。
3. 生产代码只写到刚好通过当前失败的测试。

### FIRST 原则

| 原则 | 含义 | TypeScript 示例 |
|------|------|-----------------|
| **F**ast | 测试必须快 | 用 mock 替代真实数据库调用 |
| **I**ndependent | 测试不互相依赖 | 每个测试独立 setup/teardown |
| **R**epeatable | 任何环境可跑 | 不依赖本地文件/网络 |
| **S**elf-Validating | 自动断言 | `expect(result).toBe(expected)` |
| **T**imely | 先写测试 | 生产代码之前写测试 |

### 测试结构：Arrange-Act-Assert

```typescript
describe('UserService', () => {
  it('should create user with valid data', () => {
    // Arrange
    const params = { name: 'Alice', email: 'alice@example.com' };

    // Act
    const user = userService.createUser(params);

    // Assert
    expect(user.name).toBe('Alice');
    expect(user.email).toBe('alice@example.com');
    expect(user.id).toBeDefined();
  });
});
```

### 测试命名

```typescript
// 差：名称含糊
it('should work', () => { ... });
it('test create', () => { ... });

// 好：名称描述行为和条件
it('should throw ValidationError when email is missing', () => { ... });
it('should return active users when status is active', () => { ... });
it('should calculate total with tax when country is US', () => { ... });
```

### 避免测试反模式

```typescript
// 差：测试实现细节
it('should call saveUser', () => {
  const spy = vi.spyOn(db, 'saveUser');
  userService.createUser(params);
  expect(spy).toHaveBeenCalled(); // 测试了实现，不是行为
});

// 好：测试行为
it('should persist user to database', () => {
  userService.createUser(params);
  const found = db.findUserByEmail(params.email);
  expect(found).toBeDefined();
  expect(found.name).toBe(params.name);
});
```