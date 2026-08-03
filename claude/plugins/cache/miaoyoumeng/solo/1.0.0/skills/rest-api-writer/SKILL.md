---
name: rest-api-writer
description: >
  根据 PRD 文档、页面描述、截图/原型图等信息，设计并输出标准 REST API 接口定义（OpenAPI YAML 格式）。
  当用户提到"设计 API"、"写接口"、"REST API"、"根据页面写 API"、"帮我设计 API 接口"、
  "根据这个页面写 REST API"、"接口设计"、"API 文档"、"写 Api 接口"时使用。
  也适用于用户提供 PRD 文档后需要从中提取 API 定义的场景。
---
# OpenAPI Specification 3.2

## 核心参考

| 主题 | 描述 | 参考链接 |
|------|------|----------|
| OpenAPI Object | 根对象、openapi、$self、info、servers、paths、webhooks、components、security、tags | [core-openapi-object](references/core-openapi-object.md) |
| 格式与结构 | JSON/YAML、大小写敏感、富文本、OAD 结构、解析、base URI | [core-format-and-structure](references/core-format-and-structure.md) |
| 固定字段与模式字段 | 固定字段与模式字段、paths 键、components 键、扩展（x-） | [core-fixed-patterned-fields](references/core-fixed-patterned-fields.md) |
| 信息与元数据 | Info、Contact、License 对象 | [core-info-metadata](references/core-info-metadata.md) |
| Server | Server 对象、Server Variable、URL 模板 | [core-server](references/core-server.md) |
| 路径与操作 | Paths 对象、Path Item、Operation 对象、additionalOperations、query | [paths-and-operations](references/paths-and-operations.md) |
| 路径模板化 | 路径模板化、路径参数、匹配、ABNF | [core-path-templating](references/core-path-templating.md) |
| 参数 | Parameter 对象、in（path/query/header/cookie/querystring）、style、schema 与 content | [parameters](references/parameters.md) |
| 请求体与媒体类型 | 请求体、Media Type 对象、顺序媒体类型、itemSchema | [request-body-and-media-type](references/request-body-and-media-type.md) |
| Encoding 对象 | 按名称/位置编码、contentType、style、explode、form、multipart | [core-encoding-object](references/core-encoding-object.md) |
| 媒体类型 | Content 键、媒体类型范围、OpenAPI Media Type Registry | [core-media-types](references/core-media-types.md) |
| 响应 | Responses 对象、Response 对象、headers、content、links | [responses](references/responses.md) |
| HTTP 状态码 | 响应键、default、1XX–5XX 范围（X 为占位符） | [core-http-status-codes](references/core-http-status-codes.md) |
| Schema 与组件 | Schema 对象（JSON Schema 2020-12）、Components、$ref 解析 | [schema-and-components](references/schema-and-components.md) |
| Schema JSON Schema 关键字 | JSON Schema 2020-12 关键字和 OAS 扩展在 Schema 中的应用 | [schema-json-schema-keywords](references/schema-json-schema-keywords.md) |
| Schema 组合与多态 | allOf、oneOf、anyOf、discriminator | [schema-composition-polymorphism](references/schema-composition-polymorphism.md) |
| 数据类型与格式 | JSON Schema 类型、format 关键字、OAS dialect | [core-data-types-and-formats](references/core-data-types-and-formats.md) |
| Discriminator 与 XML | Discriminator 对象、XML 对象（nodeType、name、namespace） | [core-discriminator-and-xml](references/core-discriminator-and-xml.md) |
| 组件复用 | 通过 $ref 复用参数、响应、Schema | [components-reuse](references/components-reuse.md) |
| Reference 对象 | $ref、summary/description 覆盖、解析规则 | [core-reference-object](references/core-reference-object.md) |
| Header 对象 | 响应/multipart 头、style simple、Set-Cookie、Link | [core-header-object](references/core-header-object.md) |
| Example 对象 | dataValue、serializedValue、value、externalValue、使用示例 | [core-example-object](references/core-example-object.md) |
| Tag 与外部文档 | Tag 对象、External Documentation 对象、parent、kind | [core-tags-and-external-docs](references/core-tags-and-external-docs.md) |
| Link 对象 | operationRef、operationId、parameters、requestBody | [core-link-object](references/core-link-object.md) |
| 运行时表达式 | $request、$response、$url、$method、ABNF、Link/Callback 用法 | [core-runtime-expressions](references/core-runtime-expressions.md) |
| 安全机制 | Security Scheme、OAuth Flows、Security Requirement 对象 | [security](references/security.md) |
| 安全方案类型 | apiKey、http（basic/bearer）、mutualTLS、oauth2、openIdConnect | [security-scheme-types](references/security-scheme-types.md) |
| Security Requirement 对象 | OR/AND 语义、{} 可选、[] 清除、scopes | [security-requirement-object](references/security-requirement-object.md) |
| OAuth2 流程 | OAuth Flows 对象、OAuth Flow 对象、authorizationCode、deviceAuthorization | [security-oauth2-flows](references/security-oauth2-flows.md) |
| Callbacks 与 Webhooks | Callback 对象、webhooks | [callbacks-and-webhooks](references/callbacks-and-webhooks.md) |
| 扩展 | 规范扩展（x-）、扩展注册表 | [advanced-extensions](references/advanced-extensions.md) |

