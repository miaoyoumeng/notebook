---
description: 调度 skill-creator 完成 Claude Skill 的初始化、优化、用例编写、评分、基准测试与清理。
allowed-tools: ["Bash(find *)", "Bash(mkdir *)", "Bash(uv run python *)", "Glob", "Read", "Write", "Edit", "AskUserQuestion", "Skill", "Task"]
argument-hint: init | improve | evals | score | benchmark | clean <skill-name>
---

# Commander Skill

你是 skill-creator 的调度器。根据用户传入的子命令，调用 skill-creator 技能完成对应操作。

本命令不直接执行 `skill-creator` 目录下的脚本。用例生成、对拍评分、基准聚合、结果查看器由 skill-creator 技能负责；frontmatter 按`frontmatter 规则`核对。

用户输入：`$ARGUMENTS`

## 解析规则

`$ARGUMENTS` 是整串输入，按空白切词：第 1 个 token 是子命令，第 2 个是技能名称，其余为补充说明。斜杠命令按位注入的参数忽略不用。

子命令仅接受下列英文名，不做中文或同义词映射。子命令不在其中、或技能名称为空时，输出用法说明并停止。

## 通用约定

下文路径均相对当前工作目录；技能目录记作 `skills/<skill-name>`。

**标准目录结构**：

```text
[当前工作目录]
    ├── skills/
    │     └── <skill-name>/
    │         ├── SKILL.md          # 必需：frontmatter + 指令正文
    │         ├── README.md         # 必需：介绍如何使用这个 skill
    │         ├── scripts/          # 可选：确定性可执行脚本
    │         ├── references/       # 可选：按需加载的参考文档
    │         ├── assets/           # 可选：模板/资源文件
    │         └── evals/
    │              └── evals.json   # 可选：测试用例
```

**技能目录存在性检查**：

```bash
find skills/<skill-name> -maxdepth 0 -type d 2>/dev/null
```

有输出表示存在，无输出表示不存在。

**frontmatter 规则**（逐项核对）：

- 必需字段 `name`、`description`；可选字段 `license`、`allowed-tools`、`metadata`、`compatibility`，此外的字段非法。
- `name`：小写字母、数字、连字符，与 `<skill-name>` 目录名一致，≤64 字符。
- `description`：加引号，不含尖括号，≤1024 字符。

**用法说明**（子命令不合法或缺失时原样输出）：

```text
用法：<子命令> <skill-name> [补充说明]

子命令：
  init       按标准目录结构初始化技能（幂等，已存在则跳过）
  improve    优化 SKILL.md、scripts/、references/ 的内容
  evals      编写 evals/evals.json 中的测试用例
  score      静态质量评分，满分 10 分
  benchmark  有技能 / 无技能双跑基准对比
  clean      删除技能目录下的空目录

示例：init my-skill
      improve my-skill 把 README 里「写入本地文件」改成输出到控制台
```

## 子命令：init

**用途**：按标准目录结构初始化技能。**幂等**——已存在的文件和文件夹一律跳过，只补建缺失项，不覆盖已有内容。

**执行步骤**：

1. 技能用途不明时，用 `AskUserQuestion` 询问这个技能做什么、什么场景该触发。
2. 调用 `skill-creator` 技能，按其规范确定 `description` 的写法。
3. 逐项对照`标准目录结构`检查，按下表处理：

   | 路径 | 缺失时 | 已存在时 |
   |------|--------|----------|
   | `SKILL.md` | 创建 | 跳过 |
   | `README.md` | 创建 | 跳过 |
   | `scripts/` | 创建空目录 | 跳过 |
   | `references/` | 创建空目录 | 跳过 |
   | `assets/` | 创建空目录 | 跳过 |
   | `evals/evals.json` | 创建空骨架 | 跳过 |

4. 新建的 `SKILL.md` 写入 frontmatter 与 `## 概述`，`name` 取目录名，其余章节留待 `improve` 补全：

   ```markdown
   ---
   name: <skill-name>
   description: "<技能用途>"
   ---

   # <skill-name>

   ## 概述
   ```

