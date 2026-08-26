# 测试反模式

**加载时机：** 写或改测试、添加 mock、或在生产类上加仅测试用方法时。

## 核心原则

> 测试必须验证真实行为，不是 mock 行为。

**遵循严格的 TDD 可以防止这些反模式。**

---

## 铁律

```
1. 永不测试 mock 行为
2. 永不在生产类上添加仅测试用方法
3. 永不在未理解依赖的情况下使用 mock
```

---

## 反模式 1：测试 Mock 行为

**违规：**
```typescript
// ❌ 测试 mock 是否存在，而不是真实行为
test('renders sidebar', () => {
  const wrapper = mount(Page);
  expect(wrapper.find('[data-testid="sidebar-mock"]').exists()).toBe(true);
});
```

**为什么错：**
- 你在验证 mock 是否生效，不是组件是否工作
- mock 在测试就过，mock 不在就失败
- 什么真实行为都没告诉你

**修正：**
```typescript
// ✅ 测试真实组件，或者不 mock 它
test('renders sidebar', () => {
  const wrapper = mount(Page);  // 不 mock sidebar
  expect(wrapper.find('[role="navigation"]').exists()).toBe(true);
});

// 或者如果 sidebar 必须 mock：
// 不要断言 mock — 测试 Page 在 sidebar 存在时的行为
```

### 门控函数

```
断言任何 mock 元素之前：
  问："我在测试真实组件行为还是仅 mock 是否存在？"

  如果是测试 mock 是否存在：
    停下 — 删掉断言或不 mock 该组件
    测试真实行为
```

---

## 反模式 2：生产类中的仅测试用方法

**违规：**
```typescript
// ❌ destroy() 仅在测试中使用
class Session {
  async destroy() {  // 看起来像生产 API！
    await this._workspaceManager?.destroyWorkspace(this.id);
    // ... 清理
  }
}

// 在测试中
afterEach(() => session.destroy());
```

**为什么错：**
- 生产类被测试代码污染
- 在生产环境意外调用很危险
- 违反 YAGNI 和关注点分离
- 混淆对象生命周期和实体生命周期

**修正：**
```typescript
// ✅ 测试工具处理测试清理
// Session 没有 destroy() — 它在生产中是无状态的

// 在 test-utils/
export async function cleanupSession(session: Session) {
  const workspace = session.getWorkspaceInfo();
  if (workspace) {
    await workspaceManager.destroyWorkspace(workspace.id);
  }
}

// 在测试中
afterEach(() => cleanupSession(session));
```

### 门控函数

```
添加任何方法到生产类之前：
  问："这是否仅被测试使用？"

  如果是：
    停下 — 不要加
    放到测试工具里

  问："这个类拥有这个资源的生命周期吗？"

  如果不是：
    停下 — 方法放错类了
```

---

## 反模式 3：不理解依赖就 mock

**违规：**
```typescript
// ❌ mock 破坏了测试逻辑
test('detects duplicate server', () => {
  // mock 阻止了测试依赖的 config 写入！
  vi.mock('./toolCatalog', () => ({
    discoverAndCacheTools: vi.fn().mockResolvedValue(undefined),
  }));

  await addServer(config);
  await addServer(config);  // 应该抛错 — 但不会！
});
```

**为什么错：**
- 被 mock 的方法有测试依赖的副作用（写 config）
- "保险起见"过度 mock 破坏实际行为
- 测试因错误原因通过或神秘失败

**修正：**
```typescript
// ✅ 在正确层级 mock
test('detects duplicate server', () => {
  // 只 mock 慢的部分，保留测试需要的行为
  vi.mock('./slowServerStarter');

  await addServer(config);  // config 已写入
  await addServer(config);  // 重复检测生效 ✓
});
```

### 门控函数

