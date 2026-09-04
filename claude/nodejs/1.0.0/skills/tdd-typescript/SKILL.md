---
name: "tdd-typescript"
description: "TypeScript TDD 单元测试 skill，基于 Vitest + Vue 3 + TDesign + Vite 技术栈。严格遵循 TDD 铁律：没有失败测试之前禁止写产品代码。当用户要求编写单元测试、实践 TDD、修复 bug、提升测试覆盖率、生成 mock/stub 时使用此 skill。"
---

# TDD TypeScript

TypeScript + Vue 3 + TDesign + Vite 项目的严格 TDD 工作流，基于 Vitest。

---

## 铁律

```
没有失败的测试之前，禁止写产品代码
```

**违反铁律的惩罚：**
- 已经写了产品代码？删掉。从头开始。
- 不要保留"作为参考"
- 不要在写测试时"适配"它
- 不要看它
- 删除就是删除

```
从测试出发重新实现。句号。
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

## Red-Green-Refactor

```
RED ──→ 验证失败 ──→ GREEN ──→ 验证通过 ──→ REFACTOR ──→ 验证通过 ──→ 下一个
   ↑                                                           │
   └───────────────────────────────────────────────────────────┘
```

```dot
digraph tdd_cycle {
    rankdir=LR;
    red [label="RED\nWrite failing test", shape=box, style=filled, fillcolor="#ffcccc"];
    verify_red [label="Verify fails\ncorrectly", shape=diamond];
    green [label="GREEN\nMinimal code", shape=box, style=filled, fillcolor="#ccffcc"];
    verify_green [label="Verify passes\nAll green", shape=diamond];
    refactor [label="REFACTOR\nClean up", shape=box, style=filled, fillcolor="#ccccff"];
    next [label="Next", shape=ellipse];

    red -> verify_red;
    verify_red -> green [label="yes"];
    verify_red -> red [label="wrong\nfailure"];
    green -> verify_green;
    verify_green -> refactor [label="yes"];
    verify_green -> green [label="no"];
    refactor -> verify_green [label="stay\ngreen"];
    verify_green -> next;
    next -> red;
}

### RED — 写失败测试

写一个最小的测试，描述**期望的行为**。

**好：**
```typescript
// cart.test.ts
import { describe, it, expect } from 'vitest';
import { Cart } from './cart';

describe('Cart.addItem', () => {
  it('should reject quantity of zero or negative', () => {
    const cart = new Cart();
    expect(() =>
      cart.addItem({ id: 'sku-1', name: 'Widget', price: 9.99, qty: 0 })
    ).toThrow('Quantity must be positive');
  });
});
```
- 清晰的名称
- 测真实行为
- 一个测试一个行为
- 真实代码（非 mock，除非不可避免）

**坏：**
```typescript
// ❌ 模糊的名字，测试的是 mock 而不是代码
it('addItem works', () => {
  const mockAdd = vi.fn();
  mockAdd();
  expect(mockAdd).toHaveBeenCalled();
});
```

**要求：**
- 一个行为
- 清晰的名称
- 真实代码（mock 只在不可避免时使用）

### 验证 RED — 必须看它失败

**强制。永不跳过。**

```bash
pnpm vitest run path/to/cart.test.ts
```

确认：
- 测试**失败**（不是报错）
- 失败信息**符合预期**
- 失败原因**是功能缺失**（不是语法错误）

**测试通过了？** 你测的是已存在的行为。修测试。

**测试报错了？** 修错误，重新运行，直到它**正确地失败**。

### GREEN — 最小实现

写能让测试通过的**最简代码**。

**好：**
```typescript
// cart.ts
export class Cart {
  addItem(item: CartItem): void {
    if (item.qty <= 0) throw new Error('Quantity must be positive');
    this.items.push({ ...item });
  }
}
```
仅仅足够让测试通过。

**坏：**
```typescript
// ❌ 过度工程 YAGNI
export class Cart {
  addItem(item: CartItem, options?: {
    maxQty?: number;
    onAdd?: () => void;
    retry?: { attempts: number; backoff: 'linear' | 'exponential' };
  }): void { /* ... */ }
}
```

**不要：**
- 添加功能
- 重构其他代码
- 超出测试范围的"改进"

### 验证 GREEN — 必须看它通过

**强制。**

