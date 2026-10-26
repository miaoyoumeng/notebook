---
name: typescript-clean
description: "基于 Robert C. Martin《Clean Code》原则，把能运行的 TypeScript 代码整理为整洁代码，覆盖命名、函数、注释、格式化、对象、错误处理、测试、类与代码臭味。当用户要求清理、重构、审查或整理 TypeScript 代码，提到可读性、命名、长函数、注释、格式、异常处理、单元测试、代码臭味，或直接引用 Clean Code、整洁代码时使用；不用于改变功能行为或修复缺陷。"
---

# typescript-clean

## 概述

把能运行的代码转化为整洁的代码。依据《Clean Code》，从命名、函数、注释、格式化、对象、错误处理、测试、类与代码臭味九个维度整理 TypeScript 代码。整理过程保持可观察行为不变；改变行为的需求不属于本技能的处理范围。

## 上下文层级

| 层级 | 信息 | 示例 |
|------|------|------|
| 通用 | 语言与运行时 | TypeScript、Node.js |
| 项目 | 工程结构与约定 | monorepo、ESLint、Prettier、package.json 脚本 |
| 具体 | 目标文件与模块 | src/utils/、src/services/ |

## 使用时机

在以下场景使用：

- 编写新的 TypeScript 代码，从一开始控制质量；
- 审查 Pull Request，按 Clean Code 原则给出可执行的修改意见；
- 重构遗留代码，识别并消除代码臭味；
- 统一团队编码标准。

以下场景不使用：

- 改变功能行为、修复业务缺陷或调整性能；
- 处理自动生成代码；
- 用户未提出整洁化需求，仅在讨论代码。

## 编码四原则

1. 先理解再修改：读取目标代码、调用方与测试，明确改动意图。
2. 简洁优先：用最少代码解决问题，不做推测性设计。
3. 精准修改：只改动需要改的代码，不顺手扩大范围。
4. 目标驱动：先定义成功标准，改完按标准验证。

## 流程

### 1. 分析代码现状

读取目标文件、相邻模块、调用方与现有测试。按`代码分析`章节的维度表逐项检查，按该章节的输出格式记录问题。涉及命名、函数或代码臭味等细节时，加载`参考资料`中对应的文档。

### 2. 执行整洁化改造

按风险从低到高推进，一次完成一组相关改动。每完成一组，保留可验证的中间状态。

#### 2.1 有意义的命名

```typescript
// 差：不揭示意图
const d = getDays();
const list = getAccountData();

// 好：名称即文档
const elapsedTimeInDays = calculateElapsedTime(startDate, endDate);
const activeAccounts = getActiveAccounts();
```

| 元素 | 规则 | TypeScript 示例 |
|------|------|----------------|
| 变量 | 名词，揭示意图 | `elapsedTimeInDays` |
| 函数 | 动词，描述行为 | `deletePage()`、`isPasswordValid()` |
| 类 | 名词，避免 Manager/Data | `Customer`、`WikiPage` |
| 布尔值 | is/has/can/should 前缀 | `isActive`、`hasPermission` |
| 枚举 | 含义明确 | `enum PaymentStatus { Pending, Completed, Failed }` |

禁忌：

- 使用误导性名称，例如 `accountList` 实际是 Map；
- 制造无意义区分，例如 `ProductData` 与 `ProductInfo`；
- 使用不可发音的缩写，例如 `genymdhms`。

#### 2.2 函数

```typescript
// 差：长函数，混合抽象层级
const processOrder = (order: Order) => {
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
};

// 好：每个函数只做一件事，抽象层级一致
const processOrder = (order: Order): void => {
  validateOrder(order);
  const totals = calculateTotals(order);
  saveOrder(order, totals);
  notifyCustomer(order, totals);
};
```

规则：

- 短小：目标不超过 20 行；超过 20 行优先拆分，超过 50 行必须拆分。
- 只做一件事：函数名无法拆解为「做 X 做 Y」。
- 单一抽象层级：不混合高层业务逻辑与底层细节。
- 参数：0 个最理想，1-2 个可接受；3 个需要强理由；4 个及以上用对象参数封装。
- 无副作用：不在函数内悄悄修改全局状态；有副作用时在函数名中体现。

#### 2.3 注释

