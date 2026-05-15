# 安全指南

## 何时启动安全检查

在以下场景中必须启动安全检查：

- 实现认证或授权功能
- 处理用户输入或文件上传
- 创建新的 API 接口
- 处理密钥或凭证
- 实现支付功能
- 存储或传输敏感数据
- 集成第三方 API

---

## 强制安全检查

在**任何提交之前**，必须确保：

- [ ] 没有硬编码的敏感信息（API 密钥、密码、令牌）
- [ ] 所有用户输入都已校验
- [ ] 防止 SQL 注入（使用参数化查询）
- [ ] 防止 XSS（对 HTML 进行清理/转义）
- [ ] 已启用 CSRF 防护
- [ ] 已验证认证/授权机制
- [ ] 所有接口均设置了限流
- [ ] 错误信息不会泄露敏感数据

---

## 1. 密钥管理

### ❌ 绝对不要这样做

```typescript
const apiKey = "sk-proj-xxxxx"  // 硬编码密钥
const dbPassword = "password123" // 写在源码中
```

### ✅ 始终这样做

```typescript
const apiKey = process.env.OPENAI_API_KEY
const dbUrl = process.env.DATABASE_URL

// 验证密钥存在
if (!apiKey) {
  throw new Error('OPENAI_API_KEY not configured')
}
```

### 验证步骤

- [ ] 没有硬编码的 API 密钥、令牌或密码
- [ ] 所有密钥都使用环境变量
- [ ] `.env.local` 在 .gitignore 中
- [ ] 密钥不在 git 历史中
- [ ] 生产环境密钥使用托管平台管理（Vercel、Railway 等）
- [ ] 在应用启动时校验必要的密钥是否存在
- [ ] 对任何可能泄露的密钥进行轮换

---

## 2. 输入校验

### 始终校验用户输入

```typescript
import { z } from 'zod'

// 定义校验 schema
const CreateUserSchema = z.object({
  email: z.string().email(),
  name: z.string().min(1).max(100),
  age: z.number().int().min(0).max(150)
})

// 处理前验证
export async function createUser(input: unknown) {
  try {
    const validated = CreateUserSchema.parse(input)
    return await db.users.create(validated)
  } catch (error) {
    if (error instanceof z.ZodError) {
      return { success: false, errors: error.errors }
    }
    throw error
  }
}
```

### 文件上传校验

```typescript
function validateFileUpload(file: File) {
  // 大小检查（最大 5MB）
  const maxSize = 5 * 1024 * 1024
  if (file.size > maxSize) {
    throw new Error('File too large (max 5MB)')
  }

  // 类型检查
  const allowedTypes = ['image/jpeg', 'image/png', 'image/gif']
  if (!allowedTypes.includes(file.type)) {
    throw new Error('Invalid file type')
  }

  // 扩展名检查
  const allowedExtensions = ['.jpg', '.jpeg', '.png', '.gif']
  const extension = file.name.toLowerCase().match(/\.[^.]+$/)?.[0]
  if (!extension || !allowedExtensions.includes(extension)) {
    throw new Error('Invalid file extension')
  }

  return true
}
```

### 验证步骤

- [ ] 所有用户输入都使用 schema 校验
- [ ] 文件上传已限制（大小、类型、扩展名）
- [ ] 用户输入不直接用于查询
- [ ] 使用白名单校验（而非黑名单）
- [ ] 错误信息不泄露敏感数据

---

## 3. 认证与授权

### JWT 令牌处理

```typescript
// ❌ 错误：localStorage（易受 XSS 攻击）
localStorage.setItem('token', token)

// ✅ 正确：httpOnly cookies
res.setHeader('Set-Cookie',
  `token=${token}; HttpOnly; Secure; SameSite=Strict; Max-Age=3600`)
```

### 授权检查

```typescript
export async function deleteUser(userId: string, requesterId: string) {
  // 始终先验证授权
  const requester = await db.users.findUnique({
    where: { id: requesterId }
  })

  if (requester.role !== 'admin') {
    return NextResponse.json(
      { error: 'Unauthorized' },
      { status: 403 }
    )
  }

  // 继续执行删除
  await db.users.delete({ where: { id: userId } })
}
```

### 验证步骤

- [ ] 令牌存储在 httpOnly cookies 中（而非 localStorage）
- [ ] 敏感操作前进行授权检查
- [ ] 启用行级安全（Row Level Security）
- [ ] 实现基于角色的访问控制
- [ ] 会话管理安全

---

## 4. XSS 防护

### 清理 HTML

```typescript
import DOMPurify from 'isomorphic-dompurify'

// 始终清理用户提供的 HTML
function renderUserContent(html: string) {
  const clean = DOMPurify.sanitize(html, {
    ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'p'],
    ALLOWED_ATTR: []
  })
  return <div dangerouslySetInnerHTML={{ __html: clean }} />
}
```

### 内容安全策略 (CSP)

```typescript
// next.config.js
const securityHeaders = [
  {
    key: 'Content-Security-Policy',
    value: `
      default-src 'self';
      script-src 'self' 'unsafe-eval' 'unsafe-inline';
      style-src 'self' 'unsafe-inline';
      img-src 'self' data: https:;
      font-src 'self';
      connect-src 'self' https://api.example.com;
    `.replace(/\s{2,}/g, ' ').trim()
  }
]
```

### 验证步骤

- [ ] 用户提供的 HTML 已清理
- [ ] CSP 头部已配置
- [ ] 无未校验的动态内容渲染
- [ ] 使用框架内置的 XSS 防护

