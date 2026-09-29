# 代码臭味与重构处方

## 什么是代码臭味？

> "代码臭味是表面症状，通常指向系统中更深层的问题。" — Martin Fowler

## 常见臭味清单

### 1. 僵硬性（Rigidity）

**症状**：每次修改都牵一发而动全身。

```typescript
// 臭味：硬编码依赖
class OrderService {
  private db = new MySQLDatabase(); // 直接依赖实现
  private mailer = new SendGridMailer();

  processOrder(order: Order) {
    this.db.save(order);
    this.mailer.send(order.customer.email, 'Order confirmed');
  }
}
// 想换数据库？想换邮件服务商？必须改这个类

// 处方：依赖注入
class OrderService {
  constructor(
    private db: Database,       // 依赖接口
    private mailer: Mailer,     // 依赖接口
  ) {}

  processOrder(order: Order) {
    this.db.save(order);
    this.mailer.send(order.customer.email, 'Order confirmed');
  }
}
// 换数据库/邮件服务商？只需注入新实现
```

### 2. 脆弱性（Fragility）

**症状**：改一处，多处崩溃。

```typescript
// 臭味：共享可变状态
class UserRegistry {
  private users: User[] = [];

  addUser(user: User) { this.users.push(user); }
  getUsers() { return this.users; } // 返回内部引用！
}

const registry = new UserRegistry();
const users = registry.getUsers();
users.push(fakeUser); // 意外修改了 registry 内部状态！

// 处方：返回副本
class UserRegistry {
  getUsers(): readonly User[] {
    return [...this.users]; // 返回副本
  }
}
```

### 3. 不可移植性（Immobility）

**症状**：代码无法在其他模块中复用。

```typescript
// 臭味：与特定上下文耦合
function sendEmail(to: string, body: string) {
  const companyEmail = 'support@acme.com'; // 硬编码
  // ...
}

// 处方：参数化
function sendEmail(to: string, body: string, from: string = DEFAULT_FROM) {
  // ...
}
```

### 4. 粘滞性（Viscosity）

**症状**：做正确的事比做错误的事更难。

```typescript
// 臭味：没有 lint/格式化工具
// 团队用不同格式风格，提交时冲突不断
// 做正确的事（格式化）比做错误的事（不格式化）更麻烦

// 处方：自动化
// .prettierrc + lint-staged + husky
// 保存时自动格式化，提交时自动检查
```

### 5. 不必要的复杂性（Needless Complexity）

**症状**：过度设计，"以防将来需要"。

```typescript
// 臭味：为永远不会发生的场景设计
abstract class PaymentStrategyFactory {
  abstract create(type: PaymentType): PaymentProcessor;
}

class CreditCardPaymentStrategyFactory extends PaymentStrategyFactory {
  create(): PaymentProcessor { return new CreditCardProcessor(); }
}
// 只有一种支付方式，却建了工厂模式

// 处方：YAGNI
function processPayment(payment: Payment) {
  return processCreditCard(payment);
}
// 等有第二种支付方式时再引入策略模式
```

### 6. 不必要的重复（DRY 违反）

**症状**：同样的逻辑出现在多个地方。

```typescript
// 臭味：重复的验证逻辑
// file: userService.ts
if (!user.name || user.name.length < 2) throw new Error('Invalid name');
if (!user.email || !user.email.includes('@')) throw new Error('Invalid email');

// file: orderService.ts
if (!customer.name || customer.name.length < 2) throw new Error('Invalid name');
if (!customer.email || !customer.email.includes('@')) throw new Error('Invalid email');

// 处方：提取共用验证函数
function validatePerson(person: { name: string; email: string }): void {
  if (!person.name || person.name.length < 2) throw new ValidationError('Invalid name');
  if (!person.email || !isValidEmail(person.email)) throw new ValidationError('Invalid email');
}

// userService.ts
validatePerson(user);
// orderService.ts
validatePerson(customer);
```

### 7. 过大的类（God Class）

**症状**：一个类承担过多职责。

```typescript
// 臭味：300 行的大类
class UserService {
  createUser() { ... }
  deleteUser() { ... }
  sendWelcomeEmail() { ... }
  generateReport() { ... }
  backupToDatabase() { ... }
}

// 处方：按职责拆分
class UserRepository {
  create() { ... }
  delete() { ... }
}
class UserEmailService {
  sendWelcome() { ... }
}
class UserReportGenerator {
  generate() { ... }
}
```

### 8. 过长函数

**症状**：函数超过 20 行。

**处方**：提取子函数，每层保持单一抽象层级。

```typescript
// 臭味
function processOrder(order: Order) {
  // 50 行混合验证、计算、保存、通知的代码
}

// 处方
function processOrder(order: Order) {
  validateOrder(order);
  const totals = calculateTotals(order);
  persistOrder(order, totals);
  notifyCustomer(order, totals);
}
```

## 臭味检测检查表

| 检查项 | 臭味信号 | 行动 |
|--------|---------|------|
| 文件 > 300 行 | 过大类/模块 | 按职责拆分 |
| 函数 > 20 行 | 过长函数 | 提取子函数 |
| 参数 > 3 个 | 参数过多 | 对象参数封装 |
| if/else 嵌套 > 3 层 | 深层嵌套 | 提前返回/提取函数 |
| 同一逻辑出现 > 2 次 | 重复代码 | 提取共用函数 |
| 修改需改 > 3 个文件 | 僵硬性 | 解耦/依赖注入 |
| 需要注释才能理解 | 表达力不足 | 重写，用命名表达 |
