# API 请求层设计

本项目使用基于 axios 的 `RequestHttp` 类封装请求层，统一管理拦截器、错误处理和类型定义。

## 目录结构

```
src/request/
├── index.ts      # 创建并导出 http 实例
├── request.ts    # RequestHttp 类（核心封装）
└── modules.ts    # 类型定义（Result、ResultData、ResPage 等）
```

## 1. 类型定义（modules.ts）

所有 API 请求和响应必须使用统一的类型：

```ts
// src/request/modules.ts

// 请求响应参数（不包含 data）
export interface Result {
  code: string;
  msg: string;
}

// 请求响应参数（包含 data）
export interface ResultData<T = any> extends Result {
  data: T;
}

// 分页响应参数
export interface ResPage<T> {
  list: T[];
  pageNum: number;
  pageSize: number;
  total: number;
}

// 分页请求参数
export interface ReqPage {
  pageNum: number;
  pageSize: number;
}
```

## 2. RequestHttp 核心封装（request.ts）

`RequestHttp` 类基于 axios 创建实例，封装请求/响应拦截器和 HTTP 方法。

### 请求拦截器

```ts
this.instance.interceptors.request.use(
  config => {
    config.headers['Content-Type'] = ContentTypeEnum.JSON;
    const userStore = useUserStore();
    if (userStore && userStore.token) {
      config.headers.Authorization = userStore.token;
    }
    return config;
  },
  error => {
    this.showErrorMessage(error);
    return Promise.reject(new Error(error || 'Error'));
  }
);
```

- 自动设置 `Content-Type` 为 `application/json;charset=UTF-8`
- 从 Pinia `useUserStore()` 获取 token，设置 `Authorization` 请求头

### 响应拦截器

```ts
this.instance.interceptors.response.use(
  res => {
    const data = res.data;
    const code = data.code;
    return new Promise((resolve, reject) => {
      if (code === ResultCodeEnum.SUCCESS) {
        resolve(data);
      } else if (code >= 1000 && code <= 2000) {
        this.showWarningMessage(data.msg);
        resolve(data);
      } else if (code === ResultCodeEnum.UNAUTHORIZED) {
        clearLoginStores();
        router.push({ path: TO_LOGIN_URL });
      } else if (code === ResultCodeEnum.FORBIDDEN) {
        this.showWarningMessage('权限访问拒绝');
      } else {
        this.showErrorMessage(data.msg);
        reject(new Error(data.msg || 'Error'));
      }
    });
  },
  error => { /* 网络错误处理 */ }
);
```

**状态码处理规则**：

| 状态码 | 行为 | 说明 |
|--------|------|------|
| `200` | resolve(data) | 请求成功 |
| `401` | 清除登录信息 + 跳转登录页 | 未授权 |
| `403` | 警告提示 | 权限拒绝 |
| `500` | reject(error) | 服务器错误 |
| `1000-2000` | resolve(data) + 警告提示 | 业务警告码 |

### HTTP 方法

```ts
get<T>(url: string, params?: object, _object = {}): Promise<ResultData<T>>
post<T>(url: string, params?: object, _object = {}): Promise<ResultData<T>>
put<T>(url: string, params?: object, _object = {}): Promise<ResultData<T>>
delete<T>(url: string, params?: object, _object = {}): Promise<ResultData<T>>
download(url: string, params?: object, _object = {}): Promise<BlobPart>
```

### ContentTypeEnum

```ts
export enum ContentTypeEnum {
  JSON = 'application/json;charset=UTF-8',
  TEXT = 'text/plain;charset=UTF-8',
  FORM_URLENCODED = 'application/x-www-form-urlencoded;charset=UTF-8',
  FORM_DATA = 'multipart/form-data;charset=UTF-8'
}
```

## 3. http 实例创建（index.ts）

```ts
// src/request/index.ts
import RequestHttp from './request';
import { ContentTypeEnum } from './request';

const http = new RequestHttp({
  baseURL: import.meta.env.VITE_API_URL as string,
  timeout: 5000,
  headers: { 'Content-Type': ContentTypeEnum.JSON }
});

export default http;
```

## 4. API 模块化定义

在 `src/api/` 下按业务模块拆分：

```
src/api/
├── modules/              # 数据结构定义
│   ├── user.ts          # user 模块的数据结构
│   └── order.ts         # order 模块的数据结构
├── user.ts              # user 模块的 API 调用函数
├── order.ts             # order 模块的 API 调用函数
└── index.ts             # 统一导出
```

### 数据结构（src/api/modules/<模块名>.ts）

```ts
// src/api/modules/user.ts
export interface UserInfo {
  id: number;
  name: string;
  avatar: string;
}
```

### API 调用函数（src/api/<模块名>.ts）

**开发阶段使用 mock 数据**：

```ts
// src/api/user.ts
import mockData from '@/assets/jsons/userList.json';

export const getUserListApi = (params: ReqPage) => {
  // todo 后期改为使用 HTTP 请求获取 JSON 数据
  console.log(params);
  return mockData;
};
```

**后端就绪后改为真实请求**：

```ts
// src/api/user.ts
import http from '@/request';
import type { UserInfo, ReqPage, ResultData, ResPage } from '@/request/modules';

export const getUserListApi = (params: ReqPage) => {
  return http.get<ResultData<ResPage<UserInfo>>>('/api/user/list', params);
};
```

## 5. 错误处理流程

- **响应拦截器统一处理错误码**：401 自动跳转登录、403 提示权限拒绝、500 提示服务器错误
- **MessagePlugin 统一提示**：警告使用 `MessagePlugin.warning()`，错误使用 `MessagePlugin.error()`
- **组件层只需 catch**：拦截器已处理的状态码不会抛到组件，只需 catch 网络错误

## 6. Store 中调用 API

```ts
// src/stores/modules/user.ts
import { defineStore } from 'pinia';
import { getUserListApi } from '@/api/user';
import type { ReqPage } from '@/request/modules';

export const useUserStore = defineStore('user', () => {
  async function fetchUserList(params: ReqPage) {
    const res = await getUserListApi(params);  // 开发阶段返回 src/assets/jsons/ 中的静态 JSON
    return res.data;
  }

  return { fetchUserList };
});
```
