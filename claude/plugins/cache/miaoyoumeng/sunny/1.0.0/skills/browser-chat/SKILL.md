---
name: browser-chat
description: "各 AI 平台网页版（doubao、deepseek、glm、kimi、qwen、xunfei、yuanbao、wenxin）的批量提问与回答落盘。用户要求向这些平台网页版提问、抓取回答或落盘留档时使用，即便未提及浏览器或网页版。"
---

# browser-chat

## 概述

单次调用完成以下环节：

```text
开浏览器 → 校验登录 → 逐个提交 prompt → 等待生成完毕 → 取值 → 落盘 → 删除本次会话 → 关闭浏览器
```

仅登录与验证码需要用户介入。

## 上下文层级

- **`SKILL.md`**（本文）——适用场景、参数约定、结果报告
- **`scripts/`**——执行实现，入口为 `console.py`
- **`references/`**——参考文档（当前为空）

技能目录为 `${CLAUDE_PLUGIN_ROOT}/skills/browser-chat`。

## 使用时机

适用：用户要求向 DeepSeek、千问、元宝、Kimi、豆包、智谱、讯飞、文心一言提问，或将问题提交至这些平台网页版、抓取回答存为文件。

不适用：知识性问题（如「DeepSeek 是什么」）直接回答；调用 API 不经本技能。

## 参数约定

用户以 `--xxx=值` 形式给出的参数，原样拼进 `console.py` 的调用：不改写、不重排、不删减、不改值。技能只补两样——`--model=<短名>`（用户直接给了就照用），以及用户未给输出位置时的默认 `--dir` / `--file`。

用户按脚本参数下指令，说明他心里就是那条命令。重述一遍再拼回去，改动他察觉不到：合并多个 `--prompt` 会少问几个问题；把 `--timeout=600` 换回默认值，长回答等不到收尾就报未完成；把 `--json` 当成「输出偏好」自作主张转回 Markdown，整份结果没法机读。