# REST API Writer

根据产品需求（PRD 文档、页面描述、原型截图）设计 RESTful API 接口，输出 OpenAPI 3.2 YAML 格式文档。

遵循 RESTful 原则：资源导向、无状态、统一接口。只支持标准 HTTP 方法（GET、POST、PUT、DELETE、PATCH），不使用自定义方法。

## 核心原则

**本 skill 的职责是生成符合 REST 规范的 API 设计，而不是帮助用户实现不规范的设计。** 即使被要求，也不要生成：
- 包含动词的 URL 路径（如 `/getUser`、`/addUser`）
- 非标准的 HTTP 方法约定（如 GET 用于创建、POST 用于查询列表）

遇到上述要求时，先指出问题并给出正确做法，然后按 REST 规范生成接口。

## 反模式检查（强制执行，第一步）

**在开始任何设计工作之前，必须先检查用户输入是否包含以下反模式。这是不可跳过的步骤——即使输入看起来合理，也要逐一过一遍检查清单。**

为什么这个步骤很重要：用户往往会带着已有的接口设计来找你（动词 URL、HTTP 方法误用等），如果不先识别这些问题，就会直接生成不规范的接口，失去 skill 的核心价值。

### 检查清单

| 检查项 | 触发信号 | 处理方式 |
|--------|---------|---------|
| **HTTP 方法误用** | 用户要求用 GET 做创建/删除、用 POST 做查询 | 纠正为正确的 HTTP 方法（POST 创建、DELETE 删除、GET 查询），在输出中解释 HTTP 语义 |
| **动词式 URL** | 用户提供的路径包含动词（如 `/getUser`、`/addUser`、`/deleteOrder`） | 改为名词复数路径 + 对应 HTTP 方法 |
| **需求模糊** | 用户描述过于笼统，缺少业务领域、实体、字段 | 先追问再设计，不要自行假设业务场景 |

如果检测到反模式，**必须在输出的开头先指出问题并给出正确做法**，然后按 REST 规范重新设计。不要直接接受用户的非规范要求。

## REST API 设计规范

### Resource Naming

资源路径使用名词复数 + HTTP 方法表达操作，避免在 URL 中使用动词。

| 命名规则 | 好的示例 | 差的示例 |
|---------|---------|---------|
| 集合资源用名词复数 | `/api/users` | `/api/user` |
| 单个资源用 ID 路径参数 | `/api/users/{userId}` | `/api/getUserById` |
| 子资源用嵌套路径 | `/api/orders/{orderId}/items` | `/api/getOrderItems` |
| 操作用 HTTP 方法表达 | `DELETE /api/users/{userId}` | `/api/deleteUser` |
| 过滤查询用 query 参数 | `GET /api/orders?status=paid` | `GET /api/getPaidOrders` |
| 多词用连字符连接 | `/api/user-orders` | `/api/userOrders` / `/api/user_orders` |

