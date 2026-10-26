# 用户中心 API 需求文档

## 1. 概述

本文档描述用户中心模块的 API 需求，包含用户管理、地址管理、收藏夹三个子模块。

## 2. 用户管理

### 2.1 注册

- **方法**: POST
- **路径**: /api/v2/users/register
- **请求体**:
  - `username` (string, 必填): 用户名，4-20 字符
  - `password` (string, 必填): 密码，最少 8 字符
  - `email` (string, 必填): 邮箱地址
  - `phone` (string, 可选): 手机号
- **响应**: 201 Created，返回用户信息（不含密码）

### 2.2 登录

- **方法**: POST
- **路径**: /api/v2/users/login
- **请求体**:
  - `username` (string, 必填)
  - `password` (string, 必填)
- **响应**: 200 OK，返回 token 和用户信息

### 2.3 获取个人信息

- **方法**: GET
- **路径**: /api/v2/users/profile
- **认证**: 需要 Bearer Token
- **响应**: 200 OK，返回用户完整信息

### 2.4 更新个人信息

- **方法**: PUT
- **路径**: /api/v2/users/profile
- **认证**: 需要 Bearer Token
- **请求体**: nickname, avatar, phone, bio（均为可选）
- **响应**: 200 OK，返回更新后的用户信息

## 3. 地址管理

### 3.1 地址列表

- **方法**: GET
- **路径**: /api/v2/addresses
- **认证**: 需要 Bearer Token
- **响应**: 200 OK，返回地址列表

### 3.2 新增地址

- **方法**: POST
- **路径**: /api/v2/addresses
- **认证**: 需要 Bearer Token
- **请求体**:
  - `recipient` (string, 必填): 收货人
  - `phone` (string, 必填): 联系电话
  - `province` (string, 必填): 省份
  - `city` (string, 必填): 城市
  - `district` (string, 必填): 区县
  - `detail` (string, 必填): 详细地址
  - `isDefault` (boolean, 可选): 是否默认地址
- **响应**: 201 Created

### 3.3 删除地址

- **方法**: DELETE
- **路径**: /api/v2/addresses/{id}
- **认证**: 需要 Bearer Token
- **响应**: 204 No Content

## 4. 收藏夹

### 4.1 收藏列表

- **方法**: GET
- **路径**: /api/v2/favorites
- **认证**: 需要 Bearer Token
- **查询参数**: page, pageSize
- **响应**: 200 OK，返回收藏的商品列表

### 4.2 添加收藏

- **方法**: POST
- **路径**: /api/v2/favorites
- **认证**: 需要 Bearer Token
- **请求体**:
  - `productId` (integer, 必填): 商品 ID
- **响应**: 201 Created

### 4.3 取消收藏

- **方法**: DELETE
- **路径**: /api/v2/favorites/{id}
- **认证**: 需要 Bearer Token
- **响应**: 204 No Content
