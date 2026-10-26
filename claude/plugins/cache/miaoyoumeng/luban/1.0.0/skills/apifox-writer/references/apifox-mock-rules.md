# Apifox Mock 数据规则

将 OpenAPI YAML 转换为 Apifox 增强版 YAML，在 response schema 中添加 `x-apifox-mock` 扩展字段。

## 转换步骤

1. 读取 OpenAPI 3.2 YAML，解析 paths、components.schemas、responses、webhooks
2. 保持 paths、operations、parameters 等业务逻辑不变
3. 为 response schema 的每个属性添加 `x-apifox-mock` 扩展字段

## Mock 规则映射

**字段类型到 Mock 规则映射：**

| 字段类型/用途 | Mock 规则 |
|---------------|-----------|
| ID / 主键 | `@integer(1, 9999)` |
| UUID | `@uuid` |
| 人名 | `@cname` |
| 标题/名称 | `@ctitle` 或 `@cword(2, 6)` |
| 描述/备注 | `@cparagraph` |
| 邮箱 | `@email` |
| 手机号 | `@phone` |
| URL/链接 | `@url` |
| 图片 | `@image("200x200")` |
| 时间/日期 | `@datetime("yyyy-MM-dd HH:mm:ss")` |
| 布尔值 | `@boolean` |
| 整数/数量 | `@integer(min, max)` |
| 浮点数/金额 | `@float(0.01, 9999.99, 2, 2)` |
| 字符串(通用) | `@string(length)` |
| 状态/枚举 | `@pick(val1, val2, val3)` |
| 身份证号 | `@id` |
| 随机整数 | `{{$randomInt}}` |
| 时间戳 | `{{$timestamp}}` |

**属性名关键词到 Mock 规则映射：**

| 属性名关键词 | 推荐 Mock 规则 |
|--------------|----------------|
| `id`, `Id`, `ID` | `@integer(1, 9999)` 或 `@uuid` |
| `name`, `Name`, `title` | `@cname` 或 `@ctitle` |
| `email`, `Email`, `mail` | `@email` |
| `phone`, `Phone`, `mobile` | `@phone` |
| `url`, `Url`, `URL`, `link` | `@url` |
| `image`, `Image`, `avatar`, `photo` | `@image("200x200")` |
| `time`, `Time`, `date`, `Date`, `createdAt`, `updatedAt` | `@datetime("yyyy-MM-dd HH:mm:ss")` |
| `status`, `Status`, `type`, `Type`, `state` | `@pick(...)` 使用枚举值 |
| `desc`, `description`, `remark`, `note` | `@cparagraph` 或 `@cword(4, 10)` |
| `price`, `amount`, `money`, `cost` | `@float(0.01, 9999.99, 2, 2)` |
| `count`, `num`, `quantity` | `@integer(1, 100)` |
| `bool`, `enable`, `active`, `isXxx` | `@boolean` |

## 转换示例

**原始：**

```yaml
components:
  schemas:
    User:
      type: object
      properties:
        id:
          type: integer
        name:
          type: string
        email:
          type: string
        status:
          type: string
          enum: [active, inactive]
        createdAt:
          type: string
          format: date-time
```

**添加 Mock 后：**

```yaml
components:
  schemas:
    User:
      type: object
      properties:
        id:
          type: integer
          x-apifox-mock: "@integer(1, 9999)"
        name:
          type: string
          x-apifox-mock: "@cname"
        email:
          type: string
          x-apifox-mock: "@email"
        status:
          type: string
          enum: [active, inactive]
          x-apifox-mock: "@pick(active, inactive)"
        createdAt:
          type: string
          format: date-time
          x-apifox-mock: "@datetime(\"yyyy-MM-dd HH:mm:ss\")"
```

## 注意事项

- `x-apifox-mock` 必须添加到 schema 的**属性级别**，不是顶层
- 对于 `allOf`、`oneOf`、`anyOf` 组合 schema，递归到每个子 schema 属性中添加
- 数组类型 (`type: array`)，在 `items` 的属性中添加
- 枚举字段优先使用 `@pick(val1, val2, ...)` 从实际枚举值中随机选择
- 嵌套对象需要递归处理每一层属性
- 转换后的 YAML 文件应保持 OpenAPI 3.2 规范