---

## 5. CSRF 防护

### CSRF 令牌

```typescript
import { csrf } from '@/lib/csrf'

export async function POST(request: Request) {
  const token = request.headers.get('X-CSRF-Token')

  if (!csrf.verify(token)) {
    return NextResponse.json(
      { error: 'Invalid CSRF token' },
      { status: 403 }
    )
  }

  // 处理请求
}
```

### SameSite Cookies

```typescript
res.setHeader('Set-Cookie',
  `session=${sessionId}; HttpOnly; Secure; SameSite=Strict`)
```

### 验证步骤

- [ ] 状态变更操作需要 CSRF 令牌
- [ ] 所有 cookies 设置 SameSite=Strict
- [ ] 实现双重提交 cookie 模式

---

## 6. 限流

### API 限流

```typescript
import rateLimit from 'express-rate-limit'

const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 分钟
  max: 100, // 每个窗口 100 次请求
  message: 'Too many requests'
})

// 应用到路由
app.use('/api/', limiter)
```

### 高成本操作限流

```typescript
// 搜索操作的严格限流
const searchLimiter = rateLimit({
  windowMs: 60 * 1000, // 1 分钟
  max: 10, // 每分钟 10 次请求
  message: 'Too many search requests'
})

app.use('/api/search', searchLimiter)
```

### 验证步骤

- [ ] 所有 API 接口都有限流
- [ ] 高成本操作有更严格的限制
- [ ] 基于 IP 限流
- [ ] 已认证用户基于用户限流

---

## 7. 敏感数据暴露防护

### 日志记录

```typescript
// ❌ 错误：记录敏感数据
console.log('User login:', { email, password })
console.log('Payment:', { cardNumber, cvv })

// ✅ 正确：脱敏敏感数据
console.log('User login:', { email, userId })
console.log('Payment:', { last4: card.last4, userId })
```

### 错误信息

```typescript
// ❌ 错误：暴露内部细节
catch (error) {
  return NextResponse.json(
    { error: error.message, stack: error.stack },
    { status: 500 }
  )
}

// ✅ 正确：通用错误信息
catch (error) {
  console.error('Internal error:', error)
  return NextResponse.json(
    { error: 'An error occurred. Please try again.' },
    { status: 500 }
  )
}
```

### 验证步骤

- [ ] 日志中无密码、令牌或密钥
- [ ] 用户错误信息通用化
- [ ] 详细错误仅记录在服务器日志中
- [ ] 不向用户暴露堆栈跟踪

---

## 8. 依赖安全

### 定期更新

```bash
# 检查漏洞
pnpm audit

# 自动修复可修复的问题
pnpm audit fix

# 更新依赖
pnpm update

# 检查过时的包
pnpm outdated
```

### 锁文件

```bash
# 始终提交锁文件
git add pnpm-lock.yaml

# 在 CI/CD 中使用可重现构建
pnpm install --frozen-lockfile
```

### 验证步骤

- [ ] 依赖保持最新
- [ ] 无已知漏洞（pnpm audit clean）
- [ ] 锁文件已提交
- [ ] 启用 Dependabot（GitHub）
- [ ] 定期安全更新

---

## 安全测试

### 自动化安全测试

```typescript
// 测试认证
test('requires authentication', async () => {
  const response = await fetch('/api/protected')
  expect(response.status).toBe(401)
})

// 测试授权
test('requires admin role', async () => {
  const response = await fetch('/api/admin', {
    headers: { Authorization: `Bearer ${userToken}` }
  })
  expect(response.status).toBe(403)
})

// 测试输入校验
test('rejects invalid input', async () => {
  const response = await fetch('/api/users', {
    method: 'POST',
    body: JSON.stringify({ email: 'not-an-email' })
  })
  expect(response.status).toBe(400)
})

// 测试限流
test('enforces rate limits', async () => {
  const requests = Array(101).fill(null).map(() =>
    fetch('/api/endpoint')
  )

  const responses = await Promise.all(requests)
  const tooManyRequests = responses.filter(r => r.status === 429)

  expect(tooManyRequests.length).toBeGreaterThan(0)
})
```

---

## 部署前安全检查清单

在**任何生产部署之前**，必须确保：

- [ ] **密钥**：无硬编码密钥，全部使用环境变量
- [ ] **输入校验**：所有用户输入已校验
- [ ] **SQL 注入**：所有查询参数化
- [ ] **XSS**：用户内容已清理
- [ ] **CSRF**：防护已启用
- [ ] **认证**：正确的令牌处理
- [ ] **授权**：角色检查到位
- [ ] **限流**：所有接口已启用
- [ ] **HTTPS**：生产环境强制使用
- [ ] **安全头部**：CSP、X-Frame-Options 已配置
- [ ] **错误处理**：错误中无敏感数据
- [ ] **日志**：无敏感数据被记录
- [ ] **依赖**：已更新，无漏洞
- [ ] **行级安全**：数据库已启用
- [ ] **CORS**：正确配置
- [ ] **文件上传**：已校验（大小、类型）

---

## 安全响应流程

如果发现安全问题：

1. **立即停止**当前操作
2. 使用 **security-reviewer** agent
3. 在继续之前修复所有**严重（CRITICAL）问题**
4. **轮换**所有已暴露的密钥
5. **审查**整个代码库，查找类似问题

---

## 资源

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Web Security Academy](https://portswigger.net/web-security)

---

**记住**：安全不是可选项。一个漏洞可能危及整个平台。如有疑问，宁可谨慎。
