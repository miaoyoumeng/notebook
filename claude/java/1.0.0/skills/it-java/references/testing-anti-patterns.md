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
```java
// ❌ 测试 mock 是否被调用，而不是真实业务行为
@Test
void testDeleteUser() {
    userService.deleteUser(1L);

    verify(userMapper).deleteById(1L);
    verify(redisTemplate).delete("user:1");
    // 只验证了 mock 被调用，没有验证组合行为是否正确
}
```

**为什么错：**
- 你在验证 mock 是否生效，不是业务逻辑是否工作
- mock 调了测试就过，mock 没调就失败
- 什么真实行为都没告诉你

**修正：**
```java
// ✅ 测试真实业务结果
@Test
void shouldRemoveUserFromDatabase_whenDeleteUser() {
    // 准备真实数据（用 H2 内存数据库）
    userMapper.insert(new UserDO(1L, "Alice"));

    userService.deleteUser(1L);

    // 验证真实结果
    assertNull(userMapper.selectById(1L));
}

// 如果必须 mock：
// 测试 Service 的编排逻辑 + 验证业务结果，不只是 verify mock
@Test
void shouldClearCacheAfterDelete_whenDeleteUser() {
    Long userId = 1L;
    when(userMapper.existsById(userId)).thenReturn(true);

    userService.deleteUser(userId);

    // 验证编排逻辑：先查是否存在 → 删除 → 清缓存
    InOrder inOrder = inOrder(userMapper, redisTemplate);
    inOrder.verify(userMapper).existsById(userId);
    inOrder.verify(userMapper).deleteById(userId);
    inOrder.verify(redisTemplate).delete("user:" + userId);
}
```

### 门控函数

```
断言任何 mock 调用之前：
  问："我在测试真实业务行为还是仅 mock 是否被调用？"

  如果是测试 mock 是否被调用：
    停下 — 删掉断言或不 mock 该依赖
    测试真实业务结果

  如果测试的是编排逻辑（多步调用的顺序和参数）：
    确保 mock 不是被测对象本身
    用 InOrder 或 ArgumentCaptor 验证调用正确性
```

---

## 反模式 2：生产类中的仅测试用方法

**违规：**
```java
// ❌ reset() 仅在测试中使用
@Service
public class SessionManager {

    private WorkspaceManager workspaceManager;

    public void reset() {  // 看起来像生产 API！
        workspaceManager.destroyCurrent();
    }
}

// 在测试中
@AfterEach
void tearDown() {
    sessionManager.reset();
}
```

**为什么错：**
- 生产类被测试代码污染
- 在生产环境意外调用很危险
- 违反 YAGNI 和关注点分离
- 混淆对象生命周期和实体生命周期

**修正：**
```java
// ✅ 测试工具处理测试清理
// SessionManager 没有 reset() — 它在生产中是无状态的

// 在 test-utils/
public class TestSessionHelper {
    public static void cleanup(SessionManager sessionManager) {
        WorkspaceInfo workspace = sessionManager.getWorkspaceInfo();
        if (workspace != null) {
            // 直接操作底层依赖清理
        }
    }
}

// 在测试中
@AfterEach
void tearDown() {
    TestSessionHelper.cleanup(sessionManager);
}
```

### 门控函数

```
添加任何方法到生产类之前：
  问："这是否仅被测试使用？"

  如果是：
    停下 — 不要加
    放到测试工具类里

  问："这个类拥有这个资源的生命周期吗？"

  如果不是：
    停下 — 方法放错类了
```

---

## 反模式 3：不理解依赖就 mock

**违规：**
```java
// ❌ mock 破坏了测试逻辑
@Test
void shouldDetectDuplicateUser() {
    // mock 了 userMapper.insert，但 insert 的副作用（写数据库）是测试需要的！
    when(userMapper.insert(any())).thenReturn(1);

    userService.register(new UserDTO("alice@example.com"));
    userService.register(new UserDTO("alice@example.com"));  // 应该抛重复异常 — 但不会！
}
```

