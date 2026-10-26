# TDesign ColorPicker 颜色选择器

颜色选择器用于选择颜色值。

## Props

| 属性名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| value/v-model | string | - | 颜色值 |
| disabled | boolean | false | 是否禁用 |
| enableAlpha | boolean | true | 是否支持透明度 |
| format | string | CSS | 格式：`CSS` / `HEX` / `RGB` / `HSL` / `HSV` |

## Events

| 事件名 | 参数 | 说明 |
|--------|------|------|
| change | `(value: string, context: ColorPickerChangeContext) => void` | 颜色变化 |

## 示例

```vue
<template>
  <Space>
    <ColorPicker v-model="color1" />
    <ColorPicker v-model="color2" :enable-alpha="true" />
  </Space>
</template>
<script setup lang="ts" name="ColorPickerDemo">
import { ColorPicker, Space } from 'tdesign-vue-next';
import { ref } from 'vue';

const color1 = ref('#0052d9');
const color2 = ref('rgba(0, 82, 217, 0.5)');
</script>
<style scoped>
</style>
```
