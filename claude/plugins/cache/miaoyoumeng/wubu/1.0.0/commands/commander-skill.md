---
description: 调度 skill-creator 完成 Claude Skill 的初始化、优化、用例编写、评分、基准测试与清理。
allowed-tools: ["Bash(uv run python *)", "Bash(python3 *)", "Bash(cd *)", "Bash(find *)", "Bash(git *)", "Read", "Glob", "Write", "Edit", "AskUserQuestion", "Skill", "Task"]
argument-hint: init | improve | evals | score | benchmark | clean <skill-name>
---

# Commander Skill

你是 skill-creator 的调度器。根据用户传入的子命令，调用 skill-creator 完成对应操作。

用户输入：`$ARGUMENTS`

## 解析规则

- `$1` = 子命令（init / improve / evals / score / benchmark / clean）
- `$2` = 技能名称

子命令仅接受上述英文名，不做中文或同义词映射。子命令不在上述六者中、或技能名称为空，均输出用法说明并停止。

---

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
    └── [other dir]                 # 已存在的目录无需再创建
```

**技能目录存在性检查**（多个子命令复用）：

```bash
find skills/<skill-name> -maxdepth 0 -type d 2>/dev/null
```

有输出表示存在，无输出表示不存在。`-maxdepth 0` 只匹配目录自身，不会递归命中嵌套的同名目录。

**frontmatter 校验命令**（多个子命令复用）：

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/skill-creator/scripts/quick_validate.py skills/<skill-name>
```

退出码 0 为通过；非 0 时按输出的错误信息修正 `SKILL.md` 的 frontmatter。

**用法说明**（子命令不合法或缺失时原样输出）：

```text
用法：<子命令> <skill-name>

子命令：
  init       按标准目录结构初始化技能（幂等，已存在则跳过）
  improve    优化 SKILL.md、scripts/、references/ 的内容
  evals      编写 evals/evals.json 中的测试用例
  score      静态质量评分，满分 10 分
  benchmark  有技能 / 无技能双跑基准对比
  clean      删除技能目录下的空目录

示例：init my-skill
```

---

## 子命令：init

**用途**：按标准目录结构初始化技能。**幂等**——已存在的文件和文件夹一律跳过，只补建缺失项，不覆盖已有内容。

**执行步骤**：

1. 调用 `skill-creator` 技能，说明要创建 `skills/<skill-name>/` 目录。
2. 逐项对照`标准目录结构`检查，按下表处理：

   | 路径 | 缺失时 | 已存在时 |
   |------|--------|----------|
   | `SKILL.md` | 创建骨架 | 跳过 |
   | `README.md` | 创建 | 跳过 |
   | `scripts/` | 创建空目录 | 跳过 |
   | `references/` | 创建空目录 | 跳过 |
   | `assets/` | 创建空目录 | 跳过 |
   | `evals/evals.json` | 创建空骨架 | 跳过 |

3. 新建 `SKILL.md` 时写入最小骨架，正文留待 `improve` 子命令完善：

   ```markdown
   ---
   name: <skill-name>
   description: <待完善>
   ---

   # <skill-name>

   ## 何时使用

   ## 执行步骤
   ```

4. 无法从上下文推断技能用途时，用 `AskUserQuestion` 询问这个技能做什么、什么场景该触发，再做落笔。

5. 校验 frontmatter 必填字段（命令见「通用约定」）：
   - `name`：小写 + 连字符，≤64 字符，必须与 `<skill-name>` 目录名一致，不一致就提示修改。
   - `description`：≤1024 字符，包含触发关键词。
   - 不得包含保留词（"anthropic"、"claude"、其他模型名称）。

6. 校验失败，按错误信息修正后重新校验。
7. 输出初始化结果，分「已创建」「已跳过」两栏列出，并提示下一步用 `improve` 子命令完善内容。

---

## 子命令：improve

**用途**：优化 `skills/<skill-name>` 下 `SKILL.md`、`scripts/`、`references/` 的内容。

**执行步骤**：

1. 检查 `skills/<skill-name>` 是否存在（命令见「通用约定」），不存在则提示先运行 `init` 子命令。
2. 读取 `SKILL.md`，并列出 `scripts/`、`references/` 的文件清单；按需读取这些文件的内容。
3. 调用 `skill-creator` 技能，按文件类型应用其编辑工作流：

   **`SKILL.md`**
   - 删除基础模型已具备的通用建议
   - 保留关键的命令语法、认证注意事项、安全规则和校验步骤
   - 除非明确需要，否则把表格替换为项目符号列表
   - 放松散文风格，允许使用片段
   - frontmatter 规则：`description` 必须加引号；描述写成名词短语，包含简短通用的触发短语，而非完整工作流；只把触发关键信息放进 frontmatter

   **`scripts/`**
   - 修正逻辑错误，补输入校验与失败提示
   - 抽掉重复代码；多个脚本共用的逻辑提取为独立模块
   - 在 `SKILL.md` 中补上每个脚本的用途与调用示例

   **`references/`**
   - 补齐被 `SKILL.md` 引用、但内容缺失的章节
   - 处理悬空文档：删掉未被引用的，或反过来在 `SKILL.md` 中补上引用
   - 超过 300 行的文件补目录

