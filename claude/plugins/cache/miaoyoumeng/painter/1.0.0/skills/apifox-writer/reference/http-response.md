## 返回状态码

**说明**


| 状态码 | 含义 | 用途 |
|------|---------|---------|
| 200 | OK |  GET, PATCH, PUT 成功|
| 201 | Created | 创建成功 |
| 202 | Accepted | 异步处理已接受 |
| 204 | No Content | 删除成功 |
| 206 | Partial Content | 成功处理了部分请求 |
| 301 | Moved Permanently | 资源已永久移动 |
| 302 | moved temporarily | 资源临时移动 |
| 304 | Not Modified | 缓存有效，请使用本地副本 |
| 307 | Temporary Redirect | 临时重定向 |
| 400 | Bad Request | 参数验证错误 |
| 401 | Unauthorized | 缺少身份验证 |
| 403 | Forbidden | 权限不足 |
| 404 | Not Found | 资源不存在 |
| 409 | Conflict | 违反约束或冲突 |
| 422 | Unprocessable Entity | 验证失败（语义错误） |
| 429 | Too Many Requests | 限流 |
| 500 | Internal Server Error | 服务器内部错误 |
| 502 | Bad Gateway | 服务器暂时关闭 |
| 503 | Service Unavailable | 限流 |
| 504 | Gateway Timeout | 服务超时 |


**业务逻辑错误：**

- code（状态码） 范围：10000 <= ${code} <= 65535 


## 数据响应返回格式

**一、成功请求返回格式说明**

```text
{
  "code": 200,                 # 状态码，参见后续说明
  "data": {},                   # 响应数据
  "msg": "success",            # "success" 或者 "failure"
  "uniqCode": "SUCCESS_CODE",   # 全局唯一业务编码
  "displayMsg": "操作成功"       # 提示给用户展示的文案 
}
```

**二、错误请求返回格式说明**

**2.1. 普通错误响应：**

```json
{
  "code": 500,
  "data": {},
  "msg": "error",
  "uniqCode": "VALIDATION_ERROR",
  "displayMsg": "Invalid email format"
}
```


**2.2. 超限响应：**

```json

{
  "code": 500,
  "data": {},
  "msg": "failure",
  "uniqCode": "RATE_LIMIT_EXCEEDED",
  "displayMsg": "Too many requests"
}
```

**三、分页数据响应数据：**

- 响应数据使用驼峰，命名属性
- 分页请求响应数据返回结构统一包含 `total`、`list`、`pageNo`、 `pageSize`。

```json
{
  "code": 200,
  "data": {
    "list": [
      {
        "namespace": "县候把广任",
        "description": "adsfadsfasdf",
        "createTime": "1992-10-09 02:23:41"
      }
    ],
    "pageNo": 3,
    "total": 86,
    "pageSize": 10
  },
  "msg": "success",
  "uniqCode": "SUCCESS_CODE",
  "displayMsg": "操作成功"
}
```

