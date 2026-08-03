---
name: apifox-writer
description: Apifox 导入与质量门禁：支持 OpenAPI 3.2、Postman/Apifox 原生格式，导入前校验 spec 完整性、tags 分组、schema/body 覆盖率，导入后验证计数、模块和资源可见性。
---

# 导入与质量门禁

## 快速决策树

根据用户任务快速判断入口，减少不必要的文件读取：

| 用户任务特征 | 入口 | 补充操作 |
|-------------|------|---------|
| "导入" + 有文件 | Step 3 | 先确认 YAML 格式 |
| "从代码/PRD/文档生成" | Step 1 | 先搜项目内生成器 |
| "自动导入/同步" | 读 CLI help | 创建 auto-import 配置 |
| "迁移/备份/复制项目" | 原生格式 | 读 `references/apifox-native-import.md` |
| "测试场景/步骤" | 转 `apifox-test-scenario` | 不走 OpenAPI import |
| "添加 Mock" | 正常流程 | 需要时读 `references/apifox-mock-rules.md` |

## 前置条件

- 执行 cli 命令 `apifox -v`，确定版本至少是：`2.2.7`，低于这个版本，直接终止任务，要求用户升级 apifox 版本。
- 先阅读 `references/apifox-cli.md` 和 `references/apifox-template.md`。若入口与本 skill 的领域规则冲突，以当前 `apifox help` 和本 skill 为准。
- 需要 Mock 数据时阅读 `references/apifox-mock-rules.md`。
- 需要原生格式导入时阅读 `references/apifox-native-import.md`。

具体命令参数以当前 CLI help 为准。导入前重点检查文件格式、OpenAPI 质量门禁、路由骨架风险、tags 分组、原生格式模块策略、ignoreCount 和是否需要干净项目验证。Agent 导入后必须按 agentHints、list/get 和必要的 run/report 做结果确认，不要只依据导入命令返回成功判断完成。

**不适用场景：** 测试场景步骤的导入/维护转 `apifox-test-scenario`。

## 核心原则（不可违反）

1. 优先查项目内已有生成器，不要先手写提取脚本。
2. 不要把”路径完整”误判为”接口 spec 完整”。
3. 导入前必须输出质量指标。
4. 完整性和可读性要同时验收。
5. 导入策略不确定时，优先新建临时/修正版项目验证，不要污染已有项目。
6. 导入结果里的大量 `ignoreCount` 是风险信号，不是普通成功。
7. Apifox 目录分组依赖 OpenAPI operation tags。
8. 导入文件仅支持 YAML 格式，不接受 JSON 格式。
9. 不要假设文件扩展名代表实际格式。
10. 添加 Mock 数据时，`x-apifox-mock` 必须添加到 schema 属性级别，不是顶层。

## 标准流程

### Step 1. 明确任务类型 & 搜索生成器

先判断用户任务类型（参考顶部快速决策树）。如果用户没有指定目标项目、团队、导入策略，根据上下文判断；不确定时问一个最小必要问题。

遇到”从源码/文档/PRD/测试文档/讨论生成 API spec”的需求，先搜索项目内是否已有：`openapi`、`swagger`、`routegen`、`route-gen`、`docs generator`、`api docs`、`schema generator`、`cmd/openapi`、`cmd/*openapi*`。

- 先运行项目自带生成器，优先使用能抽取 handler request/response struct、DTO、schema 的工具。
- 不要先手写脚本从 router 文件提取路径。

> **决策点：** 找到生成器 → 继续 Step 2；未找到 → 跳过 Step 2，直接从路由/注释/DTO 生成后跳到 Step 3。

### Step 2. 生成 spec 并确认文件格式

运行项目自带生成器或官方生成命令，保存原始产物。**仅支持 YAML 格式**，JSON 必须先转换。扩展名不可信，以实际内容判断格式。

> **决策点：** 确认 YAML 格式 → 继续 Step 3；如果是 JSON → 先转换为 YAML 再进 Step 3。

### Step 3. 统计导入前质量指标

导入前必须实际解析生成的 OpenAPI 文件，并报告真实统计值。不要使用示例值、默认值或占位值。

必须统计：

| 指标 | 含义 | 用途 |
|------|------|------|
| `paths` | OpenAPI paths 数量 | 判断接口规模 |
| `operations` | 实际 operation 数量 | 判断导入规模 |
| `schemas` | `components.schemas` 数量 | 判断模型完整度 |
| `writes` | POST/PUT/PATCH 等写接口数量 | 判断 body 覆盖目标 |
| `withBody` | 写接口中有 requestBody 的数量 | 判断 requestBody 覆盖率 |
| `emptyObjectBodies` | requestBody schema 是空对象的数量 | 判断是否路由骨架 |

输出时必须写”真实统计结果”，例如使用表格或 JSON 均可，但每个值必须来自当前文件解析结果。

> **决策点：** 统计完成后，继续 Step 4 判断完整性。

### Step 4. 判断 spec 完整性

