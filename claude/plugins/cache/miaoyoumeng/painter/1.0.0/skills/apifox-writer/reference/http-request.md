## 请求方法（method)

| 方法 | 幂等 | 安全 | Purpose 
|--------|-----------|------|---------|
| GET | 是 | 是 | 检索资源 | 
| POST | 否 | 是 | 创建资源 | 
| DELETE | 是 | 是 | 删除资源 |
| PUT | 是 | 是 | 替换资源 | 
| PATCH | 否 | 是 | 部分更新资源 | 

## 请求资源命名（URI）

- 命名规则：先资源，再动作。
- 用`英文单词`和`数字`命名，必须小写，用"中划线"连接。

### 资源建模

**识别资源：**
1. 列出主要实体（用户、产品、订单）
2. 识别关系（用户拥有订单，订单包含商品）
3. 确定层级关系（帖子有评论）

**设计 URL 结构：**

```
正确：GET /users/list
正确：GET /users/info
正确：GET /user-info
正确：GET /user-list
正确：POST /users/create
正确：PUT /users/{id}
正确：/resources/{id}
正确：/resources/{id}/sub-resources

错误：GET /getUsers
错误：GET /listUsers
错误：POST /createUser
```

## 请求参数（query）

- 用`英文单词`和`数字`命名，优先使用驼峰格式，其次用"下划线"连接。


**筛选：**
```text
GET /api/products?category=electronics&priceMin=100
```

**排序：**
```text
GET /products?sort=price&order=desc
GET /api/products?sort=-price,name 
```

**分页：**
```
GET /api/products?pageNo=2&pageSize=20 
GET /api/products?start=2&limit=20
```

**字段选择**
```
GET /api/products?fields=id,name,price
```

**搜索：**
```
GET /products?q=laptop
```

## 请求体（body）

- 请求body参数，优先使用驼峰格式，其次用"下划线"连接。

```
POST /users/bulk
Content-Type: application/json

{
  "users": [
    { "name": "User 1" },
    { "name": "User 2" }
  ]
}
```

**批量更新：**
```
PATCH /users/bulk
Content-Type: application/json

{
  "updates": [
    { "id": 1, "status": "active" },
    { "id": 2, "status": "inactive" }
  ]
}
```

**PUT — 替换资源：**
```
PUT /users/{id}
Content-Type: application/json

{
  "name": "John Smith",
  "email": "john.smith@example.com"
}
```

### 文件上传

**单文件上传：**
```
POST /files
Content-Type: multipart/form-data

file: [binary data]
```

**带元数据：**
```
POST /documents
Content-Type: multipart/form-data

file: [binary data]
title: "Document Title"
category: "reports"
```


## 请求参数（header）

#### 速率限制

**包含响应头：**
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1640995200
```