5. 按`frontmatter 规则`逐项核对，不符则修正。
6. 输出初始化结果，分「已创建」「已跳过」两栏列出，并提示下一步用 `improve` 子命令完善内容。

## 子命令：improve

**用途**：优化 `skills/<skill-name>` 下 `SKILL.md`、`scripts/`、`references/` 的内容。

**执行步骤**：

1. 检查 `skills/<skill-name>` 是否存在（命令见「通用约定」），不存在则提示先运行 `init` 子命令。
2. 读取 `SKILL.md`，并列出 `scripts/`、`references/` 的文件清单；按需读取这些文件的内容。
3. 调用 `skill-creator` 技能完成修改，只做必要变更，覆盖下列要求：

   - **`SKILL.md`**——按`SKILL.md 章节模板`组织章节，按`格式要求`与`行文分格`组织行文
   - **`scripts/`**——在 `SKILL.md` 中补上每个脚本的用途与调用示例
   - **`references/`**——补齐被 `SKILL.md` 引用但缺失的章节

4. 修改后按`frontmatter 规则`复核；改动过 `scripts/` 时，运行受影响的脚本验证仍可执行。
5. 输出变更摘要与校验结果。

**约束条件**：

- `SKILL.md` 最多 500 行。
- `references/` 下参考文档最多 350 行。
- `scripts/` 下脚本不限行数。

## 子命令：evals

**用途**：为 `skills/<skill-name>` 编写 `evals/evals.json` 中的测试用例。

**执行步骤**：

1. 检查 `skills/<skill-name>` 是否存在（命令见「通用约定」），不存在则提示先运行 `init` 子命令。
2. 读取 `SKILL.md`，理解技能解决什么问题、什么场景触发。
3. 调用 `skill-creator` 技能生成 2-3 个测试用例，每个包含：
   - `prompt`：真实用户会打出来的话，带上下文与具体细节，不用抽象任务
   - `expected_output`：人类可读的成功标准
   - `expectations`：可客观验证的断言；写作风格、设计美感这类主观产物不硬套断言
   - `files`：输入文件路径（相对技能根目录），没有则省略
4. 写入 `evals/evals.json`：

   ```json
   {
     "skill_name": "<skill-name>",
     "evals": [
       {
         "id": 1,
         "prompt": "...",
         "expected_output": "...",
         "files": [],
         "expectations": ["...", "..."]
       }
     ]
   }
   ```

5. 用 `AskUserQuestion` 把用例展示给用户确认，按反馈增删改。
6. 输出最终用例清单与数量。

## 子命令：score

**用途**：对 `skills/<skill-name>` 做静态质量评分，满分 10 分。**不运行测试用例**——需要客观基准请用 `benchmark` 子命令。

**执行步骤**：

1. 检查 `skills/<skill-name>` 是否存在（命令见「通用约定」），不存在则提示先运行 `init` 子命令。
2. 读取 `SKILL.md`，以及 `scripts/`、`references/` 的文件清单和内容。
3. 按五维框架逐项打分，每个维度满分 10 分：

   | 维度 | 权重 | 评分要点 |
   |------|------|----------|
   | 文档质量 | 40% | frontmatter 完整性、章节覆盖、内容深度、AI 可执行程度 |
   | 代码质量 | 10% | `scripts/` 中脚本的正确性、可维护性（无脚本则给基准分） |
   | 参考文档质量 | 15% | `references/` 内容完整性与深度；是否存在未被 `SKILL.md` 引用的悬空文档 |
   | 完整性 | 20% | 目录结构是否齐全、必需文件是否存在 |
   | 可用性 | 15% | 触发描述是否包含用户会说的关键词、指令是否可执行 |

4. 计算加权总分：

   ```text
   总分 = 文档质量×0.40 + 代码质量×0.10 + 参考文档质量×0.15 + 完整性×0.20 + 可用性×0.15
   ```

