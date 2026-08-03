# OpenAPI 3.2 YAML 输出模板

生成OpenAPI YAML 文档，基于 OpenAPI 3.2 规范标准。

每个 HTTP 方法独立成段，用 `---` 分隔符分割。生成时按需组合使用这些方法模板。

---

## GET - 获取资源列表

```yaml
get:
  summary: 获取{资源}列表
  description: "{功能说明，如：支持关键词搜索、状态筛选、分页等}"
  operationId: list{Resource}s
  parameters:
    - name: page
      in: query
      description: 页码，从 1 开始
      required: false
      schema:
        type: integer
        default: 1
        minimum: 1
    - name: page_size
      in: query
      description: 每页数量
      required: false
      schema:
        type: integer
        default: 20
        minimum: 1
        maximum: 100
    - name: keyword
      in: query
      description: 搜索关键词
      required: false
      schema:
        type: string
    - name: sort_by
      in: query
      description: 排序字段
      required: false
      schema:
        type: string
        default: created_at
    - name: sort_order
      in: query
      description: 排序方向
      required: false
      schema:
        type: string
        enum:
          - asc
          - desc
        default: desc
  responses:
    '200':
      description: 成功
      content:
        application/json:
          schema:
            type: object
            properties:
              code:
                type: integer
                example: 0
              data:
                type: object
                properties:
                  total:
                    type: integer
                    description: 总记录数
                  list:
                    type: array
                    items:
                      $ref: '#/components/schemas/{Resource}'
              msg:
                type: string
                example: success
              uniqCode:
                type: string
                example: SUCCESS
              displayMsg:
                type: string
                example: 操作成功
          example:
            code: 0
            data:
              total: 100
              list:
                - id: 1
                  name: 示例
            msg: success
            uniqCode: SUCCESS_CODE
            displayMsg: 操作成功
    '400':
      $ref: '#/components/responses/BadRequest'
    '401':
      $ref: '#/components/responses/Unauthorized'
    '403':
      $ref: '#/components/responses/Forbidden'
  security:
    - BearerAuth: []
```

---

## GET - 获取资源详情

```yaml
get:
  summary: 获取{资源}详情
  description: "{功能说明}"
  operationId: get{Resource}
  parameters:
    - name: {resourceId}
      in: path
      description: 资源 ID
      required: true
      schema:
        type: string
  responses:
    '200':
      description: 成功
      content:
        application/json:
          schema:
            type: object
            properties:
              code:
                type: integer
                example: 0
              data:
                $ref: '#/components/schemas/{Resource}'
              msg:
                type: string
                example: success
              uniqCode:
                type: string
                example: SUCCESS
              displayMsg:
                type: string
                example: 操作成功
          example:
            code: 0
            data:
              id: 1
              name: 示例
            msg: success
            uniqCode: SUCCESS_CODE
            displayMsg: 操作成功
    '400':
      $ref: '#/components/responses/BadRequest'
    '401':
      $ref: '#/components/responses/Unauthorized'
    '403':
      $ref: '#/components/responses/Forbidden'
    '404':
      $ref: '#/components/responses/NotFound'
  security:
    - BearerAuth: []
```

---

## POST - 创建资源

```yaml
post:
  summary: 创建{资源}
  description: "{功能说明}"
  operationId: create{Resource}
  requestBody:
    required: true
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/{Resource}CreateRequest'
        example:
          field1: 示例值
          field2: 100
  responses:
    '201':
      description: 创建成功
      content:
        application/json:
          schema:
            type: object
            properties:
              code:
                type: integer
                example: 0
              data:
                $ref: '#/components/schemas/{Resource}'
              msg:
                type: string
                example: success
              uniqCode:
                type: string
                example: SUCCESS
              displayMsg:
                type: string
                example: 创建成功
          example:
            code: 0
            data:
              id: 1
              name: 示例
            msg: success
            uniqCode: SUCCESS_CODE
            displayMsg: 创建成功
    '400':
      $ref: '#/components/responses/BadRequest'
    '401':
      $ref: '#/components/responses/Unauthorized'
    '403':
      $ref: '#/components/responses/Forbidden'
  security:
    - BearerAuth: []
```

---

## PUT - 全量更新资源

