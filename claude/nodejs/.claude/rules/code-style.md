# 编码风格规范

---

### 1. 代码风格

###### 命名规范
- 尽量用业务对应的英文单词命名，**禁止中文拼音**
- 文件/文件夹：使用小写单词命名，可以用 `-` 连接。例如： `kebab-case`、`user-profile.ts`, `components/user-card.vue`
- 类/组件名：使用首字母大写的单词命名。 例如 `PascalCase`， `UserCard.vue`。
- 变量/函数：必须使用小驼峰命名。例如 `camelCase`
- 常量/枚举：必须使用英文大写字母和 `_` 命名。例如 `UPPER_SNAKE_CASE`
- Vue 组件文件名必须与内部 `name` 属性（如果显式定义）和 PascalCase 引用保持一致
- 如果命名太长，则可以稍微简化，比如可以用` attr `代表` attribute `

###### 安全优先
- **严禁使用 `any`**。如果必须处理未知类型，请使用 `unknown` 并进行类型收窄 (Type Narrowing)
- 始终使用 ES Modules (`import`/`export`)，禁止使用 CommonJS (`require`/`module.exports`)，除非在特定的 Node.js 遗留脚本中

###### 注释
- 函数：函数命名尽量用业务英文单词命名，但是函数所有参数必须包含中文注释。
- 类型：所有变量必须班号中文注释。

---

### 2. 不可变性（关键）

**始终创建新对象，绝不要修改已有对象**:

```
// 伪代码
错误：modify(original, field, value) → 直接修改原对象
正确：update(original, field, value) → 返回包含修改的新对象副本
```

**原因**: 不可变数据可以防止隐藏的副作用，使调试更容易，并支持安全的并发。

---

### 3. 编码规范

#### 3.1 Vue 组件

###### 3.1.1 文件结构

- 在 `.vue` 文件中，标签顺序必须为：`<script>` > `<template>` > `<style>`。

###### 3.1.2 组件通信

- **Props**: 必须使用 `defineProps<{ ... }>()` 泛型进行类型定义。
- **Emits**: 必须使用 `defineEmits<{ (e: 'eventName', payload: Type): void }>()` 定义事件类型。
- **双向绑定**: 优先使用 `defineModel()` (Vue 3.4+) 实现 `v-model`。

###### 3.1.3 模板语法

- **列表渲染**: 始终为 `v-for` 添加唯一的 `:key` (避免使用 index，除非列表是静态且不可排序的)。
- **自闭合标签**: 对没有子元素的组件使用自闭合标签 (e.g., `<MyComponent />`)。
- **属性顺序**: 建议遵循 `v-if` > `v-for` > `:key` > `:id` > `:class` > `:style` > `@click` 等事件 > 其他属性 的顺序。

#### 3.2 TypeScript

- **函数定义**: 优先使用函数表达式 (`const myFunc = () => {}`)。
- **非空断言**: 尽量避免使用 `!`。如果确定值存在，请先进行条件检查或使用可选链 `?.`。
- **枚举**: 避免使用常规 `enum`，推荐使用联合字面量类型 (e.g., `type Status = 'active' | 'inactive'`)。
- **响应式系统**:
    - 原始值 (string, number, boolean) 使用 `ref()`。
    - 对象/数组 使用 `reactive()`，但在需要解构或替换整个对象时，为保持一致性优先使用 `ref()`。
    - 在 TypeScript 中访问 `ref` 的值必须使用 `.value`。

#### 3.3 安全与校验

- **输入校验**: 永远不信任外部数据。在系统边界（如 API 响应、用户输入）使用 Zod 或 Joi 进行 Schema 校验，确保快速失败并返回清晰的报错信息。
- **环境变量**: 使用 `process.env` 访问环境变量，并在应用启动时验证必要的环境变量是否存在。

### 4. 异步与错误处理

- **异步处理**: 优先使用 `async/await` 语法，避免回调地狱。
- **错误处理**:
    - **分层处理**: 在每一层（如 Composables, API 调用）显式处理错误，禁止吞没错误。
    - **信息反馈**: 服务端记录详细上下文，UI 端展示用户友好的提示。
    - **组合式函数**: 在 `async` 组合式函数中，需妥善处理 `loading` 和 `error` 状态。
- **日志**: 使用结构化日志库（如 `pino` 或 `winston`），避免在生产环境代码中直接使用 `console.log`。

### 5. 禁止事项

- **禁止** 使用 `var` 声明变量。
- **禁止** 在客户端组件中直接调用数据库。
- **禁止** 在没有迁移计划的情况下修改现有架构。
- **禁止** 硬编码字符串拼接文件路径，应使用 `path` 模块或 `node:url` (`fileURLToPath`)。

### 6. 常用命令

在每次内容修改后，都需要执行以下命令以检查代码质量：

```shell
pnpm run lint:eslint && pnpm run build
```


