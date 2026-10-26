---
name: playwright-cli
description: "用 playwright-cli 在真实浏览器中执行自动化操作：打开页面、点击输入、截图导出、录制视频与追踪、读取控制台和网络请求，并运行、生成、调试 Playwright 测试。用户提出浏览器自动化、网页功能验证、表单填报、页面截图、模拟接口返回或 Playwright 测试相关需求时使用。"
allowed-tools: Bash(playwright-cli:*) Bash(pnpm:*)
---

# playwright-cli

## 概述

playwright-cli 以命令行驱动本机浏览器。每条命令作用于当前命名会话中的浏览器实例，执行后返回页面状态与快照文件路径；快照中的元素引用（形如 `e15`）是后续操作的主要定位依据。

基本闭环：打开会话 → 快照取 ref → 操作元素 → 再次快照确认 → 关闭会话。

## 上下文层级

| 层级 | 内容 | 加载时机 |
|------|------|----------|
| 第一层 | 本文件：命令清单、标准流程、验证清单 | 默认加载 |
| 第二层 | `references/` 下的专题文档 | 涉及测试运行、请求模拟、追踪、视频、登录态、规格驱动测试等主题时按需读取 |

不要预先读取全部参考文档。

## 使用时机

满足任一条件即触发：

- 打开网页并执行交互：点击、输入、拖拽、上传、选择、勾选
- 验证页面功能或复现前端缺陷
- 截图、导出 PDF、录制视频或追踪
- 查看控制台日志、网络请求，或拦截并模拟接口响应
- 生成、运行、调试 Playwright 测试
- 保存并复用登录态

不触发：

- 不涉及浏览器渲染的纯 HTTP 接口测试
- 大规模长时间爬取

## 快速开始

以下命令假设 `playwright-cli` 已在 PATH；本地安装场景将 `playwright-cli` 替换为 `pnpm exec playwright-cli`。

```bash
# 打开浏览器
playwright-cli open
# 导航
playwright-cli goto https://playwright.dev
# 用快照中的 ref 操作元素
playwright-cli click e15
playwright-cli type "page.click"
playwright-cli press Enter
# 截图（快照更常用）
playwright-cli screenshot
# 关闭
playwright-cli close
```

## 流程

### 1. 确认命令可用

```bash
playwright-cli --version
pnpm exec playwright-cli --version
```

全局命令不可用时试本地命令；本地可用则后续统一使用 `pnpm exec playwright-cli`。两者都不可用时安装：

```bash
pnpm add -g @playwright/cli@latest
```

### 2. 打开浏览器

```bash
playwright-cli open
playwright-cli open https://example.com
playwright-cli -s=mysession open https://example.com --persistent
```

浏览器类型、持久化配置、连接已有浏览器等参数见「命令参考 · 打开与连接参数」。未指定 `-s` 时使用默认会话。

### 3. 获取快照

```bash
playwright-cli snapshot
```

每条命令执行后自动返回当前页面快照，格式如下：

```text
### Page
- Page URL: https://example.com/
- Page Title: Example Domain
### Snapshot
[Snapshot](.playwright-cli/page-2026-02-14T19-22-42-679Z.yml)
```

指定文件名、只快照某个元素、限制深度或附带包围盒，用 `snapshot` 的可选参数。

### 4. 定位元素

优先使用最新快照中的 ref。ref 失效时依次降级：

```bash
playwright-cli click e15
playwright-cli click "#main > button.submit"
playwright-cli click "getByRole('button', { name: 'Submit' })"
playwright-cli click "getByTestId('submit-button')"
```

### 5. 执行操作

按任务选择交互、键盘、鼠标、导航、对话框、页面求值或标签页命令，完整清单见「命令参考」。页面状态改变后重新快照。

### 6. 取证与输出

截图、PDF、控制台、网络、追踪、录像、标注命令见「命令参考」。需要管道处理或结构化结果时使用全局选项 `--raw` 与 `--json`。

### 7. 复用登录态

```bash
playwright-cli state-save auth.json
playwright-cli state-load auth.json
```

新会话用 `state-load` 恢复登录态。cookies 与本地存储的逐项操作见命令参考。

### 8. 结束会话

```bash
playwright-cli close
playwright-cli -s=mysession close
playwright-cli list
```

任务结束必须关闭浏览器。`close-all` 清理全部会话，`kill-all` 强制终止全部浏览器进程，仅用于失控场景。

## 命令参考

### 核心交互

```bash
playwright-cli open
playwright-cli open https://example.com/
playwright-cli goto https://playwright.dev
playwright-cli type "search query"
playwright-cli click e3
playwright-cli dblclick e7
playwright-cli fill e5 "user@example.com" --submit   # --submit 填完后按 Enter
playwright-cli drag e2 e8
playwright-cli drop e4 --path=./image.png             # 从页面外部拖入文件
playwright-cli drop e4 --data="text/plain=hello world"
playwright-cli hover e4
playwright-cli select e9 "option-value"
playwright-cli upload ./document.pdf
playwright-cli check e12
playwright-cli uncheck e12
playwright-cli snapshot
playwright-cli eval "document.title"
playwright-cli eval "el => el.textContent" e5
playwright-cli eval "el => el.id" e5
playwright-cli eval "el => el.getAttribute('data-testid')" e5
playwright-cli dialog-accept
playwright-cli dialog-accept "confirmation text"
playwright-cli dialog-dismiss
playwright-cli resize 1920 1080
playwright-cli close
```

