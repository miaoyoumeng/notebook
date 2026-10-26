---
name: rest-api-writer
description: "根据 PRD 文档、页面描述、原型截图或文字需求设计 RESTful API，输出 OpenAPI 3.2 YAML 接口文档。当用户提到设计 API、写接口、REST API、接口设计、API 文档、根据页面写 API、从 PRD 提取接口，或描述业务模块需要落地为接口时使用；也适用于用户提供 PRD 后未明确说要写接口文档的情况。不适用于接口代码实现、接口压测与调试、前端页面开发。"
---

# rest-api-writer

## 概述

根据产品需求设计 RESTful API，输出 OpenAPI 3.2 YAML 文档。输入包括 PRD、页面描述、原型截图与文字需求，输出可直接导入 Apifox 等 API 管理工具。

接口遵循资源导向、无状态、统一接口，仅使用 GET、POST、PUT、PATCH、DELETE 五种标准方法。

## 上下文层级

资源按三层加载：

1. 元数据：frontmatter 的 `name`、`description` 常驻上下文，用于判断是否触发本技能。
2. 指令：本文件，触发后加载，包含设计原则、流程、检查项与约束。
3. 参考资料：执行到对应步骤时按需读取。
   - `references/rest-api-template-*.md`：输出模板，生成 YAML 前读取。
   - `references/core-*.md`、`references/security*.md` 等：OpenAPI 3.2 规范主题，遇到对应主题时读取。
   - `scripts/validate.py`：校验脚本，生成后执行，不读取。

## 使用时机

触发场景：

- 用户提供 PRD、页面描述、原型截图或文字需求，要求设计接口。
- 用户要求生成 OpenAPI YAML、API 文档或 REST API。
- 用户描述业务模块（用户管理、订单、内容发布等），需要落地为接口。
- 用户提供 PRD，需要从中提取 API 定义。

不适用场景：

- 接口代码实现（Controller、Service、DTO）。
- 接口压测、调试、Mock 数据生成。
- 前端页面开发。
- 修改已有 OpenAPI 文件中的少量字段。

## 接口设计原则

### 资源命名

资源路径使用名词复数与 HTTP 方法表达操作，不在 URL 中使用动词。

| 规则 | 正确示例 | 错误示例 |
|------|----------|----------|
| 集合资源用名词复数 | `/api/users` | `/api/user` |
| 单个资源用 ID 路径参数 | `/api/users/{userId}` | `/api/getUserById` |
| 子资源用嵌套路径 | `/api/orders/{orderId}/items` | `/api/getOrderItems` |
| 操作用 HTTP 方法表达 | `DELETE /api/users/{userId}` | `/api/deleteUser` |
| 过滤查询用 query 参数 | `GET /api/orders?status=paid` | `GET /api/getPaidOrders` |
| 多词用连字符连接 | `/api/user-orders` | `/api/userOrders`、`/api/user_orders` |

命名格式：

| 对象 | 规则 | 示例 |
|------|------|------|
| 路径 | 小写、复数、连字符分隔 | `/api/user-orders` |
| Schema | PascalCase | `User`、`OrderCreateRequest` |
| 参数 | camelCase | `pageSize`、`createdAt` |

### HTTP 方法

| 方法 | 用途 | 说明 |
|------|------|------|
| `GET` | 获取资源或列表 | 安全、幂等，不产生副作用 |
| `POST` | 创建资源 | 新增数据 |
| `PUT` | 全量更新 | 替换整个资源 |
| `PATCH` | 部分更新、状态变更 | 状态变更、流程推进、部分字段修改均使用 PATCH |
| `DELETE` | 删除资源 | 移除指定资源 |

### 查询参数

列表接口包含分页参数：

| 参数 | 类型 | 说明 | 默认值 |
|------|------|------|--------|
| `page` | integer | 页码，从 1 开始 | 1 |
| `pageSize` | integer | 每页条数 | 20 |
| `sortField` | string | 排序字段 | - |
| `sortOrder` | string | `asc` 或 `desc` | `desc` |

按业务需要添加 `keyword`、`status`、`startTime`、`endTime` 等过滤参数。

### 请求体

- Content-Type 使用 `application/json`，文件上传使用 `multipart/form-data`。
- POST 包含创建资源所需的全部字段；PUT 包含完整数据；PATCH 只包含需要修改的字段。
- Schema 标注 `required` 数组，枚举字段使用 `enum` 定义可选值。

### 统一响应结构

成功响应字段固定为 `code`、`displayMsg`、`data`、`uniqCode`、`msg`。`data` 按场景返回对象、数组或分页结构；失败时 `data` 为 `null`。

