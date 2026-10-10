---
name: deepseek-picker
description: "DeepSeek 网页版问答抓取：委托 playwright-cli 技能在 https://chat.deepseek.com/ 提交问题，并把回答以 Markdown 输出到控制台。用户要求向 DeepSeek 提问、或抓取 DeepSeek 网页对话内容时使用，即便用户没提到浏览器或网页版。"
allowed-tools: Skill Bash(playwright-cli:*) Bash(uv run:*) AskUserQuestion
---

# deepseek-picker

## 概述

把问题打进 DeepSeek 网页版，把回答捞回来，在控制台以 Markdown 展示。

三条红线，任何步骤都不越过：

- **不写文件**——结果只输出到控制台，留档由用户自己复制
- **不代用户登录**——不代填密码，不尝试绕过登录
- **不触碰凭证**——不读取、不转存 cookie 与 token

前置条件：`playwright-cli` 技能可用（`/wubu:playwright-cli`）。

## 上下文层级

本技能横跨三层，各层归各层管：

- **本文（`SKILL.md`）**——参数、步骤、成功判据。只有本技能特有的知识放这里
- **`playwright-cli` 技能（`/wubu:playwright-cli`）**——全部浏览器命令的语法出处。本文只写"调哪个动作"，不抄它的手册
- **`scripts/extract_markdown.py`**——HTML → Markdown 转换。直接执行，不用读源码

跨层共用三个词，全篇不换同义词：

- **会话**——命名浏览器实例，本技能固定为 `-s=chat.deepseek`
- **snapshot**——读取页面状态与元素 ref 的命令，名就叫 `snapshot`，不译作「快照」
- **ref**——snapshot 给每个元素分配的编号（形如 `e15`），点击和填写都以它为靶子

## 使用时机

- 用户给出一个问题，要求「问 DeepSeek」「让 DeepSeek 回答」
- 用户要求抓取 chat.deepseek.com 上的对话内容
- 用户要求把 DeepSeek 的回答取出来（含连续追问的多轮问答）

不适用：用户问的是「DeepSeek 是什么」这类知识问题——直接回答即可，不用开浏览器。

## 流程

```mermaid
flowchart TD
    A["1 打开浏览器<br/>访问 chat.deepseek.com"] --> B{"2 已登录?"}
    B -- 否 --> C["3 请用户在窗口里登录"]
    C --> B
    B -- 是 --> D["4 选中「深度思考」模式"]
    D --> E["5 提交 prompt<br/>要求 Markdown 回复"]
    E --> F["6 等待结果<br/>上限 5 分钟"]
    F --> G{"7 目标达成?"}
    G -- 否 --> E
    G -- 是 --> H["8 控制台输出 Markdown"]
    H --> I["9 关闭浏览器"]
```

两条回环都有上限：单轮等待最多 5 分钟（步骤 6），追问最多 5 轮（步骤 7）。到点不再重试，直接输出已有结果。

### 步骤 1 · 打开浏览器

分三步走：**先开浏览器，再把窗口最小化，最后才导航**。这样窗口不会在你工作时跳出来挡视线。

```bash
playwright-cli -s=chat.deepseek open --persistent --headed
```

窗口一开就最小化：

```bash
playwright-cli -s=chat.deepseek run-code "async page => { const cdp = await page.context().newCDPSession(page); const r = await cdp.send('Browser.getWindowForTarget'); await cdp.send('Browser.setWindowBounds', { windowId: r.windowId, bounds: { windowState: 'minimized' } }); return 'minimized'; }"
```

再导航到 DeepSeek：

```bash
playwright-cli -s=chat.deepseek goto https://chat.deepseek.com/
```

- `--headed`：显示窗口——登录、验证码要肉眼确认。窗口登录时会恢复出来，见步骤 3
- `--persistent`：持久化 profile——默认是内存模式，不持久化关掉就丢登录态
- `-s=chat.deepseek`：固定会话名——**后续每条命令都要带上**
- 最小化用 `run-code` 发 CDP 指令：playwright-cli 没有 minimize 命令，只有 `resize`，改不了窗口状态
- 窗口最小化不影响后续任何命令——snapshot、eval、取值照常

### 步骤 2 · 判断登录状态

```bash
playwright-cli -s=chat.deepseek snapshot
```

- 快照里能看到输入框 → 已登录，直接进步骤 4
- 停在登录页 → 进步骤 3

### 步骤 3 · 让用户登录

**先把窗口恢复出来**——步骤 1 把它最小化了，用户看不到登录页：