### 导航

```bash
playwright-cli go-back
playwright-cli go-forward
playwright-cli reload
```

### 键盘

```bash
playwright-cli press Enter
playwright-cli press ArrowDown
playwright-cli keydown Shift
playwright-cli keyup Shift
```

### 鼠标

```bash
playwright-cli mousemove 150 300
playwright-cli mousedown
playwright-cli mousedown right
playwright-cli mouseup
playwright-cli mouseup right
playwright-cli mousewheel 0 100
```

### 截图与 PDF

```bash
playwright-cli screenshot
playwright-cli screenshot e5
playwright-cli screenshot --filename=page.png
playwright-cli screenshot --hires
playwright-cli pdf --filename=page.pdf
```

### 标签页

```bash
playwright-cli tab-list
playwright-cli tab-new
playwright-cli tab-new https://example.com/page
playwright-cli tab-close
playwright-cli tab-close 2
playwright-cli tab-select 0
```

### 存储

```bash
# 整体状态
playwright-cli state-save
playwright-cli state-save auth.json
playwright-cli state-load auth.json

# Cookies
playwright-cli cookie-list
playwright-cli cookie-list --domain=example.com
playwright-cli cookie-get session_id
playwright-cli cookie-set session_id abc123
playwright-cli cookie-set session_id abc123 --domain=example.com --httpOnly --secure
playwright-cli cookie-delete session_id
playwright-cli cookie-clear

# LocalStorage
playwright-cli localstorage-list
playwright-cli localstorage-get theme
playwright-cli localstorage-set theme dark
playwright-cli localstorage-delete theme
playwright-cli localstorage-clear

# SessionStorage
playwright-cli sessionstorage-list
playwright-cli sessionstorage-get step
playwright-cli sessionstorage-set step 3
playwright-cli sessionstorage-delete step
playwright-cli sessionstorage-clear
```

### 网络

```bash
playwright-cli route "**/*.jpg" --status=404
playwright-cli route "https://api.example.com/**" --body='{"mock": true}'
playwright-cli route-list
playwright-cli unroute "**/*.jpg"
playwright-cli unroute
```

### 控制台与调试

```bash
playwright-cli console
playwright-cli console warning
playwright-cli requests
playwright-cli request 5
playwright-cli run-code "async page => await page.context().grantPermissions(['geolocation'])"
playwright-cli run-code --filename=script.js
playwright-cli tracing-start
playwright-cli tracing-stop
playwright-cli video-start video.webm
playwright-cli video-chapter "Chapter Title" --description="Details" --duration=2000
playwright-cli video-stop
playwright-cli video-show-actions --duration=600 --position=top-right
playwright-cli video-hide-actions
playwright-cli show --annotate
playwright-cli generate-locator e5 --raw
playwright-cli highlight e5
playwright-cli highlight e5 --style="outline: 3px dashed red"
playwright-cli highlight e5 --hide
playwright-cli highlight --hide
```

`video-show-actions` 为后续每个操作添加标注，显示动作名称并高亮目标元素。`show --annotate` 打开标注面板，用户框选页面并留言，命令返回标注截图、区域快照与文字说明。`generate-locator` 由 ref 或选择器生成 Playwright 定位器。`highlight` 为元素显示持久高亮浮层，`--style` 自定义样式。

### 全局选项

`--raw` 去掉页面状态、生成代码与快照段落，只返回结果值；无输出命令返回空。`--json` 将响应包装为 JSON。

```bash
playwright-cli --raw eval "JSON.stringify(performance.timing)" | jq '.loadEventEnd - .navigationStart'
playwright-cli --raw eval "JSON.stringify([...document.querySelectorAll('a')].map(a => a.href))" > links.json
playwright-cli --raw snapshot > before.yml
playwright-cli click e5
playwright-cli --raw snapshot > after.yml
diff before.yml after.yml
TOKEN=$(playwright-cli --raw cookie-get session_id)
playwright-cli --raw localstorage-get theme
playwright-cli list --json
```

### 快照参数

```bash
playwright-cli snapshot                              # 默认：按时间戳命名保存到文件
playwright-cli snapshot --filename=after-click.yaml  # 指定文件名
playwright-cli snapshot "#main"                      # 只快照指定元素
playwright-cli snapshot --depth=4                    # 限制深度
playwright-cli snapshot --boxes                      # 附带包围盒 [box=x,y,width,height]
```

### 元素定位

