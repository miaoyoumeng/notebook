---
description: 向指定 AI 平台网页版提问，抓取回答并转成标准化 User Story 文档落盘
argument-hint: doubao | deepseek | kimi | qwen | xunfei | yuanbao <--prompt=[prompt]> [--dir=<目录>]
---

# commander-story

## 定位

编排两个技能，完成「向平台提问 → 写成 User Story 并落盘」：

```text
解析参数 → 提交 prompt（browser-chat）→ 生成 User Story 并落盘（user-story-writer）→ 报告
```

命令只做编排，不设用户批准环节。

## 执行步骤

### 步骤 1 · 解析并校验参数

从 `$ARGUMENTS` 取出三个参数，按下表核对：

| 短名 | 平台 | 中文名 |
|------|------|--------|
| `doubao` | 豆包 | 豆包 |
| `deepseek` | DeepSeek | DeepSeek |
| `kimi` | Kimi | Kimi |
| `qwen` | 千问 | 千问 |
| `xunfei` | 讯飞星火 | 讯飞星火 |
| `yuanbao` | 腾讯元宝 | 腾讯元宝 |

```text
model name  第一个位置参数，必填，必须命中小表；中文名按表转换
--prompt    取 = 之后的原文；至少一个，可同时出现多个
--dir       取 = 之后的原文；未给时取默认值 /tmp/story
```

三个值在此确定，供步骤 2、步骤 3 共用，后续步骤不再变更。
`model name` 或 `--prompt` 不通过：报出可选值或用法后停止，不执行后续步骤。

### 步骤 2 · 提交 prompt

调用 Skill 工具，`skill: "browser-chat"`（用户侧写作 `/sunny:browser-chat`），`args` 按下式拼接后整体交给它：

```text
--model=<model name> --prompt="<问题 1 原文>" [--prompt="<问题 2 原文>" …] --dir="<落盘目录>"
```

各占位符填入步骤 1 确定的值。用户额外写的其他 browser-chat 参数，追加到同一串末尾：

```text
--model=kimi --prompt="…" --dir="/tmp/story" --timeout=600 --no-markdown-hint
```

可追加的参数：

```text
--no-markdown-hint   不在 prompt 末尾追加「。请用 Markdown 格式回答。」
--timeout=N          单个 prompt 等待上限秒数（默认 300）
--keep-conversation  保留左侧本次会话记录
--interval=N         轮询间隔秒数
--page-timeout=N     等待页面就绪的秒数上限
```

上表仅供参考，参数含义与完整清单以 browser-chat 的 SKILL.md 为准。

技能自行完成开浏览器、校验登录、处理验证码、提交问题、等待生成、取值、落盘、清理会话。原始回答的文件名与个数由 browser-chat 按其 `--dir` 约定决定，本命令不复述。

在`控制台`上输出 `browser-chat` 产生的 markdown 文件路径，格式如下：
```text
- [/path/to/prompt-story-response.md]
……
- [/path/to/prompt-story-response.md]
```


### 步骤 3 · 生成 User Story 并落盘

逐个读取`步骤 2`产生的 markdown 文件，调用 Skill 工具，`skill: "user-story-writer"`（用户侧写作 `/sunny:user-story-writer`），覆盖该技能的三项默认：

```text
上下文材料   = 步骤 2 在 <落盘目录> 下写出的原始回答文件。
落盘位置     = <落盘目录>/story-<序号>.md。
文件数量     = 一个`步骤 2 产生的文件` 对应 一个`<落盘目录>/story-<序号>.md`。
落盘时机     = 生成后直接写入，不等待用户批准。
落盘后操作   = 删除 `步骤 2 产生的文件`。
```

澄清轮次、`[待确认]` 规则、INVEST 与验收标准等编写规范，以该技能自带约定为准。

落盘目录不存在时先建立：

```bash
mkdir -p "<落盘目录>"
```

目标文件已存在时**直接覆盖**，不询问、不改名。

### 步骤 4 · 报告

| 项 | 内容 |
|----|------|
| 平台 | model name |
| User Story 文件 | 完整路径 |
| 异常 | 未生成完的轮次、`[待确认]` 项数；无则填「无」 |

报告所列文件须真实存在，路径与实际一致。

## 约束

- **参数按值拼接**——除 `--dir` 缺省补 `/tmp/story` 外，不解析、不改写用户输入的任何参数。
- **技能是唯一边界**——不得绕过技能直接调用其内部脚本，也不得重复调用或自行重跑；失败前可能已提交 prompt，重跑会造成重复提问、留下重复会话。原样报错，交用户决定。
- **不得伪造平台回答**——平台失败或无回答时，不得以模型自身输出顶替或「完善」原始回答，失败即如实报告。
- **不清理文件**——原始回答文件保留，供复核与复盘。
- **落盘兜底**——`user-story-writer` 配置为 `max_turns: 3` 且工具集不含 `Write`；若其未能写盘，由本命令代为 `Write`（内容取自其生成结果，不作改写），并在报告中注明来源。
