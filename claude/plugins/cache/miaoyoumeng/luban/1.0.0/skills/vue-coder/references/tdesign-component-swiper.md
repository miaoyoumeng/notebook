# TDesign Swiper 轮播框

轮播框用于循环展示内容。

## Props

| 属性名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| autoplay | boolean | true | 是否自动播放 |
| interval | number | 3000 | 自动播放间隔(ms) |
| duration | number | 300 | 切换动画时长(ms) |
| direction | string | horizontal | 方向：`horizontal` / `vertical` |
| trigger | string | hover | 指示器触发：`hover` / `click` |
| navigation | object | - | 导航配置 |
| type | string | default | 轮播类型 |

## Events

| 事件名 | 参数 | 说明 |
|--------|------|------|
| change | `(current: number, context: SwiperChangeContext) => void` | 切换 |

## Slots

| 插槽名 | 说明 |
|--------|------|
| default | 轮播项（SwiperItem） |

## 示例

```vue
<template>
  <Swiper :autoplay="true" :interval="3000">
    <SwiperItem v-for="i in 3" :key="i">
      <div style="height: 200px; display: flex; align-items: center; justify-content: center">
        第 {{ i }} 页
      </div>
    </SwiperItem>
  </Swiper>
</template>
<script setup lang="ts" name="SwiperDemo">
import { Swiper, SwiperItem } from 'tdesign-vue-next';
</script>
<style scoped>
</style>
```
