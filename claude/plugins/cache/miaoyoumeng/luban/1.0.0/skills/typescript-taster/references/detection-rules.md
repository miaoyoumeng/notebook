# AI 味道检测规则

按 P0 至 P4 优先级组织。每条规则含严重程度、定义、检测方式、示例与修复建议。

## P0：类型冗余

### P0.1 冗余的函数类型注解（High）

**定义**：返回值类型可从函数体推断，仍显式声明。

**检测正则**：`function\s+\w+\s*\([^)]*\)\s*:\s*\w+` 或 `const\s+\w+\s*=\s*\([^)]*\)\s*:\s*\w+\s*=>`

**示例**：

```typescript
// Bad
const add = (a: number, b: number): number => a + b;

// Good
const add = (a: number, b: number) => a + b;
```

**修复建议**：内部函数删除返回值注解，交给 TypeScript 推断；公共 API 的返回值显式声明。

### P0.2 冗余的变量类型注解（High）

**定义**：变量初始化时类型可推断，仍显式声明。

**检测正则**：`(const|let|var)\s+\w+\s*:\s*\w+\s*=`

**示例**：

```typescript
// Bad
const name: string = "Alice";
const count: number = 42;

// Good
const name = "Alice";
const count = 42;
```

**修复建议**：删除类型注解，让 TypeScript 推断。

### P0.3 过度使用联合类型（Medium）

**定义**：只在一处使用的联合类型仍抽出类型别名。

**示例**：

```typescript
// Bad
type Status = "pending" | "success" | "error";

const status: Status = "pending";

// Good
const status = "pending";
```

**修复建议**：联合类型跨模块复用或需要命名表达语义时保留别名；仅使用一次时内联。

## P1：过度注释

### P1.1 显而易见的注释（Medium）

**定义**：注释只是重复代码的含义。

**示例**：

```typescript
// Bad
// 增加计数
count++;

// 返回用户对象
return user;

// Good
// 重试 3 次后仍然失败，记录错误
logger.error("Failed after 3 retries", error);
```

**修复建议**：删除显而易见的注释，保留解释原因的内容。

### P1.2 函数头部描述性注释（Medium）

**定义**：函数头部有大段描述性注释，函数名已说明用途。

**示例**：

```typescript
// Bad
/**
 * 计算两个数的和
 * @param a 第一个数
 * @param b 第二个数
 * @returns 两数之和
 */
const add = (a: number, b: number) => a + b;

// Good
const add = (a: number, b: number) => a + b;
```

**修复建议**：函数名已说明用途时删除 JSDoc；参数含义无法从签名读出时保留。

### P1.3 每行都有注释（Critical）

**定义**：代码与注释交替出现，注释比代码多。

**检测正则**：`(\/\/.*\n.*){3,}`

**示例**：

```typescript
// Bad
// 获取用户
const user = getUser();
// 验证用户
validate(user);
// 保存用户
save(user);

// Good
const user = getUser();
validate(user);
save(user);
```

**修复建议**：删除逐行注释，只保留关键步骤的说明。

## P2：防御性检查

### P2.1 不必要的 null 检查（Medium）

**定义**：对已知非空的值做 null、undefined 检查。

**示例**：

```typescript
// Bad
const getUser = (id: string) => {
  if (!id) {
    throw new Error("ID is required");
  }
  return db.find(id);
};

// Good
const getUser = (id: string) => db.find(id);
```

**修复建议**：删除类型系统已保证的检查。

### P2.2 过度使用 try-catch（Medium）

**定义**：函数用 try-catch 包裹，但内部操作不会抛出异常。

**示例**：

```typescript
// Bad
const add = (a: number, b: number) => {
  try {
    return a + b;
  } catch (e) {
    return 0;
  }
};

// Good
const add = (a: number, b: number) => a + b;
```

**修复建议**：只在实际可能失败的操作外使用 try-catch。

### P2.3 内部函数参数验证（Medium）

**定义**：对内部函数的参数做重复验证。

**示例**：

```typescript
// Bad
const processUser = (user: User) => {
  if (!user) {
    throw new Error("User is required");
  }
  if (!user.name) {
    throw new Error("Name is required");
  }
  // 处理用户
};

// Good
const processUser = (user: User) => {
  // 类型系统保证 user 与 user.name 存在
};
```

**修复建议**：内部函数依赖类型系统，外部输入在边界处校验一次。

## P3：模板化模式

### P3.1 模板化错误处理（High）

**定义**：所有错误处理都只调用 `console.log` 或 `console.error`。

**检测正则**：`catch\s*\([^)]*\)\s*\{\s*console\.(log|error)`

**示例**：

```typescript
// Bad
try {
  await fetchData();
} catch (e) {
  console.log(e);
}

// Good
try {
  await fetchData();
} catch (e) {
  logger.error("Failed to fetch data", e);
  throw new AppError("FETCH_FAILED", "Failed to fetch data", e);
}
```

**修复建议**：使用项目统一的日志与错误类型，保留错误上下文。

### P3.2 异步函数不返回值（Medium）

**定义**：异步函数返回 `Promise<void>`，调用方拿不到操作结果。

**示例**：

```typescript
// Bad
const createUser = async (data: UserData): Promise<void> => {
  await db.insert(data);
};

// Good
const createUser = async (data: UserData): Promise<User> => db.insert(data);
```

**修复建议**：返回有意义的值，便于调用方链式处理。

### P3.3 接口字段全部可选（High）

**定义**：接口定义中所有字段都标为可选。

**示例**：

```typescript
// Bad
interface User {
  id?: string;
  name?: string;
  email?: string;
}

// Good
interface User {
  id: string;
  name: string;
  email?: string;
}
```

**修复建议**：区分必填字段与可选字段。

## P4：命名风格

### P4.1 混用命名风格（Low）

**定义**：同一文件中混用 camelCase 与 snake_case。

**检测正则**：`(_[a-z]+)|([a-z]+_[a-z]+)`

**示例**：

```typescript
// Bad
const user_name = "Alice";
const userAge = 30;

// Good
const userName = "Alice";
const userAge = 30;
```

**修复建议**：统一使用 camelCase。

### P4.2 变量名过于冗长（Low）

**定义**：变量名超过 30 个字符。

**检测正则**：`(const|let|var)\s+([a-zA-Z]{30,})\s*=`

**示例**：

```typescript
// Bad
const userProfileInformationFromDatabase = getUser();

// Good
const userProfile = getUser();
```

**修复建议**：保留核心含义，删除可从上下文得知的修饰词。

### P4.3 布尔变量命名不规范（Low）

**定义**：布尔变量不以 is、has、can、should 开头。

**示例**：

```typescript
// Bad
const active = true;
const valid = false;

// Good
const isActive = true;
const isValid = false;
```

**修复建议**：布尔变量使用 is、has、can、should 前缀。