```
mock 任何方法之前：
  停下 — 先不要 mock

  1. 问："真实方法有什么副作用？"
  2. 问："这个测试依赖这些副作用中的哪些？"
  3. 问："我是否完全理解这个测试需要什么？"

  如果依赖副作用：
    在更低层 mock（真正慢/外部的操作）
    或使用保留必要行为的测试替身
    而不是测试依赖的高层方法

  如果不确定测试需要什么：
    先用真实实现跑测试
    观察实际需要发生什么
    然后在正确层级加最小 mock

  红旗：
    - "我保险起见 mock 这个"
    - "这个可能很慢，最好 mock"
    - 不理解依赖链就 mock
```

---

## 反模式 4：不完整的 Mock

**违规：**
```typescript
// ❌ 部分 mock — 只有你认为需要的字段
const mockResponse = {
  status: 'success',
  data: { userId: '123', name: 'Alice' },
  // 缺失：下游代码使用的 metadata
};

// 之后：当代码访问 response.metadata.requestId 时崩了
```

**为什么错：**
- **部分 mock 隐藏结构假设** — 你只 mock 了你知道的字段
- **下游代码可能依赖你没包含的字段** — 静默失败
- **测试通过但集成失败** — mock 不完整，真实 API 完整
- **虚假信心** — 测试证明不了真实行为

**铁律：** mock 的必须是完整的数据结构，就像真实 API 返回的一样，而不只是你当前测试用的字段。

**修正：**
```typescript
// ✅ 镜像真实 API 的完整性
const mockResponse = {
  status: 'success',
  data: { userId: '123', name: 'Alice' },
  metadata: { requestId: 'req-789', timestamp: 1234567890 },
  // 真实 API 返回的所有字段
};
```

### 门控函数

```
创建 mock 响应之前：
  检查："真实 API 响应包含什么字段？"

  行动：
    1. 查看真实 API 响应的文档/示例
    2. 包含系统下游可能消费的所有字段
    3. 验证 mock 完全匹配真实响应 schema

  关键：
    如果你在创建 mock，你必须理解整个结构
    部分 mock 在代码依赖被省略字段时会静默失败

  如果不确定：包含所有文档化字段
```

---

## 反模式 5：测试当作后续工作

**违规：**
```
✅ 实现完成
❌ 没写测试
"准备好测试了"
```

**为什么错：**
- 测试是实现的一部分，不是可选的后续
- TDD 本来就会抓到这个
- 没有测试不能声称完成

**修正：**
```
TDD 循环：
1. 写失败测试
2. 实现到通过
3. 重构
4. 然后才能声称完成
```

---

## Mock 变得过于复杂时

**警告信号：**
- Mock 设置比测试逻辑长
- Mock 一切才能让测试通过
- Mock 缺少真实组件有的方法
- mock 改动时测试就崩

**用户的提问：** "我们这里真的需要 mock 吗？"

**考虑：** 用真实组件的集成测试往往比复杂 mock 更简单

---

## TDD 如何防止这些反模式

**为什么 TDD 有效：**
1. **先写测试** → 强制你思考到底在测什么
2. **看它失败** → 确认测试测的是真实行为，不是 mock
3. **最小实现** → 测试专用方法不会悄悄爬进来
4. **真实依赖** → 在 mock 之前你能看到测试真正需要什么

**如果你在测试 mock 行为，你违反了 TDD** — 你在没有先看到测试对真实代码失败之前就加了 mock。

---

## 快速参考

| 反模式 | 修正 |
|--------|------|
| 断言 mock 元素 | 测试真实组件或不 mock |
| 生产类中仅测试用方法 | 移到测试工具 |
| 不理解就 mock | 先理解依赖，最小 mock |
| 不完整 mock | 完全镜像真实 API |
| 测试当作后续 | TDD — 测试先行 |
| 过于复杂的 mock | 考虑集成测试 |

---

## 红旗

- 断言检查 `*-mock` test ID
- 方法仅在测试文件中调用
- Mock 设置占测试 >50%
- 移除 mock 测试就失败
- 说不清为什么需要 mock
- Mock "保险起见"

---

## 底线

**Mock 是用来隔离的工具，不是用来测试的东西。**

如果 TDD 暴露你在测试 mock 行为，你就走错了。

修正：测试真实行为，或质疑为什么需要 mock。