**为什么错：**
- 被 mock 的方法有测试依赖的副作用（写入数据库）
- "保险起见"过度 mock 破坏实际行为
- 测试因错误原因通过或神秘失败

**修正：**
```java
// ✅ 在正确层级 mock
@Test
void shouldDetectDuplicateEmail() {
    // 只 mock 真正需要隔离的外部部分，保留测试需要的行为
    // 用真实 H2 内存数据库
    userService.register(new UserDTO("alice@example.com"));

    assertThrows(DuplicateEmailException.class, () ->
        userService.register(new UserDTO("alice@example.com"))
    );
}
```

### 门控函数

```
mock 任何方法之前：
  停下 — 先不要 mock

  1. 问："真实方法有什么副作用？"
  2. 问："这个测试依赖这些副作用中的哪些？"
  3. 问："我是否完全理解这个测试需要什么？"

  如果依赖副作用：
    在更低层 mock（真正慢/外部的操作，如 Redis、外部 API）
    或使用保留必要行为的测试替身（H2 代替 MySQL）
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
```java
// ❌ 部分 mock — 只有你认为需要的字段
UserDTO mockUser = new UserDTO();
mockUser.setId(1L);
mockUser.setName("Alice");
// 缺失：email、phone、status 等下游代码使用的字段

// 之后：当代码访问 mockUser.getEmail() 时返回 null，测试崩了
```

**为什么错：**
- **部分 mock 隐藏结构假设** — 你只 mock 了你知道的字段
- **下游代码可能依赖你没包含的字段** — 静默失败（NPE）
- **测试通过但集成失败** — mock 不完整，真实数据完整
- **虚假信心** — 测试证明不了真实行为

**铁律：** mock 的必须是完整的数据结构，就像真实数据一样，而不只是你当前测试用的字段。

**修正：**
```java
// ✅ 构建完整的 mock 数据
UserDTO mockUser = UserDTO.builder()
    .id(1L)
    .name("Alice")
    .email("alice@example.com")
    .phone("13800138000")
    .status(UserStatus.ACTIVE)
    .createdAt(LocalDateTime.now())
    .build();
```

### 门控函数

```
创建 mock 数据之前：
  检查："真实数据对象包含什么字段？"

  行动：
    1. 查看 Entity/DTO 类的所有字段
    2. 包含系统下游可能消费的所有字段
    3. 验证 mock 数据与真实数据 schema 完全匹配

  关键：
    如果你在创建 mock，你必须理解整个结构
    部分 mock 在代码依赖被省略字段时会静默失败（NPE）

  如果不确定：用 Builder 填充所有必填字段 + 常用可选字段
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
- Mock 缺少真实依赖有的方法
- mock 改动时测试就崩

**考虑：** 用 @SpringBootTest 的集成测试往往比复杂 mock 更简单。

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
| 断言 mock 调用但没有断言业务结果 | 测试真实业务结果 |
| 生产类中仅测试用方法 | 移到测试工具类 |
| 不理解就 mock | 先理解依赖，最小 mock |
| 不完整 mock 数据 | 用 Builder 完整填充所有字段 |
| 测试当作后续 | TDD — 测试先行 |
| 过于复杂的 mock | 考虑集成测试（@SpringBootTest） |

---

## 红旗

- verify(mock) 没有对应的 assert 真实结果
- 方法仅在测试文件中调用
- Mock 设置占测试 >50%
- 移除 mock 测试就失败
- 说不清为什么需要 mock
- Mock "保险起见"
- 用 System.out 做验证而不是 assert
- 测试之间互相调用或有执行顺序依赖

---

## 底线

**Mock 是用来隔离的工具，不是用来测试的东西。**

如果 TDD 暴露你在测试 mock 行为，你就走错了。

修正：测试真实行为，或质疑为什么需要 mock。