```bash
playwright-cli -s=chat.deepseek run-code "async page => { const cdp = await page.context().newCDPSession(page); const r = await cdp.send('Browser.getWindowForTarget'); await cdp.send('Browser.setWindowBounds', { windowId: r.windowId, bounds: { windowState: 'normal' } }); return 'restored'; }"
```

再把已经打开的那个窗口交给用户，让他自己走完 DeepSeek 的登录流程（手机号、微信、邮箱都行），登完说一声再继续。

- **不要关掉浏览器重开**——登录态是在这个窗口里建立的
- **不要代填密码，也不要尝试绕过登录**

登完存一份登录态，profile 万一被清掉可以恢复，不用麻烦用户重登：

```bash
playwright-cli -s=chat.deepseek state-save ~/.deepseek-picker-state.json
```

路径落在用户主目录，**别落在项目里**——那文件含 token。恢复时用 `state-load ~/.deepseek-picker-state.json`。

登完回步骤 2 复核，确认进了聊天界面再往下走。

### 步骤 4 · 选中「深度思考」模式

DeepSeek 默认不开深度思考，得自己打开。**snapshot 看不出它选没选**——选中前后快照长得一模一样，只能用 `eval` 读按钮属性：

```bash
playwright-cli -s=chat.deepseek --raw eval "[...document.querySelectorAll('.ds-toggle-button')].map(b => b.textContent.trim() + ':' + b.getAttribute('aria-pressed')).join(', ')"
```

读出 `深度思考:true` → 已选中，直接进步骤 5。读出 `深度思考:false` → 未选中，接着点。

点击要走 snapshot 拿 ref：

```bash
playwright-cli -s=chat.deepseek snapshot
playwright-cli -s=chat.deepseek click <「深度思考」那一行的 ref>
```

- 点**带 `cursor=pointer` 的那一层**，不是写着「深度思考」四个字的那层——文字节点不接收点击
- 按钮是 toggle，点一下就切换。所以**必须先判断再点**，不能无条件点，否则已选中时会被取消
- 点完用上面那条 `eval` 复核，读到 `深度思考:true` 才算成功
- 旁边的按钮互不干扰，不用管

### 步骤 5 · 提交 prompt

先取 snapshot 拿输入框的 ref，再填入并提交：

```bash
playwright-cli -s=chat.deepseek snapshot
playwright-cli -s=chat.deepseek fill <输入框 ref> "<prompt>" --submit
```

- prompt 末尾加一句要求 DeepSeek 用 Markdown 格式回答——网页端默认就输出 Markdown，显式要求是为了锁死格式，免得被压成纯文本
- `--submit` 是填入后回车。若消息没发出去，补一条 `press Enter`；若 `fill` 对输入框无效，改用 `type "<prompt>"` 再 `press Enter`
- **每条浏览器命令前重新 snapshot**。ref 会在两次 snapshot 之间失效

发出后**先确认真的落地**再进步骤 6——这一步不能省，理由见「危险信号」。

### 步骤 6 · 等待并取值

DeepSeek 是流式输出，提交完立刻读只拿到半截。等到下面任一条成立再取值：

- 回答区文本长度，隔 3-5 秒读两次，两次一样
- snapshot 里「停止生成」按钮消失

**5 分钟是等待上限**。到点还没结束就停下，把已拿到的部分标成「未生成完」交给用户，不要继续干等。

取值走本技能的脚本：

```bash
uv run --project <插件根目录> python <本技能目录>/scripts/extract_markdown.py
```

- `--project` 指向插件根目录，也就是 `pyproject.toml` 所在那一层；带上它，不管当前在哪个目录都能跑
- 输出 JSON 数组，按对话顺序每轮一个元素，下标即轮次

为什么不能直接读页面文本：页面上看到的是 HTML 渲染结果，`**加粗**` 的星号、代码围栏、公式的 `$` 定界符在渲染时就被吃掉了；步骤 8 要求原样保留 Markdown，得沿 DOM 反推回语法。浏览器由 `playwright-cli` 托管（管道通信，没开调试端口，外部进程连不进去），所以脚本内部先让它把回答区 HTML 取回来，再由 Python 做转换。

### 步骤 7 · 判断是否继续追问

每轮回答到手后判断一次：用户的原始目标达成了吗？

- 没达成，或回答里有需要澄清的点 → 带新问题回步骤 5，再来一轮
- 达成了 → 进步骤 8

判断要保守：用户没要求的多轮追问别自己加。拿不准就用 `AskUserQuestion` 问一句。

