# Vue + TypeScript 示例

## 定义数据模型

文件路径：`src/views/user/components/types/models.ts`

使用 `declare namespace` 定义业务数据结构，避免使用 `any`，为每个字段提供明确的类型。

```ts
declare namespace UserModel {
  /** 用户状态枚举 */
  type UserStatus = 0 | 1

  /** 用户基本信息 */
  interface IUserItem {
    id: number
    username: string
    email: string
    phone: string
    status: UserStatus
    role: string
    createTime: string
    updateTime: string
  }

  /** 搜索表单参数 */
  interface IUserSearchParams {
    keyword: string
    status: UserStatus | undefined
    page: number
    pageSize: number
  }

  /** API 响应包裹结构 */
  interface IApiResponse<T = unknown> {
    code: number
    displayMsg: string
    data: T
    uniqCode: string
    msg: string
  }

  /** 分页列表响应 */
  interface IPaginatedData<T = unknown> {
    list: T[]
    total: number
  }

  /** 用户列表 API 响应类型 */
  type IUserListResponse = IApiResponse<IPaginatedData<IUserItem>>

  /** 删除用户 API 响应类型 */
  type IDeleteUserResponse = IApiResponse<boolean>
}

export type {
  UserModel,
}
```

### 要点
- 使用 `declare namespace` 将相关类型组织在同一命名空间下
- 为枚举值创建字面量联合类型（如 `UserStatus`）
- 定义通用的 `IApiResponse<T>` 包裹类型，适配项目 API 规范
- 泛型 `IPaginatedData<T>` 可复用于其他列表接口

---

## 业务逻辑封装与数据调用（步骤 3.4）

文件路径：`src/views/user/components/types/useUserLogic.ts`

使用箭头函数声明业务逻辑函数，通过 import JSON 返回 mock 数据。

```ts
import mockUserList from '@/assets/mocks/user-list.json'
import type { UserModel } from './models'

/**
 * 获取用户状态选项（用于下拉框）
 */
export const getUserStatusOptions = (): { label: string; value: UserModel.UserStatus }[] => [
  { label: '启用', value: 1 },
  { label: '禁用', value: 0 },
]

/**
 * 获取用户列表（mock）
 */
export const fetchUserList = async (
  params: UserModel.IUserSearchParams,
): Promise<Model.IUserListResponse> => {
  // 模拟异步请求
  return new Promise((resolve) => {
    setTimeout(() => {
      const { keyword, status, page, pageSize } = params
      let filtered = [...(mockUserList as UserModel.IUserItem[])]

      // 关键词过滤
      if (keyword) {
        filtered = filtered.filter((u) =>
          u.username.includes(keyword) || u.email.includes(keyword),
        )
      }

      // 状态过滤
      if (status !== undefined) {
        filtered = filtered.filter((u) => u.status === status)
      }

      const total = filtered.length
      const start = (page - 1) * pageSize
      const list = filtered.slice(start, start + pageSize)

      resolve({
        code: 0,
        displayMsg: 'success',
        data: { list, total },
        uniqCode: 'fetchUserList',
        msg: 'ok',
      })
    }, 300)
  })
}

/**
 * 删除用户（mock）
 */
export const deleteUser = async (id: number): Promise<Model.IDeleteUserResponse> => {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({
        code: 0,
        displayMsg: '删除成功',
        data: true,
        uniqCode: 'deleteUser',
        msg: 'ok',
      })
    }, 200)
  })
}
```

### 要点
- 使用箭头函数（Arrow Function）声明所有业务函数
- 函数返回值使用明确的 Promise 泛型类型，不使用 `any`
- Mock 数据通过 `import JSON` 方式引入，不硬编码在函数体内
- 搜索/过滤逻辑在 mock 层模拟，后续替换真实 API 时只需修改函数体
- 每个函数独立导出，方便单独测试
