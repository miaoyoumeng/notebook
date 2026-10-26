---
name: issues-writer
description: "使用 tracer-bullet 垂直分片，把计划、PRD、技术规范或功能描述拆成可独立领取的开发 issues。当用户提到拆分任务、创建 tickets、sprint 规划、把文档转成 issues 时使用。每个 issue 必须是完整功能路径（schema → API → UI → 测试），严禁按技术层水平拆分。不适用于写 PRD、修 bug 或 issue 排序。"
---

# issues-writer

## 概述

把计划、PRD、技术规范或功能描述拆成可独立领取的开发 issues。核心方法是 tracer bullet（跟踪弹）：端到端实现一条极小但完整的路径，贯穿系统各层，先验证技术路线可行，再铺设完整功能。

### 垂直切片与水平切片

以「用户登录」为例：

| 维度 | 水平切片 | 垂直切片 |
|------|----------|----------|
| 切法 | 按技术层切：数据库层 → API 层 → 前端层 → 测试层 | 按功能路径切：一条穿过所有层的完整窄路径 |
| Issue 1 | 设计 user 表 | 用户能用邮箱+密码注册并看到欢迎页 |
| Issue 2 | 实现 /login API | 用户能用邮箱+密码登录并跳转到首页 |
| Issue 3 | 写登录页面 UI | 用户能重置密码并通过邮件链接设置新密码 |
| Issue 4 | 加集成测试 | — |
| 结果 | 所有 issue 合在一起才能验证任何一个功能 | 每个 issue 完成后都能独立 demo 或验证 |

本技能只使用垂直切片，禁止水平切片。

### Issue 类型

| type | 适用场景 | 核心特征 |
|------|----------|----------|
| feature | 已有功能的增强 | 明确依赖已有功能，验收标准覆盖新旧功能兼容性；PRD 文档修改用此类型，严禁产出技术相关内容 |
| task | 从 PRD 拆分出的新功能 | 描述 end-to-end 用户路径，验收标准面向用户可观测行为 |
| bug | 已发现缺陷的修复 | 包含复现路径与影响范围，验收标准覆盖修复验证与回归防护 |
| question | 技术方案决策或咨询 | 产出是文档或决策，验收标准面向文档质量与决策完整性 |

## 上下文层级

- 通用层：垂直切片方法论、issue 类型体系、issue 模板结构（`references/issue-<type>-template.md`）
- 中间层：项目上下文材料——PRD、技术规范、计划文档、已有 issue、领域词汇表、ADRs（Architecture Decision Record，架构决策记录）
- 具体层：本次产出的 slice 分解方案与发布到 issue tracker 的 issues

## 使用时机

以下场景使用：

- 把计划、PRD、技术规范或功能描述拆成可独立领取的开发 issues
- 拆分任务、创建 tickets、sprint 规划
- 把文档转成 issues

不适用：

- 从头写 PRD，改用 `prd-writer`
- 修复已有 bug，直接定位和修改代码
- 给已有 issue 排序，属于 issue 管理操作

## 流程

### 第一步：信息收集（可选）

基于对话上下文工作。用户传入 issue 参考资料（issue number、URL 或 path）时，读取完整内容与备注信息。

### 第二步：研究参考资料（可选）

未探索参考资料时先探索，理解任务上下文与当前状态。Issue Title 和描述使用项目领域词汇表，遵守相关 ADRs。

### 第三步：起草垂直切片

把计划拆成 tracer bullet issues。每个 issue 是薄垂直切片，end-to-end 穿过所有集成层，而不是某一层的水平切片。

每个 slice 标记为 HITL 或 AFK：

- HITL：需要人类交互，例如架构设计、设计结果检查
- AFK：可以无人交互地实现并合并，优先选择

切片规则：

- 每个 slice 交付一条窄但完整的路径，穿过 schema、API、UI、tests 每一层
- 完成后的 slice 自身可 demo 或验证
- 偏好多而薄的 slice，而不是少而厚的 slice

### 第四步：用户验证

把分解方案作为编号列表展示，每个 slice 包含：

| 字段 | 内容 |
|------|------|
| Title | 短描述名 |
| Type | HITL 或 AFK |
| Summary | 简要描述，限制 50 汉字以内 |
| To | 承接角色 |
| Blocked by | 必须先完成的其他 slice，没有则写「无」 |

向用户确认：

- 粒度是否合适（太粗或太细）
- issues 依赖关系是否正确
- 是否需要合并或继续拆分某些 slice
- HITL 与 AFK 标记是否正确

按反馈迭代，直到用户批准 breakdown。

### 第五步：编写 issues

对每个批准的 slice 发布 issue，套用 `references/issue-<type>-template.md`，参考 `references/issue-<type>-example.md`。

