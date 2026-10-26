---
name: tdesign-vue-next
description: "为 Vue 3 项目使用 TDesign 组件库（tdesign-vue-next 1.x）提供选型与实现指导：覆盖基础组件、表单、表格、选择器、上传、树、级联、弹窗抽屉、主题定制、暗黑模式与 AI Chat 组件。当用户要安装或配置 tdesign-vue-next、选择组件、编写页面/表单/表格、处理大数据量或远程数据、定制主题色或暗黑模式、接入 @tdesign-vue-next/chat 时使用；不适用于 tdesign-react、tdesign-miniprogram 或非 TDesign 的 UI 需求。"
---

# tdesign-vue-next

## 概述

TDesign Vue Next（包名 `tdesign-vue-next`，1.x）是腾讯开源的企业级 Vue 3 组件库，覆盖基础、布局、导航、输入、数据展示、反馈与 AI 对话七类组件，支持按需引入、CSS 变量主题与暗黑模式。本技能给出安装、组件选型、常用写法、复杂场景路由与验证方法。

## 上下文层级

1. 常驻上下文：frontmatter 中的 `name` 与 `description`。
2. 技能触发时加载：本文件，含安装、选型规则、决策链与验证清单。
3. 按需读取：`references/` 下的专题文档，提供复杂场景的完整写法。

组件属性、事件与类型以 `references/` 和官方文档为准。网页端属性不能套用到 `tdesign-react` 或 `tdesign-miniprogram`。

## 使用时机

以下场景使用本技能：

- 在 Vue 3 项目中安装、配置 `tdesign-vue-next`，选择全量或按需引入。
- 根据需求选择组件，确认属性、事件、插槽与类型。
- 编写表单、表格、选择器、上传、树、级联、弹窗与抽屉页面。
- 处理动态表单、服务端分页、虚拟滚动、异步加载等复杂场景。
- 定制主题色、暗黑模式或多品牌主题。
- 接入 AI 对话界面，使用 `@tdesign-vue-next/chat`。
- 排查样式不生效、类型报错、图标不显示、暗黑模式异常。

不适用于 `tdesign-react`、`tdesign-miniprogram`，也不适用于非 TDesign 的 UI 需求。

## 输入要求

开始实现前确认以下信息。用户未提供时按默认值处理，并在回答中说明假设：

| 信息 | 用途 | 默认值 |
| --- | --- | --- |
| Vue 版本 | 判断可用语法与 API | 3.3+ |
| 包管理器 | 安装与脚本命令 | pnpm |
| 构建工具 | 自动导入与样式配置 | Vite |
| 是否已有 `ConfigProvider` | 决定主题与国际化配置位置 | 无，新增 |
| 是否需要暗黑模式 | 决定 CSS 变量与 `theme-mode` | 否 |
| 是否需要国际化 | 决定 `ConfigProvider` 的 `i18n` | 否 |
| 数据量级 | 决定是否启用虚拟滚动 | 少于 1000 行 |
| 目标组件或页面 | 决定读取哪篇 references | 按需求判断 |

默认假设：TypeScript + `<script setup>`；主题通过 CSS 变量与 `ConfigProvider` 配置；根级只放一个 `ConfigProvider`；图标使用 `tdesign-icons-vue-next`；组件按需引入。

## 编码四原则

- 文档优先：属性与事件查 `references/` 或官方文档，不凭记忆补全。
- 组件优先：TDesign 已覆盖的结构直接使用组件，不手写等价实现。
- 变量优先：颜色、圆角、间距通过 CSS 变量或 `ConfigProvider` 定制，不覆盖组件内部类名。
- 类型优先：使用 `tdesign-vue-next` 导出的类型，不用 `@ts-ignore` 绕过检查。
- 如实反馈：发现文档与行为不一致时，明确告知用户并建议提交 Issue，不猜测属性或事件。

## 流程

### 1. 安装依赖

```bash
pnpm add tdesign-vue-next tdesign-icons-vue-next
```

AI 对话组件位于独立包，需要时再安装：

```bash
pnpm add @tdesign-vue-next/chat
```

### 2. 选择引入方式

全量引入：

```ts
// main.ts
import { createApp } from "vue";
import TDesign from "tdesign-vue-next";
import "tdesign-vue-next/es/style/index.css";
import App from "./App.vue";

createApp(App).use(TDesign).mount("#app");
```

按需引入（推荐）：

```ts
// main.ts
import { createApp } from "vue";
import { Button, Form, FormItem, Input } from "tdesign-vue-next";
import "tdesign-vue-next/es/style/index.css";
import App from "./App.vue";

const app = createApp(App);
app.use(Button).use(Form).use(FormItem).use(Input);
app.mount("#app");
```

