# apifox-writer

Apifox 导入与质量门禁 Skill。支持 OpenAPI 3.2、Postman/Apifox 原生格式，导入前校验 spec 完整性、tags 分组、schema/body 覆盖率，导入后验证计数、模块和资源可见性。

## 目录结构

```
apifox-writer/
├── SKILL.md                # Skill 核心内容（工作流程 + 质量门禁 + 导入策略，221 行）
├── README.md               # 使用说明（本文件）
├── references/
│   ├── apifox-cli.md       # Apifox CLI 参考文档
│   ├── apifox-template.md  # Apifox 模板参考文档
│   ├── apifox-mock-rules.md    # Mock 数据规则（x-apifox-mock 映射表）
│   └── apifox-native-import.md # 原生格式导入策略
├── evals/
│   ├── evals.json          # 测试用例
│   └── fixtures/           # 测试 fixture 文件
│       ├── openapi-small.yaml           # 3 GET 健康检查接口
│       ├── openapi-large-skeleton.yaml  # 50 接口但 2 schema 的路由骨架
│       ├── openapi-with-mock.yaml       # 完整 request/response schema
│       └── tags-mechanical.yaml         # tags 按技术路径分组
```

## 触发条件

**何时使用：**

- "导入 Apifox" / "Apifox 导入" / "上传到 Apifox"
- "导入 YAML/OpenAPI 到 Apifox" / "把接口导入 Apifox"
- 从代码库、PRD、需求文档、测试文档、讨论记录生成 API spec 并导入
- 配置自动导入
- 迁移、备份或复制 Apifox 项目
- 判断生成的 spec 是否只是"路由骨架"
- "添加 Mock 数据" / "OpenAPI 转 Apifox"

**不应使用：**

- 导入已有 endpoint/test-case 到测试场景 → 转 `apifox-test-scenario`
- 精细维护测试场景步骤/变量/断言/处理器 → 转 `apifox-test-scenario`

## 核心原则

| # | 原则 | 说明 |
|---|------|------|
| 1 | 先查生成器 | 优先使用项目内已有的 OpenAPI/Swagger 生成器，不要先手写提取脚本 |
| 2 | 路径 ≠ 完整 | 不要只有 method + path 就误判为 spec 完整 |
| 3 | 必须输出质量指标 | 导入前必须报告 paths、operations、schemas 等真实统计值 |
| 4 | 完整性 + 可读性 | 两者同时验收，缺一不可 |
| 5 | 干净项目优先 | 导入策略不确定时，先建临时项目验证，不污染已有项目 |
| 6 | ignoreCount 是风险信号 | 大量忽略不是普通成功，需要进一步排查 |
| 7 | tags 决定目录分组 | Apifox 目录结构依赖 operation tags，需按业务域分组 |
| 8 | 仅支持 YAML 格式 | 导入文件必须是 YAML，不接受 JSON，必须先转换 |
| 9 | 不信扩展名 | `.json` 文件里可能是 YAML 内容，实际解析判断格式 |

## 标准工作流程

### Step 0. 明确任务类型

| 任务类型 | 入口 |
|---------|------|
| 从源码/文档生成 spec 并导入 | 从 Step 1 开始 |
| 直接导入已有文件 | 从 Step 3 开始 |
| 配置自动导入 | 先读 CLI help 和 schema，再创建配置 |
| 迁移/备份 Apifox 项目 | 使用原生格式导入，确认模块策略 |
| 导入资源到测试场景 | 转 `apifox-test-scenario` |

不确定目标项目、团队、导入策略时，根据上下文判断；最小必要问题只问一个。

### Step 1-2. 搜索生成器 & 生成 spec

- 搜索项目内是否有 `openapi`、`swagger`、`routegen`、`api docs`、`schema generator` 等
- 优先使用能抽取 handler request/response struct、DTO、schema 的工具
- 保存原始产物，不直接覆盖用户已有文件
- **仅支持 YAML 格式导入**，生成的 JSON 必须先转换为 YAML
- 不要根据扩展名判断格式，实际解析确认内容

### Step 3. 导入前质量指标

必须解析 OpenAPI 文件并报告以下真实统计值：

| 指标 | 含义 | 用途 |
|------|------|------|
| `paths` | paths 数量 | 判断接口规模 |
| `operations` | 实际 operation 数量 | 判断导入规模 |
| `schemas` | components.schemas 数量 | 判断模型完整度 |
| `writes` | POST/PUT/PATCH 等写接口数量 | 判断 body 覆盖目标 |
| `withBody` | 写接口中有 requestBody 的数量 | 判断 requestBody 覆盖率 |
| `emptyObjectBodies` | requestBody schema 是空对象的数量 | 判断是否路由骨架 |

