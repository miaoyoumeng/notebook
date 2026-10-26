# 文件上传模板

生成 OpenAPI 3.2 YAML 的文件上传、批量上传、文件列表操作与 File Schema。

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