两种方式选一种，不要混用。需要自动导入时使用 `unplugin-vue-components`：

```ts
// vite.config.ts
import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import Components from "unplugin-vue-components/vite";
import { TDesignResolver } from "unplugin-vue-components/resolvers";

export default defineConfig({
  plugins: [
    vue(),
    Components({
      resolvers: [TDesignResolver({ library: "vue-next" })],
    }),
  ],
});
```

### 3. 在根组件配置 ConfigProvider

```vue
<template>
  <ConfigProvider>
    <App />
  </ConfigProvider>
</template>

<script setup lang="ts">
import { ConfigProvider } from "tdesign-vue-next";
import App from "./App.vue";
</script>
```

需要统一类名前缀、层级或国际化时，传入 `global-config` 与 `i18n`。

### 4. 按场景选择组件

| 场景 | 推荐组件 | 说明 |
| --- | --- | --- |
| 简单列表展示 | `List` | 数据量小，无复杂交互 |
| 复杂数据表格 | `Table` | 支持排序、筛选、分页 |
| 大数据表格 | `Table` + 虚拟滚动 | 行数超过 1000 时启用 |
| 树形数据选择 | `TreeSelect` | 单选或多选树节点 |
| 多级联动选择 | `Cascader` | 省市区等层级数据 |
| 简单下拉 | `Select` | 选项数量适中 |
| 远程搜索 | `Select` + `filterable` | 关闭本地过滤 |
| 文件上传 | `Upload` | 支持拖拽与多文件 |
| 表单收集 | `Form` + `FormItem` | 统一校验与提交 |
| 轻量提示 | `Message` | 操作反馈，自动消失 |
| 重要通知 | `Notification` | 需要确认或包含操作 |
| 确认操作 | `Dialog` / `Popconfirm` | 按上下文选择 |
| 侧边详情 | `Drawer` | 不中断页面流程 |
| AI 对话 | `@tdesign-vue-next/chat` | 独立包，非主包组件 |

### 5. 表单决策链

```text
需要收集用户输入？
  ├── 是 → 使用 Form
  │     ├── 需要动态增删字段 → 读 references/form-advanced.md
  │     ├── 需要跨字段或异步校验 → 读 references/form-advanced.md
  │     └── 简单校验 → Form + FormItem + rules
  └── 否 → 直接使用输入组件
```

Form 的数据源是 `data`，不是 `model`：

```vue
<template>
  <ConfigProvider>
    <Form :data="formData" :rules="rules" @submit="onSubmit">
      <FormItem label="用户名" name="username">
        <Input v-model="formData.username" placeholder="请输入用户名" />
      </FormItem>
      <FormItem>
        <Button theme="primary" type="submit">提交</Button>
      </FormItem>
    </Form>
  </ConfigProvider>
</template>

<script setup lang="ts">
import { reactive } from "vue";
import { Button, ConfigProvider, Form, FormItem, Input } from "tdesign-vue-next";
import type { FormRules, SubmitContext } from "tdesign-vue-next";

const formData = reactive({ username: "" });

const rules: FormRules<typeof formData> = {
  username: [{ required: true, message: "请输入用户名" }],
};

const onSubmit = ({ validateResult }: SubmitContext) => {
  if (validateResult === true) {
    console.log("提交成功", formData);
  }
};
</script>
```

### 6. 表格决策链

```text
需要展示列表数据？
  ├── 行数超过 1000 → 启用虚拟滚动，读 references/table-advanced.md
  ├── 需要服务端分页、排序或筛选 → 读 references/table-advanced.md
  ├── 需要单元格编辑 → 读 references/table-advanced.md
  └── 简单表格 → Table + columns + data
```

Table 必须提供稳定唯一的 `row-key`，列配置用 `computed` 缓存。

### 7. 主题决策链

```text
需要定制主题？
  ├── 只改品牌色 → 覆盖 CSS 变量 --td-brand-color
  ├── 改多个 token → 读 references/theming-advanced.md
  ├── 需要暗黑模式 → 读 references/dark-mode.md
  └── 运行时切换主题 → 读 references/theming-advanced.md
```

### 8. 复杂场景路由

命中下表条件时，先告知用户这是复杂场景，再读取对应文档并按其中的模式实现。

