# 规格驱动测试：规划 → 生成 → 修复

使用 `playwright-cli` 编写与维护 Playwright 测试的端到端流程。以下三节可独立使用：

- **规划**：探查应用，产出描述测试场景的规格文件。
- **生成**：把规格转为 Playwright 测试文件。规格含糊或过期时更新规格。
- **修复**：诊断失败测试，修正代码，使规格与实际一致。

三节都依赖同一机制：后台运行 `npx playwright test --debug=cli`，再用 `playwright-cli attach tw-XXXX` 交互操作暂停的页面。调试与连接机制见测试运行文档；每个 `playwright-cli` 操作生成的 Playwright TypeScript 见测试生成文档。

---

## 1. 规划

目标：产出规格文件（例如 `specs/<feature>.plan.md`），枚举待测场景。规格必须写入文件。

### 1.1 前置条件：工作区

先确认工作区已安装 Playwright：

```bash
# 以下任一命令可确认工作区
test -f playwright.config.ts || test -f playwright.config.js
npx --no-install playwright --version
```

未安装 Playwright 时初始化，由用户选择默认选项：

```bash
pnpm create playwright@latest
```

### 1.2 前置条件：种子测试

**种子测试**是最小测试，把页面带入每个场景的起始状态：导航到应用、必要的登录、功能开关等。场景假定种子之后从全新状态开始。`--debug=cli` 在该测试内部暂停，因此规划与生成会话都从种子开始。

最小可用种子：

```ts
// tests/seed.spec.ts
import { test } from '@playwright/test';

test('seed', async ({ page }) => {
  await page.goto('https://example.com/');
});
```

推荐做法：把导航放进 fixture，供场景测试复用：

```ts
// tests/fixtures.ts
import { test as baseTest } from '@playwright/test';
export { expect } from '@playwright/test';

export const test = baseTest.extend({
  page: async ({ page }, use) => {
    await page.goto('https://example.com/');
    await use(page);
  },
});
```

```ts
// tests/seed.spec.ts
import { test } from './fixtures';

test('seed', async ({ page }) => {
  // fixture 已完成导航。空函数体标明操作起点。
});
```

没有种子时，创建至少能导航到应用的种子。

### 1.3 探查应用

通过种子启动应用并连接：

```bash
PLAYWRIGHT_HTML_OPEN=never npx playwright test tests/seed.spec.ts --debug=cli
# 等待 "Debugging Instructions" 与会话名 tw-XXXX
playwright-cli attach tw-XXXX
```

恢复执行，让种子跑完，然后探查：

```bash
playwright-cli resume                   # 恢复执行，让种子测试完整运行
playwright-cli snapshot                 # 列出可交互元素
playwright-cli click e5                 # 跟随流程
playwright-cli eval "location.href"     # 读取 URL 与状态
playwright-cli show --annotate          # 请用户指出目标位置
```

梳理：

- 交互面：表单、按钮、列表、筛选器、弹窗。
- 主要用户旅程的完整路径。
- 边界情况：空状态、校验错误、超长输入、边界值。
- 持久化：刷新、local/session storage、URL 片段。
- 导航：哪些控件改变 URL、前进后退行为。

**重要**：不要直接用 playwright-cli 打开应用 URL，始终通过测试进入，以保留其中的自定义设置。
**重要**：探查结束后停止后台测试。

### 1.4 编写规格文件

保存到 `specs/<feature>.plan.md`，使用下列结构：

```markdown
# <功能> 测试计划

## 应用概述

<一段说明，描述功能用途与价值。>

## 测试场景

### 1. <分组名称>

**Seed:** `tests/seed.spec.ts`

#### 1.1. <kebab-case-场景名>

**File:** `tests/<group>/<kebab-case-场景名>.spec.ts`

**Steps:**
  1. <具体用户步骤>
    - expect: <可观察结果>
    - expect: <另一个可观察结果>
  2. <下一步骤>
    - expect: <结果>

#### 1.2. <下一场景>
...

### 2. <下一分组>

**Seed:** `tests/seed.spec.ts`
...
```

规则：

- 每个场景独立，从种子的全新状态开始，不得串联场景。
- 场景名用 kebab-case，与测试文件名一致（`should-add-single-todo` → `should-add-single-todo.spec.ts`）。
- 覆盖正常路径、边界情况、校验、异常流程、持久化。
- 步骤写在用户层面（"在输入框输入 'Buy milk'"），而非 API 层面（"调用 `fill`"）。
- 可观察结果写入 `- expect:` 条目，生成阶段逐条转为断言。

---

## 2. 生成

目标：把规格文件转为 Playwright 测试文件。规格偏离时可选更新。

### 2.1 输入

- **规格文件**，例如 `specs/basic-operations.plan.md`。
- **目标**：单个场景（例如 `1.2`）、整个分组（`1`）或全部。
- **种子文件**：从场景所属分组的 `**Seed:**` 行读取。

### 2.2 生成单个场景

依次处理每个目标场景，不得并行（场景共享种子会话）：

```bash
PLAYWRIGHT_HTML_OPEN=never npx playwright test <seed-file> --debug=cli   # 后台运行
playwright-cli attach tw-XXXX
# resume
```

