# rest-api-writer

根据产品需求（PRD 文档、页面描述、原型截图）设计 RESTful API 接口，输出 OpenAPI 3.2 YAML 格式文档。

## 目录结构

```
rest-api-writer/
├── SKILL.md                 # Skill 核心内容（设计规范 + 工作流程）
├── README.md                # 使用说明
├── references/
│   └── rest-api-template.md   # OpenAPI 3.2 YAML 参考模板
└── evals/
    └── evals.json           # 测试用例（正面 + 反面用例）
```

## 触发方式

当用户提到以下内容时触发：

| 类别 | 触发短语 |
|------|----------|
| API 设计 | "设计 API"、"写接口"、"REST API"、"接口设计"、"API 文档" |
| 页面驱动 | "根据页面写 API"、"根据这个页面写 REST API"、"帮我设计 API 接口" |
| PRD 提取 | 用户提供 PRD 文档后需要从中提取 API 定义 |

## 支持的输入

- **PRD 文档内容** — 从需求文档中提取业务模块和数据字段
- **文字描述** — 用户口述的页面结构和功能说明
- **截图/原型图** — 分析页面元素推断所需接口

## 工作流程

| 步骤 | 内容 | 说明 |
|------|------|------|
| Step 1 | 理解输入 | 分析 PRD、页面描述、截图，提取业务模块和数据字段 |
| Step 1.5 | 反模式检查 | 检查 URL 动词、RPC 风格、数据库表暴露、HTTP 方法误用、需求模糊 |
| Step 2 | 识别资源与操作 | 将业务需求映射为 REST 资源模型（名词实体 + CRUD） |
| Step 3 | 设计接口细节 | 定义路径参数、查询参数、请求体、响应体、认证要求 |
| Step 4 | 生成 OpenAPI YAML | 按 OpenAPI 3.2 模板输出 YAML 文档 |
| Step 5 | 质量检查 | 按分类清单逐项自检（接口完整性/URL规范/Schema规范/响应格式/HTTP语义） |
| Step 6 | 输出验证 | 重新读取生成的 YAML，11 项验证全部通过后才输出 |

## REST API 设计规范

### 资源命名

| 规则 | 好的示例 | 差的示例 |
|------|---------|---------|
| 集合资源用名词复数 | `/api/v1/users` | `/api/v1/user` |
| 单个资源用 ID 路径参数 | `/api/v1/users/{userId}` | `/api/v1/getUserById` |
| 子资源用嵌套路径 | `/api/v1/orders/{orderId}/items` | `/api/v1/getOrderItems` |
| 操作用 HTTP 方法表达 | `DELETE /api/v1/users/{userId}` | `/api/v1/deleteUser` |
| 过滤查询用 query 参数 | `GET /api/v1/orders?status=paid` | `GET /api/v1/getPaidOrders` |
| 多词用连字符连接 | `/api/v1/user-orders` | `/api/v1/userOrders` |

### HTTP 方法

| 方法 | 用途 | 说明 |
|------|------|------|
| `GET` | 获取资源/列表 | 安全的、幂等的，无副作用 |
| `POST` | 创建资源 | 新增一条数据 |
| `PUT` | 全量更新 | 替换整个资源 |
| `PATCH` | 部分更新/状态变更 | 修改部分字段，包括状态变更、流程推进 |
| `DELETE` | 删除资源 | 移除指定资源 |

### 统一响应格式

```json
{
   "code": 200,
   "displayMsg": "操作成功",
   "data": { ... },
   "uniqCode": "SUCCESS",
   "msg": "success"
}
```

分页响应结构：

```json
{
   "code": 200,
   "displayMsg": "操作成功",
   "data": {
       "list": [{ ... }],
       "pageNo": 1,
       "total": 81,
       "pageSize": 10
   },
   "uniqCode": "SUCCESS",
   "msg": "success"
}
```

### 分页参数

列表接口必须包含：`page`（默认 1）、`pageSize`（默认 20）、`sortField`、`sortOrder`（默认 desc）。

### 敏感字段过滤

密码类（pwd/password/passwd）、密钥类（secret/apiKey/token）字段不出现在任何接口的请求或响应中。

## 常见反模式

| 反模式 | 问题 | 正确处理 |
|--------|------|---------|
| URL 包含动词 | REST 以资源为中心，URL 应该是名词 | 改为名词复数路径 + 对应 HTTP 方法 |
| RPC 风格接口 | 设计理念不同，失去 REST 语义优势 | 映射为 REST 资源路径，login/logout 归入 securitySchemes |
| 直接暴露数据库表 | 泄露实现细节，暴露敏感字段 | 从业务角度抽象资源，过滤敏感字段，隐藏中间表 |
| HTTP 方法误用 | GET 做创建/删除违反 HTTP 语义 | 纠正为正确的 HTTP 方法 |
| 需求描述过于模糊 | 缺少关键信息无法设计 | 追问业务领域、数据实体、操作类型、字段定义 |

## 输出格式

OpenAPI 3.2 YAML 文档，包含：

- **info** — API 基本信息（标题、描述、版本、联系方式）
- **servers** — 服务器地址列表
- **paths** — 所有接口路径及操作（含 operationId、tags、example）
- **components** — 可复用的 Schema、responses、securitySchemes
- **security** — 全局安全要求（Bearer JWT）

生成的文档可直接导入 Apifox 等 API 管理工具使用。