```typescript
// 差：用注释解释可以用代码表达的逻辑
// 检查员工是否有资格享受全额福利
if (employee.flags & HOURLY && employee.age > 65) { ... }

// 好：用代码自身表达意图
if (employee.isEligibleForFullBenefits()) { ... }
```

规则：

- 不注释烂代码，重写它。
- 好注释：法律信息、意图说明、复杂正则的解释、TODO、警告。
- 坏注释：含糊其辞、冗余、误导、注释掉的代码、噪音、位置标记。
- 注释掉的代码直接删除，由版本控制保留历史。

#### 2.4 格式化

- 报纸隐喻：高层概念在顶部，细节在底部。
- 垂直密度：相关代码紧密排列。
- 声明靠近使用：变量声明靠近其使用位置。
- 缩进一致：结构可读性依赖缩进。
- 自上而下：代码像叙事，先主流程后实现细节。

#### 2.5 对象与数据结构

```typescript
// 差：违反得墨忒耳法则
order.getCustomer().getAddress().getCity().getName();

// 好：封装，不暴露内部结构
order.getDeliveryCity();
```

规则：

- 数据抽象：用接口隐藏实现。
- 得墨忒耳法则：模块不操纵其依赖对象的内部结构。
- DTO：只有公开变量、没有方法的类。

#### 2.6 错误处理

```typescript
// 差：返回错误码
const parseInput = (input: string): number | null => {
  if (!input) return null;
  const num = parseInt(input);
  return isNaN(num) ? null : num;
};

// 好：使用异常
const parseInput = (input: string): number => {
  if (!input) throw new ValidationError('Input is required');
  const num = parseInt(input);
  if (isNaN(num)) throw new ValidationError(`Invalid number: ${input}`);
  return num;
};
```

规则：

- 用异常替代返回码，保持主逻辑清晰。
- 先写 try-catch-finally，界定资源与错误处理范围。
- 不返回 null：无结果时抛异常，集合无结果时返回空集合。
- 不传入 null：用类型系统禁止 null 或 undefined 参数。

#### 2.7 测试

TDD 定律：

1. 在写出失败的单元测试之前，不写生产代码。
2. 单元测试只写到刚好失败；编译失败也算失败。
3. 生产代码只写到刚好通过当前失败的测试。
4. 不为 `index.ts` 与 `types.ts` 编写对应单元测试；已有此类测试直接删除。

FIRST 原则：

| 原则 | 含义 |
|------|------|
| Fast（快速） | 测试必须快，否则没人愿意跑 |
| Independent（独立） | 测试之间不互相依赖 |
| Repeatable（可重复） | 任何环境下都能跑 |
| Self-Validating（自验证） | 布尔输出，不需要人工检查日志 |
| Timely（及时） | 在生产代码之前写 |

#### 2.8 类

- 单一职责（SRP）：类只有一个变更理由。
- 按职责拆分大类，避免 God Class。

#### 2.9 代码臭味

| 臭味 | 症状 | 处方 |
|------|------|------|
| 僵硬性 | 难以修改 | 解耦依赖，引入接口 |
| 脆弱性 | 改动一处，多处崩溃 | 缩小影响范围 |
| 不可移植性 | 难以复用 | 提取公共逻辑 |
| 粘滞性 | 做正确的事比做错误的事更难 | 简化正确路径，使用自动化工具 |
| 不必要的复杂性 | 过度设计 | YAGNI |
| 不必要的重复 | 违反 DRY | 提取共用函数或类 |

### 3. 验证改造结果

按`验证`章节执行类型检查、Lint、格式检查与测试；对照`验证清单`与`实现检查表`确认改动范围与代码质量。出现回归时，回滚最后一项高风险改动，保留其余安全改动，并记录未完成项。

## 代码分析

| 维度 | 检查点 |
|------|--------|
| 命名 | 名称是否揭示意图？是否可搜索？是否产生歧义？ |
| 函数 | 是否短小？是否只做一件事？参数数量？是否有副作用？ |
| 注释 | 是否在用注释解释本该用代码表达的内容？ |
| 格式化 | 代码是否像报纸一样从高层到底层阅读？ |
| 对象与数据结构 | 是否暴露内部结构？是否违反得墨忒耳法则？ |
| 错误处理 | 是否使用异常而非返回码？是否返回或传入 null？ |
| 测试 | 是否符合 TDD 与 FIRST？是否覆盖本次修改的行为？ |
| 类 | 是否只有一个变更理由？ |
| 代码臭味 | 是否存在僵硬性、脆弱性、不必要的复杂性或重复？ |

