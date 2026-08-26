# Pinia 状态管理详解

## 目录结构

```
src/stores/
├── index.ts                    # Pinia 实例创建 + 持久化插件注册
├── interface/
│   └── index.ts               # 统一类型定义
├── config/
│   └── persist.ts             # 持久化配置工具函数
└── modules/
    ├── user.ts                # 用户信息 store
    ├── auth.ts                # 权限路由 store
    ├── page.ts                # 页面状态 store
    └── keepAlive.ts           # KeepAlive 缓存管理
```

## 1. Pinia 实例创建（index.ts）

```ts
// src/stores/index.ts
import { createPinia } from 'pinia';
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate';

const pinia = createPinia();
pinia.use(piniaPluginPersistedstate);

export default pinia;
```

在 `main.ts` 中注册：

```ts
import pinia from '@/stores';
app.use(pinia);
```

## 2. Options Store 模式

项目使用 **Options Store**（`state` / `getters` / `actions`），而非 Setup Store。

```ts
import { defineStore } from 'pinia';
import type { UserInfo } from '@/stores/interface';

export const useUserStore = defineStore('store_name', {
  // state: 初始状态，必须用函数返回
  state: (): UserInfo => ({
    token: '',
    timestamp: 0,
    info: {
      name: '',
      displayName: '游客',
      roles: [],
      profilePicture: ''
    }
  }),

  // getters: 派生状态，可访问 this
  getters: {
    tokenUserInfo: state => state.info
  },

  // actions: 支持同步和异步，可访问 this
  actions: {
    setToken(token: string, timestamp?: number) {
      this.token = token;
      this.timestamp = timestamp ? timestamp : Date.now();
    },
    async clear() {
      this.token = undefined;
      this.timestamp = undefined;
      this.info = undefined;
    }
  }
});
```

**关键规则**：
- `state` 必须用箭头函数返回，不能用对象字面量直接赋值
- `getters` 参数 `state` 指向当前 store，也可用 `this`
- `actions` 中修改状态直接通过 `this.xxx`，**不需要 `.value`**
- 暴露的内容通过 return（Setup Store）或自动暴露（Options Store）

## 3. 类型定义（interface/index.ts）

所有 store 的类型集中定义在 `src/stores/interface/index.ts`：

```ts
// 用户信息
export interface UserInfo {
  token?: string;
  timestamp?: number;
  info?: {
    name: string;
    displayName: string;
    roles: number[];
    profilePicture: string;
  };
}

// 权限状态
export interface AuthState {
  roleCode: string;
  authRouterList: RouteRecordRaw[];
}

// 页面状态
export interface PageState {
  layout: LayoutType;
  assemblySize: AssemblySizeType;
  language: LanguageType;
  maximize: boolean;
  primary: string;
  isDark: boolean;
  isGrey: boolean;
  isWeak: boolean;
  asideInverted: boolean;
  headerInverted: boolean;
  isCollapse: boolean;
  accordion: boolean;
  breadcrumb: boolean;
  breadcrumbIcon: boolean;
  tabs: boolean;
  tabsIcon: boolean;
  footer: boolean;
}

// KeepAlive 状态
export interface KeepAliveState {
  keepAliveName: string[];
}
```

新增 store 时，先在 `interface/index.ts` 中定义状态类型，再在 `modules/` 下创建 store 文件引用该类型。

## 4. 持久化配置（config/persist.ts）

通过 `pinia-plugin-persistedstate` 插件 + 自定义配置函数实现持久化：

```ts
// src/stores/config/persist.ts
const piniaPersistConfig = (key: string, paths?: string[]) => {
  return {
    key: key,
    storage: localStorage,
    pick: paths,  // 可选：只持久化指定字段
    debug: true
  };
};

export default piniaPersistConfig;
```

在 store 中使用：

```ts
import piniaPersistConfig from '@/stores/config/persist';

export const useUserStore = defineStore('user_info_store', {
  state: () => ({ ... }),
  getters: { ... },
  actions: { ... },
  persist: piniaPersistConfig('login_user_info')  // 整个 store 持久化
  // 或只持久化特定字段:
  // persist: piniaPersistConfig('login_user_info', ['token', 'timestamp'])
});
```

## 5. 用户信息 store 示例（modules/user.ts）

存储 token、用户信息和角色，支持登录/登出场景：

```ts
// src/stores/modules/user.ts
import { defineStore } from 'pinia';
import { UserInfo } from '@/stores/interface';
import piniaPersistConfig from '@/stores/config/persist';

export const useUserStore = defineStore('user_info_store', {
  state: (): UserInfo => ({
    token: '',
    timestamp: 0,
    info: {
      name: '',
      displayName: '游客',
      roles: [],
      profilePicture: ''
    }
  }),
  getters: {
    tokenUserInfo: state => state.info
  },
  actions: {
    setToken(token: string, timestamp?: number) {
      this.token = token;
      this.timestamp = timestamp ? timestamp : Date.now();
    },
    setUserInfo(info: UserInfo['info']) {
      this.info = info;
    },
    async clear() {
      this.token = undefined;
      this.timestamp = undefined;
      this.info = undefined;
    }
  },
  persist: piniaPersistConfig('login_user_info')
});
```

## 6. 权限 store 示例（modules/auth.ts）

管理动态路由列表和角色编码，在路由守卫中调用：

```ts
// src/stores/modules/auth.ts
import { defineStore } from 'pinia';
import { RouteRecordRaw } from 'vue-router';
import { AuthState } from '@/stores/interface';
import { getAppRouters } from '@/api/auth';
import piniaPersistConfig from '@/stores/config/persist.ts';

export const useAuthStore = defineStore('leaf-vein-auth', {
  state: (): AuthState => ({
    roleCode: '',
    authRouterList: []
  }),
  getters: {
    routerListGet: (state: AuthState) => state.authRouterList
  },
  actions: {
    async getRouterList(appId: number) {
      const { data } = await getAppRouters(appId);
      this.authRouterList = getFlatMenuList(data);
    },
    async setRoleCode(code: string) {
      this.roleCode = code;
    },
    async clear() {
      this.roleCode = '';
      this.authRouterList = [];
    }
  },
  persist: piniaPersistConfig('auth_router_info')
});

// 扁平化菜单工具函数
function getFlatMenuList(routeList: RouteRecordRaw[]): RouteRecordRaw[] {
  return routeList.flatMap(item => {
    const children = item.children || [];
    item.children = [];
    return [item, ...(children.length ? getFlatMenuList(children) : [])];
  });
}
```

## 7. Store 间通信

Store 可以直接导入并调用其他 store 的实例：

```ts
// 在 auth store 中调用 user store
import { useUserStore } from './user';

export const useAuthStore = defineStore('auth', {
  actions: {
    async login(token: string) {
      const userStore = useUserStore();
      userStore.setToken(token);
      // ...
    }
  }
});
```

## 8. 命名规范

| 项目 | 约定 | 示例 |
|------|------|------|
| Store 文件名 | camelCase.ts | `user.ts`、`auth.ts` |
| Store 导出函数 | use + PascalCase + Store | `useUserStore`、`useAuthStore` |
| Store id | kebab-case，可带前缀 | `'user_info_store'`、`'leaf-vein-auth'` |
| 持久化 key | snake_case | `'login_user_info'`、`'auth_router_info'` |
| 类型定义 | PascalCase，后缀 State | `UserInfo`、`AuthState`、`PageState` |

Pinia 代码示例见 [vue-state-management-examples](vue-state-management-examples.md)。
