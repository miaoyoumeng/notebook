# 文档头部与可复用组件模板

生成 OpenAPI 3.2 文档的 `info`、`servers`、`components`、`security` 部分。

---

## 文档头部模板

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
          description: 业务状态码，与 HTTP 状态码一致
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