- 不按固定 schema 数量判定质量。
- 小型、纯 GET、健康检查、webhook 透传、无 JSON body 项目，`schemas=0/1` 可以接受。
- 大项目如果接口很多、写接口很多，但 schemas 极少，视为疑似路由骨架 spec。
- 大量 POST/PUT/PATCH 的 body 缺失或是空 `{}`，是强风险信号。
- 只有 method + path 不能证明 requestBody、response、schema 完整。

风险判断：

| 现象 | 判断 | 处理 |
|------|------|------|
| 大项目、写接口多，schemas 极少 | 疑似路由骨架 | 查 DTO、handler struct、生成器 |
| withBody 覆盖明显不足 | requestBody 不完整 | 补充 request DTO 或换生成器 |
| emptyObjectBodies 很多 | 强风险（空壳 body） | 不作为最终 spec 导入 |
| 小型、纯 GET、健康检查 | schemas 少可能合理 | 结合业务形态判断 |

判定为路由骨架 spec → 不导入为最终版本，最多导入临时项目用于探索。

> **决策点：** 疑似路由骨架 或 emptyObjectBodies 很多 → **停止**，标记风险，建议查找完整来源；小型纯 GET 项目 schemas 少 → 通过，继续 Step 5；其他通过情况 → 继续 Step 5。

### Step 5. 校验 tags 和文档可读性

API spec 不只要模型完整，还要在 Apifox 中可读、可导航、分组合理。

必须检查：

- operation 是否有业务化 `tags`，按业务域分组而非 URL path 机械分组。
- schema 是否保留完整。
- operationId、summary、description 是否可读。

推荐 tags 形态：`tags: [<业务域名称>]`（如"用户管理"而非 `api/v1/user`）。

目录服务于业务导航，非代码路径还原。tags 明显过粗或机械来自技术路径（`api`、`v1`、`rest`、`service`、`controller`）→ 停在导入前，询问用户是否允许生成修正版 spec。用户同意前，不导入为最终项目。

> **决策点：** tags 按技术路径机械分组 → **停止**，询问是否修正；tags 按业务域合理分组 → 继续 Step 6。

### Step 6. 选择导入项目

- 导入策略不确定时，优先创建临时/修正版项目验证。
- 不要用新 spec 反复导入污染已有项目。
- 如果已有项目里导入过骨架 spec，再导入完整 spec 可能出现旧接口 ignore、新接口追加、项目混杂。
- 临时项目命名建议表达版本和目的，例如 `API - Full Spec`、`API - Grouped Full Spec`。

### Step 7. 执行导入并检查结果

导入后不要只看命令成功，还要看结果计数。

如果导入结果中 `ignoreCount` 明显偏高，不能把”命令执行成功”当成”导入质量合格”。必须继续判断：

- 是否导入到了已有项目。
- 是否接口匹配策略不符合预期。
- 是否旧 spec 和新 spec 混杂。
- 是否应该改用干净项目重新导入。

> **决策点：** ignoreCount 明显偏高 → **停止**，排查原因，建议干净项目重导；ignoreCount 正常 → 继续 Step 7.1 或 7.2（按需）。

#### Step 7.1 添加 Mock 数据（可选）

如需为接口添加 Mock 数据，详见 `references/apifox-mock-rules.md`。核心要点：
- 为 response schema 的每个属性添加 `x-apifox-mock` 扩展字段
- 值使用 Mock.js 语法（`@integer`、`@email`、`@cname` 等）
- 必须添加到**属性级别**，不是顶层（核心原则 #10）
- `allOf`/`oneOf`/`anyOf`/数组/嵌套对象需递归处理

#### Step 7.2 原生格式导入策略（可选）

适用于项目迁移、备份、跨项目复制。详见 `references/apifox-native-import.md`。核心要点：
- 默认使用 `--module-import-mode match-name`
- 需要精确控制时用 `--module-map “源模块名=目标模块ID”`
- 导入后必须验证模块和资源数量

### Step 8. 回读验证并汇报

- 回读接口列表，确认接口总数与导入结果一致。
- 抽查至少一个读接口和一个写接口；写接口要确认 requestBody、response、schema 引用正常。
- 如导入了数据模型，抽查 schema 能否正常回读。
- 如导入 Apifox 原生格式，额外确认模块策略、测试用例分类、测试场景和测试套件引用。
- 最终汇报必须包含文件路径、质量指标或导入项目、导入计数、抽查结果和遗留风险。

## 常见恢复

| 现象 | 处理 |
|------|------|
| 只有路径 | 回查生成器，找 DTO/handler schema |
| schemas 极少 | 结合 writes/withBody/emptyObjectBodies 判断路由骨架 |
| 大量空 body | 回查 request DTO 或项目生成器 |
| 目录按 URL 分组 | 重写 tags 后导入干净项目 |
| 大量 ignoreCount | 判断污染，新建干净项目验证 |
| JSON 格式 | 先转 YAML 再导入 |
| 原生格式重复模块 | 检查 `match-name`，用 `--module-map` 精确映射 |

