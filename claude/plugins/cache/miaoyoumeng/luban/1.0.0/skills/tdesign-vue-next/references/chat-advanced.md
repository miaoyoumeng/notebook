# AI 对话（Chat）复杂场景

## 包与组件

AI 对话组件不在 `tdesign-vue-next` 主包内，需要安装独立包：

```bash
pnpm add @tdesign-vue-next/chat
```

常用组件：

| 组件 | 用途 |
| --- | --- |
| `ChatList` | 消息列表容器，按 `data` 渲染消息 |
| `ChatItem` | 单条消息，可自定义渲染 |
| `ChatInput` | 输入框与发送、停止操作 |
| `ChatThinking` | 思考过程展示 |
| `ChatReference` | 引用来源展示 |

从 `@tdesign-vue-next/chat` 导入，不要从 `tdesign-vue-next` 导入。

## 基础对话

```vue
<template>
  <div class="chat-container">
    <ChatList :data="messages" :loading="loading" />
    <ChatInput
      v-model="inputValue"
      placeholder="输入消息..."
      :loading="loading"
      @send="onSend"
      @abort="onAbort"
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { ChatInput, ChatList } from "@tdesign-vue-next/chat";
import type { ChatData } from "@tdesign-vue-next/chat";

const messages = ref<ChatData[]>([]);
const inputValue = ref("");
const loading = ref(false);

let abortController: AbortController | null = null;

const onSend = async (value: string) => {
  if (!value.trim()) return;

  messages.value.push({
    role: "user",
    content: value,
    datetime: new Date().toLocaleString(),
  });
  inputValue.value = "";

  const assistant: ChatData = {
    role: "assistant",
    content: "",
    datetime: new Date().toLocaleString(),
  };
  messages.value.push(assistant);

  loading.value = true;
  abortController = new AbortController();

  try {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: value }),
      signal: abortController.signal,
    });
    const data = await response.json();
    assistant.content = data.reply;
  } catch (error) {
    if ((error as Error).name !== "AbortError") {
      assistant.content = "请求失败，请稍后重试。";
    }
  } finally {
    loading.value = false;
    abortController = null;
  }
};

const onAbort = () => {
  abortController?.abort();
};
</script>

<style scoped>
.chat-container {
  display: flex;
  flex-direction: column;
  gap: 12px;
  height: 600px;
  padding: 16px;
  border: 1px solid var(--td-border-level-2-color);
  border-radius: var(--td-radius-default);
}
</style>
```

`ChatData` 至少包含 `role` 与 `content`；`role` 取 `user` 或 `assistant`。

## 流式响应

服务端返回 SSE 或纯文本流时，持续追加到最后一条助手消息：

```vue
<script setup lang="ts">
import { ref } from "vue";
import type { ChatData } from "@tdesign-vue-next/chat";

const messages = ref<ChatData[]>([]);
const loading = ref(false);
let abortController: AbortController | null = null;

const sendStream = async (value: string) => {
  messages.value.push({ role: "user", content: value });

  const assistant: ChatData = { role: "assistant", content: "" };
  messages.value.push(assistant);

  loading.value = true;
  abortController = new AbortController();

  try {
    const response = await fetch("/api/chat/stream", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: value }),
      signal: abortController.signal,
    });

    const reader = response.body?.getReader();
    const decoder = new TextDecoder();
    if (!reader) throw new Error("响应体不可读");

    let buffer = "";

    while (true) {
      const { done, value: chunk } = await reader.read();
      if (done) break;

      buffer += decoder.decode(chunk, { stream: true });
      const lines = buffer.split("\n");
      buffer = lines.pop() ?? "";

      for (const line of lines) {
        if (!line.startsWith("data:")) continue;

        const payload = line.slice(5).trim();
        if (payload === "[DONE]") continue;

        try {
          const parsed = JSON.parse(payload);
          if (parsed.content) {
            assistant.content += parsed.content;
          }
        } catch {
          // 忽略非 JSON 的心跳行
        }
      }
    }
  } catch (error) {
    if ((error as Error).name !== "AbortError") {
      assistant.content = "流式响应中断，请重试。";
    }
  } finally {
    loading.value = false;
    abortController = null;
  }
};
</script>
```

不要每收到一个分片就替换整个 `messages` 数组，直接修改最后一条消息的 `content`。