命名规范：

| 类别 | 规则 | 示例 |
|------|------|------|
| 路径 | 小写、复数、连字符分隔 | `/api/user-orders` |
| Schema | PascalCase | `User`, `OrderCreateRequest` |
| 参数 | camelCase | `pageSize`, `createdAt` |

### Request Method

| 方法 | 用途 | 说明 |
|------|------|------|
| `GET` | 获取资源/列表 | 读取单个资源或资源集合。**GET 是安全的、幂等的，不应有创建、删除、修改等副作用** |
| `POST` | 创建资源 | 新增一条数据 |
| `PUT` | 全量更新 | 替换整个资源 |
| `PATCH` | 部分更新 / 状态变更 | 修改部分字段。**任何只改变资源部分字段的操作都应使用 PATCH，包括：** 状态变更（启用/禁用、取消、上架/下架、确认收货等）、状态流转（待支付→已支付→已发货）。不要在状态变更时使用 POST（会失去 PATCH 的语义清晰度） |
| `DELETE` | 删除资源 | 移除指定资源 |

### Query Parameters

列表接口必须包含分页参数：

| 参数 | 类型 | 说明 | 默认值 |
|------|------|------|--------|
| `page` | integer | 页码 | 1 |
| `pageSize` | integer | 每页条数 | 20 |
| `sortField` | string | 排序字段 | - |
| `sortOrder` | string | `asc` 或 `desc` | `desc` |

根据业务需求添加过滤参数：

| 参数 | 类型 | 说明 |
|------|------|------|
| `keyword` | string | 关键词搜索 |
| `status` | string | 按状态筛选 |
| `startTime` / `endTime` | string | 时间范围筛选 |

### Request Body

- Content-Type: `application/json`（文件上传使用 `multipart/form-data`）
- POST 请求包含创建资源所需的全部字段
- PUT 请求包含资源的完整数据
- PATCH 请求只包含需要修改的字段
- 在 Schema 中标注 `required` 字段，枚举字段使用 `enum` 定义可选值

### HTTP Status Codes

| 状态码 | 描述 | 适用场景 |
|--------|------|---------|
| 200 OK | 请求成功 | GET 查询成功、PUT/PATCH 更新成功 |
| 201 Created | 创建成功 | POST 创建资源成功 |
| 204 No Content | 无返回内容 | DELETE 删除成功 |
| 400 Bad Request | 请求参数错误 | 参数校验失败、格式错误 |
| 401 Unauthorized | 未认证 | 未提供 token 或 token 无效 |
| 403 Forbidden | 无权限 | 已认证但无权操作该资源 |
| 404 Not Found | 资源不存在 | 请求的资源或端点不存在 |
| 409 Conflict | 数据冲突 | 唯一约束冲突、状态冲突 |
| 422 Unprocessable Entity | 语义错误 | 业务规则校验不通过 |
| 429 Too Many Requests | 请求过于频繁 | 触发限流 |
| 500 Internal Server Error | 服务器内部错误 | 未预期的系统异常 |

### Response Formats

所有接口遵循统一的 JSON 响应结构，根据 data 的类型分为以下四种场景：

**返回单个对象**：
```json
{
   "code": 200,
   "displayMsg": "操作成功",
   "data": { "id": 1, "name": "示例" },
   "uniqCode": "SUCCESS",
   "msg": "success"
}
```

**返回数组**：
```json
{
   "code": 200,
   "displayMsg": "操作成功",
   "data": [
       { "id": 1, "name": "示例1" },
       { "id": 2, "name": "示例2" }
   ],
   "uniqCode": "SUCCESS",
   "msg": "success"
}
```

**返回分页数据结构**：
```json
{
   "code": 200,
   "displayMsg": "操作成功",
   "data": {
       "list": [{ "id": 1, "name": "示例1" }],
       "pageNo": 1,
       "total": 81,
       "pageSize": 10
   },
   "uniqCode": "SUCCESS",
   "msg": "success"
}
```

