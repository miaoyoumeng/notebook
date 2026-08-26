# API 统一返回结构

所有接口遵循统一的 JSON 响应结构，根据 data 的类型分为以下四种场景：

**返回单个对象**：
```json
{
   "code": 200,
   "data": { "id": 1, "name": "示例" },
   "displayMsg": "操作成功",
   "uniqCode": "SUCCESS",
   "msg": "success"
}
```

**返回数组**：
```json
{
   "code": 200,
   "data": [
       { "id": 1, "name": "示例1" },
       { "id": 2, "name": "示例2" }
   ],
   "displayMsg": "操作成功",
   "uniqCode": "SUCCESS",
   "msg": "success"
}
```

**返回分页数据结构**：
```json
{
   "code": 200,
   "data": {
       "list": [{ "id": 1, "name": "示例1" }],
       "pageNo": 1,
       "total": 81,
       "pageSize": 10
   },
   "displayMsg": "操作成功",
   "uniqCode": "SUCCESS",
   "msg": "success"
}
```

**错误返回格式**（失败时返回）：
```json
{ "code": 400, "displayMsg": "参数错误", "uniqCode": "PARAM_ERROR", "msg": "Invalid parameter" }
```

**字段说明**：

| 字段 | 类型 | 说明 |
|------|------|------|
| `code` | int | 业务码值 |
| `data` | object/array/null | 业务数据，成功时返回数据，失败时为 null |
| `displayMsg` | string | 中文提示，直接展示给用户 |
| `uniqCode` | string | 系统全局唯一字母数字错误码 |
| `msg` | string | 英文错误提示 |