```json
{
  "code": 200,
  "displayMsg": "操作成功",
  "data": { "id": 1, "name": "示例" },
  "uniqCode": "SUCCESS",
  "msg": "success"
}
```

分页响应的 `data` 包含 `list`、`pageNo`、`pageSize`、`total`：

```json
{
  "code": 200,
  "displayMsg": "操作成功",
  "data": {
    "list": [{ "id": 1, "name": "示例" }],
    "pageNo": 1,
    "pageSize": 10,
    "total": 81
  },
  "uniqCode": "SUCCESS",
  "msg": "success"
}
```

错误响应：

```json
{ "code": 400, "displayMsg": "参数错误", "uniqCode": "PARAM_ERROR", "msg": "Invalid parameter" }
```

响应字段说明：

| 字段 | 类型 | 说明 |
|------|------|------|
| `code` | int | 业务码值 |
| `displayMsg` | string | 中文提示，直接展示给用户 |
| `data` | object/array/null | 业务数据，失败时为 `null` |
| `uniqCode` | string | 系统全局唯一字母数字错误码 |
| `msg` | string | 英文错误提示 |

## 流程

### Step 1 理解输入

读取用户提供的材料，提取：

- 业务模块：涉及的业务领域。
- 页面与功能清单：每个页面需要的操作（列表、详情、新增、编辑、删除、状态变更）。
- 数据字段：实体属性、类型、必填与枚举值。
- 权限要求：认证方式与角色区分。

输入来源可以是 PRD 内容、文字描述、截图或原型图，也可能同时提供多种。

信息不足时，列出缺失项并追问，不自行假设业务场景。

### Step 2 反模式检查

按`危险信号`章节逐项检查输入。即使输入看起来合理，也要完整执行一遍。

检测到反模式时，在输出开头指出问题并给出正确做法，再按 REST 规范重新设计。不直接按用户的非规范要求生成接口。

### Step 3 识别资源与操作

1. 从业务描述中提取名词实体（User、Order、Product 等）。
2. 确定每个实体需要的操作（CRUD 与状态变更）。
3. 按`资源命名`与`HTTP 方法`确定路径和方法。
4. 确定资源层级，子资源使用嵌套路径。

### Step 4 设计接口细节

为每个接口定义：

- 请求路径：`METHOD /api/{resource}`。
- 路径参数：资源 ID 等。
- 查询参数：分页、过滤、排序。
- 请求体：POST、PUT、PATCH 的数据结构。
- 响应体：成功与失败的数据结构。
- 认证要求：Bearer Token 等。

状态变更、流程推进、部分字段修改使用 PATCH，不使用 POST。

### Step 5 生成 OpenAPI 3.2 YAML

按内容读取模板：

| 内容 | 模板 |
|------|------|
| 文档头部、复用组件、错误响应、安全方案 | `references/rest-api-template-components.md` |
| GET 列表、GET 详情 | `references/rest-api-template-crud-read.md` |
| POST、PUT、PATCH、DELETE | `references/rest-api-template-crud-write.md` |
| 文件上传、批量上传、文件列表 | `references/rest-api-template-file-upload.md` |
| 完整文档骨架 | `references/rest-api-template-full-example.md` |

输出文档包含 `openapi`、`info`、`servers`、`paths`、`components`、`security` 六个部分，每个 HTTP 方法独立成段。

### Step 6 运行校验脚本

将 YAML 保存到临时文件，执行：

```shell
uv run python scripts/validate.py /tmp/api.yaml
```

也可从标准输入读取：

```shell
cat /tmp/api.yaml | uv run python scripts/validate.py --stdin
```

校验失败时按错误信息修正，重新运行，直到通过。

### Step 7 质量自检

按`验证清单`逐项检查。存在不满足项时修正后重新检查。

### Step 8 输出验证

按`验证`章节的 9 项断言逐项检查。全部通过后输出；存在不满足项时回到 Step 4 或 Step 5 修正。

## 验证清单

输出前逐项自检。

**接口完整性**

- [ ] 每个资源都有完整的 CRUD（GET、POST、PUT、DELETE）。
- [ ] 列表接口支持 `page`、`pageSize` 分页参数。
- [ ] 状态变更操作使用 PATCH。
- [ ] 文件上传接口使用 `multipart/form-data`。

**URL 规范**

- [ ] 路径使用名词复数、小写、连字符分隔。
- [ ] 路径参数使用 `{paramName}` 格式。
- [ ] URL 中不包含动词。