5. 输出评分报告：

   ```markdown
   ## Skill 评分报告：<skill-name>

   总分：X/10

   | 维度 | 得分 |
   |------|------|
   | 文档质量 | X/10 |
   | 代码质量 | X/10 |
   | 参考文档质量 | X/10 |
   | 完整性 | X/10 |
   | 可用性 | X/10 |

   主要改进建议：
   - ...
   - ...
   ```

## 子命令：benchmark

**用途**：对 `skills/<skill-name>` 跑基准测试——同一批测试用例分别在**有技能**、**无技能**两种配置下运行，对比通过率、耗时与 token 消耗。

**前置条件**：`evals/evals.json` 存在且至少含一个用例。缺失时提示先运行 `evals` 子命令。

**执行步骤**：

1. 检查 `skills/<skill-name>` 是否存在（命令见「通用约定」），不存在则提示先运行 `init` 子命令。
2. 读取 `evals/evals.json` 确定用例列表。工作区取 `skills/<skill-name>-workspace/iteration-<N>/`，`<N>` 从 1 起，已存在则递增。
3. 按 `skill-creator` 技能的对拍规范，**同一轮**为每个用例启动两组子代理：

   - `with_skill` 组：传入技能路径 `skills/<skill-name>`
   - `without_skill` 组：不传技能
   - 产物落到 `iteration-<N>/eval-<ID>/{with_skill,without_skill}/outputs/`

4. 每收到一个子代理完成通知，立即把 `total_tokens`、`duration_ms` 写入该运行目录的 `timing.json`——这是唯一的捕获时机。
5. 全部完成后，为每个运行目录生成 `grading.json`；能程序化校验的断言写脚本跑，不要目测。
6. 调用 `skill-creator` 技能聚合基准数据并生成结果查看器，产出 `benchmark.json`、`benchmark.md` 与查看器页面。
7. 向用户报告：通过率、耗时、token 三项差值，以及聚合统计会掩盖的模式（例如始终通过的断言可能不具区分度、高方差的用例可能不稳定）。

## 子命令：clean

**用途**：删除 `skills/<skill-name>` 下不含任何文件的空目录。

**执行步骤**：

1. 列出待删清单：

   ```bash
   find skills/<skill-name> -depth -mindepth 1 -type d -empty -print
   ```

   `-mindepth 1` 保证技能根目录本身不会被删。

2. 清单为空，报告「无空目录」并停止。
3. 清单非空，用 `AskUserQuestion` 让用户确认后执行删除：

   ```bash
   find skills/<skill-name> -depth -mindepth 1 -type d -empty -exec rmdir {} +
   ```

4. 输出删除结果。

## SKILL.md 章节模板

```markdown
## 概述        [必填]
## 上下文层级   [必填]
## 使用时机     [必填]
## 编码四原则   [可选]
## 流程        [必填]
## 代码分析     [可选]
## 验证清单     [必填]
## 危险信号     [必填]
## 理由辩解     [必填]
## 验证        [必填]
## 实现检查表   [可选]
## 参考资料     [必填]
```

### 格式要求

- `references/` 下的文档必须被 `SKILL.md` 引用，未被引用的直接删除。
- `references/` 下的文档之间不得相互引用。
- 前后矛盾的条款重新组织，必要时直接删除。
- 有歧义的条款重新组织，必要时直接删除。
- 含义重复的条款重新组织，必要的时候直接删除。
- 不利于 AI 识别执行流程、没有意义的条款，直接删除。
- 避免生成需要用户介入和干预的条款。

### 行文分格

1. **公文风格**——准确、简明、庄重、规范，少用修辞，强调条理和格式。
2. **删除填充短语**——去除开场白和强调性拐杖词。
3. **打破公式结构**——避免二元对比、戏剧性分段、修辞性设置。
4. **变化节奏**——混合句子长度；两项优于三项；段落结尾多样化。
5. **信任读者**——直接陈述事实，跳过软化、辩解和手把手引导。
6. **删除金句**——听起来像可引用的语句，重写它。
