# TDesign StickyTool 侧边栏

侧边栏工具组件，固定在页面一侧，提供快捷操作入口，常用于帮助、反馈、客服等场景。

## Props

### StickyTool Props

| 属性名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| offset-bottom | number | - | 距离窗口底部的偏移量 |
| offset-right | number | 0 | 距离窗口右侧的偏移量 |
| placement | string | right-bottom | 固定位置：`left-top` / `left-bottom` / `right-top` / `right-bottom` |
| popup-props | object | - | Popup 透传属性（展开面板） |

### StickyToolItem Props

| 属性名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| content | string / object | - | 弹出面板内容 |
| icon | RenderFunction | - | 自定义图标 |
| label | string | - | 悬浮提示文字 |
| popup-props | object | - | Popup 透传属性 |

## Events

| 事件名 | 参数 | 说明 |
|--------|------|------|
| click | `(context: { e: MouseEvent }) => void` | 工具项点击时触发 |

## Slots

| 插槽名 | 说明 |
|--------|------|
| default | StickyToolItem 列表 |

## 示例

```vue
<template>
  <div class="sticky-demo">
    <div class="page-content">
      <p>页面内容（滚动查看固定效果）</p>
      <p v-for="i in 30" :key="i">内容行 {{ i }}</p>
    </div>

    <!-- 基础用法 -->
    <StickyTool>
      <StickyToolItem
        label="帮助"
        :icon="() => '❓'"
      >
        <template #content>
          <div class="popup-content">
            <h4>帮助中心</h4>
            <p>使用文档和常见问题</p>
          </div>
        </template>
      </StickyToolItem>
      <StickyToolItem
        label="反馈"
        :icon="() => '💬'"
      >
        <template #content>
          <div class="popup-content">
            <h4>意见反馈</h4>
            <p>请描述您遇到的问题</p>
          </div>
        </template>
      </StickyToolItem>
    </StickyTool>

    <!-- 自定义位置 -->
    <StickyTool placement="right-top" :offset-right="20" :offset-bottom="100">
      <StickyToolItem label="客服" :icon="() => '🎧'" />
      <StickyToolItem label="微信" :icon="() => '💚'" />
      <StickyToolItem label="微博" :icon="() => '🔵'" />
    </StickyTool>

    <!-- 点击事件 -->
    <StickyTool @click="handleClick">
      <StickyToolItem label="分享" :icon="() => '🔗'" />
      <StickyToolItem label="收藏" :icon="() => '⭐'" />
    </StickyTool>
  </div>
</template>
<script setup lang="ts" name="StickyToolDemo">
import { StickyTool, StickyToolItem } from 'tdesign-vue-next';

const handleClick = (context: { e: MouseEvent }) => {
  console.log('工具项点击:', context);
};
</script>
<style scoped>
.page-content {
  min-height: 200vh;
  padding: 20px;
}
.popup-content {
  padding: 16px;
  min-width: 200px;
}
</style>
```