**错误返回格式**（失败时返回）：
```json
{ "code": 400, "displayMsg": "参数错误", "uniqCode": "PARAM_ERROR", "msg": "Invalid parameter" }
```

**字段说明**：

| 字段 | 类型 | 说明 |
|------|------|------|
| `code` | int | 业务码值 |
| `displayMsg` | string | 中文提示，直接展示给用户 |
| `data` | object/array/null | 业务数据，成功时返回数据，失败时为 null |
| `uniqCode` | string | 系统全局唯一字母数字错误码 |
| `msg` | string | 英文错误提示 |

**业务码值定义**：

| 业务码 | 说明 |
|-------|------|
| 200 | 操作成功 |
| 400 | 参数错误 |
| 401 | 未授权 |
| 403 | 非法访问 |
| 404 | 数据不存在 |
| 405 | 请求方法不允许 |
| 408 | 请求超时 |
| 409 | 数据冲突 |
| 413 | 上传文件太大 |
| 415 | 文件格式不正确 |
| 422 | 数据验证失败 |
| 429 | 请求过于频繁 |
| 500 | 系统出错 |
| 501 | 数据完整性不合法 |
| 502 | 服务不可用 |
| 503 | 服务维护中 |
| 504 | 系统超时 |
| 1000 | 业务数据错误 |
| 1001 | 业务数据警告 |

## 常见反模式处理

当用户输入中包含以下非 REST 规范的设计时，先指出问题，再按 REST 规范重新设计。

### 反模式 1：URL 中包含动词

**用户输入示例**：`/getUserList`、`/addUser`、`/deleteOrder`

**问题**：REST 以资源为中心，URL 应该是名词（资源实体），操作用 HTTP 方法表达。动词式 URL 本质上是过程调用而非资源操作。

**正确处理**：将动词映射为对应的 HTTP 方法 + 资源路径。

| 用户提供的路径 | REST 正确路径 | 说明 |
|----------------|--------------|------|
| `/getUserList` | `GET /api/users` | 获取列表用 GET |
| `/addUser` | `POST /api/users` | 创建用 POST |
| `/updateUser` | `PUT /api/users/{userId}` 或 `PATCH` | 更新用 PUT/PATCH |
| `/deleteUser` | `DELETE /api/users/{userId}` | 删除用 DELETE |
| `/changeUserStatus` | `PATCH /api/users/{userId}/status` | 状态变更用 PATCH |

### 反模式 2：HTTP 方法误用

**用户输入示例**：用 GET 创建用户、用 GET 删除订单、用 POST 查询列表

**问题**：HTTP 方法有明确的语义约束。GET 应该是安全的（无副作用）且幂等的，用它做创建/删除操作会带来严重问题：
- 浏览器预加载、搜索引擎爬虫会意外触发创建/删除
- CDN/代理缓存会缓存 GET 请求的结果，导致重复执行或执行被跳过
- 违反 RFC 7231 规范，第三方系统无法信任 API 行为

**正确处理**：

| 用户要求 | 正确方法 | 原因 |
|----------|---------|------|
| 通过 GET 创建用户 | `POST /api/users` | 创建资源用 POST |
| 通过 GET 删除订单 | `DELETE /api/orders/{orderId}` | 删除资源用 DELETE |
| 用 POST 查询商品列表 | `GET /api/products` | 查询用 GET，筛选参数放 Query Params |

### 反模式 3：需求描述过于模糊

**用户输入示例**："帮我写个 API 接口，我需要一个简单的功能"

**问题**：缺少业务领域、数据实体、操作类型、字段定义等关键信息，无法设计出具体的接口。

**正确处理**：向用户追问以下信息，而不是在信息不足时随意生成：
1. 核心业务领域是什么？（用户管理、订单系统、内容发布等）
2. 需要操作哪些数据实体？（用户、订单、商品等）
3. 需要哪些功能操作？（列表、详情、新增、编辑、删除、状态变更等）
4. 每个实体涉及哪些数据字段？（名称、类型、是否必填、枚举值等）

## Skill 工作流程

