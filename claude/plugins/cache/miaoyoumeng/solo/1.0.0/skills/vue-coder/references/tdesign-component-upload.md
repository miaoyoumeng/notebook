# TDesign Upload 上传

文件上传组件，支持拖拽和批量上传。

## Props

| 属性名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| files/v-model | array | - | 文件列表 |
| action | string | - | 上传地址 |
| multiple | boolean | false | 是否多选 |
| disabled | boolean | false | 是否禁用 |
| drag | boolean | false | 是否拖拽上传 |
| sizeLimit | object | - | 文件大小限制 |
| accept | string | - | 接受的文件类型 |
| max | number | 0 | 最大上传数量 |
| theme | string | file | 主题：`file` / `image` / `custom` |

## Events

| 事件名 | 参数 | 说明 |
|--------|------|------|
| success | `(context: UploadSuccessContext) => void` | 上传成功 |
| fail | `(context: UploadFailContext) => void` | 上传失败 |
| change | `(context: UploadChangeContext) => void` | 列表变化 |
| remove | `(context: UploadRemoveContext) => void` | 移除文件 |

## Slots

| 插槽名 | 说明 |
|--------|------|
| default | 自定义触发器 |

## 示例

```vue
<template>
  <Space>
    <Upload v-model:files="files1" action="/api/upload" />
    <Upload v-model:files="files2" action="/api/upload" multiple :max="5" />
    <Upload v-model:files="files3" action="/api/upload" drag />
    <Upload v-model:files="files4" theme="image" action="/api/upload" />
    <Upload v-model:files="files5" accept="image/*" :size-limit="{ size: 2, unit: 'MB' }" />
  </Space>
</template>
<script setup lang="ts" name="UploadDemo">
import { Upload, Space } from 'tdesign-vue-next';
import { ref } from 'vue';

const files1 = ref([]);
const files2 = ref([]);
const files3 = ref([]);
const files4 = ref([]);
const files5 = ref([]);
</script>
<style scoped>
</style>
```
