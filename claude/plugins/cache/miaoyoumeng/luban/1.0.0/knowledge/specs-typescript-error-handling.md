# 错误处理与测试原则

## 错误处理

### 用异常替代返回码

```typescript
// 差：返回错误码
const divide = (a: number, b: number): number | 'ERROR' => {
  if (b === 0) return 'ERROR';
  return a / b;
};
// 调用方必须记住检查返回值

// 好：抛出异常
const divide = (a: number, b: number): number => {
  if (b === 0) throw new DivisionByZeroError('Cannot divide by zero');
  return a / b;
};
// 异常无法被忽视
```

### 先写 try-catch-finally

```typescript
// 先定义操作范围，再填充细节
const readFile = (filePath: string): string => {
  let file: File | null = null;
  try {
    file = openFile(filePath);
    return file.read();
  } finally {
    file?.close(); // 确保资源被释放
  }
};
```

### 不返回 null

```typescript
// 差：返回 null
const findUser = (id: string): User | null =>
  database.users.find(u => u.id === id) ?? null;
// 每个调用方都必须做 null 检查

// 好：返回空集合或抛出异常
const findUser = (id: string): User => {
  const user = database.users.find(u => u.id === id);
  if (!user) throw new UserNotFoundError(`User ${id} not found`);
  return user;
};

// 或返回空数组
const findUsersByRole = (role: string): User[] => {
  // 没有匹配时返回空数组，而非 null
  return database.users.filter(u => u.role === role);
};
```

### 不传入 null

```typescript
// 差：允许 null 参数
const processPayment = (amount: number | null, currency: string | null) => {
  if (!amount) throw new Error('Amount required');
  if (!currency) throw new Error('Currency required');
};

// 好：类型系统禁止 null
const processPayment = (amount: number, currency: string): void => {
  // 类型系统保证参数不为 null
  savePayment(amount, currency);
};
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
const handleCreateOrder = async (req: Request): Promise<Response> => {
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
};
```

