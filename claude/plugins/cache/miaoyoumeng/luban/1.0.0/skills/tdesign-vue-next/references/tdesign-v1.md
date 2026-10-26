# TDesign Vue Next 1.x 版本参考

## 适用场景

- 确认 `tdesign-vue-next` 1.x 的运行环境与包结构。
- 从 0.x 或其它 UI 库迁移到 1.x。
- 排查安装、样式、类型、图标与 SSR 问题。

## 版本范围

| 项目 | 要求 |
| --- | --- |
| `tdesign-vue-next` | 1.x |
| Vue | 3.3+ |
| TypeScript | 5.x |
| Node.js | 18+（构建环境） |
| 包管理器 | pnpm |

1.x 的主要能力：

| 能力 | 说明 |
| --- | --- |
| Composition API | 支持 `<script setup>` |
| TypeScript | 提供组件属性、事件与实例类型 |
| Tree Shaking | 支持按需引入 |
| CSS 变量 | 主题基于 CSS 变量 |
| 暗黑模式 | 通过 `theme-mode` 属性切换 |
| SSR | 支持服务端渲染 |

## 安装

```bash
pnpm add tdesign-vue-next tdesign-icons-vue-next
```

AI 对话组件不在主包内：

```bash
pnpm add @tdesign-vue-next/chat
```

## 引入方式

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

全量引入：

```ts
// main.ts
import { createApp } from "vue";
import TDesign from "tdesign-vue-next";
import "tdesign-vue-next/es/style/index.css";
import App from "./App.vue";

createApp(App).use(TDesign).mount("#app");
```

两种方式只选一种。按需引入时不要忘记样式文件，否则组件没有基础外观。

自动导入：

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

使用自动导入后，不要再手动 `app.use` 同一组件。

## 从 0.x 升级到 1.x

1. 升级依赖：

```bash
pnpm add tdesign-vue-next@latest tdesign-icons-vue-next@latest
pnpm add vue@^3.3.0
```

2. 移除 Vue 2 写法：`new Vue()`、`Vue.use()`、选项式 API 中的 `this.$t` 等替换为 Vue 3 对应写法。

3. 检查组件命名：1.x 直接导出组件名，例如 `Button`、`Form`、`Table`，不再使用旧前缀。

4. 检查事件与类型：事件回调参数改为对象形式，使用导出的 `SubmitContext`、`TableSort`、`PageInfo` 等类型。

5. 检查主题配置：优先使用 CSS 变量，不使用旧的 Less 变量或内部类名覆盖。

6. 运行类型检查与构建：

```bash
pnpm exec vue-tsc --noEmit
pnpm run build
```

## 常见问题

### 样式不生效

确认已引入：

```ts
import "tdesign-vue-next/es/style/index.css";
```

按需引入时同样需要该文件。若使用自动导入插件，确认插件已生效且未与手动注册混用。

### TypeScript 类型报错

推荐 `tsconfig.json`：

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "strict": true,
    "jsx": "preserve"
  }
}
```

属性类型使用官方导出：

```ts
import type { ButtonProps, FormRules, TableProps } from "tdesign-vue-next";
```

不要用 `@ts-ignore` 压制错误。

### 图标不显示

安装并引入图标库：

```bash
pnpm add tdesign-icons-vue-next
```

```vue
<script setup lang="ts">
import { SearchIcon } from "tdesign-icons-vue-next";
</script>

<template>
  <SearchIcon />
</template>
```

### SSR 首屏样式闪烁

在 HTML 根元素写入主题属性，并在服务端输出主题变量：

```html
<html theme-mode="light">
  <head>
    <style>
      :root {
        --td-brand-color: #0052d9;
      }
    </style>
  </head>
</html>
```

### 找不到 Chat 组件

`tdesign-vue-next` 主包不导出 Chat。安装并使用：

```bash
pnpm add @tdesign-vue-next/chat
```

```ts
import { ChatList, ChatInput } from "@tdesign-vue-next/chat";
```

### 按需引入后包体仍然很大

检查是否同时全量引入；确认构建工具使用 ESM；确认只注册实际使用的组件。

## 最小示例

```vue
<template>
  <ConfigProvider>
    <Space direction="vertical" style="width: 100%">
      <Button theme="primary">主要按钮</Button>
      <Button theme="default">次要按钮</Button>
      <Button theme="danger">危险按钮</Button>
    </Space>
  </ConfigProvider>
</template>

<script setup lang="ts">
import { Button, ConfigProvider, Space } from "tdesign-vue-next";
</script>
```

## 参考资源

- 官方文档：https://tdesign.tencent.com/vue-next/overview
- 更新日志：https://tdesign.tencent.com/vue-next/changelog
- GitHub Releases：https://github.com/Tencent/tdesign-vue-next/releases
- AI Chat 文档：https://tdesign.tencent.com/vue-next-chat/getting-started
