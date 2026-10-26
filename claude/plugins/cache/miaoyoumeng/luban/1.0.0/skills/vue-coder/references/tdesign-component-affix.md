# TDesign Affix 固钉

固钉组件用于将内容固定在可视区域的指定位置，滚动时保持可见。常用于吸顶导航、返回顶部按钮等场景。

## Props

| 属性名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| container | string / () => HTMLElement | () => window | 滚动容器 |
| offset-bottom | number | - | 距离底部偏移量（px） |
| offset-top | number | 0 | 距离顶部偏移量（px） |
| z-index | number | 100 | 固定状态下的层级 |

## Events

| 事件名 | 参数 | 说明 |
|--------|------|------|
| fixed-change | `(affixed: boolean) => void` | 固定状态变化时触发 |

## Slots

| 插槽名 | 说明 |
|--------|------|
| default | 固钉内容 |

## 示例

```vue
<template>
  <div class="affix-demo">
    <!-- 基础用法：距离顶部 50px 吸顶 -->
    <Affix :offset-top="50">
      <Button theme="primary">距离顶部 50px 吸顶</Button>
    </Affix>

    <!-- 距离底部固定 -->
    <Affix :offset-bottom="100">
      <Button theme="success">距离底部 100px 固定</Button>
    </Affix>

    <!-- 指定滚动容器 -->
    <div ref="scrollContainer" class="scroll-container">
      <Affix :container="scrollContainer" :offset-top="0">
        <Button>容器内吸顶</Button>
      </Affix>
      <div class="scroll-content">
        <p v-for="i in 20" :key="i">滚动内容 {{ i }}</p>
      </div>
    </div>

    <!-- 状态监听 -->
    <Affix :offset-top="0" @fixed-change="handleFixedChange">
      <Button :theme="isAffixed ? 'danger' : 'primary'">
        {{ isAffixed ? '已固定' : '未固定' }}
      </Button>
    </Affix>
  </div>
</template>
<script setup lang="ts" name="AffixDemo">
import { ref } from 'vue';
import { Affix, Button } from 'tdesign-vue-next';

const scrollContainer = ref<HTMLElement | null>(null);
const isAffixed = ref(false);

const handleFixedChange = (affixed: boolean) => {
  isAffixed.value = affixed;
  console.log('固定状态变化:', affixed);
};
</script>
<style scoped>
.affix-demo {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.scroll-container {
  height: 300px;
  overflow: auto;
  border: 1px solid #dcdcdc;
  padding: 16px;
}
.scroll-content {
  height: 800px;
}
</style>
```
