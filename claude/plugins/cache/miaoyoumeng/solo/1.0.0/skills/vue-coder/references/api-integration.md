# API 请求层集成指南

本项目使用基于 axios 的 `RequestHttp` 类封装请求层，统一管理拦截器、错误处理和类型定义。

## 目录结构

```
src/request/
├── index.ts      # 创建并导出 http 实例
├── request.ts    # RequestHttp 类（核心封装）
└── modules.ts    # 类型定义（Result、ResultData、ResPage 等）

src/api/
├── modules/              # 数据结构定义
│   └── <模块名>.ts      # 各模块数据类型
├── <模块名>.ts           # API 调用函数
└── index.ts              # 统一导出
```

## 1. 类型定义（modules.ts）

```ts
// src/request/modules.ts

export interface Result {
  code: string;
  msg: string;
}

export interface ResultData<T = unknown> extends Result {
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

### ContentTypeEnum

```ts
export enum ContentTypeEnum {
  JSON = 'application/json;charset=UTF-8',
  TEXT = 'text/plain;charset=UTF-8',
  FORM_URLENCODED = 'application/x-www-form-urlencoded;charset=UTF-8',
  FORM_DATA = 'multipart/form-data;charset=UTF-8'
}
```

### 请求拦截器

```ts
this.instance.interceptors.request.use(
  config => {
    config.headers['Content-Type'] = ContentTypeEnum.JSON;
    const userStore = useUserStore();
    if (userStore?.token) {
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

| 状态码 | 行为 | 说明 |
|--------|------|------|
| `200` | resolve(data) | 请求成功 |
| `401` | 清除登录信息 + 跳转登录页 | 未授权 |
| `403` | 警告提示 | 权限拒绝 |
| `500` | reject(error) | 服务器错误 |
| `1000-2000` | resolve(data) + 警告 | 业务警告码 |

### HTTP 方法

```ts
get<T>(url: string, params?: object): Promise<ResultData<T>>
post<T>(url: string, params?: object): Promise<ResultData<T>>
put<T>(url: string, params?: object): Promise<ResultData<T>>
delete<T>(url: string, params?: object): Promise<ResultData<T>>
download(url: string, params?: object): Promise<BlobPart>
```

## 3. http 实例创建（index.ts）

```ts
// src/request/index.ts
import RequestHttp from './request';

const http = new RequestHttp({
  baseURL: import.meta.env.VITE_API_URL as string,
  timeout: 5000,
  headers: { 'Content-Type': ContentTypeEnum.JSON }
});

export default http;
```

## 4. API 模块化定义

### 数据结构（src/api/modules/<模块名>.ts）

```ts
// src/api/modules/user.ts
export declare namespace User {
  interface UserInfo {
    id: number;
    name: string;
    avatar: string;
  }
}
```

### API 调用函数（src/api/<模块名>.ts）

**开发阶段（mock）**：

```ts
// src/api/user.ts
import { ResultData } from '@/request/modules';
import { User } from '@/api/modules/user';
import mockData from '@/assets/mocks/userList.json';

export const getUserListApi = (): Promise<ResultData<User.UserInfo[]>> => {
  // TODO 后期改为 HTTP 请求
  return Promise.resolve(mockData as unknown as ResultData<User.UserInfo[]>);
};
```

**后端就绪后**：

```ts
// src/api/user.ts
import http from '@/request';
import type { ResultData } from '@/request/modules';
import { User } from '@/api/models/user';

export const getUserListApi = () => {
  return http.get<ResultData<User.UserInfo[]>>('/api/user/list');
};
```

## 5. 页面中使用

```ts
import { getUserListApi } from '@/api/user';
import { User } from '@/api/modules/user';

const renderUsers = async () => {
  const { data } = await getUserListApi();
  if (data?.length) {
    users.value = data;
  }
};
```

## 6. Store 中调用 API

```ts
// src/stores/modules/user.ts
import { defineStore } from 'pinia';
import { getUserListApi } from '@/api/user';
import type { ReqPage } from '@/request/modules';

export const useUserStore = defineStore('user', () => {
  async function fetchUserList(params: ReqPage) {
    const res = await getUserListApi(params);
    return res.data;
  }
  return { fetchUserList };
});
```

## 7. 错误处理规范

- **响应拦截器统一处理错误码**：401 自动跳转登录、403 提示权限拒绝、500 提示服务器错误
- **MessagePlugin 统一提示**：警告用 `MessagePlugin.warning()`，错误用 `MessagePlugin.error()`
- **组件层只需 catch**：拦截器已处理的状态码不会抛到组件，只需 catch 网络错误