## 思考过程与引用

```vue
<script setup lang="ts">
import { ref } from "vue";
import { ChatInput, ChatList } from "@tdesign-vue-next/chat";
import type { ChatData } from "@tdesign-vue-next/chat";

const messages = ref<ChatData[]>([
  {
    role: "assistant",
    content: "Composition API 是 Vue 3 的组合式 API。",
    thinking: "先确认用户问的是 Vue 3，再给出 Composition API 的定义。",
    references: [
      { name: "Vue 3 文档", url: "https://cn.vuejs.org/guide/extras/composition-api-faq" },
    ],
    datetime: "2026-10-26 10:00",
  },
]);

const inputValue = ref("");
const send = (value: string) => {
  messages.value.push({ role: "user", content: value });
  inputValue.value = "";
};
</script>

<template>
  <ChatList :data="messages" />
  <ChatInput v-model="inputValue" @send="send" />
</template>
```

`thinking` 展示推理过程，`references` 展示引用来源，二者都放在 `ChatData` 上。

## 自定义消息

`ChatItem` 的 `custom-render` 用于替换消息内容渲染：

```vue
<template>
  <div class="message-list">
    <ChatItem
      v-for="message in messages"
      :key="message.id"
      :role="message.role"
      :name="message.name"
      :avatar="message.avatar"
      :datetime="message.datetime"
      :custom-render="() => renderMessage(message)"
    />
  </div>
</template>

<script setup lang="ts">
import { h, ref } from "vue";
import { ChatItem } from "@tdesign-vue-next/chat";
import type { ChatData } from "@tdesign-vue-next/chat";

interface UiChatData extends ChatData {
  id: string;
}

const messages = ref<UiChatData[]>([
  { id: "1", role: "user", name: "我", content: "介绍一下 TDesign" },
  { id: "2", role: "assistant", name: "AI 助手", content: "TDesign 是腾讯开源的企业级设计体系。" },
]);

const renderMessage = (message: ChatData) => {
  if (message.role === "assistant") {
    return h("div", { innerHTML: message.content });
  }
  return h("div", message.content);
};
</script>

<style scoped>
.message-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
</style>
```

渲染 `innerHTML` 前必须先做 XSS 过滤；生产环境使用 `marked` 等库时开启安全选项。

## 输入框操作

```vue
<template>
  <ChatInput
    v-model="inputValue"
    placeholder="输入消息..."
    :loading="loading"
    :actions="actions"
    @send="onSend"
    @abort="onAbort"
    @change="onChange"
  />
</template>

<script setup lang="ts">
import { h, ref } from "vue";
import { ChatInput } from "@tdesign-vue-next/chat";
import { AttachIcon } from "tdesign-icons-vue-next";
import type { ActionItem } from "@tdesign-vue-next/chat";

const inputValue = ref("");
const loading = ref(false);

const actions: ActionItem[] = [
  { name: "attach", icon: () => h(AttachIcon), disabled: false },
];

const onSend = (value: string) => {
  console.log("发送", value);
};

const onAbort = () => {
  loading.value = false;
};

const onChange = (value: string) => {
  inputValue.value = value;
};
</script>
```

附件上传由业务层完成，把上传后的 URL 写入消息内容或 `references`。

## 长对话与错误处理

- 只保留最近 N 条消息，更早的历史按需加载。
- 请求失败时保留用户消息，在助手消息中写入错误提示。
- 停止生成时保留已生成内容，不删除消息。
- 流式响应结束后关闭 `loading` 并释放 `AbortController`。

## 常见问题

### 从主包导入 Chat 报错

`tdesign-vue-next` 不导出 Chat。安装并导入 `@tdesign-vue-next/chat`。

### 流式响应内容不更新

确认直接修改最后一条消息对象的 `content`，而不是替换数组中的元素引用。

### 停止生成后仍继续追加

在 `abort` 后检查 `AbortController` 状态，并停止写入后续分片。

### 消息过多导致卡顿

限制保留条数，历史消息分页加载，避免一次渲染全部对话。

## 必须避免

- 从 `tdesign-vue-next` 导入 Chat 组件。
- 每收到一个流式分片就重建整个消息数组。
- 不处理 loading 状态。
- 不处理网络错误。
- 用 `v-html` 渲染未过滤的模型输出。
- 消息缺少稳定 `key`。
