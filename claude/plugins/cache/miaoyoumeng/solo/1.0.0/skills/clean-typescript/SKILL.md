---
name: clean-typescript
description: "基于 Robert C. Martin《Clean Code》原则，将'能运行的代码'转化为'整洁的代码'。覆盖命名、函数、注释、格式化、错误处理、测试等维度。开发语言：TypeScript。"
---

# clean-typescript

## 概述

将"能运行的代码"转化为"整洁的代码"。基于 Robert C. Martin 的《Clean Code》核心原则，从命名、函数、注释、格式化、对象、错误处理、测试、类、代码臭味等维度提供系统性指导。

> "代码如果可以被除原作者之外的开发者阅读和改进，那它就是整洁的。" — Grady Booch

## 上下文层级

| 层级 | 信息 | 示例 |
|------|------|------|
| 通用 | 编程语言和运行时 | TypeScript, Node.js |
| 项目 | 项目结构和约定 | monorepo, ESLint 规则 |
| 具体 | 目标文件和模块 | src/utils/, src/services/ |

## 使用时机

- **编写新代码**：从一开始就保证高质量
- **审查 Pull Request**：提供基于原则的建设性反馈
- **重构遗留代码**：识别并消除代码臭味
- **提升团队标准**：对齐业界最佳实践

## 编码四原则

1. **先思考再编码** — 明确改动意图，不确定时暴露困惑
2. **简洁优先** — 用最少代码解决问题，不做推测性工作
3. **精准修改** — 只触碰需要改的代码，不"顺手改进"
4. **目标驱动** — 定义成功标准，循环直到验证通过

## 流程

### 步骤 1：分析代码现状

阅读目标代码，按以下维度评估：

| 维度 | 检查点 |
|------|--------|
| 命名 | 名称是否揭示意图？是否可搜索？是否产生歧义？ |
| 函数 | 是否短小？是否只做一件事？参数数量？是否有副作用？ |
| 注释 | 是否在用注释解释本该用代码表达的内容？ |
| 格式化 | 代码是否像报纸一样从高层到底层阅读？ |
| 错误处理 | 是否使用异常而非返回码？是否返回 null？ |
| 测试 | 是否符合 FIRST 原则？ |
| 代码臭味 | 是否存在僵硬性、脆弱性、不必要的复杂性？ |

**输出格式**：

```markdown
## 代码分析

### 需要改进
1. [维度] 具体问题 → 建议改法
2. [维度] 具体问题 → 建议改法

### 已符合原则
- [维度] 好的做法（保留）
```

### 步骤 2：执行整洁化改造

#### 2.1 有意义的命名

```typescript
// 差：不揭示意图
const d = getDays();
const list = getAccountData();

// 好：名称即文档
const elapsedTimeInDays = calculateElapsedTime(startDate, endDate);
const activeAccounts = getActiveAccounts();
```

**命名规则**：

| 元素 | 规则 | TypeScript 示例 |
|------|------|----------------|
| 变量 | 名词，揭示意图 | `elapsedTimeInDays` |
| 函数 | 动词，描述行为 | `deletePage()`, `isPasswordValid()` |
| 类 | 名词，避免 Manager/Data | `Customer`, `WikiPage` |
| 布尔值 | is/has/can/should 前缀 | `isActive`, `hasPermission` |
| 枚举 | 含义明确 | `enum PaymentStatus { Pending, Completed, Failed }` |

**禁忌**：
- 不使用误导性名称（`accountList` 实际是 Map）
- 不造无意义区分（`ProductData` vs `ProductInfo`）
- 不使用不可发音的缩写（`genymdhms`）

#### 2.2 函数

```typescript
// 差：长函数，混合抽象层级
function processOrder(order: Order) {
  // 验证
  if (!order.items.length) throw new Error('Empty order');
  if (order.items.some(i => i.price < 0)) throw new Error('Invalid price');

  // 计算
  const subtotal = order.items.reduce((sum, i) => sum + i.price * i.qty, 0);
  const tax = subtotal * 0.1;

  // 保存
  const db = getDatabase();
  db.orders.insert({ ...order, subtotal, tax });

  // 通知
  sendEmail(order.customer, `Order total: ${subtotal + tax}`);
}

// 好：每个函数只做一件事，抽象层级一致
function processOrder(order: Order): void {
  validateOrder(order);
  const totals = calculateTotals(order);
  saveOrder(order, totals);
  notifyCustomer(order, totals);
}
```

**函数规则**：
- **短小**： ideally 不超过 20 行
- **只做一件事**：函数名应能拆解为"做 X 做 Y"，不能拆解才好
- **单一抽象层级**：不混合高层业务逻辑和底层细节
- **参数**：0 个最理想，1-2 个可接受，3 个以上需要强理由
- **无副作用**：函数不应悄悄修改全局状态

#### 2.3 注释

```typescript
// 差：用注释解释可以用代码表达的逻辑
// 检查员工是否有资格享受全额福利
if (employee.flags & HOURLY && employee.age > 65) { ... }

// 好：用代码自身表达意图
if (employee.isEligibleForFullBenefits()) { ... }
```

**注释原则**：
- **不要注释烂代码——重写它**
- 好注释：法律信息、意图说明、复杂正则的解释、TODO
- 坏注释：含糊其辞、冗余、误导、噪音、位置标记

#### 2.4 格式化

- **报纸隐喻**：高层概念在顶部，细节在底部
- **垂直密度**：相关代码应紧密排列
- **声明靠近使用**：变量声明靠近其使用位置
- **缩进一致**：结构可读性依赖缩进