输出格式：

```markdown
### 需要改进
1. [维度] 具体问题 → 建议改法
2. [维度] 具体问题 → 建议改法

### 已符合原则
- [维度] 好的做法（保留）
```

## 验证清单

- [ ] 已读取目标代码、调用方与相关测试
- [ ] 已有覆盖本次改动的测试，且测试通过
- [ ] TypeScript 类型检查通过
- [ ] ESLint 检查通过
- [ ] Prettier 格式检查通过
- [ ] 改动未改变可观察行为
- [ ] 改动清单与前后对比已记录
- [ ] 未完成项与回滚项已说明

## 危险信号

| 信号 | 说明 |
|------|------|
| 函数超过 50 行 | 违反短小原则，必须拆分 |
| 函数需要注释才能理解 | 重写函数，用命名表达意图 |
| 参数达到 3 个 | 检查能否合并或封装；达到 4 个必须用对象参数 |
| 返回 null 或错误码 | 改为抛出异常；集合无结果时返回空集合 |
| 链式调用超过 3 层 | 违反得墨忒耳法则 |
| 类有超过一个变更理由 | 违反 SRP，按职责拆分 |
| 修改一处，多处失败 | 耦合过紧，解耦依赖 |
| 用 any、类型断言或 @ts-ignore 消除类型错误 | 类型错误说明契约受影响，调整实现而非掩盖 |
| 为通过检查而弱化或删除有效测试 | 测试是行为基线，不得弱化 |

## 理由辩解

| 借口 | 判断 |
|------|------|
| 这函数虽然长，但逻辑清晰 | 长度本身是问题，超过 20 行就应拆分 |
| 加个注释更快 | 注释是代码表达失败的标志，重写更持久 |
| 这个参数必须传这么多 | 3 个参数需要强理由；4 个及以上用对象参数封装，例如 `{ page, size, filter }` |
| 返回 null 是行业惯例 | 返回 null 迫使每个调用方防御检查，改用异常或空集合 |
| 这个 TODO 以后再说 | TODO 是债务标记，本次能处理的立即处理，否则删除 |
| 先跑通再说，以后再重构 | 烂代码不会自动变好，本次改动内保持整洁 |

## 验证

按项目已有脚本执行，顺序如下：

1. 类型检查：`pnpm exec tsc --noEmit`
2. Lint：`pnpm exec eslint <改动文件或目录>`
3. 格式检查：`pnpm exec prettier --check <改动文件或目录>`
4. 测试：`pnpm test`；需要指定范围时使用项目测试命令，例如 `pnpm exec vitest run <测试文件>`

`package.json` 已定义对应脚本时，优先使用项目脚本。命令缺失或无法运行时，记录原因并缩小验证范围，不声称已通过。

判定标准：

- 全部检查通过，保留改动；
- 出现新错误，回滚最后一项高风险改动并重新验证；
- 仅格式或命名问题，修正后重跑对应检查。

结果报告必须包含：

1. 改造清单：按维度列出所有改动；
2. 前后对比：关键改动的前后代码；
3. 验证结果：类型检查、Lint、格式检查与测试的实际输出。

## 实现检查表

- [ ] 函数不超过 20 行
- [ ] 每个函数只做一件事
- [ ] 名称揭示意图、可搜索、不误导
- [ ] 代码自身表达意图，未用注释解释烂代码
- [ ] 参数不超过 2 个；3 个有强理由；4 个及以上使用对象参数
- [ ] 未返回 null，未传入 null
- [ ] 链式调用不超过 3 层
- [ ] 类只有一个变更理由
- [ ] 无重复逻辑、死代码与未使用分支
- [ ] if/else 嵌套不超过 3 层

## 参考资料

- [naming-conventions.md](references/naming-conventions.md)：命名原则、按返回值命名、TypeScript 命名约定与反模式。
- [functions-and-comments.md](references/functions-and-comments.md)：函数拆分、参数设计、副作用控制、注释取舍。
- [error-handling-and-testing.md](references/error-handling-and-testing.md)：异常分层、null 处理、TDD 与 FIRST 原则、测试反模式。
- [code-smells.md](references/code-smells.md)：六类代码臭味的症状与重构处方。