### Step 1: 理解输入

读取用户提供的材料，识别以下内容：

- **业务模块**：涉及哪些业务领域（用户、订单、商品等）
- **页面/功能清单**：每个页面或功能点需要的操作（列表、新增、编辑、删除、详情、状态变更等）
- **数据字段**：每个实体的属性及类型
- **权限要求**：是否需要认证、角色区分

**输入来源**（可能是一种或多种组合）：
- PRD 文档内容（直接读取文档中的功能描述）
- 文字描述（用户口述的页面结构）
- 截图/原型图（分析页面元素推断所需接口）

### Step 1.5: 反模式检查

已在"反模式检查（强制执行，第一步）"章节中定义。确保已执行该检查清单，并据此修正用户的不规范输入。

### Step 2: 识别资源与操作

将业务需求映射为 REST 资源模型：

1. 从业务描述中提取名词实体（User、Order、Product 等）
2. 确定每个实体需要的操作（CRUD + 状态变更）
3. 参考 **REST API 设计规范** 中的 Resource Naming 和 Request Method 确定 URL 路径和 HTTP 方法
4. 确定资源间的层级关系（子资源使用嵌套路径，如 `/api/orders/{orderId}/items`）

### Step 3: 设计接口细节

为每个接口定义：

- **请求路径**：`METHOD /api/{resource}`
- **路径参数**（Path Params）：资源 ID 等
- **查询参数**（Query Params）：分页、过滤、排序
- **请求体**（Request Body）：POST/PUT/PATCH 的数据结构
- **响应体**（Response Body）：成功/失败的数据结构
- **认证要求**：Bearer Token 等

**PATCH 方法使用提醒**：如果业务需求中包含以下操作，应使用 PATCH 方法：
- 状态变更：启用/禁用、激活/冻结、上架/下架
- 流程推进：创建订单→支付→发货→确认收货→完成
- 部分字段修改：只修改名称、只修改邮箱等

### Step 4: 生成 OpenAPI YAML

严格按照模板输出 OpenAPI 3.2 规范的 YAML 文档。

**读取参考模板**：`references/rest-api-template.md`

模板包含以下结构：
- `openapi` - 版本号（3.2）
- `info` - API 基本信息（标题、描述、版本、联系方式）
- `servers` - 服务器地址列表
- `paths` - 所有接口路径及操作（含 operationId、example）
- `components` - 可复用的 Schema、responses、securitySchemes
- `security` - 全局安全要求（Bearer JWT）

### Step 5: 使用脚本验证 YAML

将生成的 YAML 内容保存到临时文件后，运行验证脚本检查 OpenAPI 规范合规性：

```shell
uv run scripts/validate.py <path-to-yaml-file>
```

也可以从标准输入读取：

```shell
cat output.yaml | uv run scripts/validate.py --stdin
```

如果验证失败，根据错误信息修正后重新运行验证，直到通过为止。

### Step 6: 质量检查

输出前按以下分类逐项自检：

**接口完整性**