**Schema 规范**

- [ ] POST、PUT、PATCH 接口有请求体 Schema，GET、DELETE 接口有参数定义。
- [ ] 每个接口都有响应体 Schema。
- [ ] 所有 Schema 标注 `required` 字段。
- [ ] 敏感字段（密码、密钥、token）不出现在响应 Schema 中。

**响应格式**

- [ ] 成功响应包含 `code`、`data`、`displayMsg`、`uniqCode`、`msg`。
- [ ] 列表接口返回 `list`、`pageNo`、`pageSize`、`total` 分页结构。
- [ ] 错误响应使用业务码。
- [ ] 响应字段类型与 Schema 定义一致。

**HTTP 方法语义**

- [ ] GET 仅用于查询，无创建、删除、修改副作用。
- [ ] POST 用于创建资源。
- [ ] DELETE 用于删除资源。
- [ ] 状态变更使用 PATCH。

## 危险信号

| 信号 | 识别方式 | 处理 |
|------|----------|------|
| HTTP 方法误用 | 用户要求用 GET 创建或删除，用 POST 查询列表 | 改用正确方法，并解释 HTTP 语义 |
| 动词式 URL | 路径包含 `get`、`add`、`update`、`delete`、`change` 等动词 | 改为名词复数路径加对应 HTTP 方法 |
| 需求模糊 | 缺少业务领域、数据实体、操作类型或字段定义 | 列出缺失项并追问 |
| RPC 风格接口 | URL 为动作名，如 `/login`、`/logout`、`/changeStatus` | 映射为资源操作；登录认证放入 `securitySchemes` |
| 直接暴露数据库表 | 路径与表名一一对应，包含中间表或敏感字段 | 按业务抽象资源，过滤敏感字段，隐藏中间表 |

## 理由辩解

### 动词式 URL

REST 以资源为中心，URL 表示资源实体，操作用 HTTP 方法表达。动词式 URL 是过程调用，无法利用 HTTP 方法的语义和缓存机制。

| 用户输入 | 正确处理 | 说明 |
|----------|----------|------|
| `/getUserList` | `GET /api/users` | 获取列表用 GET |
| `/addUser` | `POST /api/users` | 创建用 POST |
| `/updateUser` | `PUT /api/users/{userId}` 或 `PATCH` | 全量更新用 PUT，部分更新用 PATCH |
| `/deleteUser` | `DELETE /api/users/{userId}` | 删除用 DELETE |
| `/changeUserStatus` | `PATCH /api/users/{userId}/status` | 状态变更用 PATCH |

### HTTP 方法误用

GET 是安全且幂等的方法。用 GET 创建或删除会导致浏览器预加载、搜索引擎爬虫、CDN 与代理缓存意外触发操作，也可能重复执行或跳过执行。

| 用户要求 | 正确方法 | 原因 |
|----------|----------|------|
| 通过 GET 创建用户 | `POST /api/users` | 创建资源用 POST |
| 通过 GET 删除订单 | `DELETE /api/orders/{orderId}` | 删除资源用 DELETE |
| 用 POST 查询商品列表 | `GET /api/products` | 查询用 GET，筛选参数放 query |

### 需求模糊

缺少业务领域、数据实体、操作类型或字段定义时，无法设计具体接口。向用户追问以下信息：

1. 核心业务领域是什么（用户管理、订单系统、内容发布等）？
2. 需要操作哪些数据实体（用户、订单、商品等）？
3. 需要哪些功能操作（列表、详情、新增、编辑、删除、状态变更等）？
4. 每个实体涉及哪些字段（名称、类型、是否必填、枚举值等）？

## 验证

### 脚本校验

`scripts/validate.py` 读取 OpenAPI YAML，检查 YAML 语法与 OpenAPI 规范合规性，通过时退出码为 0，失败时为 1。

```shell
uv run python scripts/validate.py /tmp/api.yaml
```

```shell
cat /tmp/api.yaml | uv run python scripts/validate.py --stdin
```

### 输出断言

将生成的 YAML 作为输入，逐项执行检查：

