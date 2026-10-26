# TypeScript 命名规范详解

## 命名核心原则

> "如果名称需要注释来补充，那它就没有揭示意图。" — Robert C. Martin

## 变量命名

### 揭示意图

```typescript
// 差：含义不明
const d = 42;
const tmp = getData();
const list = getItems();

// 好：名称即文档
const elapsedTimeInMilliseconds = 42;
const userConfig = loadUserConfig();
const activeUsers = getActiveUsers();
```

### 可搜索

```typescript
// 差：难以全局搜索
for (let i = 0; i < 100; i++) { ... }
// `i` 出现在无数地方

// 好：有意义的循环变量
for (let userIndex = 0; userIndex < users.length; userIndex++) { ... }
// 或者使用更具语义的命名
users.forEach((user) => { ... });
```

### 避免误导

```typescript
// 差：名字暗示是数组，实际是 Map
const accountList = new Map<string, Account>();

// 好：准确反映数据结构
const accountsByUserId = new Map<string, Account>();
```

## 函数命名

### 使用动词

```typescript
// 差
const result = userData();
const status = payment();

// 好
const result = fetchUserData();
const status = checkPaymentStatus();
```

### 根据返回值命名

| 返回类型 | 命名前缀 | 示例 |
|----------|---------|------|
| boolean | is/has/can/should | `isPasswordValid()` |
| array | get/find/filter | `getActiveUsers()` |
| object | create/build/compute | `createOrder()` |
| void | 动作动词 | `saveOrder()`, `notifyUser()` |

## 类命名

### 名词，避免模糊后缀

```typescript
// 差：Manager 含义模糊
class UserManager { ... }
class DataHandler { ... }

// 好：具体描述职责
class UserRegistrationService { ... }
class PaymentProcessor { ... }
```

### 避免 Info/Data 后缀

```typescript
// 差
interface ProductInfo { ... }
interface UserData { ... }

// 好
interface Product { ... }
interface User { ... }
```

## 布尔值命名

```typescript
// 差
const done = checkValidation();
const valid = checkAge(age);

// 好
const isValid = checkValidation();
const isAgeAppropriate = checkAge(age);
const hasPermission = checkPermission(user);
const canEdit = checkEditPermission(user);
```

## 枚举命名

```typescript
// 差
enum Status {
  A, B, C
}

// 好
enum PaymentStatus {
  Pending = 'PENDING',
  Processing = 'PROCESSING',
  Completed = 'COMPLETED',
  Failed = 'FAILED',
}
```

## 常见反模式

| 反模式 | 问题 | 修正 |
|--------|------|------|
| 单字母变量 `i, j, k` | 循环内可接受，循环外禁用 | 使用描述性名称 |
| 匈牙利命名法 `strName` | TypeScript 有类型系统，无需前缀 | 直接用 `name: string` |
| 缩写 `usrMgr` | 不可读 | 用完整单词 `userManager` |
| 无意义区分 `data1, data2` | 无法区分含义 | 用语义区分 `userData, orderData` |
| 编码信息 `nameUtf8` | 实现细节不应出现在名称中 | 用 `name`，编码由类型/接口约束 |

## TypeScript 特有约定

| 元素 | 约定 | 示例 |
|------|------|------|
| 接口 | PascalCase，不加 `I` 前缀 | `interface User { ... }` |
| 类型别名 | PascalCase | `type UserId = string` |
| 泛型参数 | 单字母或描述性 | `T` 或 `TItem` |
| 常量 | UPPER_SNAKE_CASE 或 camelCase | `MAX_RETRY_COUNT` |
| 私有成员 | `#` 前缀或 `_` 前缀 | `#internalState` |
| 文件名 | kebab-case | `user-service.ts` |