```yaml
put:
  summary: 全量更新{资源}
  description: "{功能说明，如：需要传递所有字段，未传递的字段将被清空或设为默认值}"
  operationId: update{Resource}
  parameters:
    - name: {resourceId}
      in: path
      description: 资源 ID
      required: true
      schema:
        type: string
  requestBody:
    required: true
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/{Resource}UpdateRequest'
        example:
          field1: 示例值
          field2: 100
  responses:
    '200':
      description: 更新成功
      content:
        application/json:
          schema:
            type: object
            properties:
              code:
                type: integer
                example: 0
              data:
                $ref: '#/components/schemas/{Resource}'
              msg:
                type: string
                example: success
              uniqCode:
                type: string
                example: SUCCESS
              displayMsg:
                type: string
                example: 更新成功
          example:
            code: 0
            data:
              id: 1
              name: 示例
            msg: success
            uniqCode: SUCCESS_CODE
            displayMsg: 更新成功
    '400':
      $ref: '#/components/responses/BadRequest'
    '401':
      $ref: '#/components/responses/Unauthorized'
    '403':
      $ref: '#/components/responses/Forbidden'
    '404':
      $ref: '#/components/responses/NotFound'
  security:
    - BearerAuth: []
```

---

## PATCH - 部分更新资源

```yaml
patch:
  summary: 部分更新{资源}
  description: "{功能说明，如：仅传递需要修改的字段，未传递的字段保持不变}"
  operationId: patch{Resource}
  parameters:
    - name: {resourceId}
      in: path
      description: 资源 ID
      required: true
      schema:
        type: string
  requestBody:
    required: true
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/{Resource}PatchRequest'
        example:
          field1: 新值
  responses:
    '200':
      description: 更新成功
      content:
        application/json:
          schema:
            type: object
            properties:
              code:
                type: integer
                example: 0
              data:
                $ref: '#/components/schemas/{Resource}'
              msg:
                type: string
                example: success
              uniqCode:
                type: string
                example: SUCCESS
              displayMsg:
                type: string
                example: 更新成功
          example:
            code: 0
            data:
              id: 1
              name: 新值
            msg: success
            uniqCode: SUCCESS_CODE
            displayMsg: 更新成功
    '400':
      $ref: '#/components/responses/BadRequest'
    '401':
      $ref: '#/components/responses/Unauthorized'
    '403':
      $ref: '#/components/responses/Forbidden'
    '404':
      $ref: '#/components/responses/NotFound'
  security:
    - BearerAuth: []
```

---

## DELETE - 删除资源

```yaml
delete:
  summary: 删除{资源}
  description: "{功能说明，如：逻辑删除或物理删除}"
  operationId: delete{Resource}
  parameters:
    - name: {resourceId}
      in: path
      description: 资源 ID
      required: true
      schema:
        type: string
  responses:
    '200':
      description: 删除成功
      content:
        application/json:
          schema:
            type: object
            properties:
              code:
                type: integer
                example: 0
              data:
                type: 'null'
              msg:
                type: string
                example: success
              uniqCode:
                type: string
                example: SUCCESS
              displayMsg:
                type: string
                example: 删除成功
          example:
            code: 0
            data: null
            msg: success
            uniqCode: SUCCESS_CODE
            displayMsg: 删除成功
    '400':
      $ref: '#/components/responses/BadRequest'
    '401':
      $ref: '#/components/responses/Unauthorized'
    '403':
      $ref: '#/components/responses/Forbidden'
    '404':
      $ref: '#/components/responses/NotFound'
  security:
    - BearerAuth: []
```

---

## 文档头部模板

```yaml
openapi: 3.2
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
```

---

## 可复用组件模板

