# 函数设计与注释原则

## 函数设计

### 短小原则

> "函数应该短小，比你能想到的还要短小。"

```typescript
// 差：50 行的函数
function processPayment(payment: Payment) {
  // 验证
  if (!payment.amount) throw new Error('Missing amount');
  if (payment.amount <= 0) throw new Error('Invalid amount');
  if (!payment.currency) throw new Error('Missing currency');
  if (!SUPPORTED_CURRENCIES.includes(payment.currency)) {
    throw new Error('Unsupported currency');
  }
  // 计算手续费
  const feeRate = getFeeRate(payment.currency);
  const fee = payment.amount * feeRate;
  const total = payment.amount + fee;
  // 记录日志
  console.log(`Processing payment: ${payment.amount} ${payment.currency}`);
  console.log(`Fee: ${fee}, Total: ${total}`);
  // 保存
  const record = { ...payment, fee, total, status: 'processed' };
  database.payments.insert(record);
  // 通知
  sendNotification(payment.userId, `Payment of ${total} processed`);
}

// 好：每个函数 3-5 行
function processPayment(payment: Payment): void {
  validatePayment(payment);
  const total = calculateTotal(payment);
  savePayment(payment, total);
  notifyUser(payment.userId, total);
}
```

### 只做一件事

**判断标准**：如果函数名可以拆解为"做 X 做 Y 做 Z"，它做了太多事。

```typescript
// 差：做了验证、计算、保存三件事
function handleOrder(order: Order) { ... }

// 好：每个函数一件事
function validateOrder(order: Order): void { ... }
function calculateOrderTotal(order: Order): number { ... }
function saveOrder(order: Order): void { ... }
```

### 单一抽象层级

```typescript
// 差：混合高层业务逻辑和底层实现
function generateReport(users: User[]) {
  const report = users.map(u => `${u.name} (${u.email})`).join('\n');
  const fs = require('fs');
  fs.writeFileSync('report.txt', report);
}

// 好：每层一个抽象层级
function generateReport(users: User[]): void {
  const content = formatUserReport(users);
  writeToFile('report.txt', content);
}

function formatUserReport(users: User[]): string {
  return users.map(formatUserLine).join('\n');
}

function formatUserLine(user: User): string {
  return `${user.name} (${user.email})`;
}
```

### 参数设计

| 数量 | 建议 | 做法 |
|------|------|------|
| 0 | 最理想 | 从函数外部获取 |
| 1 | 常见 | 单个参数，语义清晰 |
| 2 | 可接受 | 考虑是否需要合并 |
| 3 | 需理由 | 用对象参数封装 |
| 4+ | 重构 | 必须封装为参数对象 |

```typescript
// 差：参数过多
function createUser(name: string, email: string, age: number, role: string) { ... }

// 好：对象参数
function createUser(params: CreateUserParams): User { ... }

interface CreateUserParams {
  name: string;
  email: string;
  age: number;
  role: UserRole;
}
```

### 无副作用

```typescript
// 差：函数悄悄修改了外部状态
let userCache: Map<string, User> = new Map();

function getUser(id: string): User {
  const user = database.findUser(id);
  userCache.set(id, user); // 副作用！
  return user;
}

// 好：明确分离副作用
function getUser(id: string): User {
  return database.findUser(id);
}

function cacheUser(id: string, user: User): void {
  userCache.set(id, user); // 函数名明确告知有副作用
}
```

## 注释原则

### 用代码表达，而非注释

```typescript
// 差：注释解释代码
// 如果用户年龄超过 18 岁，并且账户已激活
if (user.age > 18 && user.isAccountActive) { ... }

// 好：代码自身表达意图
if (user.isAdult() && user.isActive()) { ... }
```

### 好注释的类型

| 类型 | 示例 | 说明 |
|------|------|------|
| 法律信息 | `// Copyright 2024 Acme Corp` | 版权声明 |
| 意图说明 | `// 强制分页大小为 10 以优化内存使用` | 解释 why |
| 复杂正则 | `// 匹配 YYYY-MM-DD 格式的日期` | 解释 regex |
| TODO | `// TODO: 添加速率限制` | 标记待办 |
| 警告 | `// WARNING: 此操作不可逆` | 提醒风险 |

### 坏注释的类型

| 类型 | 示例 | 为什么坏 |
|------|------|---------|
| 含糊其辞 | `// 做一些处理` | 没提供信息 |
| 冗余 | `// 设置名称` 跟着 `user.name = name` | 重复代码 |
| 误导 | `// 返回 true 表示成功` 但实际返回 boolean | 比没注释更糟 |
| 注释掉的代码 | `// const oldResult = ...` | 用 git 管理历史 |
| 噪音 | `// 构造函数` 跟着 `constructor()` | 无意义 |
| 位置标记 | `// ========== 区域 A ==========` | 应该用函数拆分 |

### 注释的删除规则

- 注释掉的代码 → 直接删除，git 保留历史
- 重复代码含义的注释 → 重写代码
- 含糊的注释 → 要么精确化，要么删除
- 过时的注释 → 必须删除或更新
