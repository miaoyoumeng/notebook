# 查询接口模板

生成 OpenAPI 3.2 YAML 的 GET 列表与详情操作。每个方法独立成段。

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
    - name: pageSize
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
    - name: sortField
      in: query
      description: 排序字段
      required: false
      schema:
        type: string
        default: created_at
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
      description: 成功
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
                  pageNo:
                    type: integer
                    description: 当前页码
                  pageSize:
                    type: integer
                    description: 每页条数
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
            code: 200
            data:
              pageNo: 1
              pageSize: 20
              total: 100
              list:
                - id: 1
                  name: 示例
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
                example: 200
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
            code: 200
            data:
              id: 1
              name: 示例
            msg: success
            uniqCode: SUCCESS
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