```bash
pnpm vitest run path/to/cart.test.ts
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
| **最小** | 一个行为。名字有"and"就拆开 | `it('validates email and domain and whitespace')` |
| **清晰** | 名字描述行为 | `it('test1')` |
| **体现意图** | 展示期望的 API | 掩盖代码应该做什么 |

---

## 为什么顺序重要

> "我先写代码再补测试验证它有效"

写完代码再补的测试立即通过。**立即通过什么都证明不了：**
- 可能测的是错误的东西
- 可能测的是实现而不是行为
- 可能遗漏了你没想到的边界
- 你从来没看到它捕获 bug

测试先行强制你看到测试失败，证明它**确实在测某个东西**。

> "删除 X 小时的工作太浪费了"

**沉没成本谬误。** 时间已经过去了。你现在的选择：
- 删除并用 TDD 重写（X 小时，**高信心**）
- 留着再补测试（30 分钟，**低信心**，可能有 bug）

"浪费"是保留你**无法信任**的代码。没有真实测试的代码就是技术债。

> "TDD 太教条了，实用主义应该灵活"

**TDD 就是实用的：**
- 提交前发现 bug（比事后调试快）
- 防止回归（测试立即捕获破坏）
- 文档化行为（测试展示如何使用代码）
- 使重构可行（随意修改，测试捕获破坏）

"实用的捷径" = 在生产环境调试 = 更慢。

---

## 常见合理化借口

| 借口 | 真相 |
|------|------|
| "太简单不需要测试" | 简单代码也会崩。测试 30 秒。 |
| "我之后再补测试" | 立即通过的测试什么都证明不了。 |
| "已经手动测试过了" | 临时的 ≠ 系统的。无记录，无法重跑。 |
| "删除 X 小时工作太浪费" | 沉没成本谬误。保留未验证代码是技术债。 |
| "保留作参考，但先写测试" | 你会去适配它。这就是后补测试。删除就是删除。 |
| "需要先探索" | 可以。但探索完就丢弃，用 TDD 重新开始。 |
| "测试很难写 = TDD 不适合" | 难测试 = 难使用。简化接口。 |
| "TDD 会让我变慢" | TDD 比调试快。实用 = 测试先行。 |
| "手动测试更快" | 手动测试证明不了边界。每次改动都要重测。 |
| "现有代码没测试" | 你在改进它。为现有代码补测试。 |

---

## 红旗 — 立即停止，从头开始

- 在测试之前写代码
- 实现后再写测试
- 测试立即通过
- 说不清测试为什么失败
- "以后再补"测试
- 合理化"就这一次"
- "我已经手动测试过了"
- "保留作参考"或"适配现有代码"
- "已经花了 X 小时，删掉太浪费"
- "TDD 太教条，我在实用"
- "这次不一样因为..."

**以上任何一项都意味着：删除代码。用 TDD 重新开始。**

---

## 示例：Bug 修复

**Bug：** 空邮箱被接受

**RED**
```typescript
// form.test.ts
import { describe, it, expect } from 'vitest';
import { submitForm } from './form';

describe('submitForm', () => {
  it('should reject empty email', async () => {
    const result = await submitForm({ email: '' });
    expect(result.error).toBe('Email required');
  });
});
```

**验证 RED**
```bash
$ pnpm vitest run form.test.ts
FAIL: expected 'Email required', got undefined
```
正确地失败 — 进入 GREEN。

**GREEN**
```typescript
// form.ts
export async function submitForm(data: FormData) {
  if (!data.email?.trim()) {
    return { error: 'Email required' };
  }
  // ...
}
```

**验证 GREEN**
```bash
$ pnpm vitest run form.test.ts
PASS
```

**REFACTOR**
如果有多个字段，提取校验函数。

---

## Vue 3 组件测试（TDD）

### Composable 测试

```typescript
// useCounter.test.ts
import { describe, it, expect } from 'vitest';
import { useCounter } from './useCounter';

describe('useCounter', () => {
  it('should start with initial value', () => {
    const { count } = useCounter(5);
    expect(count.value).toBe(5);
  });

  it('should increment count', () => {
    const { count, increment } = useCounter(0);
    increment();
    expect(count.value).toBe(1);
  });
});
```

### TDesign 组件测试

```typescript
// UserTable.test.ts
import { describe, it, expect } from 'vitest';
import { mount } from '@vue/test-utils';
import TDesign from 'tdesign-vue-next';
import UserTable from './UserTable.vue';

const mockUsers = [
  { id: '1', name: 'Alice', email: 'alice@example.com' },
  { id: '2', name: 'Bob', email: 'bob@example.com' },
];

