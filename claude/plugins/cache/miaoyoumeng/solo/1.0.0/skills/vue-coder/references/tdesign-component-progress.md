# TDesign Progress 进度条

进度条用于展示操作进度。

## Props

| 属性名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| percentage | number | 0 | 进度百分比 |
| theme | string | line | 主题：`line` / `plump` / `circle` |
| status | string | - | 状态：`success` / `error` / `warning` / `active` |
| size | string/number | medium | 尺寸 |
| strokeWidth | number | - | 线宽 |
| label | boolean | true | 是否显示标签 |
| color | string | - | 自定义颜色 |

## Slots

| 插槽名 | 说明 |
|--------|------|
| default | 自定义标签内容 |

## 示例

```vue
<template>
  <Space>
    <Progress :percentage="60" />
    <Progress :percentage="80" theme="plump" />
    <Progress :percentage="100" status="success" />
    <Progress :percentage="50" theme="circle" />
    <Progress :percentage="30" color="#ff0000" />
  </Space>
</template>
<script setup lang="ts" name="ProgressDemo">
import { Progress, Space } from 'tdesign-vue-next';
</script>
<style scoped>
</style>
```
