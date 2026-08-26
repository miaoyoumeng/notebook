# TDesign BackTop 回到顶部

回到顶部组件用于在长页面滚动超过一定距离后，提供快速回到页面顶部的按钮。

## Props

| 属性名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| container | string / () => HTMLElement | () => window | 指定滚动的容器 |
| duration | number | 200 | 回到顶部动画耗时（ms） |
| size | string | medium | 尺寸：`small` / `medium` / `large` |
| target | string / () => HTMLElement | - | 监听该元素内滚动条的滚动 |
| text | string | - | 按钮自定义文本 |
| theme | string | round | 按钮形状：`round` / `half-round` / `square` |
| visible-height | number | 200 | 滚动条高度超过该值后显示按钮 |

## Events

| 事件名 | 参数 | 说明 |
|--------|------|------|
| click | `(e: MouseEvent) => void` | 点击按钮时触发 |

## Slots

| 插槽名 | 说明 |
|--------|------|
| default | 自定义按钮内容 |

## 示例

```vue
<template>
  <div class="backtop-demo">
    <div ref="scrollContainer" class="scroll-container">
      <p v-for="i in 50" :key="i">滚动内容 {{ i }}</p>

      <!-- 基础用法 -->
      <BackTop :container="scrollContainer" />

      <!-- 自定义文本 -->
      <BackTop :container="scrollContainer" text="↑ 顶部" />

      <!-- 自定义形状 -->
      <BackTop :container="scrollContainer" theme="square" text="TOP" />
      <BackTop :container="scrollContainer" theme="half-round" />

      <!-- 自定义可见高度阈值 -->
      <BackTop :container="scrollContainer" :visible-height="100" />

      <!-- 自定义动画时长 -->
      <BackTop :container="scrollContainer" :duration="500" />

      <!-- 自定义内容 -->
      <BackTop :container="scrollContainer" @click="handleClick">
        <div class="custom-backtop">
          <Icon name="backtop" />
        </div>
      </BackTop>

      <!-- 监听整个窗口滚动 -->
      <BackTop :visible-height="300" @click="handleWindowBacktop" />
    </div>
  </div>
</template>
<script setup lang="ts" name="BackTopDemo">
import { ref } from 'vue';
import { BackTop, Icon } from 'tdesign-vue-next';

const scrollContainer = ref<HTMLElement | null>(null);

const handleClick = (e: MouseEvent) => {
  console.log('回到顶部按钮点击', e);
};

const handleWindowBacktop = (e: MouseEvent) => {
  console.log('窗口回到顶部', e);
};
</script>
<style scoped>
.backtop-demo {
  position: relative;
}
.scroll-container {
  height: 400px;
  overflow: auto;
  border: 1px solid #dcdcdc;
  padding: 16px;
}
.custom-backtop {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: #0052d9;
  color: #fff;
}
</style>
```