### Step 4. 判断 spec 完整性

| 现象 | 判断 | 处理 |
|------|------|------|
| 接口规模大、写接口多，但 schemas 极少 | 疑似路由骨架 spec | 继续查 DTO、生成器 |
| 写接口多，withBody 覆盖不足 | requestBody 不完整 | 补充 DTO 或换生成器 |
| emptyObjectBodies 很多 | 强风险，可能只是空壳 | 不要作为最终 spec 导入 |
| 小型、纯 GET、健康检查 | schemas 少可能合理 | 结合业务形态判断 |

### Step 5. 校验 tags 和文档可读性

必须检查：
- operation 是否有业务化 `tags`，而非按 URL path 机械分组
- tags 是否按业务域分组（推荐：`tags: [业务域名称]`）
- operationId、summary、description 是否可读

如果 tags 明显过粗或机械来自技术路径（如 `api`、`v1`、`rest`、`controller`），**停在导入前**，先询问用户是否允许生成修正版。

### Step 6. 选择导入项目

- 不确定时优先创建临时项目验证
- 不要在已有项目上反复试错导入
- 临时项目命名建议表达版本和目的（如 `API - Full Spec`、`API - Grouped Full Spec`）

### Step 7. 执行导入并检查结果

导入后必须验证结果计数：
- `ignoreCount` 偏高 → 判断是否导入到已有项目、接口匹配策略问题、新旧 spec 混杂
- 必要时新建干净项目重新导入

### Step 7A. OpenAPI YAML 转 Apifox YAML 并添加 Mock 数据

在导入前，可将 OpenAPI YAML 转换为 Apifox 增强版 YAML，在 response schema 中添加 `x-apifox-mock` 扩展字段，使 Apifox 导入后自动生成 Mock 数据。

**转换步骤：**

1. 读取 OpenAPI 3.2 YAML，解析 paths、components.schemas、responses、webhooks
2. 保持 paths、operations、parameters 等业务逻辑不变
3. 为 response schema 的每个属性添加 `x-apifox-mock` 扩展字段

**字段类型到 Mock 规则映射：**

| 字段类型/用途 | Mock 规则 |
|---------------|-----------|
| ID / 主键 | `@integer(1, 9999)` |
| UUID | `@uuid` |
| 人名 | `@cname` |
| 标题/名称 | `@ctitle` 或 `@cword(2, 6)` |
| 描述/备注 | `@cparagraph` |
| 邮箱 | `@email` |
| 手机号 | `@phone` |
| URL/链接 | `@url` |
| 图片 | `@image("200x200")` |
| 时间/日期 | `@datetime("yyyy-MM-dd HH:mm:ss")` |
| 布尔值 | `@boolean` |
| 整数/数量 | `@integer(min, max)` |
| 浮点数/金额 | `@float(0.01, 9999.99, 2, 2)` |
| 字符串(通用) | `@string(length)` |
| 状态/枚举 | `@pick(val1, val2, val3)` |
| 身份证号 | `@id` |
| 随机整数 | `{{$randomInt}}` |
| 时间戳 | `{{$timestamp}}` |

**属性名关键词到 Mock 规则映射：**

| 属性名关键词 | 推荐 Mock 规则 |
|--------------|----------------|
| `id`, `Id`, `ID` | `@integer(1, 9999)` 或 `@uuid` |
| `name`, `Name`, `title` | `@cname` 或 `@ctitle` |
| `email`, `Email`, `mail` | `@email` |
| `phone`, `Phone`, `mobile` | `@phone` |
| `url`, `Url`, `URL`, `link` | `@url` |
| `image`, `Image`, `avatar`, `photo` | `@image("200x200")` |
| `time`, `Time`, `date`, `Date`, `createdAt`, `updatedAt` | `@datetime("yyyy-MM-dd HH:mm:ss")` |
| `status`, `Status`, `type`, `Type`, `state` | `@pick(...)` 使用枚举值 |
| `desc`, `description`, `remark`, `note` | `@cparagraph` 或 `@cword(4, 10)` |
| `price`, `amount`, `money`, `cost` | `@float(0.01, 9999.99, 2, 2)` |
| `count`, `num`, `quantity` | `@integer(1, 100)` |
| `bool`, `enable`, `active`, `isXxx` | `@boolean` |

