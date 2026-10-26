# 写入接口模板

生成 OpenAPI 3.2 YAML 的 POST、PUT、PATCH、DELETE 操作。每个方法独立成段。

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
                example: 创建成功
          example:
            code: 200
            data:
              id: 1
              name: 示例
            msg: success
            uniqCode: SUCCESS
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
                example: 更新成功
          example:
            code: 200
            data:
              id: 1
              name: 示例
            msg: success
            uniqCode: SUCCESS
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
                example: 更新成功
          example:
            code: 200
            data:
              id: 1
              name: 新值
            msg: success
            uniqCode: SUCCESS
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
                example: 200
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
            code: 200
            data: null
            msg: success
            uniqCode: SUCCESS
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