```yaml
components:
  schemas:
    # ===== 资源主 Schema =====
    {Resource}:
      type: object
      required:
        - id
        - created_at
        - updated_at
      properties:
        id:
          type: integer
          description: 唯一标识
        name:
          type: string
          description: 名称
        code:
          type: string
          description: 编码
        status:
          type: string
          description: 状态
          enum:
            - active
            - inactive
            - deleted
        description:
          type: string
          description: 描述
        image:
          type: string
          description: 图片URL
        url:
          type: string
          description: 链接地址
        email:
          type: string
          description: 邮箱
        phone:
          type: string
          description: 手机号
        price:
          type: number
          description: 价格
        quantity:
          type: integer
          description: 数量
        percentage:
          type: integer
          description: 百分比
        sort_order:
          type: integer
          description: 排序
        is_default:
          type: boolean
          description: 是否默认
        created_at:
          type: string
          format: date-time
          description: 创建时间
        updated_at:
          type: string
          format: date-time
          description: 更新时间
        deleted_at:
          type: string
          format: date-time
          description: 删除时间

    # ===== 创建请求 Schema =====
    {Resource}CreateRequest:
      type: object
      required:
        - name
        - code
      properties:
        name:
          type: string
          description: 名称
          maxLength: 100
        code:
          type: string
          description: 编码
          maxLength: 50
        status:
          type: string
          description: 状态
          enum:
            - active
            - inactive
          default: active
        description:
          type: string
          description: 描述
          maxLength: 500
        sort_order:
          type: integer
          description: 排序
          default: 0
        is_default:
          type: boolean
          description: 是否默认
          default: false

    # ===== 全量更新请求 Schema =====
    {Resource}UpdateRequest:
      type: object
      required:
        - name
        - code
      properties:
        name:
          type: string
          description: 名称
          maxLength: 100
        code:
          type: string
          description: 编码
          maxLength: 50
        status:
          type: string
          description: 状态
          enum:
            - active
            - inactive
            - deleted
        description:
          type: string
          description: 描述
          maxLength: 500
        sort_order:
          type: integer
          description: 排序
        is_default:
          type: boolean
          description: 是否默认

    # ===== 部分更新请求 Schema =====
    {Resource}PatchRequest:
      type: object
      properties:
        name:
          type: string
          description: 名称
          maxLength: 100
        status:
          type: string
          description: 状态
          enum:
            - active
            - inactive
            - deleted
        description:
          type: string
          description: 描述
          maxLength: 500
        sort_order:
          type: integer
          description: 排序

    # ===== 统一错误响应 =====
    Error:
      type: object
      properties:
        code:
          type: integer
          description: 业务状态码，与HTTP状态码一致1001)'
        data:
          type: 'null'
          description: 业务数据，错误时为null
        msg:
          type: string
          description: 英文错误提示
        uniqCode:
          type: string
          description: 唯一错误码
        displayMsg:
          type: string
          description: 中文错误提示
      required:
        - code
        - data
        - msg
        - uniqCode
        - displayMsg

  responses:
    BadRequest:
      description: 请求参数错误
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'
          example:
            code: 400
            data: null
            msg: Invalid request parameters
            uniqCode: PARAM_ILLEGAL_CODE
            displayMsg: 请求参数错误

    Unauthorized:
      description: 未认证
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'
          example:
            code: 401
            data: null
            msg: Login expired
            uniqCode: UNAUTHORIZED_CODE
            displayMsg: 未登录或登录已过期

    Forbidden:
      description: 无权限
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'
          example:
            code: 403
            data: null
            msg: Access denied
            uniqCode: FORBIDDEN_CODE
            displayMsg: 无权访问

    NotFound:
      description: 资源不存在
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'
          example:
            code: 404
            data: null
            msg: Resource not found
            uniqCode: NOT_EXIST_CODE
            displayMsg: 资源不存在

    Conflict:
      description: 数据冲突
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'
          example:
            code: 409
            data: null
            msg: Data conflict
            uniqCode: DATA_CONFLICT
            displayMsg: 数据冲突

    PayloadTooLarge:
      description: 上传文件太大
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'
          example:
            code: 413
            data: null
            msg: File too large
            uniqCode: FILE_TOO_LARGE
            displayMsg: 上传文件太大

    UnsupportedMediaType:
      description: 文件格式不支持
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'
          example:
            code: 415
            data: null
            msg: Unsupported file type
            uniqCode: UNSUPPORTED_MEDIA_TYPE
            displayMsg: 文件格式不支持

  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT

security:
  - BearerAuth: []
```

---

## POST - 文件上传（multipart/form-data）

```yaml
post:
  summary: 上传文件
  description: "单文件上传，支持图片、文档、视频等类型"
  operationId: uploadFile
  tags:
    - 文件管理
  requestBody:
    required: true
    content:
      multipart/form-data:
        schema:
          type: object
          required:
            - file
          properties:
            file:
              type: string
              format: binary
              description: 上传文件
            fileType:
              type: string
              enum:
                - image
                - document
                - video
                - other
              description: 文件类型
  responses:
    '201':
      description: 上传成功
      content:
        application/json:
          schema:
            type: object
            properties:
              code:
                type: integer
                example: 200
              data:
                $ref: '#/components/schemas/File'
              msg:
                type: string
                example: success
              uniqCode:
                type: string
                example: SUCCESS
              displayMsg:
                type: string
                example: 上传成功
          example:
            code: 200
            data:
              fileId: f_abc123
              fileName: photo.jpg
              fileUrl: https://cdn.example.com/files/photo.jpg
              fileSize: 1048576
              fileType: image
              uploadedAt: "2026-01-15T10:30:00Z"
            msg: success
            uniqCode: SUCCESS
            displayMsg: 上传成功
    '400':
      $ref: '#/components/responses/BadRequest'
    '401':
      $ref: '#/components/responses/Unauthorized'
    '413':
      $ref: '#/components/responses/PayloadTooLarge'
    '415':
      $ref: '#/components/responses/UnsupportedMediaType'
  security:
    - BearerAuth: []
```

---

## POST - 批量文件上传