#### 2.5 对象与数据结构

```typescript
// 差：违反得墨忒耳法则
order.getCustomer().getAddress().getCity().getName();

// 好：封装，不暴露内部结构
order.getDeliveryCity();
```

- **数据抽象**：用接口隐藏实现
- **得墨忒耳法则**：模块不应操纵其依赖对象的内部结构
- **DTO**：只有公开变量、没有方法的类

#### 2.6 错误处理

```typescript
// 差：返回错误码
function parseInput(input: string): number | null {
  if (!input) return null;
  const num = parseInt(input);
  return isNaN(num) ? null : num;
}

// 好：使用异常
function parseInput(input: string): number {
  if (!input) throw new ValidationError('Input is required');
  const num = parseInt(input);
  if (isNaN(num)) throw new ValidationError(`Invalid number: ${input}`);
  return num;
}
```

- **用异常替代返回码**：保持逻辑清晰
- **先写 try-catch-finally**：定义操作范围
- **不返回 null**：强迫调用方每次检查
- **不传入 null**：杜绝 NullPointerException

#### 2.7 测试

**TDD 定律**：
1. 在写出失败的单元测试之前，不要写生产代码
2. 不要写出超过"刚好失败"程度的单元测试
3. 不要写出超过"刚好通过"程度的生产代码
4. 不要对 index.ts 和 types.ts 写对应的单元测试代码，如果现有代码存在这种情况，则直接删除。

**FIRST 原则**：

| 原则 | 含义 |
|------|------|
| Fast（快速） | 测试必须快，否则没人愿意跑 |
| Independent（独立） | 测试之间不互相依赖 |
| Repeatable（可重复） | 任何环境下都能跑 |
| Self-Validating（自验证） | 布尔输出，不需要人工检查日志 |
| Timely（及时） | 在生产代码之前写 |

#### 2.8 类

- **单一职责（SRP）**：类应该只有一个变更理由
- **阶梯规则**：代码读起来像自上而下的叙事

#### 2.9 代码臭味

| 臭味 | 症状 | 处方 |
|------|------|------|
| 僵硬性 | 难以修改 | 解耦依赖，引入接口 |
| 脆弱性 | 改动一处，多处崩溃 | 缩小影响范围 |
| 不可移植性 | 难以复用 | 提取公共逻辑 |
| 粘滞性 | 做正确的事比做错误的事更难 | 简化正确路径 |
| 不必要的复杂性 | 过度设计 | YAGNI |
| 不必要的重复 | DRY 违反 | 提取共用函数/类 |

### 步骤 3：验证改造结果

```markdown
## 验证清单

- [ ] 函数是否不超过 20 行？
- [ ] 每个函数是否只做一件事？
- [ ] 所有名称是否可搜索、揭示意图？
- [ ] 是否通过让代码更清晰而避免了注释？
- [ ] 参数数量是否合理（≤ 2）？
- [ ] 是否有覆盖本次修改的测试？
- [ ] 所有测试通过？
- [ ] TypeScript 编译无错误？
```

## 危险信号

| 信号 | 说明 |
|------|------|
| 函数超过 50 行 | 违反"短小"原则，需拆分 |
| 函数需要注释才能理解 | 应重写函数，用命名表达意图 |
| 参数超过 3 个 | 考虑用对象参数封装 |
| 返回 null 或错误码 | 改为抛出异常 |
| 链式调用超过 3 层 | 违反得墨忒耳法则 |
| 类有超过一个变更理由 | 违反 SRP，需拆分 |
| 修改一处，多处失败 | 耦合过紧，需解耦 |

## 理由辩解

| 借口 | 打脸 |
|------|------|
| "这函数虽然长，但逻辑清晰" | 长度本身是问题，超过 20 行就应拆分 |
| "加个注释更快" | 注释是代码表达失败的标志，重写更持久 |
| "这个参数必须传这么多" | 用对象参数封装，`{ page, size, filter }` 而非 3 个独立参数 |
| "返回 null 是行业惯例" | 返回 null 迫使每个调用方做防御检查，用 Optional 或异常 |
| "这个 TODO 以后再说" | TODO 是债务标记，要么现在做，要么删除 |
| "先跑通再说，以后再重构" | 烂代码不会自动变好，技术债会复利增长 |

## 验证

完成时必须提供以下证据：

1. **改造清单** — 按维度列出所有改动
2. **前后对比** — 关键改动的前后代码对比
3. **验证结果** — TypeScript 编译 + 测试通过的证据

## 实现检查表

- [ ] 函数是否不超过 20 行？
- [ ] 每个函数是否只做一件事？
- [ ] 所有名称是否可搜索、揭示意图？
- [ ] 是否通过让代码更清晰而避免了注释？
- [ ] 参数数量是否 ≤ 2？
- [ ] 是否有覆盖本次修改的失败测试？
- [ ] 是否返回 null？（应抛异常）
- [ ] 是否违反得墨忒耳法则？（链式调用 > 3 层）

## 参考资料

详细指南见 `references/` 目录：

- [naming-conventions.md](references/naming-conventions.md) — TypeScript 命名规范详解
- [functions-and-comments.md](references/functions-and-comments.md) — 函数设计与注释原则
- [error-handling-and-testing.md](references/error-handling-and-testing.md) — 错误处理与测试原则
- [code-smells.md](references/code-smells.md) — 代码臭味与重构处方