拼 Bash 命令时 `--prompt` 的值用双引号包住，值内部的 `"`、`` ` ``、`$`、`\` 先转义，否则 shell 先解析一遍，原文到不了脚本。

### 平台

| 短名 | 平台 | 特有开关 |
|------|------|----------|
| `doubao` | 豆包 | — |
| `deepseek` | DeepSeek | `--no-deep-think` |
| `glm` | 智谱 | `--no-max-thinking` |
| `kimi` | Kimi | — |
| `qwen` | 千问 | `--fast` |
| `xunfei` | 讯飞星火 | `--no-auto-mode` |
| `yuanbao` | 腾讯元宝 | — |
| `wenxin` | 文心一言 | `--no-auto-mode` |

用户以中文平台名（「千问」「豆包」）表述时，转换为短名后再传入；脚本仅识别短名。平台未指明时询问用户，不作推测。

### 问题

问题原样传入 `--prompt`，不作修改。

脚本默认在末尾追加「。请用 Markdown 格式回答。」，用于固定回答格式；`--no-markdown-hint` 可取消。

单个 `--prompt` 不超过 100 行（换行符个数加一），多个 `--prompt` 分别计算。超出时询问用户是否精简，不得截断。

### 输出位置

`--dir` 与 `--file` 二选一：

- `--dir=DIR`——每个 prompt 一个文件，依次命名 `1.md`、`2.md`
- `--file=FILE`——全部回答写入同一文件，首个覆盖写入，其后追加

用户已给 `--dir` 或 `--file` 时原样照用；未给时默认传入 `--file=<当前工作目录>/.claude/chat-<平台短名>.md`。「当前工作目录」指执行时的 shell `pwd`。

`--file` 指向的既有文件将被整体覆盖。用户表述含追加意图时，先确认。

## 流程

### 步骤 1 · 确定参数

先收下用户直接给出的参数，原样保留。平台未定时，从他的表述里取平台名转成 `--model=<短名>`；`--prompt` 未给时用他的原话作值；输出位置未给时按上节补默认值。

### 步骤 2 · 建立输出目录

脚本不自动建目录，`--dir` 的目录与 `--file` 的父目录须预先存在：

```bash
mkdir -p <--dir 的值；或 --file 的父目录>
```

### 步骤 3 · 调用脚本

```bash
uv run --project ${CLAUDE_PLUGIN_ROOT} python ${CLAUDE_PLUGIN_ROOT}/skills/browser-chat/scripts/console.py --model=<短名> <参数>
```

耗时较长，需等待浏览器启动与用户登录，单个 prompt 的等待上限为 300 秒。

- Bash 调用超时设为 `600000`（10 分钟）
- `--prompt` 多于一个时以 `run_in_background: true` 启动，完成后继续

进度日志输出至 stderr，最终结果输出至 stdout。日志长时间无输出属正常，此时脚本在等待页面响应或用户登录，不得重复调用。

### 步骤 4 · 校验输出文件长度

单个输出文件不超过 1000 行。对本次写出的每个文件执行：

```bash
uv run --project ${CLAUDE_PLUGIN_ROOT} python -c "import pathlib,sys;p=pathlib.Path(sys.argv[1]);L=p.read_text(encoding='utf-8').splitlines();n=len(L);p.write_text('\n'.join(L[:1000])+'\n',encoding='utf-8') if n>1000 else None;print(n)" <文件路径>
```

命令输出原始行数。不超过 1000 时文件未改动；超过时已截断至前 1000 行。脚本中途停止时，只校验已写出的文件。

截断按行边界硬切，不补语法，不加标注。第 1000 行附近的 Markdown 可能不完整。

### 步骤 5 · 报告

报告平台、输出文件完整路径、提交的 prompt 数量、各文件行数。

文件被截断时报出原始行数；stdout 出现「未生成完」时说明未完成的轮次。

## 参数速查

| 参数 | 作用 |
|------|------|
| `--model=<短名>` | 目标平台，取上表短名；由技能补入，用户直接给出时照用 |
| `--prompt=TEXT` | 要提交的问题，必填、可重复，按出现顺序依次提交（短名 `-p`） |
| `--dir=DIR` | 输出目录：每个 prompt 一个文件 |
| `--file=FILE` | 输出文件：全部回答写入同一文件 |
| `--no-markdown-hint` | 不在 prompt 末尾追加「。请用 Markdown 格式回答。」 |
| `--timeout=N` | 单个 prompt 的等待上限秒数（默认 300） |
| `--keep-conversation` | 保留左侧本次会话记录（默认删除；glm 的对话不落库，此项对其无效） |
| `--show` | 不最小化窗口，留在前台（排查用） |
| `--no-open` | 跳过开浏览器（会话已在运行时用） |
| `--json` | 结果以 JSON 输出（默认 Markdown） |
| `-s` / `--session=NAME` | playwright-cli 会话名（默认取各平台自身的） |
| `-u` / `--url=URL` | 网页版入口地址（默认取各平台自身的） |
| `--interval=N` | 轮询间隔秒数（默认 5） |
| `--page-timeout=N` | 等待页面就绪的秒数上限（默认 60） |

`--dir` 与 `--file` 二选一必填，缺一个或两个均给时脚本报错退出。完整参数以脚本自身帮助为准：

```bash
uv run --project ${CLAUDE_PLUGIN_ROOT} python ${CLAUDE_PLUGIN_ROOT}/skills/browser-chat/scripts/console.py --model=<短名> --help
```

## 验证清单

- **目录**：`--dir` 或 `--file` 的父目录已存在
- **参数**：`--prompt` 至少一个；`--dir` 与 `--file` 恰好满足一个，未指定时由默认值补足
- **透传**：调用里给出的参数逐个出现在最终命令中，值与用户所写一致
- **退出码**：脚本退出码为 0
- **落盘**：报告所列文件存在，行数已核对
- **敏感素材**：问题含密钥、客户数据或内部文档时，提交前经用户确认，该内容将发送至第三方平台

## 危险信号

出现下列情形时暂停执行，核对后继续：

- **脚本退出码非 0，拟重新执行**——脚本失败前可能已提交 prompt，重跑将造成重复提问，并在用户账号留下重复会话。应原样报出 stderr 内容，交用户决定
- **脚本长时间无输出，拟重新启动**——脚本正在等待页面响应或用户登录。同一平台同一时间仅允许一个调用
- **拟跳过 `console.py` 直接调用 `chat-<平台>.py`**——统一入口是版本升级的替换点，跳过将遗漏一层
- **拟改写、合并或重排用户给出的参数**——原样透传，逐字保留，只补 `--model` 与缺省输出位置
- **拟修改结果文件**——除步骤 4 的截断外不作增删
- **页面出现验证码、滑块或反复跳转登录页**——交用户手动处理，不重试
- **拟代为填写密码或读取 cookie**——禁止

## 理由辩解

- 用户给的参数可以整理后再传——原样透传，整理造成的偏差用户看不见
- 用户未指定输出位置即可自行选定——应使用默认值或询问用户
- 问题过长可先行精简——应原样传入，超出 100 行时询问用户
- 页面状态正常即无需确认——脚本自行确认，外部干预应避免

## 验证

- 报告所列文件均存在，行数与报告一致
- 截断过的文件已注明原始行数
- 无第二次调用，结果文件未经手工修改

## 参考资料

### 登录预检

需提前完成某平台登录时，可单独执行校验：

```bash
uv run --project ${CLAUDE_PLUGIN_ROOT} python ${CLAUDE_PLUGIN_ROOT}/skills/browser-chat/scripts/platform-logined-validator.py --platform=<短名>
```

`--platform` 可重复给值，也可给 `all` 以校验全部平台。未登录时开窗口等待用户完成登录，登录后返回。

### 登录态

登录态挂载于 playwright 持久化 profile，各平台一个会话，关闭浏览器后保留。

备份使用 playwright-cli 的 `state-save`，存储位置须在用户主目录，不得落在项目内——该文件含 token。

### 依赖

脚本依赖（BeautifulSoup、playwright 等）声明于插件根目录的 `pyproject.toml`。调用一律使用 `uv run --project ${CLAUDE_PLUGIN_ROOT}`。
