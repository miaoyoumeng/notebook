# Apifox OpenAPI 3.2 模板

## 支持的 HTTP 方法

仅支持以下 HTTP 方法：
- `GET` - 查询资源
- `POST` - 创建资源
- `PUT` - 全量更新资源
- `DELETE` - 删除资源
- `PATCH` - 部分更新资源

不支持其他 HTTP 方法（如 HEAD、OPTIONS、CONNECT、TRACE 等）。

## 支持的协议

仅支持 `HTTP/HTTPS` 协议，不支持其他协议（如 WebSocket、gRPC、Socket.IO 等）。

## 统一响应格式

所有 API 响应必须遵循以下统一格式：

```json
{
   "code": 200,
   "displayMsg": "操作成功",
   "data": { "id": 1, "name": "示例" },
   "uniqCode": "SUCCESS",
   "msg": "success"
}
```

### 响应字段说明

| 字段 | 类型 | 说明 | Mock 规则 |
|------|------|------|-----------|
| `code` | integer | 业务状态码 | `@integer(200, 500)` |
| `displayMsg` | string | 展示给用户的提示信息 | `@pick(操作成功,操作失败,参数错误,系统异常)` |
| `data` | object | 业务数据 | 根据具体接口定义 |
| `uniqCode` | string | 唯一错误码 | `@pick(SUCCESS,FAIL,PARAM_ERROR,SYSTEM_ERROR)` |
| `msg` | string | 技术调试信息 | `@pick(success,error,param_error,system_error)` |

## GET 接口模板

```yaml
paths:
  /api/v1/{resource}:
    get:
      summary: 查询资源列表
      tags:
        - 资源管理
      operationId: getResourceList
      parameters:
        - name: page
          in: query
          schema:
            type: integer
            x-apifox-mock: "@integer(1, 100)"
        - name: pageSize
          in: query
          schema:
            type: integer
            x-apifox-mock: "@integer(10, 50)"
      responses:
        '200':
          description: 成功
          content:
            application/json:
              schema:
                allOf:
                  - $ref: '#/components/schemas/UnifiedResponse'
                  - type: object
                    properties:
                      data:
                        type: object
                        properties:
                          total:
                            type: integer
                            x-apifox-mock: "@integer(1, 1000)"
                          list:
                            type: array
                            items:
                              $ref: '#/components/schemas/ResourceItem'
```

## POST 接口模板

```yaml
paths:
  /api/v1/{resource}:
    post:
      summary: 创建资源
      tags:
        - 资源管理
      operationId: createResource
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CreateResourceRequest'
      responses:
        '200':
          description: 成功
          content:
            application/json:
              schema:
                allOf:
                  - $ref: '#/components/schemas/UnifiedResponse'
                  - type: object
                    properties:
                      data:
                        type: object
                        properties:
                          id:
                            type: integer
                            x-apifox-mock: "@integer(1, 9999)"
```

## PUT 接口模板

```yaml
paths:
  /api/v1/{resource}/{id}:
    put:
      summary: 全量更新资源
      tags:
        - 资源管理
      operationId: updateResource
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: integer
            x-apifox-mock: "@integer(1, 9999)"
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/UpdateResourceRequest'
      responses:
        '200':
          description: 成功
          content:
            application/json:
              schema:
                allOf:
                  - $ref: '#/components/schemas/UnifiedResponse'
                  - type: object
                    properties:
                      data:
                        type: 'null'
```

## DELETE 接口模板

```yaml
paths:
  /api/v1/{resource}/{id}:
    delete:
      summary: 删除资源
      tags:
        - 资源管理
      operationId: deleteResource
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: integer
            x-apifox-mock: "@integer(1, 9999)"
      responses:
        '200':
          description: 成功
          content:
            application/json:
              schema:
                allOf:
                  - $ref: '#/components/schemas/UnifiedResponse'
                  - type: object
                    properties:
                      data:
                        type: 'null'
```

## PATCH 接口模板

```yaml
paths:
  /api/v1/{resource}/{id}:
    patch:
      summary: 部分更新资源
      tags:
        - 资源管理
      operationId: patchResource
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: integer
            x-apifox-mock: "@integer(1, 9999)"
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/PatchResourceRequest'
      responses:
        '200':
          description: 成功
          content:
            application/json:
              schema:
                allOf:
                  - $ref: '#/components/schemas/UnifiedResponse'
                  - type: object
                    properties:
                      data:
                        type: 'null'
```

## 通用 Schema 定义

```yaml
components:
  schemas:
    # 统一响应结构
    UnifiedResponse:
      type: object
      properties:
        code:
          type: integer
          description: 业务状态码
          x-apifox-mock: "@integer(200, 500)"
        displayMsg:
          type: string
          description: 展示给用户的提示信息
          x-apifox-mock: "@pick(操作成功,操作失败,参数错误,系统异常)"
        data:
          type: object
          description: 业务数据
        uniqCode:
          type: string
          description: 唯一错误码
          x-apifox-mock: "@pick(SUCCESS,FAIL,PARAM_ERROR,SYSTEM_ERROR)"
        msg:
          type: string
          description: 技术调试信息
          x-apifox-mock: "@pick(success,error,param_error,system_error)"
      required:
        - code
        - displayMsg
        - uniqCode
        - msg

    # 示例资源项
    ResourceItem:
      type: object
      properties:
        id:
          type: integer
          description: 资源ID
          x-apifox-mock: "@integer(1, 9999)"
        name:
          type: string
          description: 资源名称
          x-apifox-mock: "@ctitle"
        status:
          type: integer
          description: 状态
          x-apifox-mock: "@pick(0, 1)"
        createdAt:
          type: string
          format: date-time
          description: 创建时间
          x-apifox-mock: "@datetime(\"yyyy-MM-dd HH:mm:ss\")"
        updatedAt:
          type: string
          format: date-time
          description: 更新时间
          x-apifox-mock: "@datetime(\"yyyy-MM-dd HH:mm:ss\")"
      required:
        - id
        - name

    # 创建请求
    CreateResourceRequest:
      type: object
      properties:
        name:
          type: string
          description: 资源名称
          x-apifox-mock: "@ctitle"
        status:
          type: integer
          description: 状态
          x-apifox-mock: "@pick(0, 1)"
      required:
        - name

    # 更新请求（全量）
    UpdateResourceRequest:
      type: object
      properties:
        name:
          type: string
          description: 资源名称
          x-apifox-mock: "@ctitle"
        status:
          type: integer
          description: 状态
          x-apifox-mock: "@pick(0, 1)"
      required:
        - name
        - status

    # 更新请求（部分）
    PatchResourceRequest:
      type: object
      properties:
        name:
          type: string
          description: 资源名称
          x-apifox-mock: "@ctitle"
        status:
          type: integer
          description: 状态
          x-apifox-mock: "@pick(0, 1)"
```

## Mock 规则速查

| 字段类型 | Mock 规则 |
|----------|-----------|
| ID | `@integer(1, 9999)` |
| 名称 | `@ctitle` 或 `@cname` |
| 状态码 | `@integer(200, 500)` |
| 状态枚举 | `@pick(0, 1)` |
| 消息提示 | `@pick(操作成功,操作失败,参数错误)` |
| 时间 | `@datetime("yyyy-MM-dd HH:mm:ss")` |
| 邮箱 | `@email` |
| 手机号 | `@phone` |
| URL | `@url` |
| 描述 | `@cparagraph` |
| 布尔值 | `@boolean` |
| 金额 | `@float(0.01, 9999.99, 2, 2)` |
| 数量 | `@integer(1, 100)` |
