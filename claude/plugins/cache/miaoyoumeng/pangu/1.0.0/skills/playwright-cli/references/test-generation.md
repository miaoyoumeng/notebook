# 测试生成

在浏览器中操作时自动生成 Playwright 测试代码。

## 工作方式

`playwright-cli` 的每个操作都会生成对应的 Playwright TypeScript 代码。代码出现在输出中，可直接复制进测试文件。

## 示例流程

```bash
# 启动会话
playwright-cli open https://example.com/login

# 快照查看元素
playwright-cli snapshot
# 输出：e1 [textbox "Email"], e2 [textbox "Password"], e3 [button "Sign In"]

# 填写表单，自动生成代码
playwright-cli fill e1 "user@example.com"
# Ran Playwright code:
# await page.getByRole('textbox', { name: 'Email' }).fill('user@example.com');

playwright-cli fill e2 "password123"
# Ran Playwright code:
# await page.getByRole('textbox', { name: 'Password' }).fill('password123');

playwright-cli click e3
# Ran Playwright code:
# await page.getByRole('button', { name: 'Sign In' }).click();
```

## 组装测试文件

把生成的代码收集为 Playwright 测试：

```typescript
import { test, expect } from '@playwright/test';

test('login flow', async ({ page }) => {
  // 来自 playwright-cli 会话的生成代码：
  await page.goto('https://example.com/login');
  await page.getByRole('textbox', { name: 'Email' }).fill('user@example.com');
  await page.getByRole('textbox', { name: 'Password' }).fill('password123');
  await page.getByRole('button', { name: 'Sign In' }).click();

  // 补充断言
  await expect(page).toHaveURL(/.*dashboard/);
});
```

## 实践规则

### 1. 使用语义化定位器

生成的代码优先使用基于角色的定位器，稳定性更高：

```typescript
// 生成结果（推荐：语义化）
await page.getByRole('button', { name: 'Submit' }).click();

// 避免（脆弱：CSS 选择器）
await page.locator('#submit-btn').click();
```

### 2. 录制前先探查

录制操作前先快照，理解页面结构：

```bash
playwright-cli open https://example.com
playwright-cli snapshot
# 查看元素结构
playwright-cli click e5
```

### 3. 手动补充断言

生成代码只捕获操作，不包含断言。在测试中使用下列匹配器补充预期：

- `toBeVisible()`：元素已渲染且可见
- `toHaveText(text)`：元素文本匹配
- `toHaveValue(value) / toBeEmpty()`：输入框或下拉框的值匹配
- `toBeChecked() / toBeUnchecked()`：复选框状态匹配
- `toMatchAriaSnapshot(snapshot)`：页面或定位器匹配部分可访问性快照

用 `playwright-cli generate-locator <target>` 生成断言所需定位器表达式，用快照或 `eval` 捕获期望值。

断言文本内容时，生成的定位器不得包含元素自身的文本。`getByTestId()` 或 `getByLabel()` 通常适合文本断言；定位器基于文本时，优先用 `toBeVisible()`。

用于匹配的快照不必包含全部信息，只保留断言必需的部分。不稳定值可用正则表达式。

```bash
# 获取元素 ref 的稳定定位器，用于断言
playwright-cli --raw generate-locator e5
# getByRole('button', { name: 'Submit' })

# 捕获 toHaveText 的期望文本
playwright-cli --raw eval "el => el.textContent" e5

# 捕获 toHaveValue/toBeEmpty 的期望值
playwright-cli --raw eval "el => el.value" e5

# 捕获 toMatchAriaSnapshot/toBeChecked 的期望 aria 快照
# （整页，或用 ref 限定区域）
playwright-cli --raw snapshot
playwright-cli --raw snapshot e5
```

```typescript
// 生成的操作
await page.getByRole('button', { name: 'Submit' }).click();

// 使用上述输出手动补充断言：
await expect(page.getByRole('alert', { name: 'Success' })).toBeVisible();
await expect(page.getByTestId('main-header')).toHaveText('Welcome, user');
await expect(page.getByRole('textbox', { name: 'Email' })).toHaveValue('user@example.com');
await expect(page.getByRole('checkbox', { name: 'Enable notifications' })).toBeChecked();

// 整页 toMatchAriaSnapshot，查找匹配区域
await expect(page).toMatchAriaSnapshot(`
  - heading "Welcome, user"
  - link /\\d+ new messages?/
  - button "Sign out"
`);

// 限定区域的 toMatchAriaSnapshot
await expect(page.getByRole('navigation')).toMatchAriaSnapshot(`
  - link "Home"
  - link /\\d+ new messages?/
  - link "Profile"
`);
```
