# 错误处理与测试原则

## 错误处理

### 用异常替代返回码

```typescript
// 差：返回错误码
function divide(a: number, b: number): number | 'ERROR' {
  if (b === 0) return 'ERROR';
  return a / b;
}
// 调用方必须记住检查返回值

// 好：抛出异常
function divide(a: number, b: number): number {
  if (b === 0) throw new DivisionByZeroError('Cannot divide by zero');
  return a / b;
}
// 异常无法被忽视
```

### 先写 try-catch-finally

```typescript
// 先定义操作范围，再填充细节
function readFile(filePath: string): string {
  let file: File | null = null;
  try {
    file = openFile(filePath);
    return file.read();
  } finally {
    file?.close(); // 确保资源被释放
  }
}
```

### 不返回 null

```typescript
// 差：返回 null
function findUser(id: string): User | null {
  return database.users.find(u => u.id === id) ?? null;
}
// 每个调用方都必须做 null 检查

// 好：返回空集合或抛出异常
function findUser(id: string): User {
  const user = database.users.find(u => u.id === id);
  if (!user) throw new UserNotFoundError(`User ${id} not found`);
  return user;
}

// 或返回空数组
function findUsersByRole(role: string): User[] {
  return database.users.filter(u => u.role === role);
  // 没有匹配时返回空数组，而非 null
}
```

### 不传入 null

```typescript
// 差：允许 null 参数
function processPayment(amount: number | null, currency: string | null) {
  if (!amount) throw new Error('Amount required');
  if (!currency) throw new Error('Currency required');
}

// 好：类型系统禁止 null
function processPayment(amount: number, currency: string): void {
  // 类型系统保证参数不为 null
}
```

### 异常分层

```typescript
// 底层异常
class ValidationError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'ValidationError';
  }
}

class NotFoundError extends Error {
  constructor(resource: string, id: string) {
    super(`${resource} with id ${id} not found`);
    this.name = 'NotFoundError';
  }
}

// 高层捕获并转换
async function handleCreateOrder(req: Request): Promise<Response> {
  try {
    const order = await createOrder(req.body);
    return new Response(JSON.stringify(order), { status: 201 });
  } catch (error) {
    if (error instanceof ValidationError) {
      return new Response(error.message, { status: 400 });
    }
    if (error instanceof NotFoundError) {
      return new Response(error.message, { status: 404 });
    }
    throw error; // 未知异常继续抛出
  }
}
```

## 测试原则

### TDD 三定律

1. **红灯**：在写出失败测试之前，不写生产代码
2. **绿灯**：不写出超过"刚好失败"程度的测试
3. **重构**：不写出超过"刚好通过"程度的生产代码

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
