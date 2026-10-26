# tdesign-vue-next

面向 Vue 3 项目的 TDesign 组件库使用指南，覆盖 `tdesign-vue-next` 1.x 与 AI 对话包 `@tdesign-vue-next/chat`。

## 适用对象

- 使用 Vue 3 + TypeScript 开发管理后台、表单页、数据列表或 AI 对话界面的开发者。
- 需要确认组件属性、事件、类型与引入方式的 AI 编码助手。
- 正在排查样式、类型、图标或暗黑模式问题的项目维护者。

不适用于 `tdesign-react`、`tdesign-miniprogram`，也不适用于非 TDesign 的 UI 需求。

## 安装

```bash
pnpm add tdesign-vue-next tdesign-icons-vue-next
```

需要 AI 对话组件时：

```bash
pnpm add @tdesign-vue-next/chat
```

## 快速使用

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

## 目录结构

```text
tdesign-vue-next/
├── SKILL.md                 # 安装、选型规则、决策链与验证清单
├── README.md                # 本文件
├── references/
│   ├── tdesign-v1.md        # 1.x 版本、升级与排错
│   ├── form-advanced.md     # 动态表单、联动校验、异步校验
│   ├── table-advanced.md    # 服务端数据、虚拟滚动、可编辑表格
│   ├── table-extra.md       # 固定列、展开行、合并单元格
│   ├── select-advanced.md   # 远程搜索、分页加载、自定义选项
│   ├── select-extra.md      # 分组选项、前缀图标
│   ├── upload-advanced.md   # 受控上传、自定义请求、分片上传
│   ├── upload-extra.md      # 文件列表、取消上传、URL 与进度
│   ├── tree-advanced.md     # 异步加载、拖拽、节点搜索
│   ├── tree-extra.md        # 节点增删改、单选树、实例状态
│   ├── cascader-advanced.md # 异步级联、多选、自定义面板
│   ├── cascader-extra.md    # 自定义触发器、路径读取、省市区联动
│   ├── dialog-drawer-advanced.md # 嵌套、命令式调用、关闭拦截
│   ├── dialog-drawer-extra.md    # 抽屉详情、全屏/拖拽、层级
│   ├── theming-advanced.md  # CSS 变量、运行时主题、多品牌
│   ├── dark-mode.md         # 暗黑模式、跟随系统、防闪烁、图片适配
│   └── chat-advanced.md     # AI 对话列表、输入框、流式响应
├── scripts/                 # 预留：确定性脚本
├── assets/                  # 预留：模板与资源
└── evals/
    └── evals.json           # 测试用例
```

## 使用方式

1. 先读 `SKILL.md`，确认安装方式、组件选型与决策链。
2. 命中复杂场景时，读取 `references/` 下对应文档。
3. 按 `SKILL.md` 的验证清单检查类型、构建与交互。
4. 需要新增测试用例时，编辑 `evals/evals.json`。

## 覆盖范围

- 基础与布局：Button、Icon、Link、Typography、Grid、Layout、Space、Divider。
- 导航：Menu、Tabs、Breadcrumb、Steps、Pagination。
- 输入：Form、Input、Select、Cascader、DatePicker、Upload、TreeSelect。
- 数据展示：Table、List、Tree、Card、Descriptions、Image。
- 反馈：Message、Notification、Dialog、Drawer、Loading、Popconfirm。
- 主题：CSS 变量、运行时切换、多品牌主题、暗黑模式。
- AI 对话：`@tdesign-vue-next/chat` 的 ChatList、ChatItem、ChatInput。

## 兼容性

- `tdesign-vue-next`：1.x
- Vue：3.3+
- TypeScript：5.x
- 包管理器：pnpm

## 参考资源

- TDesign Vue Next 文档：https://tdesign.tencent.com/vue-next/overview
- TDesign AI Chat 文档：https://tdesign.tencent.com/vue-next-chat/getting-started
- GitHub：https://github.com/Tencent/tdesign-vue-next
- 设计规范：https://tdesign.tencent.com/design/values

## 许可证

MIT