| 触发条件 | 文档 |
| --- | --- |
| 动态表单、跨字段校验、异步校验 | `references/form-advanced.md` |
| 服务端分页/排序/筛选、虚拟滚动、可编辑表格、树形表格 | `references/table-advanced.md` |
| 固定列、可展开行、合并单元格 | `references/table-extra.md` |
| 远程搜索、大数据选项、分页加载、自定义选项 | `references/select-advanced.md` |
| 选择器分组选项、前缀图标 | `references/select-extra.md` |
| 受控文件列表、断点续传、自定义上传请求 | `references/upload-advanced.md` |
| 上传文件列表展示、取消上传、URL 与进度 | `references/upload-extra.md` |
| 异步节点加载、父子不关联、虚拟滚动 | `references/tree-advanced.md` |
| 节点增删改、单选树、实例状态读取 | `references/tree-extra.md` |
| 异步选项、动态选项、自定义面板 | `references/cascader-advanced.md` |
| 级联自定义触发器、路径读取、多选上限 | `references/cascader-extra.md` |
| 弹窗嵌套、命令式调用、关闭拦截 | `references/dialog-drawer-advanced.md` |
| 抽屉详情、全屏/拖拽、层级与更新 | `references/dialog-drawer-extra.md` |
| 深度主题定制、运行时主题切换 | `references/theming-advanced.md` |
| 暗黑模式切换、跟随系统、防闪烁 | `references/dark-mode.md` |
| AI 对话、流式响应、自定义消息 | `references/chat-advanced.md` |
| 1.x 版本差异、升级与排错 | `references/tdesign-v1.md` |

### 9. 输出规范

回答包含以下内容：

1. 组件名称与选型理由。
2. 必需的安装与样式引入。
3. 可直接运行的 `<script setup>` 示例。
4. 大数据量、频繁更新场景的性能提示。
5. 复杂场景对应的 `references/` 路径。
6. 相关组件官方文档链接。

不得输出未验证的属性、依赖内部实现的 hack、缺少 import 的片段，或其它 TDesign 技术栈的代码。

## 流程顺序的原因

流程顺序影响状态与样式，顺序错误会直接导致异常：

- 先安装依赖并引入样式，再注册组件。缺少样式文件时组件能渲染，但没有基础外观。
- 先确定全量或按需引入，再写页面。两种方式混用会导致重复注册与包体膨胀。
- 先配置 `ConfigProvider`，再渲染业务组件。主题、国际化与层级配置依赖根级上下文。
- 先设置 `row-key`，再启用行选择、展开或编辑。缺少稳定标识时这些功能无法定位行。
- 远程搜索先关闭本地过滤，再发请求。否则服务端结果会被本地再次过滤。
- 上传先使用 `v-model:files`，再处理成功回调。非受控模式下拿不到最新文件列表。

## 代码分析

### 组件层级

```text
需求
  ├── 基础展示 → Button / Link / Icon / Typography
  ├── 布局 → Layout / Grid / Space / Divider
  ├── 导航 → Menu / Tabs / Breadcrumb / Steps / Pagination
  ├── 数据输入 → Form / Input / Select / DatePicker / Upload / ...
  ├── 数据展示 → Table / List / Tree / Card / Descriptions / ...
  ├── 反馈 → Message / Notification / Dialog / Drawer / Loading
  └── AI 对话 → @tdesign-vue-next/chat
```

### 性能与可访问性

- 表单控件提供 `label`，校验信息与字段关联。
- 大数据列表启用虚拟滚动或分页，不同时加载全量数据。
- 模板中不写复杂计算，使用 `computed`。
- 列表渲染提供稳定 `key`，不使用数组下标。
- 图标按钮补充 `aria-label`，纯图标操作有可读名称。

## 限制

- 版本范围：`tdesign-vue-next` 1.x 与 Vue 3.3+。
- 技术栈：只覆盖网页端 Vue 3，不覆盖 `tdesign-react`、`tdesign-miniprogram`。
- API 范围：只使用官方文档与 `references/` 中出现的属性、事件与类型。
- AI 对话：Chat 组件来自 `@tdesign-vue-next/chat`，不在主包内。
- 交付边界：不生成完整业务系统，不替代路由、状态管理与接口设计。

## 验证清单

- `package.json` 中是 `tdesign-vue-next` 1.x，Vue 版本不低于 3.3。
- 已引入 `tdesign-vue-next/es/style/index.css`。
- 全量引入与按需引入只选一种。
- 根组件已包 `ConfigProvider`。
- Form 使用 `:data` 绑定数据，每个 `FormItem` 有唯一 `name`。
- Table 提供稳定唯一的 `row-key`，`columns` 使用 `computed`。
- Select 远程搜索设置 `filterable` 且 `:filter="() => true"`。
- Upload 使用 `v-model:files` 控制文件列表。
- Tree 的 `keys` 与数据结构一致，异步 `load` 返回 Promise。
- Dialog 与 Drawer 使用 `v-model:visible`。
- 暗黑模式通过 `<html theme-mode="dark">` 或根元素 `theme-mode` 属性切换。
- 图标从 `tdesign-icons-vue-next` 引入。
- TypeScript 无 `@ts-ignore`，事件回调参数类型与导出一致。
- `pnpm exec vue-tsc --noEmit` 与 `pnpm run build` 通过。