**注意事项：**
- `x-apifox-mock` 必须添加到 schema 的**属性级别**，不是顶层
- 对于 `allOf`、`oneOf`、`anyOf` 组合 schema，递归到每个子 schema 属性中添加
- 数组类型 (`type: array`)，在 `items` 的属性中添加
- 枚举字段优先使用 `@pick(val1, val2, ...)` 从实际枚举值中随机选择
- 嵌套对象需要递归处理每一层属性

### Step 7B. Apifox 原生格式导入策略

适用于项目迁移、备份、跨项目复制和局部资源搬迁。

**常用命令：**

```bash
# 基本导入
apifox import --project <projectId> --format apifox --file ./project.apifox.yaml

# 默认模块策略：匹配已有，未匹配时新建
apifox import --project <projectId> --format apifox --file ./project.apifox.yaml --module-import-mode match-name

# 每次复制全新模块
apifox import --project <projectId> --format apifox --file ./project.apifox.yaml --module-import-mode new

# 精确模块映射（优先级高于 module-import-mode）
apifox import --project <projectId> --format apifox --file ./project.apifox.yaml \
  --module-map "商店 API=8049476" \
  --module-map "管理 API=8049482"
```

**模块映射写法：**

| 写法 | 用途 |
|------|------|
| `源模块名=目标模块ID` | 导入到指定已有模块 |
| `source:源模块ID=目标模块ID` | 源模块重名时精确指定 |
| `源模块名=default` | 导入到目标项目默认模块 |
| `源模块名=new` | 只让该源模块新建 |

**导入后验证：**
- 模块数量是否符合预期（二次导入不应无意新增同名模块）
- API、Schema、测试用例、测试场景等资源数量
- 单接口测试用例分类可见性
- 如导入测试套件，抽查场景和用例引用是否指向新项目资源

### Step 8. 回读验证并汇报

- 回读接口列表，确认接口总数与导入结果一致
- 抽查至少一个读接口和一个写接口（写接口确认 requestBody、response、schema 引用正常）
- 如导入了数据模型，抽查 schema 能否正常回读
- 如导入原生格式，额外确认模块策略、测试用例分类、测试场景和测试套件引用
- **最终汇报**必须包含：文件路径、质量指标、导入项目、导入计数、抽查结果、遗留风险

## 质量门禁指标速查

```yaml
# 健康指标示例（小型项目）
paths: 5
operations: 8
schemas: 0-2          # 纯 GET/健康检查可接受
writes: 0
withBody: 0
emptyObjectBodies: 0

# 风险指标示例（大型项目）
paths: 50
operations: 80
schemas: 2            # 警告：接口多但 schema 极少
writes: 25
withBody: 5           # 警告：25 个写接口中只有 5 个有 body
emptyObjectBodies: 15 # 警告：15 个空对象 body
```

## 常见恢复方案

| 现象 | 处理 |
|------|------|
| 导入成功但只有路径 | 回查生成器是否只抽路由，继续找 DTO/handler schema |
| schemas 极少 | 结合 operations/writes/withBody/emptyObjectBodies 综合判断 |
| 大量空 body | 回查 request DTO 或项目生成器 |
| Apifox 目录按 URL 分组 | 重写 operation tags 后重新导入到干净项目 |
| 大量 ignoreCount | 判断是否污染已有项目，必要时新建干净项目 |
| JSON.parse 失败 | 检查实际是否 YAML，不要信扩展名 |
| 导入文件为 JSON 格式 | 必须先转换为 YAML 格式后再导入 |
| 二次导入出现重复模块 | 检查 `match-name` 策略，必要时用 `--module-map` |
| 目标项目有多个同名模块 | 使用 `--module-map "源模块名=目标模块ID"` |

## 不可违反规则

1. 不要先手写路由提取脚本，先查项目内生成器
2. 不要把接口数量多等同于 spec 完整
3. 不要跳过导入前质量指标
4. 不要在已有项目上反复试错导入
5. 不要忽略大量 `ignoreCount`
6. 不要导入 tags 混乱、无法按业务导航的 spec 作为最终成果
7. 不要导入 JSON 格式文件，必须先转换为 YAML
8. 添加 Mock 数据时，`x-apifox-mock` 必须添加到 schema 属性级别，不是顶层

## 前提条件

- Apifox CLI 已安装（`apifox help` 可查可用命令）
- 目标 Apifox 项目 ID
- 待导入的 OpenAPI/Postman/Apifox 原生格式文件（YAML 格式）