| 验证项 | 检查方式 | 失败处理 |
|--------|----------|----------|
| YAML 可解析 | 输出为合法 YAML，缩进正确 | 重新生成 |
| 包含版本声明 | 存在 `openapi: 3.2.0` | 补充版本号 |
| 路径符合 REST 命名 | paths 下所有键不含动词前缀 | 修正路径 |
| HTTP 方法正确 | GET 无副作用，POST 用于创建，DELETE 用于删除 | 修正方法 |
| 响应格式统一 | 所有 responses 的 schema 包含 `code`、`data`、`displayMsg`、`uniqCode`、`msg` | 补齐字段 |
| 分页格式正确 | 列表接口的 data 包含 `list`、`pageNo`、`pageSize`、`total` | 修正分页结构 |
| 枚举字段有定义 | `status`、`role` 等字段包含 `enum` | 补充 `enum` |
| Schema 有 required | 每个 Schema 标注 `required` 数组 | 补充 `required` |
| 不包含反模式 | 输出中没有动词式 URL 与方法误用 | 修正并说明原因 |

9 项全部通过后输出。任意项未通过时，回到 Step 4 或 Step 5 修正，直到全部通过。

## 实现检查表

### HTTP 状态码

| 状态码 | 描述 | 适用场景 |
|--------|------|----------|
| 200 OK | 请求成功 | GET 查询、PUT/PATCH 更新成功 |
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

### 业务码

| 业务码 | 说明 |
|--------|------|
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

### 文件上传

- Content-Type 使用 `multipart/form-data`，不使用 JSON body。
- `file` 字段放在 `multipart/form-data` 的 requestBody 中。
- `fileSize` 标注 `minimum: 0`，需要上限时添加 `maximum`。
- 文件列表接口使用 `list`、`pageNo`、`total`、`pageSize` 分页结构。
- 同一参数只定义一次。

### 敏感字段

密码类（`pwd`、`password`、`passwd`）与密钥类（`secret`、`apiKey`、`token`）字段不出现在任何接口的请求或响应中。

## 参考资料

### 输出模板

| 文档 | 用途 |
|------|------|
| `references/rest-api-template-components.md` | 文档头部、Schema、错误响应、安全方案 |
| `references/rest-api-template-crud-read.md` | GET 列表与详情 |
| `references/rest-api-template-crud-write.md` | POST、PUT、PATCH、DELETE |
| `references/rest-api-template-file-upload.md` | 文件上传、批量上传、文件列表 |
| `references/rest-api-template-full-example.md` | 完整文档骨架 |

### OpenAPI 核心对象

| 文档 | 用途 |
|------|------|
| `references/core-openapi-object.md` | 根对象与字段 |
| `references/core-format-and-structure.md` | JSON/YAML、结构、解析 |
| `references/core-fixed-patterned-fields.md` | 固定字段与模式字段 |
| `references/core-info-metadata.md` | Info、Contact、License |
| `references/core-server.md` | Server 与 URL 模板 |
| `references/core-path-templating.md` | 路径模板化 |
| `references/core-reference-object.md` | `$ref` 解析 |
| `references/core-tags-and-external-docs.md` | Tag 与外部文档 |
| `references/advanced-base-uri-and-resolution.md` | Base URI 与解析 |

### 路径、参数与请求

| 文档 | 用途 |
|------|------|
| `references/paths-and-operations.md` | Paths、Path Item、Operation |
| `references/parameters.md` | Parameter 对象 |
| `references/request-body-and-media-type.md` | 请求体与 Media Type |
| `references/core-encoding-object.md` | Encoding 对象 |
| `references/core-media-types.md` | 媒体类型 |
| `references/core-header-object.md` | Header 对象 |

### 响应、Schema 与组件

| 文档 | 用途 |
|------|------|
| `references/responses.md` | Responses 与 Response |
| `references/core-http-status-codes.md` | HTTP 状态码键 |
| `references/core-example-object.md` | Example 对象 |
| `references/core-link-object.md` | Link 对象 |
| `references/core-runtime-expressions.md` | 运行时表达式 |
| `references/schema-and-components.md` | Schema 与 Components |
| `references/schema-json-schema-keywords.md` | JSON Schema 关键字 |
| `references/schema-composition-polymorphism.md` | 组合与多态 |
| `references/core-data-types-and-formats.md` | 数据类型与格式 |
| `references/core-discriminator-and-xml.md` | Discriminator 与 XML |
| `references/components-reuse.md` | 组件复用 |
| `references/best-practices-spec-authoring.md` | 编写实践 |

### 安全与扩展

| 文档 | 用途 |
|------|------|
| `references/security.md` | 安全机制总览 |
| `references/security-scheme-types.md` | 安全方案类型 |
| `references/security-requirement-object.md` | Security Requirement |
| `references/security-oauth2-flows.md` | OAuth2 流程 |
| `references/advanced-security-filtering.md` | 安全过滤 |
| `references/callbacks-and-webhooks.md` | Callback 与 Webhook |
| `references/advanced-extensions.md` | `x-` 扩展 |
