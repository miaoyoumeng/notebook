# 完整文档结构示例

将各模板组合为完整 OpenAPI 3.2 文档的骨架。

---

## 完整文档结构示例

将上述模板组合成完整的 OpenAPI 文档：

```yaml
openapi: 3.2.0
info:
  title: "{模块名称} API"
  description: "{模块功能描述}"
  version: 1.0.0
  contact:
    name: API 支持
    email: support@example.com
servers:
  - url: https://api.example.com/api/v1
    description: 生产环境
  - url: http://localhost:8080/api/v1
    description: 本地开发环境

paths:
  /{resource}:
    get:
      # 复制 GET 列表模板
    post:
      # 复制 POST 创建模板

  /{resource}/{resourceId}:
    parameters:
      - name: {resourceId}
        in: path
        description: 资源 ID
        required: true
        schema:
          type: string
    get:
      # 复制 GET 详情模板
    put:
      # 复制 PUT 全量更新模板
    patch:
      # 复制 PATCH 部分更新模板
    delete:
      # 复制 DELETE 删除模板

components:
  schemas:
  responses:
    # 错误响应
  securitySchemes:
    # 认证方案

security:
  - BearerAuth: []
```
