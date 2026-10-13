---
description: 把 prompt 提交给 deepseek / qwen / yuanbao / kimi / doubao 网页版，等回答生成完写进指定文件
allowed-tools: ["Bash(mkdir *)", "Bash(uv run python *)", "Read"]
argument-hint: deepseek | qwen | yuanbao | kimi | doubao <--prompt=[prompt]> <--dir=[目录] | --file=[文件]>
---

# Commander Chat

你是 `scripts/console.py` 的调度器：把 prompt 交给对应平台的网页版，等它回答完，结果由脚本写进指定文件。

用户输入：`$ARGUMENTS`

## 解析规则

把「用户输入」按空白切词：

- **第 1 个 token** → `provider`，取值 `deepseek`、`qwen`、`yuanbao`、`kimi`、`doubao` 之一。大小写不敏感：`DeepSeek`、`QWEN`、`Kimi` 都合法，统一按小写往下走。
- **第 1 个 token 之后的整串** → 脚本参数，**原样透传**，一个字都不改。

不做别名、不做中文映射：`ds`、`千问`、`通义`、`yb`、`元宝`、`腾讯元宝`、`moonshot`、`豆包`、`db` 一律不认。

**别用斜杠命令注入的按位编号参数（`$1`、`$2`…）来解析**：经 Skill 工具（而不是手打斜杠命令）调用时，这组编号会整体错位。以「用户输入」整串为准自己切词，两条调用路径才对得上。

**终止条件**——命中任一条，先说明原因，再原样输出「用法说明」并停止，**不调用脚本、不创建任何文件**：

- 「用户输入」为空
- provider 不在上表
- 没给 `--prompt`（短名 `-p` 也算）
- 任一 `--prompt` 的值超过 100 行（上限见「长度限制」）

## 脚本入口

一切经这个入口，**不要直接跑 `chat-<平台>.py`**：

```bash
uv run python ${CLAUDE_PLUGIN_ROOT}/scripts/console.py --model=<provider> <参数原样>
```

- `${CLAUDE_PLUGIN_ROOT}` 是**插件根目录**，`console.py` 与 5 个 `chat-<平台>.py` 都在它的 `scripts/` 下——不是当前工作目录，换个目录执行本命令，脚本位置不变
- `console.py` 只做「选哪个平台」这一件事：摘掉 `--model`，其余参数原样交给平台脚本，退出码与 stdout / stderr 全部继承
- 5 个平台脚本共用一套公共参数（`chat_base.py` 定的），另有少数平台特有参数，表末单列

### 参数表

**要提交什么、写到哪**：

| 参数 | 作用 |
|------|------|
| `--prompt=TEXT` | 要提交的问题，**必填、可重复**，按出现顺序依次提交（短名 `-p`） |
| `--dir=DIR` | 输出目录：每个 prompt 一个文件，`DIR/1.md`、`DIR/2.md`… |
| `--file=FILE` | 输出文件：本次所有回答写进这一个，第 1 个**覆盖写**、之后追加 |

`--dir` 与 `--file` **二选一**，argparse 互斥必选——缺一个、两个都给，都在脚本里报错退出。

**回答怎么处理**：

| 参数 | 作用 |
|------|------|
| `--no-markdown-hint` | 不在 prompt 末尾追加「。请用 Markdown 格式回答。」——默认会追加 |
| `--timeout=N` | 单轮等待上限秒数（默认 300） |
| `--keep-conversation` | 跑完不删左侧本次会话记录（默认会删） |

**浏览器会话**：

| 参数 | 作用 |
|------|------|
| `--show` | 不最小化窗口，留在前台（排查用） |
| `--no-open` | 跳过开浏览器（会话已经在跑时用） |
| `-s` / `--session=NAME` | playwright-cli 会话名（默认取各平台自己的） |
| `-u` / `--url=URL` | 网页版入口地址（默认取各平台自己的） |

**输出格式与轮询节奏**（一般不用动）：

| 参数 | 作用 |
|------|------|
| `--json` | 结果以 JSON 输出（默认 Markdown） |
| `--interval=N` | 轮询间隔秒数（默认 5） |
| `--page-timeout=N` | 等待页面就绪的秒数上限（默认 60） |

**平台特有**（只有这两个平台有）：

| 平台 | 参数 | 作用 |
|------|------|------|
| `deepseek` | `--no-deep-think` | 不选「深度思考」模式（默认会选上） |
| `qwen` | `--fast` | 用「快速」模式（默认切「深度思考」） |

完整参数以平台脚本自己的帮助为准——`console.py` 会把 `--help` 原样交给它：

```bash
uv run python ${CLAUDE_PLUGIN_ROOT}/scripts/console.py --model=<provider> --help
```

## 输出位置

用户没给 `--dir`、也没给 `--file` 时，**补一个**：

```text
--file=<当前工作目录>/.claude/chat-<provider>.md
```

「当前工作目录」指执行本命令时 shell 的 `pwd`——不是插件目录。换个目录执行，就写到新目录下的 `.claude/`。**给了参数就按给的走**，不要覆盖用户的选择。

`--file` 指向的文件如果已经存在，会被整个覆盖掉——这是脚本的既定语义（重跑同一批 prompt 时，旧结果本来就该换掉）。察觉用户像是要追加时，先问一句再动手。

## 长度限制

两个上限，超出时的处理不同：