```yaml
post:
  summary: 批量上传文件
  description: "一次上传多个文件"
  operationId: batchUploadFiles
  tags:
    - 文件管理
  requestBody:
    required: true
    content:
      multipart/form-data:
        schema:
          type: object
          required:
            - files
          properties:
            files:
              type: array
              items:
                type: string
                format: binary
              description: 上传文件列表
  responses:
    '201':
      description: 批量上传成功
      content:
        application/json:
          schema:
            type: object
            properties:
              code:
                type: integer
                example: 200
              data:
                type: array
                items:
                  $ref: '#/components/schemas/File'
              msg:
                type: string
                example: success
              uniqCode:
                type: string
                example: SUCCESS
              displayMsg:
                type: string
                example: 批量上传成功
          example:
            code: 200
            data:
              - fileId: f_001
                fileName: doc1.pdf
                fileUrl: https://cdn.example.com/files/doc1.pdf
                fileSize: 204800
                fileType: document
              - fileId: f_002
                fileName: photo.jpg
                fileUrl: https://cdn.example.com/files/photo.jpg
                fileSize: 102400
                fileType: image
            msg: success
            uniqCode: SUCCESS
            displayMsg: 批量上传成功
    '400':
      $ref: '#/components/responses/BadRequest'
    '401':
      $ref: '#/components/responses/Unauthorized'
    '413':
      $ref: '#/components/responses/PayloadTooLarge'
  security:
    - BearerAuth: []
```

---

## GET - 文件列表（含 fileType 筛选）

```yaml
get:
  summary: 获取文件列表
  description: "支持按文件类型筛选、分页查询"
  operationId: listFiles
  tags:
    - 文件管理
  parameters:
    - name: fileType
      in: query
      description: 文件类型筛选（image/document/video）
      required: false
      schema:
        type: string
        enum:
          - image
          - document
          - video
    - name: page
      in: query
      description: 页码，从 1 开始
      required: false
      schema:
        type: integer
        default: 1
        minimum: 1
    - name: pageSize
      in: query
      description: 每页数量
      required: false
      schema:
        type: integer
        default: 20
        minimum: 1
        maximum: 100
    - name: sortField
      in: query
      description: 排序字段
      required: false
      schema:
        type: string
        default: createdAt
    - name: sortOrder
      in: query
      description: 排序方向
      required: false
      schema:
        type: string
        enum:
          - asc
          - desc
        default: desc
  responses:
    '200':
      description: 查询成功
      content:
        application/json:
          schema:
            type: object
            properties:
              code:
                type: integer
                example: 200
              data:
                type: object
                properties:
                  list:
                    type: array
                    items:
                      $ref: '#/components/schemas/File'
                  pageNo:
                    type: integer
                  total:
                    type: integer
                  pageSize:
                    type: integer
              msg:
                type: string
                example: success
              uniqCode:
                type: string
                example: SUCCESS
              displayMsg:
                type: string
                example: 操作成功
          example:
            code: 200
            data:
              list:
                - fileId: f_001
                  fileName: doc1.pdf
                  fileUrl: https://cdn.example.com/files/doc1.pdf
                  fileSize: 204800
                  fileType: document
                  uploadedAt: "2026-01-15T10:30:00Z"
              pageNo: 1
              total: 50
              pageSize: 20
            msg: success
            uniqCode: SUCCESS
            displayMsg: 操作成功
    '400':
      $ref: '#/components/responses/BadRequest'
    '401':
      $ref: '#/components/responses/Unauthorized'
    '403':
      $ref: '#/components/responses/Forbidden'
  security:
    - BearerAuth: []
```

---

## File Schema（添加到 components/schemas 中）

```yaml
    File:
      type: object
      required:
        - fileId
        - fileName
        - fileUrl
        - fileSize
        - fileType
        - uploadedAt
      properties:
        fileId:
          type: string
          description: 文件唯一标识
        fileName:
          type: string
          description: 文件名
          maxLength: 255
        fileUrl:
          type: string
          description: 文件访问 URL
          maxLength: 500
        fileSize:
          type: integer
          description: 文件大小（字节）
          minimum: 0
        fileType:
          type: string
          description: 文件类型
          enum:
            - image
            - document
            - video
            - other
        uploadedAt:
          type: string
          format: date-time
          description: 上传时间
```

---

## 文件上传注意事项

1. **Content-Type 必须为 `multipart/form-data`**，不适用 JSON body
2. **不要将 `file` 字段放在 `application/json` schema 中**——它属于 `multipart/form-data` 的 requestBody
3. **文件大小限制**：在 File Schema 的 `fileSize` 字段中标注 `minimum: 0`，如需上限可添加 `maximum`
4. **分页结构**：文件列表接口同样使用 `list`/`pageNo`/`total`/`pageSize` 分页格式
5. **一个参数只定义一次**：不要重复定义相同的 query parameter（如 `fileType` 只出现一次）

---

## 完整文档结构示例

将上述模板组合成完整的 OpenAPI 文档：

```yaml
openapi: 3.2
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