**追问上限 5 轮**（首轮提问不计入）。到第 5 轮仍未达成目标就收手，把已有的各轮结果一并输出，并说明哪部分没答完。再往下加轮多半只是烧时间——每轮都要等一次流式输出，还可能撞上 5 分钟上限。用户明确要求继续，才可以接着问。

### 步骤 8 · 控制台输出

不写文件，把整段对话以 Markdown 直接输出到控制台：

```markdown
## 第 1 轮

**问**：<问题>

**答**：<回答>
```

- 回答原样保留 Markdown——DeepSeek 的输出本身就是 Markdown，抹平格式会丢代码块和公式
- 需要留档时让用户自己从控制台复制，本技能不主动写文件

### 步骤 9 · 关闭浏览器

输出完就收工，把浏览器关掉：

```bash
playwright-cli -s=chat.deepseek close
```

- **登录态不会丢**——步骤 1 用了 `--persistent`，profile 落在磁盘上，下次 `open` 还在
- 这跟步骤 3 那句「不要关掉浏览器重开」不冲突：那条说的是**登录过程中**别关，这里是**全程走完**再关

## 验证清单

每个关键动作做完，对照一遍：

- **登录**：snapshot 里能看到输入框
- **深度思考**：提交前 `eval` 读出 `深度思考:true`
- **提交**：页面标题或 URL 已切到新会话，或 snapshot 里看得到刚提交的提问
- **ref**：本条命令用的 ref 来自最近一次 snapshot
- **生成结束**：回答区文本长度隔 3-5 秒读两次一致，或「停止生成」按钮消失
- **敏感素材**：素材含密钥、客户数据、内部文档时，已向用户确认再发

## 危险信号

出现下面任一情况，停下来核对，别往下走：

- **命令报成功，页面却没反应**——大概率是 ref 失效，fill 打在了已被替换的元素上。重新 snapshot 再试
- **提交后页面毫无变化**——提交可能静默失败了。只等不查的话，会一路耗到 5 分钟上限，最后拿到空结果
- **回答看着完整，其实还在流式输出**——半截答案混进最终输出，用户未必看得出来
- **想跳过模式检查直接提交**——深度思考默认是关的，漏点这一下，拿回来的回答质量差一截
- **想直接读页面文本当 Markdown**——渲染已经吃掉了加粗星号、代码围栏和公式定界符
- **想帮用户省事，替他填密码或读 cookie**——触碰红线，立刻停手

## 理由辩解

这些念头冒出来时，都是错的：

- 「页面看起来正常，不用再确认落地了」——提交静默失败时页面看不出任何异常，这正是要确认的理由
- 「回答差不多了，先取了吧」——流式输出没有「差不多」，要么读完，要么标注未完成
- 「再等 30 秒可能就出来了」—— 5 分钟是上限，到点就把已拿到的部分标成「未生成完」
- 「用户没说要追问」——那就别追问。判断要保守，拿不准用 `AskUserQuestion` 问一句
- 「就差一步，帮他填个密码就好了」——登录永远由用户自己完成
- 「存成文件方便用户复制」——不写文件，让用户从控制台复制

## 验证

输出之前，逐项确认：

- 所有轮次的问答都在，按「## 第 N 轮」顺序排列，没有漏轮
- 回答原样保留 Markdown——代码块、加粗、公式定界符没有被抹平
- 遇上限中断的部分，明确标了「未生成完」，并说明哪部分没答完
- 没有产生任何文件

全部输出完，再确认收尾：浏览器已按步骤 9 关闭。

## 参考资料

### scripts/extract_markdown.py

从回答区取 HTML 并转成 Markdown，输出按轮次排列的 JSON 数组。

```bash
uv run --project <插件根目录> python <本技能目录>/scripts/extract_markdown.py
```

`--project` 指向插件根目录（`pyproject.toml` 所在那一层），带上它，不管当前在哪个目录都能跑。

### playwright-cli 技能

`/wubu:playwright-cli`——全部浏览器命令的语法出处。

### 回答区选择器

`.ds-assistant-message-main-content`，回退 `.ds-markdown`。

### 深度思考按钮

`.ds-toggle-button` 里文字为「深度思考」的那个，选中态看 `aria-pressed=true`。snapshot 不反映这个属性，只能用 `eval` 读。2026-10-10 实测：默认未选中，点击后 `aria-pressed` 转 true、class 多出 `ds-toggle-button--selected`；旁边的「智能搜索」默认已选中，两者互不排斥。