```bash
playwright-cli click e15                                  # 快照 ref
playwright-cli click "#main > button.submit"              # CSS 选择器
playwright-cli click "getByRole('button', { name: 'Submit' })"
playwright-cli click "getByTestId('submit-button')"
```

### 打开与连接参数

```bash
playwright-cli open --browser=chrome      # chrome | firefox | webkit | msedge
playwright-cli open --persistent          # 持久化配置，默认配置在内存中
playwright-cli open --profile=/path/to/profile
playwright-cli open --config=my-config.json
playwright-cli attach --extension=chrome                # 通过 Playwright 扩展连接
playwright-cli attach --cdp=chrome                      # 通过 channel 连接已运行的 Chrome
playwright-cli attach --cdp=msedge
playwright-cli attach --cdp=http://localhost:9222       # 通过 CDP 端点连接
playwright-cli close
playwright-cli -s=msedge detach           # 断开连接，保留外部浏览器
playwright-cli delete-data                # 删除默认会话的用户数据
```

### 多会话管理

```bash
playwright-cli -s=mysession open example.com --persistent
playwright-cli -s=mysession open example.com --profile=/path/to/profile
playwright-cli -s=mysession click e6
playwright-cli -s=mysession close
playwright-cli -s=mysession delete-data
playwright-cli list
playwright-cli close-all
playwright-cli kill-all
```

### Windows 下含 & 的 URL

`cmd.exe` 与 PowerShell 会把 `&` 当作命令分隔符，导致多参数 URL 被截断。

```batch
playwright-cli goto "https://example.com/?a=1^&b=2"
```

```powershell
playwright-cli --% goto "https://example.com/?a=1&b=2"
```

## 示例

### 表单提交

```bash
playwright-cli open https://example.com/form
playwright-cli snapshot
playwright-cli fill e1 "user@example.com"
playwright-cli fill e2 "password123"
playwright-cli click e3
playwright-cli snapshot
playwright-cli close
```

### 多标签

```bash
playwright-cli open https://example.com
playwright-cli tab-new https://example.com/other
playwright-cli tab-list
playwright-cli tab-select 0
playwright-cli snapshot
playwright-cli close
```

### 控制台与请求调试

```bash
playwright-cli open https://example.com
playwright-cli click e4
playwright-cli fill e7 "test"
playwright-cli console
playwright-cli requests
playwright-cli close
```

### 追踪调试

```bash
playwright-cli open https://example.com
playwright-cli tracing-start
playwright-cli click e4
playwright-cli fill e7 "test"
playwright-cli tracing-stop
playwright-cli close
```

### 交互式界面走查

```bash
playwright-cli open https://example.com
playwright-cli show --annotate
```

## 验证清单

- [ ] 命令可用性已确认（`playwright-cli --version` 或 `pnpm exec playwright-cli --version`）
- [ ] 操作前已取得快照，元素 ref 来自最新快照
- [ ] 每次改变页面状态后重新快照，确认结果符合预期
- [ ] 截图、视频、追踪、下载文件已落到指定路径
- [ ] 任务涉及控制台时，已检查未处理的报错
- [ ] 浏览器已关闭，或按用户要求保留

## 危险信号

出现下列行为时停止并纠正：

- 未快照直接猜测元素 ref 或坐标
- 使用上一次快照的 ref 操作已变化的页面
- 页面加载未完成就断言结果
- 用 `kill-all` 代替正常关闭
- 并行任务共用默认会话导致状态互相覆盖
- 未确认用户意图就执行删除账号、清空数据等不可逆操作

## 理由辩解

| 借口 | 事实 |
|------|------|
| 页面肉眼看起来正常，不用再快照 | 页面变化可能异步发生，快照是唯一可核对的证据 |
| ref 只是编号，猜一下也能点 | ref 每次快照重新分配，猜测会导致误操作 |
| 先截图再说，后面再看 | 截图不能替代快照，后续操作依赖 ref |
| 关闭浏览器会丢失状态 | 持久化需求用 `--persistent` 或 `state-save` 实现，不靠不关浏览器 |
| 测试跑一遍就行，不必看失败详情 | 失败用例必须读取错误输出与追踪，才能定位原因 |

## 验证

完成标准：

1. 用户要求的目标状态已由页面快照或输出证明，而非仅凭命令返回码。
2. 涉及文件产物时，用 `ls -l <路径>` 确认文件存在且非空。
3. 涉及测试时，报告通过数量、失败数量与失败原因。
4. 会话已按约定关闭，无残留进程。

## 参考资料

- [运行与调试 Playwright 测试](references/playwright-tests.md)
- [请求模拟](references/request-mocking.md)
- [在页面中运行代码](references/running-code.md)
- [浏览器会话管理](references/session-management.md)
- [规格驱动测试：规划、生成、修复](references/spec-driven-testing.md)
- [存储状态：cookies 与 localStorage](references/storage-state.md)
- [测试生成](references/test-generation.md)
- [追踪](references/tracing.md)
- [视频录制](references/video-recording.md)
- [元素属性检查](references/element-attributes.md)