- [ ] 每个资源都有完整的 CRUD（GET / POST / PUT / DELETE）
- [ ] 需要搜索/筛选的接口都支持分页参数 `page`(页码，从`1`开始）、`pageSize`（分页粒度）
- [ ] 状态变更操作（启用/禁用、取消、上架/下架等）使用 PATCH 方法
- [ ] 文件上传接口使用 `multipart/form-data` Content-Type

**URL 规范**

- [ ] 路径使用名词复数、小写、连字符分隔
- [ ] 路径参数使用 `{paramName}` 格式
- [ ] URL 中不包含动词（操作用 HTTP 方法表达）

**Schema 规范**

- [ ] 每个接口都有请求体 Schema（POST/PUT/PATCH）或参数定义（GET/DELETE）
- [ ] 每个接口都有响应体 Schema
- [ ] 所有 Schema 都标注了 `required` 字段
- [ ] 敏感字段（密码、密钥等）不出现在响应 Schema 中

**响应格式**

- [ ] 成功响应包含 `code`、`data`、`displayMsg`、`uniqCode`、`msg`
- [ ] 列表接口返回分页结构（`list` / `pageNo` / `pageSize` / `total`）
- [ ] 错误响应使用业务码
- [ ] 响应字段类型与 Schema 定义一致

**HTTP 方法语义**

- [ ] GET 仅用于查询，没有创建/删除/修改等副作用
- [ ] POST 用于创建资源
- [ ] DELETE 用于删除资源
- [ ] 状态变更使用 PATCH 而非 POST/GET

### Step 7: 输出验证（关键步骤）

将生成的 YAML 文件内容重新读取，按以下验证清单逐项检查。**如果发现任何不满足项，必须修正后重新输出，而不是跳过。**

**验证方法**：将 YAML 内容当作输入，逐项执行断言式检查。

| 验证项 | 检查方式 | 失败处理 |
|--------|---------|---------|
| YAML 可解析 | 检查输出是否为合法的 YAML 格式 | 重新生成，确保缩进正确 |
| 包含 OpenAPI 版本声明 | 查找 `openapi: 3.2` | 补充版本号 |
| 所有路径都符合 REST 命名 | 遍历 paths 下的所有键，确认不包含动词前缀（get/add/update/delete/change 等） | 修正路径并说明原因 |
| HTTP 方法使用正确 | 遍历每个 path 的方法，确认 GET 无副作用、POST 用于创建、DELETE 用于删除 | 修正方法并说明 HTTP 语义 |
| 响应格式统一 | 检查所有 responses 的 schema 是否包含 `code`、`data`、`displayMsg`、`uniqCode`、`msg` | 补齐缺失字段 |
| 分页格式正确 | 检查列表接口的 data 结构是否包含 `list`、`pageNo`、`pageSize`、`total` | 修正分页结构 |
| 枚举字段有 enum 定义 | 检查 role、status 等枚举字段是否包含 `enum` 约束 | 补充 enum 定义 |
| Schema 有 required 标注 | 检查每个 Schema 是否标注了 `required` 数组 | 补充 required |
| 不包含反模式 | 确认输出中没有动词式 URL 路径 | 修正并说明原因 |

**验证通过标准**：以上 9 项全部通过。如果有任意项未通过，回到 Step 3 或 Step 4 修正后重新生成，直到全部通过为止。

## 文件上传示例

设计文件上传接口时的参考规范。

**单文件上传**：

```
POST /api/files
Content-Type: multipart/form-data

Body:
  file: (binary)
```

Request Schema：
```yaml
FileUploadRequest:
  type: object
  properties:
    file:
      type: string
      format: binary
      description: 上传文件
    fileType:
      type: string
      enum: [image, document, video, other]
      description: 文件类型
  required:
    - file
```

Response：
```json
{
  "code": 200,
  "displayMsg": "上传成功",
  "data": { "fileId": "f_001", "fileName": "doc1.pdf", "fileUrl": "...", "fileSize": 204800 },
  "uniqCode": "SUCCESS",
  "msg": "success"
}
```

**多文件上传**：

```
POST /api/files/batch
Content-Type: multipart/form-data

Body:
  files: (binary, multiple)
```

Request Schema：
```yaml
FileBatchUploadRequest:
  type: object
  properties:
    files:
      type: array
      items:
        type: string
        format: binary
      description: 上传文件列表
  required:
    - files
```

Response（返回数组）：
```json
{
  "code": 200,
  "displayMsg": "批量上传成功",
  "data": [
    { "fileId": "f_001", "fileName": "doc1.pdf", "fileUrl": "...", "fileSize": 204800 },
    { "fileId": "f_002", "fileName": "doc2.pdf", "fileUrl": "...", "fileSize": 204800 }
  ],
  "uniqCode": "SUCCESS",
  "msg": "success"
}
```

**注意事项**：
- 使用 `Content-Type: multipart/form-data`，不适用 JSON body
- 文件大小限制在相关字段中标注 `maximum`（如 `fileSize`）
- 响应中返回文件 URL 供后续接口引用
- 如需关联业务，可将文件 ID 作为请求参数传入其他接口
