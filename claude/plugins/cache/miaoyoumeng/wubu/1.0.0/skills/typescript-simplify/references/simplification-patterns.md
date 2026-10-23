# 简化模式参考

本文件提供 TypeScript 代码的简化模式示例、风险分级、反模式与验证启发式。

## 适合简化的目标

优先处理：

- 用守卫语句展平嵌套条件；
- 将密集布尔表达式提取为具名局部变量；
- 用清晰分支替换嵌套三元表达式；
- 合并重复的校验或规范化逻辑；
- 删除未使用的导入、分支与局部变量；
- 重命名误导性的局部符号；
- 在运行时模型不变的前提下展平回调金字塔；
- 仅当调用点仍然可读时，把长参数列表收敛为选项对象。

## 模式示例

### 展平嵌套

修改前：

```ts
if (user) {
  if (user.active) {
    if (user.canEdit) {
      return save(user)
    }
  }
}
return null
```

修改后：

```ts
if (!user) return null
if (!user.active) return null
if (!user.canEdit) return null
return save(user)
```

### 提取复杂条件

修改前：

```ts
if (items.length > 0 && items.every((item) => item.ready) && !isProcessing) {
  run(items)
}
```

修改后：

```ts
const hasReadyItems = items.length > 0 && items.every((item) => item.ready)
const canRun = !isProcessing

if (hasReadyItems && canRun) {
  run(items)
}
```

### 合并明显重复

修改前：

```ts
const createUser = (data: UserInput) => {
  validateName(data.name)
  validateEmail(data.email)
  return db.insert(data)
}

const updateUser = (id: string, data: UserInput) => {
  validateName(data.name)
  validateEmail(data.email)
  return db.update(id, data)
}
```

修改后：

```ts
const validateUserData = (data: UserInput) => {
  validateName(data.name)
  validateEmail(data.email)
}

const createUser = (data: UserInput) => {
  validateUserData(data)
  return db.insert(data)
}

const updateUser = (id: string, data: UserInput) => {
  validateUserData(data)
  return db.update(id, data)
}
```

### 替换嵌套三元

修改前：

```ts
const label =
  status === 'active' ? 'Active' :
  status === 'pending' ? 'Pending' :
  status === 'disabled' ? 'Disabled' : 'Unknown'
```

修改后：

```ts
const getStatusLabel = (status: Status) => {
  switch (status) {
    case 'active': return 'Active'
    case 'pending': return 'Pending'
    case 'disabled': return 'Disabled'
    default: return 'Unknown'
  }
}
const label = getStatusLabel(status)
```

### 删除死代码

修改前：

```ts
import { format, parse, isValid, addDays } from 'date-fns' // parse、addDays 未使用

const processDate = (input: string) => {
  // 旧实现，保留备查
  // const parsed = parse(input, 'yyyy-MM-dd', new Date())
  if (isValid(new Date(input))) {
    return format(new Date(input), 'MMM d, yyyy')
  }
  return 'Invalid date'
}
```

修改后：

```ts
import { format, isValid } from 'date-fns'

const processDate = (input: string) => {
  if (isValid(new Date(input))) {
    return format(new Date(input), 'MMM d, yyyy')
  }
  return 'Invalid date'
}
```

### 化简布尔表达式

修改前：

```ts
if (isEnabled === true) { ... }
if (items.length === 0 ? true : false) { ... }
return condition ? true : false
```

修改后：

```ts
if (isEnabled) { ... }
if (items.length === 0) { ... }
return condition
```

### 收敛函数参数

修改前：

```ts
interface EmailOptions {
  to: string
  from: string
  subject: string
  body: string
  cc?: string
  bcc?: string
  replyTo?: string
  isHtml?: boolean
}

const sendEmail = (to: string, from: string, subject: string, body: string, cc: string | null, bcc: string | null, replyTo: string | null, isHtml: boolean) => { ... }
sendEmail('a@b.com', 'c@d.com', 'Hello', '<p>Hi</p>', null, null, null, true)
```

修改后：

```ts
const sendEmail = ({ to, from, subject, body, cc, bcc, replyTo, isHtml = false }: EmailOptions) => { ... }
sendEmail({ to: 'a@b.com', from: 'c@d.com', subject: 'Hello', body: '<p>Hi</p>', isHtml: true })
```

### 展平回调金字塔

修改前：

```ts
getUser(id, (err, user) => {
  if (err) return handleError(err)
  getOrders(user.id, (err, orders) => {
    if (err) return handleError(err)
    getInvoices(orders, (err, invoices) => {
      if (err) return handleError(err)
      sendReport(user, invoices)
    })
  })
})
```

修改后：

```ts
try {
  const user = await getUser(id)
  const orders = await getOrders(user.id)
  const invoices = await getInvoices(orders)
  await sendReport(user, invoices)
} catch (err) {
  handleError(err)
}
```

## 风险分级

低风险：

- 经引用确认的死代码删除；
- 布尔表达式化简；
- 不改变调用面的局部提取；
- 局部重命名。

中风险：

- 跨多个调用方的共享 helper 提取；
- 公开符号重命名；
- 参数结构重塑；
- 异步流程展平。

高风险：

- 任何改变求值顺序的改动；
- 触及持久化、缓存、重试、事务、鉴权或并发的改动；
- 删除边界情况处理的"简化"。

中高风险或存在多个合理方向时，先确认再执行。

## 反模式

不要：

- 以可读性为代价缩短代码；
- 用巧妙的单行写法替换直白逻辑；
- 删除仍在解释保留行为的注释；
- 弱化测试以让清理通过；
- 把清理请求扩大为架构重写；
- 假定每次调用都必须手动重读 `CLAUDE.md`。

## 验证启发式

优先选择最窄的有效验证：

1. 符号级或文件级测试；
2. 局部类型检查或编译；
3. 仅当改动位于核心或高耦合代码时运行完整测试。

没有可用验证时明确说明，并缩小改动集。