**不要**直接用 playwright-cli 打开应用 URL，始终通过测试进入，以保留其中的自定义设置。

用 `playwright-cli` 逐步执行场景的 `Steps:`，以规格为计划、以实际应用为准。步骤含糊（"点击按钮"，哪个按钮？）、引用已不存在的元素或与应用实际行为矛盾时，更新规格以匹配实际行为，然后继续。生成过程中修改规格属正常操作。

每个操作都会打印等价的 Playwright TypeScript：

```bash
playwright-cli snapshot                         # 查找 ref
playwright-cli fill e3 "John Doe"               # -> page.getByRole('textbox', {...}).fill(...)
playwright-cli press Enter
playwright-cli click e7
```

为每个 `- expect:` 条目添加显式断言。

收集生成的代码，写入规格指定的路径：

```ts
// spec: specs/basic-operations.plan.md
// seed: tests/seed.spec.ts
import { test, expect } from './fixtures';   // 没有 fixtures 文件时用 '@playwright/test'

test.describe('Signing in and out', () => {
  test('should sign in', async ({ page }) => {
    // 1. 导航到应用
    // （由种子 fixture 处理）

    // 2. 在用户名输入框输入 'John Doe'
    await page.getByRole('textbox', { name: 'username' }).fill('John Doe');

    // 3. 输入密码
    await page.getByRole('textbox', { name: 'password' }).fill('TestPassword');

    // 4. 按 Enter 提交
    await page.getByRole('textbox', { name: 'password' }).press('Enter');

    await expect(page.getByRole('heading')).toContainText('Welcome, John Doe!');
  });
});
```

规则：

- **每个文件一个测试。** 文件路径、describe 名称、测试名称原样取自规格，去掉序号。
- 每个编号步骤前加 `// N. <步骤文本>` 注释。
- describe 分组名原样取自规格，去掉 `1.` 序号。
- 项目有 `./fixtures` 时从中导入，否则用 `@playwright/test`。
- **重要**：进入下一场景前关闭 CLI 会话并停止后台测试。

### 2.3 生成多个场景

按 2.2 逐个处理目标场景，每个场景之间重启种子，确保测试从干净页面开始。每个场景完成后停止测试运行。

### 2.4 运行生成的测试

生成后运行一次新测试：

```bash
PLAYWRIGHT_HTML_OPEN=never npx playwright test tests/<group>/<scenario>.spec.ts
```

失败用例进入第 3 节。

---

## 3. 修复

目标：修复失败测试；应用预期行为变化时更新规格。

### 3.1 找出失败测试

```bash
PLAYWRIGHT_HTML_OPEN=never npx playwright test
```

记录失败的 `<file>:<line>` 列表，逐项处理。不要并行修复，共享状态与单一 CLI 会话使并行修复不可靠。

### 3.2 调试单个失败

后台以调试模式运行单个失败测试，然后连接：

```bash
PLAYWRIGHT_HTML_OPEN=never npx playwright test tests/<group>/<scenario>.spec.ts:<line> --debug=cli
# 等待 "Debugging Instructions" 与会话名 tw-XXXX
playwright-cli attach tw-XXXX
```

测试在开始时暂停。步进或运行到失败操作或断言之前，然后诊断：

```bash
playwright-cli snapshot                # 元素是否变化、移动或改名？
playwright-cli console                 # 应用侧是否报错？
playwright-cli requests                # 请求失败？负载错误？
playwright-cli show --annotate         # 请用户指出位置
```

常见原因：选择器漂移、新增包裹元素、label/ARIA 改名、时序问题（过渡动画、异步加载）、应用更新了断言文本、测试数据在多次运行间泄漏。

用 `playwright-cli` 重演修正后的交互，输出中的生成代码可直接粘回测试。

### 3.3 应用修复

编辑测试文件：更新定位器、断言、步骤顺序或输入，使其匹配修正后的行为。停止后台调试进程，重新运行单个测试确认通过。

不得通过跳过 hook 或添加 sleep 修复。不得使用 `networkidle`。

### 3.4 与规格对齐

打开测试文件 `// spec:` 头指向的规格，找到与该测试对应的场景。

- **纯技术修复**（定位器漂移、断言形式改进），规格的用户级行为仍与应用一致 → 不改规格。
- **修复改变了规格描述的用户可见步骤、输入、顺序或预期结果** → 更新规格以匹配实际。
- **无法判断应用变更是有意为之**（规格过期）**还是回归**（测试正确，应用错误）→ **停止并询问用户**。提供：
  - 场景 id（例如 `2.3`），
  - 不再匹配的规格行，
  - 观察到的应用行为（引用快照片段或具体结果）。

用户答复后，再更新规格（有意变更）或将测试标记为覆盖缺陷（回归）。

### 3.5 迭代与放弃

- 逐个修复失败，每次修复后重新运行。
- 充分调查后确认测试正确、应用错误，且用户确认是缺陷：用 `test.fixme(...)` 标记测试，并注释说明用户决定或问题链接。不得静默跳过。
