# 测试指南

## 代码质量检查清单

在标记完成之前：
- [ ] 代码可读且命名清晰
- [ ] 函数简短（<50 行）
- [ ] 文件职责单一（<800 行）
- [ ] 无过深嵌套（>4 层）
- [ ] 正确的错误处理
- [ ] 无硬编码值（使用常量或配置）
- [ ] 无可变操作（使用不可变模式）

## 测试框架

- **Vitest** - 单元测试框架

---

## 最低测试覆盖率：80%

### 测试类型（全部必需）

1. **单元测试（Unit Tests）** - 针对单个函数、工具方法、组件
2. **集成测试（Integration Tests）** - 针对 API 接口、数据库操作
3. **端到端测试（E2E Tests）** - 覆盖关键用户流程

---

## 测试驱动开发（TDD）

### 强制工作流程

1. **先编写测试（RED）** - 从一个失败的测试开始
2. **运行测试** - 应该失败
3. **编写最小实现（GREEN）** - 只写足以让测试通过的代码
4. **运行测试** - 应该通过
5. **重构（IMPROVE）** - 优化代码质量
6. **验证覆盖率（80%+）** - 确保足够的测试覆盖

### TDD 循环示意图

```
RED → GREEN → REFACTOR → (repeat)
 ↓       ↓        ↓
失败    通过     优化
```

---

## 测试最佳实践

### 1. 单元测试

针对单个函数或组件进行测试：

```typescript
import { describe, it, expect } from 'vitest'

describe('工具函数测试', () => {
  it('应该正确计算结果', () => {
    const result = add(1, 2)
    expect(result).toBe(3)
  })

  it('应该处理边界情况', () => {
    expect(() => divide(1, 0)).toThrow()
  })
})
```

### 2. 集成测试

测试多个模块协作：

```typescript
describe('API 集成测试', () => {
  it('应该成功创建用户', async () => {
    const user = await createUser({ name: 'test' })
    expect(user.id).toBeDefined()
    expect(user.name).toBe('test')
  })
})
```

### 3. E2E 测试

测试完整用户流程：

```typescript
describe('用户登录流程', () => {
  it('应该完成登录', async () => {
    await page.goto('/login')
    await page.fill('#email', 'test@example.com')
    await page.fill('#password', 'password')
    await page.click('button[type="submit"]')
    await expect(page).toHaveURL('/dashboard')
  })
})
```

---

## 测试失败排查

1. 使用 **tdd-guide** agent
2. 检查测试隔离性（测试之间不应相互依赖）
3. 验证 mocks 是否正确
4. 修复实现，而不是测试（除非测试本身有问题）

---

## 测试质量检查清单

在标记测试完成之前：

- [ ] 所有公共函数都有单元测试
- [ ] 所有 API 接口都有集成测试
- [ ] 关键用户流程都有 E2E 测试
- [ ] 边界情况已覆盖（null、空值、无效值）
- [ ] 错误路径已测试（不仅是快乐路径）
- [ ] 外部依赖使用 mocks
- [ ] 测试相互独立（无共享状态）
- [ ] 测试名称描述了测试内容
- [ ] 断言具体且有意义
- [ ] 覆盖率 80%+（通过覆盖率报告验证）

---

## 测试反模式（避免）

### ❌ 测试相互依赖

```typescript
// 错误示例
test('创建用户', () => { /* ... */ })
test('更新同一用户', () => { /* 依赖上一个测试创建的用户 */ })
```

### ✅ 独立测试

```typescript
// 正确示例
test('更新用户', () => {
  const user = createTestUser() // 每个测试自己创建数据
  // 测试逻辑
})
```

### ❌ 测试内部实现

```typescript
// 错误示例
expect(component.state.count).toBe(5)
```

### ✅ 测试用户可见行为

```typescript
// 正确示例
expect(screen.getByText('Count: 5')).toBeInTheDocument()
```

---

## 覆盖率报告

```bash
# 运行带覆盖率的测试
pnpm run test:coverage

# 查看 HTML 报告
open coverage/index.html
```

### 必需的阈值

- **分支覆盖率**: 80%+
- **函数覆盖率**: 80%+
- **行覆盖率**: 80%+
- **语句覆盖率**: 80%+

---

## 持续测试

```bash
# 开发时使用 watch 模式
pnpm test -- --watch

# 提交前运行（通过 git hook）
pnpm test && pnpm run lint

# CI/CD 集成
pnpm test -- --coverage --ci
```

---

## Agent 支持

- **tdd-guide** - 在开发新功能时主动使用，强制执行"先写测试"的原则

---

**记住**：没有测试就没有代码。测试不是可选项。它是实现自信重构、快速开发和生产环境可靠性的安全网。
