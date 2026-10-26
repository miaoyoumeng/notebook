# 测试反模式

加载时机：写或改测试、添加 mock、在生产类上添加仅测试使用的方法时。

## 铁律

1. 不测试 mock 行为。
2. 不在生产类上添加仅测试使用的方法。
3. 不在未理解依赖的情况下使用 mock。

## 反模式 1：测试 Mock 行为

违规示例：

```typescript
// 断言 mock 被调用，而不是真实业务结果
const mockAdd = vi.fn();
mockAdd({ id: 'sku-1', quantity: 1 });
expect(mockAdd).toHaveBeenCalled();
```

问题：验证的是 mock 是否生效，不是真实代码是否工作。mock 在则通过，mock 不在则失败。

修正：

```typescript
const cart = new Cart();
cart.addItem({ id: 'sku-1', quantity: 1 });
expect(cart.items).toHaveLength(1);
```

必须 mock 时，测试被测代码在依赖存在时的行为，不断言 mock 本身。

门控：

```text
断言任何 mock 之前：
  问：我在测试真实代码行为，还是仅 mock 是否被调用？
  如果仅测试 mock 是否被调用：
    删除断言，或不 mock 该模块，测试真实行为。
```

## 反模式 2：生产类中的仅测试用方法

违规示例：

```typescript
class Session {
  destroy = async () => {
    await this.workspaceManager?.destroyWorkspace(this.id);
  };
}

afterEach(() => session.destroy());
```

问题：生产类被测试代码污染；生产环境误调用有风险；违反职责分离。

修正：

```typescript
// 测试工具文件 test-utils/cleanupSession.ts
export const cleanupSession = async (session: Session) => {
  const workspace = session.getWorkspaceInfo();
  if (workspace) {
    await workspaceManager.destroyWorkspace(workspace.id);
  }
};

afterEach(() => cleanupSession(session));
```

门控：

```text
向生产类添加方法之前：
  问：这个方法是否仅被测试使用？
  是：停止，放到测试工具。
  问：这个类是否拥有该资源的生命周期？
  否：停止，方法放错类了。
```

## 反模式 3：不理解依赖就 mock

违规示例：

```typescript
// mock 阻止了测试依赖的 config 写入
vi.mock('./toolCatalog', () => ({
  discoverAndCacheTools: vi.fn().mockResolvedValue(undefined),
}));

await addServer(config);
await addServer(config); // 应抛错，实际不会
```

问题：被 mock 的方法有测试依赖的副作用；“保险起见”的过度 mock 破坏真实行为；测试因错误原因通过或神秘失败。

修正：

```typescript
// 只 mock 慢的部分，保留测试需要的行为
vi.mock('./slowServerStarter');

await addServer(config);
await addServer(config); // 重复检测生效
```

门控：

```text
mock 任何方法之前：
  1. 真实方法有什么副作用？
  2. 这个测试依赖哪些副作用？
  3. 是否完全理解测试需要什么？

  依赖副作用：在更低层 mock 真正慢或外部的操作。
  不确定：先用真实实现运行测试，观察实际需要，再加最小 mock。

  危险信号：
    - 保险起见先 mock
    - 可能很慢，最好 mock
    - 不理解依赖链就 mock
```

## 反模式 4：不完整的 Mock

违规示例：

```typescript
const mockResponse = {
  status: 'success',
  data: { userId: '123', name: 'Alice' },
  // 缺失下游代码使用的 metadata
};
```

问题：部分 mock 隐藏结构假设；下游代码访问缺失字段时静默失败；测试通过但集成失败。

规则：mock 必须完整镜像真实 API 的响应结构，而不只是当前测试用到的字段。不确定时包含全部文档化字段。

修正：

```typescript
const mockResponse = {
  status: 'success',
  data: { userId: '123', name: 'Alice' },
  metadata: { requestId: 'req-789', timestamp: 1234567890 },
};
```

## 反模式 5：测试当作后续工作

违规：实现完成、没有测试，声称“准备好测试了”。

问题：测试是实现的一部分。没有测试不能声称完成。

修正：按 RED-GREEN-REFACTOR 循环完成后再声明完成。

## Mock 过于复杂时

出现以下信号，考虑改用集成测试：

- Mock 设置比测试逻辑长。
- 必须 mock 一切才能让测试通过。
- Mock 缺少真实模块具备的方法。
- mock 改动导致测试失败。

改用真实依赖的集成测试，通常比复杂 mock 更简单。

## 快速参考

| 反模式 | 修正 |
|--------|------|
| 断言 mock 调用 | 测试真实代码，或不 mock |
| 生产类中仅测试用方法 | 移到测试工具 |
| 不理解就 mock | 先理解依赖，再最小 mock |
| 不完整 mock | 完整镜像真实 API |
| 测试当作后续 | 测试先行 |
| 过于复杂的 mock | 考虑集成测试 |

## 危险信号

- 断言只检查 mock 调用记录。
- 方法仅在测试文件中调用。
- Mock 设置占测试代码 50% 以上。
- 移除 mock 后测试失败。
- 说不清为什么需要 mock。
- 以“保险起见”为由添加 mock。

Mock 用于隔离外部依赖，不用于测试本身。测试对象必须是真实行为。