describe('UserTable', () => {
  it('should render user rows', () => {
    const wrapper = mount(UserTable, {
      props: { users: mockUsers },
      global: { plugins: [TDesign] },
    });
    expect(wrapper.findAll('tbody tr')).toHaveLength(2);
  });

  it('should show empty state when no users', () => {
    const wrapper = mount(UserTable, {
      props: { users: [] },
      global: { plugins: [TDesign] },
    });
    expect(wrapper.text()).toContain('暂无数据');
  });
});
```

---

## 测试反模式（必读）

写 mock 或添加测试工具时，参考 `references/testing-anti-patterns.md`。

**铁律：**
1. 永不测试 mock 行为
2. 永不在生产类上添加仅测试用方法
3. 永不在未理解依赖的情况下使用 mock

**常见反模式：**
- 断言 `*-mock` test ID → 测试的是 mock 而不是组件
- 类的方法只在测试文件中调用 → 放到测试工具里
- Mock 设置超过测试逻辑的一半 → 考虑集成测试
- Mock "保险起见" → 先理解依赖再 mock

**详细门控函数见 `references/testing-anti-patterns.md`。**

---

## 验证清单

完成工作前必须全部打勾：

- [ ] 每个新函数/方法都有测试
- [ ] 亲眼看过每个测试**失败**
- [ ] 每个测试因**预期原因**失败（功能缺失，不是 typo）
- [ ] 为每个测试写**最小代码**通过
- [ ] **所有测试通过**
- [ ] **输出干净**（无 error、无 warning）
- [ ] 测试用**真实代码**（mock 只在不可避免时使用）
- [ ] **边界场景和错误**已覆盖

不能全打勾？你跳过了 TDD。**从头开始。**

---

## 关键工具

| 工具 | 用途 | 使用方式 |
|------|------|---------|
| `test_generator.py` | 分析源码生成测试桩 | `uv run python scripts/test_generator.py --input src.ts` |
| `coverage_analyzer.py` | 解析 LCOV/JSON 覆盖率 | `uv run python scripts/coverage_analyzer.py --report lcov.info --threshold 80` |
| `tdd_workflow.py` | 引导 Red-Green-Refactor | `uv run python scripts/tdd_workflow.py --phase red --test cart.test.ts` |
| `fixture_generator.py` | 生成夹具和 mock | `uv run python scripts/fixture_generator.py --entity User --count 5` |

**注意：** 这些工具生成的是**测试桩**。真正写测试必须走 TDD 铁律流程。

---

## 输入要求

### 测试生成
- TypeScript 源代码（文件路径或粘贴内容）
- 可选：覆盖范围（单元、组件、composable）

### 覆盖率分析
- 覆盖率报告文件（LCOV、JSON 格式）
- 可选：源代码文件路径
- 可选：目标覆盖率阈值（默认 80%）

### TDD 工作流
- 功能需求或用户故事
- 当前阶段（RED / GREEN / REFACTOR）
- 测试代码和实现状态

---

## 测试文件命名规范

```
src/
├── utils/
│   ├── ……
│   └── validateEmail.ts
├── composables/
│   ├── ……
│   └── useCounter.ts
├── components/
│   ├── ……
│   └── UserTable.vue
└── services/
    ├── ……
    └── payment.ts
test/
├── utils/
│   ├── …….mock.test.ts
│   ├── …….real.test.ts
│   ├── validateEmail.mock.test.ts
│   └── validateEmail.real.test.ts
├── composables/
│   ├── …….mock.test.ts
│   ├── …….real.test.ts
│   ├── useCounter.mock.test.ts
│   └── useCounter.real.test.ts
├── components/
│   ├── …….mock.test.ts
│   ├── …….real.test.ts
│   ├── UserTable.mock.test.ts
│   └── UserTable.real.test.ts
└── services/
    ├── …….mock.test.ts
    ├── …….real.test.ts
    ├── payment.mock.test.ts
    └── payment.real.test.ts
```

- 测试文件放在与目录`src`同级的`test` 目录下
- mock测试用例文件与源文件同名，后缀 `*.mock.test.ts`
- 真实测试用例文件与源文件同名，后缀 `*.real.test.ts`

---

## Mock 策略

### Vitest Mock

```typescript
// Mock 模块级依赖（仅 mock 真正需要隔离的部分）
vi.mock('./api', () => ({
  fetchUsers: vi.fn().mockResolvedValue([{ id: 1, name: 'Alice' }]),
}));

// 使用 beforeEach 确保 mock 干净
beforeEach(() => {
  vi.clearAllMocks();
});
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
- "这个可能很慢，最好 mock"
- 不理解依赖链就 mock

---

## 覆盖率阈值

| 类型 | 阈值 | 说明 |
|------|------|------|
| 行覆盖率 | 80%+ | 项目基线 |
| 分支覆盖率 | 75%+ | 比行覆盖率更有意义 |
| 函数覆盖率 | 90%+ | 公共 API 应被测试 |
| 关键路径 | 100% | auth、支付、数据校验 |

---

## 调试集成

**发现 bug？写一个失败测试复现它。走 TDD 循环。**

测试**既证明修复又防止回归**。

**永不在没有测试的情况下修 bug。**

---

## 卡住时

| 问题 | 解法 |
|------|------|
| 不知道怎么测试 | 写期望的 API。先写断言。问用户。 |
| 测试太复杂 | 设计太复杂。简化接口。 |
| 必须 mock 一切 | 代码耦合太重。用依赖注入。 |
| 测试 setup 巨大 | 提取 helper。还复杂？简化设计。 |

---

## 限制

| 范围 | 细节 |
|------|------|
| 单元测试重点 | 集成和 E2E 测试需要不同模式 |
| 静态分析 | 不能运行测试或测量运行时行为 |
| 语言支持 | 专注于 TypeScript + Vue 3 |
| 框架支持 | Vitest |
| 报告格式 | LCOV、JSON |
| 生成测试 | 提供桩，复杂逻辑需人工审核 |

---

## 技术栈

- **运行时**: Node.js 22+
- **包管理器**: pnpm 9+
- **构建工具**: Vite 5+
- **框架**: Vue 3.3+ (Composition API)
- **UI 库**: TDesign Vue Next
- **测试框架**: Vitest 0.34+
- **组件测试**: @vue/test-utils 2+
- **覆盖率**: v8 (Vitest 内置)

---

## 最终规则

```
产品代码 → 必须存在测试且先失败
否则 → 不是 TDD
```

**无用户许可不得例外。**