## 危险信号

- 使用 `:model` 绑定 Form 数据，导致校验与提交取不到值。
- Table 未设置 `row-key`，行选择或展开异常。
- Select 远程搜索未关闭本地过滤，搜索结果被二次过滤。
- Upload 未使用受控模式，却期望拿到文件列表。
- 直接覆盖组件内部类名或滥用 `!important`，升级后样式失效。
- 业务代码散落硬编码色值，切换暗黑模式后配色错误。
- 从 `tdesign-vue-next` 引入 Chat 组件，实际应安装 `@tdesign-vue-next/chat`。
- 使用 Vue 2 语法或 `tdesign-react`、`tdesign-miniprogram` 的属性名。
- 用 `@ts-ignore` 掩盖类型错误。
- 代码片段缺少 import、样式引入或关键配置。

## 理由辩解

- 「只用一个组件，全量引入更省事」：全量引入增加包体，按需引入只多一行注册。
- 「直接改组件内部类名最快」：升级后类名变化，覆盖全部失效；用 CSS 变量或 `ConfigProvider`。
- 「暗黑模式以后再适配」：硬编码色值分散后改造成本更高，从 CSS 变量起步。
- 「远程搜索让本地再过滤一次更准」：本地过滤会清空服务端返回结果，必须关闭。
- 「Chat 是主包组件」：AI 对话在 `@tdesign-vue-next/chat`，主包不导出。
- 「类型报错先 @ts-ignore 压住」：错误仍在运行时出现，应按官方类型修正。

## 验证

执行类型检查与构建：

```bash
pnpm exec vue-tsc --noEmit
pnpm run build
```

启动开发服务，逐项检查：

- 使用到的组件能正常渲染，控制台无未注册组件或样式告警。
- 表单校验、提交、重置符合预期。
- 表格分页、排序、筛选、行选择可用。
- 切换暗黑模式后，组件与自定义区域配色正确。
- 大表格滚动流畅，无重复请求。
- AI 对话发送、流式追加、停止生成可用。

## 实现检查表

- [ ] 依赖安装完成，样式文件已引入。
- [ ] 引入方式统一，未混用全量与按需。
- [ ] 根组件已配置 `ConfigProvider`。
- [ ] 表单、表格、选择器、上传、树的受控值正确。
- [ ] 主题与暗黑模式通过 CSS 变量实现。
- [ ] 图标库已安装并按需引入。
- [ ] 类型检查与构建通过。

## 参考资料

- `references/tdesign-v1.md`：1.x 版本范围、安装方式、升级步骤与常见排错。
- `references/form-advanced.md`：动态表单、跨字段校验、异步校验、分步表单。
- `references/table-advanced.md`：服务端分页排序筛选、虚拟滚动、可编辑表格、树形表格。
- `references/table-extra.md`：固定列与表头、可展开行、合并单元格、表格实例。
- `references/select-advanced.md`：远程搜索、分页加载、虚拟滚动、自定义选项。
- `references/select-extra.md`：分组选项、前缀图标、分组与搜索。
- `references/upload-advanced.md`：受控文件列表、自定义请求、上传前校验、分片上传。
- `references/upload-extra.md`：文件列表展示、取消上传、服务端 URL、数量与进度。
- `references/tree-advanced.md`：异步加载、父子不关联、虚拟滚动、拖拽与节点搜索。
- `references/tree-extra.md`：节点增删改、单选树、实例状态读取、滚动定位。
- `references/cascader-advanced.md`：异步加载、任意级别选择、多选、自定义面板。
- `references/cascader-extra.md`：自定义触发器、完整路径、多选上限、省市区联动。
- `references/dialog-drawer-advanced.md`：嵌套弹窗、命令式调用、关闭拦截、抽屉用法。
- `references/dialog-drawer-extra.md`：抽屉详情、全屏/拖拽、层级与命令式更新。
- `references/theming-advanced.md`：CSS 变量、品牌色、运行时主题、多品牌主题。
- `references/dark-mode.md`：暗黑模式切换、跟随系统、局部暗黑、防闪烁。
- `references/chat-advanced.md`：`@tdesign-vue-next/chat` 的对话列表、输入框、流式响应与自定义渲染。

官方资源：

- 文档：https://tdesign.tencent.com/vue-next/overview
- AI Chat 文档：https://tdesign.tencent.com/vue-next-chat/getting-started
- GitHub：https://github.com/Tencent/tdesign-vue-next
- 设计规范：https://tdesign.tencent.com/design/values
