---
name: typescript-taster
description: "识别 TypeScript 代码中的 AI 味道。扫描代码库，检测 AI 生成的典型模式（过度注释、冗余类型、防御性检查、模板化错误处理等），输出按严重程度分级的检测报告，只检测不修改代码。用户要求检查 AI 味道、做代码味道检测或审查 AI 生成代码时使用；提到 TypeScript 代码人工痕迹重、看起来像 AI 写的也应触发。"
---

# typescript-taster

## 概述

扫描 TypeScript 代码库，识别 AI 生成代码的典型模式，按严重程度分级输出检测报告。技能定位是发现「这段代码看起来像 AI 写的」的模式，不是找 bug，也不是给重构方案。

## 上下文层级

| 层级 | 来源 | 内容 |
|------|------|------|
| 通用 | TypeScript 生态 | 常见 AI 生成模式、类型系统特性 |
| 模块 | 项目代码库 | 现有代码风格、命名约定、架构模式 |
| 具体 | 扫描文件 | 本次检测的代码片段、问题位置 |

## 使用时机

- 用户要求检查代码中的 AI 味道。
- 代码审查前，识别 AI 生成痕迹。
- 重构前，确认哪些模式需要调整。
- 新成员入职，了解项目代码质量。

不适用：纯 bug 修复、功能实现规划、性能优化。

## 输出契约

- 只输出检测报告。禁止修改任何代码文件，禁止执行代码修复。
- 报告写入用户指定目录；未指定时写入 `[当前工作目录]/.claude/taste-typescript-{YYYYMMDD}.md`。
- 报告落盘并输出摘要后立即终止，不等待回复，不主动执行修复。

## 流程

### 1. 确定扫描范围

扫描项目根目录，识别源代码目录，常见为 `src/`、`lib/`、`app/`、`packages/`。排除以下路径：

- 测试文件：`*.test.ts`、`*.spec.ts`、`__tests__/`
- 构建产物：`dist/`、`build/`、`.next/`
- 配置文件：`*.config.js`、`*.config.ts`
- 类型声明：`*.d.ts`，手写类型除外

列出待扫描目录清单后进入下一步。

### 2. 加载检测规则

读取 `references/detection-rules.md`，掌握每类 AI 味道的模式定义、检测正则、严重程度与修复建议。

### 3. 逐文件扫描

对每个 TypeScript 文件执行：

1. 读取文件内容。
2. 按 P0 类型冗余、P1 过度注释、P2 防御性检查、P3 模板化模式、P4 命名风格的顺序应用规则。
3. 记录文件路径、行号、规则 ID、严重程度与问题描述。

### 4. 问题分级

| 严重程度 | 定义 | 示例 |
|----------|------|------|
| Critical | 严重影响可读性或维护性 | 每行都有注释 |
| High | 明显的人工痕迹 | 函数签名写满冗余类型 |
| Medium | 轻微的过度工程化 | 不必要的 try-catch 包裹 |
| Low | 命名风格不一致 | 混用 camelCase 和 snake_case |

### 5. 生成报告

报告写入输出路径，结构如下：

````markdown
# AI 味道检测报告

**扫描时间**：{timestamp}
**扫描范围**：{file_count} 个文件
**问题总数**：{total_issues}

## 概览

| 严重程度 | 数量 |
|----------|------|
| Critical | {count} |
| High | {count} |
| Medium | {count} |
| Low | {count} |

## 详细问题

### {文件名}

#### {规则 ID}：{规则名称}

- **位置**：第 {line} 行
- **严重程度**：{severity}
- **问题**：{description}
- **代码片段**：

  ```typescript
  {code}
  ```

- **修复建议**：{suggestion}

## 修复优先级

1. Critical：{文件列表}
2. High：{文件列表}
3. Medium 与 Low：可批量处理

## 统计

- 最常出现的规则：{rule_id}（{count} 次）
- 问题最集中的文件：{file_path}（{count} 个问题）
````

### 6. 呈现结果并终止

输出报告路径与摘要：

````
检测报告已生成：.claude/taste-typescript-{YYYYMMDD}.md

发现 {total} 个问题：
- Critical: {count}
- High: {count}
- Medium: {count}
- Low: {count}

问题最集中的文件：
1. {file_1} - {count} 个问题
2. {file_2} - {count} 个问题
3. {file_3} - {count} 个问题

建议优先修复 Critical 和 High 级别问题。
````

结束语示例：

> 检测报告已生成：`.claude/taste-typescript-20260930.md`
> 请审阅后告知是否需要修复。

禁止行为：

- 输出报告后自动开始修复。
- 输出报告后询问是否修复，随后不等回复就执行。
- 修改任何 `.ts` 文件。

## 验证清单

- 扫描目录已排除测试文件、构建产物、配置文件与类型声明。
- 每个问题记录了文件路径、行号、规则 ID 与严重程度。
- 报告按严重程度分级。

## 危险信号

| 信号 | 问题 |
|------|------|
| 注释比代码多 | 过度注释 |
| 每行都有类型注解 | 冗余类型 |
| 所有函数都有 try-catch | 过度防御 |
| 错误处理全是 console.log | 模板化错误处理 |
| 变量命名不一致 | 风格混乱 |

## 理由辩解

| AI 常见偷懒 | 打脸 |
|-------------|------|
| 「这只是类型安全」 | 过度类型注解降低可读性 |
| 「注释是为了清晰」 | 显而易见的代码不需要注释 |
| 「防御性编程很重要」 | 不必要的检查增加复杂度 |
| 「这是最佳实践」 | 盲从最佳实践忽视上下文 |
| 「代码已经够简洁了」 | 简洁不等于省略必要类型 |

## 验证

全部条件通过才算完成：

1. 运行 `git status --porcelain`，确认无 `.ts`、`.tsx` 文件改动，仅报告文件为新增。
2. 运行 `test -f "<报告路径>"`，确认报告已写入磁盘。
3. 抽查报告条目，确认文件路径、行号、规则 ID、严重程度、修复建议五项齐全。

## 参考资料

- [specs-typescript-naming-conventions.md](${CLAUDE_PLUGIN_ROOT}/knowledge/specs-typescript-naming-conventions.md)：命名原则、按返回值命名、TypeScript 命名约定与反模式。
- [specs-typescript-functions-and-comments.md](${CLAUDE_PLUGIN_ROOT}/knowledge/specs-typescript-functions-and-comments.md)：函数拆分、参数设计、副作用控制、注释取舍。
- [specs-typescript-error-handling.md](${CLAUDE_PLUGIN_ROOT}/knowledge/specs-typescript-error-handling.md)：异常分层、null 处理。
- [detection-rules](references/detection-rules.md)：检测规则定义。