| 对象 | 上限 | 超出时 |
|------|------|--------|
| 单个 `--prompt` 的值 | 100 行 | **终止**：不调用脚本，报出实际行数让用户改短 |
| 每个输出文件 | 1000 行 | **事后截断**：脚本写完后就地切到第 1000 行，报告里说明 |

**行数口径**：换行符个数加一。`--prompt` 按该参数的值算，多个 `--prompt` **各算各的**；输出文件按文件全文算。

这两个数字是可调参数，改限制只改上表。

## 执行流程

### 步骤 1 · 解析

按「解析规则」切出 provider 与参数串。命中终止条件就输出用法说明并停下。

### 步骤 2 · 补齐输出位置并建目录

**脚本不会自己建目录**：`--dir` 给的目录必须已存在，`--file` 的父目录必须已存在，否则脚本会直接报错退出。所以先把目录建好：

1. 没有 `--dir` / `--file` → 按「输出位置」补上 `--file` 参数。
2. 建目录：

   ```bash
   mkdir -p <--dir 的值；或 --file 的父目录>
   ```

### 步骤 3 · 调用脚本

```bash
uv run python ${CLAUDE_PLUGIN_ROOT}/scripts/console.py --model=<provider> <参数原样>
```

**这一步可能跑很久**——要等浏览器起来、等你登录、每个 prompt 单轮最多等 300 秒。两点注意：

- 把 Bash 调用的 `timeout` 设成上限 `600000`（10 分钟）
- `--prompt` 不止一个、或单轮可能跑满 5 分钟时，用**后台方式**起（`run_in_background: true`），跑完再往下走。否则 Bash 会在中途超时，把脚本连人带话一起掐断

脚本的进度日志走 stderr，最终结果走 stdout，两者都能看到。**日志安静不等于卡死**——脚本在等页面渲染、等你登录，别因为没输出就重复调用。

### 步骤 4 · 校验输出文件长度

对本次写出的每个文件核一遍行数（`--dir` 模式是 `1.md`…`<prompt 个数>.md`，`--file` 模式就一个）：

```bash
uv run python -c "import pathlib,sys;p=pathlib.Path(sys.argv[1]);L=p.read_text(encoding='utf-8').splitlines();n=len(L);p.write_text('\n'.join(L[:1000])+'\n',encoding='utf-8') if n>1000 else None;print(n)" <文件路径>
```

命令打印该文件的原始行数：

- ≤ 1000 → 文件原样未动，继续
- \> 1000 → **已就地截断到前 1000 行**，报告里说明

截断是硬切：**不补代码围栏、不加省略号、不改写一个字**。第 1000 行附近的 Markdown 可能不完整，这是截断的代价，照写。

### 步骤 5 · 报告

向用户报告四项：provider、写出的文件（完整路径）、本次提交了几个 prompt、每个文件各多少行。

再补两种异常：

- 有文件被截断 → 报出截断前的原始行数
- stdout 里出现「未生成完」 → 说明哪一轮没答完

## 失败处理

| 情况 | 处理 |
|------|------|
| 脚本退出码非 0 | **原样报出 stderr 里那几行提示**，不要自动重跑 |
| 未登录 | 脚本会开浏览器窗口交给用户登；照它说的做，转告用户去那个窗口完成登录，登完由用户决定要不要重跑 |
| 输出位置报错（目录不存在、把目录当成 `--file`） | 按报错修路径后，**先问用户要不要重跑**，别自己决定 |
| 单轮超时（撞 5 分钟上限） | 脚本按「未生成完」处理，并停止提交后续 prompt；照步骤 5 报告 |

**为什么不要自动重跑**：脚本在失败前可能已经提交过 prompt。重跑会重复提问，在该平台的账号里留下重复的会话记录，还得再删一遍。

## 禁止事项

- **不要**解析或重写 `--prompt` 的值——原样透传，引号、换行、标点一个字都不动
- **不要**跳过 `console.py` 直接跑 `scripts/chat-<平台>.py`
- **不要**在脚本失败时自动重跑
- **不要**改动结果文件的内容——除了步骤 4 的截断，一个字都不加
- **不要**把 stdout 的结果另存一份到别处——脚本已经写进文件了
- **不要**在脚本还在跑的时候另起一次调用

## 用法说明

「解析规则」的终止条件命中时，先报一句原因，再原样输出下面这段并停止：

```text
用法：/wubu:commander-chat <provider> --prompt=<问题> [--dir=<目录> | --file=<文件>] [其他参数]

provider：
  deepseek / qwen / yuanbao / kimi / doubao

输出位置（二选一；都不给则写入 <当前工作目录>/.claude/chat-<provider>.md）：
  --dir=DIR    每个 prompt 一个文件：DIR/1.md、DIR/2.md …
  --file=FILE  本次所有回答写进这一个文件，第 1 个覆盖写、之后追加

其他常用参数：
  --show               窗口留在前台（排查时用）
  --no-open            跳过开浏览器（会话已经在跑时用）
  --keep-conversation  不删左侧本次会话记录
  --no-markdown-hint   不追加「请用 Markdown 格式回答。」
  --json               结果以 JSON 输出
  --timeout=N          单轮等待上限秒数（默认 300）

限制：单个 prompt 不超过 100 行；输出文件不超过 1000 行（超出自动截断）

示例：
  /wubu:commander-chat deepseek --prompt="什么是量子纠缠" --file=out/答案.md
  /wubu:commander-chat kimi --prompt="问题一" --prompt="问题二" --dir=out
  /wubu:commander-chat qwen --prompt="解释一下 Transformer 的注意力机制"
```
