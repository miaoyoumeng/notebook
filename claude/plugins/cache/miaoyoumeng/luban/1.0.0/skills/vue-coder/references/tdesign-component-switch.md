# TDesign Switch 开关

开关组件用于两种状态的切换。

## Props

| 属性名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| value/v-model | boolean | false | 选中状态 |
| disabled | boolean | false | 是否禁用 |
| loading | boolean | false | 是否加载中 |
| size | string | medium | 尺寸：`small` / `medium` / `large` |
| label | array | - | 自定义状态文本：[关, 开] |
| customValue | array | - | 自定义值：[关值, 开值] |

## Events

| 事件名 | 参数 | 说明 |
|--------|------|------|
| change | `(value: boolean, e: MouseEvent) => void` | 状态变化 |

## 示例

```vue
<template>
  <Space>
    <Switch v-model="switch1" />
    <Switch v-model="switch2" :loading="loading" />
    <Switch v-model="switch3" disabled />
    <Switch v-model="switch4" size="small" />
    <Switch v-model="switch5" :label="['关', '开']" />
  </Space>
</template>
<script setup lang="ts" name="SwitchDemo">
import { Switch, Space } from 'tdesign-vue-next';
import { ref } from 'vue';

const switch1 = ref(true);
const switch2 = ref(false);
const switch3 = ref(false);
const switch4 = ref(true);
const switch5 = ref(false);
const loading = ref(false);
</script>
<style scoped>
</style>
```
