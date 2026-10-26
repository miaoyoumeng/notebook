# TDesign Chat AI 对话

Chat 组件用于构建 AI 对话交互界面，支持消息列表、思考过程、代码高亮、引用来源等功能。

> **注意**：Chat 组件来自独立包 `@tdesign-vue-next/chat`，需单独安装。

## 安装

```bash
pnpm add @tdesign-vue-next/chat
```

## 子组件

| 组件名 | 说明 |
|--------|------|
| ChatList | 消息列表容器 |
| ChatItem | 单条消息项 |
| ChatInput | 对话输入框 |
| ChatThinking | 思考过程指示器 |
| ChatReference | 引用来源展示 |

## ChatList Props

| 属性名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| data | ChatData[] | [] | 消息数据列表 |
| loading | boolean | false | 是否显示加载状态 |

## ChatItem Props

| 属性名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| role | string | 'user' | 角色类型：`user` / `assistant` |
| name | string | '' | 显示名称 |
| avatar | string | '' | 头像 URL 或图标 |
| datetime | string | '' | 时间戳文本 |
| variant | string | 'base' | 变体：`base` / `transparent` |
| loading | boolean | false | 是否显示加载中 |
| thinking | boolean | false | 是否显示思考过程 |
| thinking-text | string | '' | 思考过程内容 |
| references | ChatReference[] | [] | 引用来源列表 |
| highlight | boolean | true | 是否启用代码高亮 |
| custom-render | RenderFunction | undefined | 自定义内容渲染函数 |

## ChatInput Props

| 属性名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| value | string | '' | 输入框内容（v-model） |
| placeholder | string | '' | 占位文本 |
| disabled | boolean | false | 是否禁用 |
| loading | boolean | false | 是否发送中 |
| auto-size | boolean / object | false | 是否自适应高度 |
| max-auto-height | number | 160 | 自适应最大高度 |
| actions | ActionItem[] | [] | 自定义操作按钮 |

## ChatInput Events

| 事件名 | 参数 | 说明 |
|--------|------|------|
| send | `(value: string) => void` | 点击发送 |
| change | `(value: string) => void` | 输入内容变化 |
| abort | `() => void` | 点击停止生成 |
| enter | `(value: string) => void` | 回车键触发 |

## 数据接口

```ts
interface ChatData {
  role: 'user' | 'assistant';
  name?: string;
  avatar?: string;
  datetime?: string;
  content: string;
  thinking?: string;
  references?: ChatReference[];
}

interface ChatReference {
  name: string;
  url?: string;
  icon?: string;
}

interface ActionItem {
  name: string;
  icon: RenderFunction;
  disabled?: boolean;
}
```

## 示例

```vue
<template>
  <div class="chat-container">
    <ChatList :data="chatData" />
    <ChatInput
      v-model="inputValue"
      placeholder="输入消息..."
      :loading="isGenerating"
      @send="handleSend"
      @abort="handleAbort"
    />
  </div>
</template>
<script setup lang="ts" name="ChatDemo">
import { ref } from 'vue';
import {
  ChatList,
  ChatInput,
  type ChatData,
} from '@tdesign-vue-next/chat';

const chatData = ref<ChatData[]>([
  {
    role: 'user',
    name: '用户',
    content: '请介绍一下 Vue 3 的 Composition API',
    datetime: '2026-08-10 10:00',
  },
  {
    role: 'assistant',
    name: 'AI 助手',
    content:
      'Composition API 是 Vue 3 引入的一套响应式 API 组合方案...\n\n```ts\nimport { ref, computed } from "vue";\n\nconst count = ref(0);\nconst doubled = computed(() => count.value * 2);\n```',
    datetime: '2026-08-10 10:01',
    thinking: '正在分析 Vue 3 Composition API 的核心特性...',
  },
]);

const inputValue = ref('');
const isGenerating = ref(false);

const handleSend = (value: string) => {
  if (!value.trim()) return;
  chatData.value.push({
    role: 'user',
    content: value,
    datetime: new Date().toLocaleString(),
  });
  inputValue.value = '';
  isGenerating.value = true;
  // todo: 调用 AI 接口获取回复
};

const handleAbort = () => {
  isGenerating.value = false;
};
</script>
<style scoped>
.chat-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
}
</style>
```