4. 用 `Edit` 工具修改，只做必要变更。
5. 修改后重新校验 YAML frontmatter（命令见「通用约定」）；改动过 `scripts/` 时，运行受影响的脚本验证仍可执行。
6. 输出变更摘要与校验结果。

---

## 子命令：evals

**用途**：为 `skills/<skill-name>` 编写 `evals/evals.json` 中的测试用例。

**执行步骤**：

1. 检查 `skills/<skill-name>` 是否存在（命令见「通用约定」），不存在则提示先运行 `init` 子命令。
2. 读取 `SKILL.md`，理解技能解决什么问题、什么场景触发。
3. 生成 2-3 个测试用例，每个包含：
   - `prompt`：**真实用户会打出来的话**——带上下文、具体细节、口语化，而不是抽象任务。反例：`"格式化数据"`；正例：`"我老板发来一个 xlsx（在下载文件夹，叫 'Q4 sales final FINAL v2.xlsx'），要加一列利润率百分比，收入在 C 列，成本在 D 列"`。
   - `expected_output`：人类可读的成功标准。
   - `expectations`：可客观验证的断言列表。写作风格、设计美感这类主观产物不要硬套断言。
   - `files`：输入文件路径（相对技能根目录），没有就省略。
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

---

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

6. 执行 score 命令期间，禁止运行 `aggregate_benchmark.py`、生成 `benchmark.json`、或启动用于对拍的子代理。

---

## 子命令：benchmark

**用途**：对 `skills/<skill-name>` 跑基准测试——同一批测试用例分别在**有技能**、**无技能**两种配置下运行，对比通过率、耗时与 token 消耗。

**前置条件**：`evals/evals.json` 存在且至少含一个用例。缺失时提示先运行 `evals` 子命令。

**执行步骤**：

1. 检查 `skills/<skill-name>` 是否存在（命令见「通用约定」），不存在则提示先运行 `init` 子命令。
2. 读取 `evals/evals.json` 确定用例列表。工作区取 `skills/<skill-name>-workspace/iteration-<N>/`，`<N>` 从 1 起，已存在则递增。
3. **同一轮**为每个用例启动两组子代理——不要先跑完有技能的再回头跑基线，否则耗时不可比：
   - `with_skill`：把技能路径 `skills/<skill-name>` 传给子代理
   - `without_skill`：不传技能
   - 产物分别落到 `iteration-<N>/eval-<ID>/with_skill/outputs/` 和 `.../without_skill/outputs/`
   - 两组的实测用例数量比控制在 `1:1` 到 `1.2:1` 之间，避免数量悬殊导致对比失真

4. 每收到一个子代理完成通知，**立即**把 `total_tokens`、`duration_ms` 写入该运行目录的 `timing.json`——这是唯一的捕获时机，事后无法恢复。

5. 全部完成后，为每个运行目录生成 `grading.json`。`expectations` 数组的字段名固定为 `text`、`passed`、`evidence`。能程序化校验的断言写脚本跑，不要目测。

6. 聚合基准数据（`aggregate_benchmark` 是包内模块，需在 skill-creator 目录下执行）：

   ```bash
   cd ${CLAUDE_PLUGIN_ROOT}/skills/skill-creator
   python3 -m scripts.aggregate_benchmark <workspace>/iteration-<N> --skill-name <skill-name>
   ```

   产出 `benchmark.json` 与 `benchmark.md`。

7. 生成结果查看器，供用户逐例查看并留反馈：

   ```bash
   python3 ${CLAUDE_PLUGIN_ROOT}/skills/skill-creator/eval-viewer/generate_review.py <workspace>/iteration-<N> --skill-name "<skill-name>" --benchmark <workspace>/iteration-<N>/benchmark.json
   ```

8. 向用户报告：通过率、耗时、token 三项差值，以及聚合统计会掩盖的模式（例如始终通过的断言可能不具区分度、高方差的用例可能不稳定）。

---

## 子命令：clean

**用途**：删除 `skills/<skill-name>` 下不含任何文件的空目录。

**执行步骤**：

1. 先列出待删清单（`-depth` 保证自底向上，父目录因内容清空而变空时能被一并识别）：

   ```bash
   find skills/<skill-name> -depth -mindepth 1 -type d -empty -print
   ```

   `-mindepth 1` 保证技能根目录本身永远不会被删。

2. 清单为空，直接报告「无空目录」并停止。
3. 清单非空，用 `AskUserQuestion` 让用户确认后再执行删除：

   ```bash
   find skills/<skill-name> -depth -mindepth 1 -type d -empty -exec rmdir {} +
   ```

4. 输出删除结果。
