# 存储管理

管理 cookies、localStorage、sessionStorage 和浏览器存储状态。

## 存储状态

保存与恢复完整浏览器状态，包括 cookies 和其他存储。

### 保存存储状态

```bash
# 保存到自动生成的文件名（storage-state-{timestamp}.json）
playwright-cli state-save

# 保存到指定文件
playwright-cli state-save my-auth-state.json
```

### 恢复存储状态

```bash
# 从文件加载存储状态
playwright-cli state-load my-auth-state.json

# 打开页面以应用 cookies
playwright-cli open https://example.com
```

### 存储状态文件格式

保存的文件包含：

```json
{
  "cookies": [
    {
      "name": "session_id",
      "value": "abc123",
      "domain": "example.com",
      "path": "/",
      "expires": 1893456000,
      "httpOnly": true,
      "secure": true,
      "sameSite": "Lax"
    }
  ],
  "origins": [
    {
      "origin": "https://example.com",
      "localStorage": [
        { "name": "theme", "value": "dark" },
        { "name": "user_id", "value": "12345" }
      ]
    }
  ]
}
```

## Cookies

### 列出全部 Cookies

```bash
playwright-cli cookie-list
```

### 按域筛选

```bash
playwright-cli cookie-list --domain=example.com
```

### 按路径筛选

```bash
playwright-cli cookie-list --path=/api
```

### 读取指定 Cookie

```bash
playwright-cli cookie-get session_id
```

### 设置 Cookie

```bash
# 基础 cookie
playwright-cli cookie-set session abc123

# 带选项的 cookie
playwright-cli cookie-set session abc123 --domain=example.com --path=/ --httpOnly --secure --sameSite=Lax

# 带过期时间的 cookie（Unix 时间戳）
playwright-cli cookie-set remember_me token123 --expires=1893456000
```

### 删除 Cookie

```bash
playwright-cli cookie-delete session_id
```

### 清空全部 Cookies

```bash
playwright-cli cookie-clear
```

### 高级：批量设置 Cookies

需要一次添加多个 cookies 时，用 `run-code`：

```bash
playwright-cli run-code "async page => {
  await page.context().addCookies([
    { name: 'session_id', value: 'sess_abc123', domain: 'example.com', path: '/', httpOnly: true },
    { name: 'preferences', value: JSON.stringify({ theme: 'dark' }), domain: 'example.com', path: '/' }
  ]);
}"
```

## LocalStorage

### 列出全部条目

```bash
playwright-cli localstorage-list
```

### 读取单值

```bash
playwright-cli localstorage-get token
```

### 设置值

```bash
playwright-cli localstorage-set theme dark
```

### 设置 JSON 值

```bash
playwright-cli localstorage-set user_settings '{"theme":"dark","language":"en"}'
```

### 删除单项

```bash
playwright-cli localstorage-delete token
```

### 清空 LocalStorage

```bash
playwright-cli localstorage-clear
```

### 高级：批量操作

需要一次设置多个值时，用 `run-code`：

```bash
playwright-cli run-code "async page => {
  await page.evaluate(() => {
    localStorage.setItem('token', 'jwt_abc123');
    localStorage.setItem('user_id', '12345');
    localStorage.setItem('expires_at', Date.now() + 3600000);
  });
}"
```

## SessionStorage

### 列出全部条目

```bash
playwright-cli sessionstorage-list
```

### 读取单值

```bash
playwright-cli sessionstorage-get form_data
```

### 设置值

```bash
playwright-cli sessionstorage-set step 3
```

### 删除单项

```bash
playwright-cli sessionstorage-delete step
```

### 清空 SessionStorage

```bash
playwright-cli sessionstorage-clear
```

## IndexedDB

### 列出数据库

```bash
playwright-cli run-code "async page => {
  return await page.evaluate(async () => {
    const databases = await indexedDB.databases();
    return databases;
  });
}"
```

### 删除数据库

```bash
playwright-cli run-code "async page => {
  await page.evaluate(() => {
    indexedDB.deleteDatabase('myDatabase');
  });
}"
```

## 常见模式

### 复用认证状态

```bash
# 步骤 1：登录并保存状态
playwright-cli open https://app.example.com/login
playwright-cli snapshot
playwright-cli fill e1 "user@example.com"
playwright-cli fill e2 "password123"
playwright-cli click e3

# 保存认证状态
playwright-cli state-save auth.json

# 步骤 2：之后恢复状态，跳过登录
playwright-cli state-load auth.json
playwright-cli open https://app.example.com/dashboard
# 已处于登录状态
```

### 保存与恢复往返

```bash
# 建立认证状态
playwright-cli open https://example.com
playwright-cli eval "() => { document.cookie = 'session=abc123'; localStorage.setItem('user', 'john'); }"

# 保存状态到文件
playwright-cli state-save my-session.json

# ... 之后在新会话中 ...

# 恢复状态
playwright-cli state-load my-session.json
playwright-cli open https://example.com
# cookies 与 localStorage 已恢复
```

## 安全事项

- 含认证令牌的存储状态文件不得提交到版本库
- 将 `*.auth-state.json` 加入 `.gitignore`
- 自动化结束后删除状态文件
- 敏感数据通过环境变量传递
- 会话默认运行在内存模式，敏感操作更安全