按依赖顺序发布，blockers first，使 Blocked by 字段能引用真实 issue 标识符。

发布时应用正确的分类标签。除非另有指示，issues 视为已准备好交给 AFK agents 接手。

每个 issue 包含：

| 字段 | 说明 |
|------|------|
| issue 名称 | 短描述，不超过 15 个汉字 |
| issue code | 唯一编码，规则见模板：`<type>-<menu name>-<issue name>-<random alphanumeric>` |
| 上级依赖 | 对父 issue 的引用，如有 |
| 任务描述 | end-to-end 行为描述，不按层描述 |
| 产出内容 | 可观测的产出物列表 |
| 验收标准 | 至少 3 条可验证的 checklist |
| Blocked by | 前置依赖或「None」 |

## 验证清单

发布前逐项核对：

- [ ] 每个 slice 穿过 schema、API、UI、tests 各层
- [ ] 每个 slice 完成后可独立 demo 或验证
- [ ] 未按技术层拆出单独的「建表」「写 API」「写 UI」「补测试」issue
- [ ] 每个 slice 标记了 HITL 或 AFK，能 AFK 的优先 AFK
- [ ] issue 名称不超过 15 个汉字，Summary 不超过 50 个汉字
- [ ] issue code 符合 `<type>-<menu name>-<issue name>-<random alphanumeric>` 且全局唯一
- [ ] 每个 issue 套用了对应 type 的模板
- [ ] 验收标准至少 3 条，可被非专业人员观测验证
- [ ] 依赖关系已标注，Blocked by 引用真实 issue 标识符
- [ ] 已应用正确的分类标签
- [ ] 描述中无具体文件路径、代码片段或完整示例

## 危险信号

以下任一模式说明拆分失败：

- 出现「设计 user 表」「实现 /login API」「写登录页面 UI」「加集成测试」这类按层拆分的 issue
- 需要所有 issue 完成才能验证任何一个功能
- issue 描述按 layer-by-layer 实现步骤组织
- 产出物无法被用户观测，没有可访问的 URL 或操作路径
- 描述中写入具体文件路径、代码片段或完整示例
- 单条 issue 跨多个不相关功能，或厚 slice 过多
- 发布时未按依赖顺序进行，Blocked by 引用不到真实 issue 标识符

## 理由辩解

| 借口 | 打脸理由 |
|------|----------|
| 「先建表，再写 API，再写 UI，最后补测试，顺序更清楚」 | 这是水平切片，所有 issue 合起来才能验证一个功能；改用垂直切片，每条 issue 独立可验收 |
| 「合并成一个大的 issue 效率更高」 | 偏多而薄：8 个 2 小时的 issue 优于 2 个 8 小时的 issue，并行领取与回滚都更容易 |
| 「依赖关系以后再说，先把 issue 都发出去」 | 按依赖顺序发布 blockers first，否则 Blocked by 字段引用不到真实 issue 标识符 |
| 「issue 里放上文件路径和代码，开发更好上手」 | 文件路径和代码片段会过时；描述保留决策密集部分，禁止放完整示例 |
| 「这个 slice 要人确认设计，标 AFK 也不影响」 | 需要人类交互的必须标 HITL，否则 AFK agent 会卡在执行中途 |
| 「参考资料没写清楚，我先按自己的理解补」 | 先读参考资料、领域词汇表和 ADRs，再起草；未明确的内容先向用户确认 |
| 「PRD 文档修改属于技术任务」 | PRD 文档修改使用 feature 类型，严禁产出技术相关内容 |

## 验证

发布完成后按以下顺序核验，逐项枚举，不靠整体印象：

1. 切片完整性：逐条检查验证清单，未通过项修复后重新检查
2. 模板合规：每个 issue 对照 `references/issue-<type>-template.md`，必填字段齐全，无模板说明文字残留
3. 编码唯一：核对全部 issue code，无重复，type 与实际分类一致
4. 依赖闭环：按 Blocked by 逐条追溯，所有引用指向已创建的 issue
5. 发布顺序：确认 blockers 先于被阻塞 issue 发布
6. 回报：列出 issue 数量、各 type 数量、发布顺序与依赖关系

## 参考资料

按 issue 类型选择模板与示例：

| type | 模板 | 示例 |
|------|------|------|
| feature | `references/issue-feature-template.md` | `references/issue-feature-example.md` |
| task | `references/issue-task-template.md` | `references/issue-task-example.md` |
| bug | `references/issue-bug-template.md` | `references/issue-bug-example.md` |
| question | `references/issue-question-template.md` | `references/issue-question-example.md` |

写 issue 前先读对应模板；需要完整范例时再读示例文件。
