# TDesign Anchor 锚点

锚点组件用于页面内跳转，通过锚点链接快速定位到对应内容区域。常用于文档目录、长页面导航等场景。

## Props

### Anchor Props

| 属性名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| affix | boolean | false | 是否开启固定模式 |
| bounds | number | 15 | 锚点滚动偏移量（px） |
| container | string / () => HTMLElement | () => window | 指定监听的滚动容器 |
| cursor | object | - | 锚点指示器样式配置 |
| size | string | medium | 尺寸：`small` / `medium` / `large` |
| target-offset | number | 0 | 目标内容距离顶部偏移量 |

### AnchorItem Props

| 属性名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| href | string | - | 锚点链接（对应元素 id） |
| title | string | - | 锚点标题 |
| target | string | - | 链接打开方式 |

## Events

| 事件名 | 参数 | 说明 |
|--------|------|------|
| change | `(href: string) => void` | 锚点切换时触发 |
| click | `(href: string, e: MouseEvent) => void` | 锚点点击时触发 |

## Slots

| 插槽名 | 说明 |
|--------|------|
| default | AnchorItem 列表 |

## 示例

```vue
<template>
  <div class="anchor-demo">
    <div class="anchor-nav">
      <!-- 基础用法 -->
      <Anchor :target-offset="20" @change="handleChange">
        <AnchorItem href="#section1" title="基础用法" />
        <AnchorItem href="#section2" title="嵌套锚点" />
        <AnchorItem href="#section3" title="固定模式" />
      </Anchor>
    </div>

    <div class="anchor-content">
      <section id="section1" class="section">
        <h2>基础用法</h2>
        <p>锚点组件的基础使用方式</p>
      </section>

      <section id="section2" class="section">
        <h2>嵌套锚点</h2>
        <Anchor>
          <AnchorItem href="#sub1" title="子锚点 1" />
          <AnchorItem href="#sub2" title="子锚点 2" />
          <AnchorItem href="#sub3" title="子锚点 3" />
        </Anchor>
        <div id="sub1" style="margin-top: 20px;">子锚点 1 内容</div>
        <div id="sub2" style="margin-top: 20px;">子锚点 2 内容</div>
        <div id="sub3" style="margin-top: 20px;">子锚点 3 内容</div>
      </section>

      <section id="section3" class="section">
        <h2>固定模式</h2>
        <Anchor affix :target-offset="20">
          <AnchorItem href="#section1" title="回到顶部" />
          <AnchorItem href="#section2" title="回到嵌套" />
          <AnchorItem href="#section3" title="当前区域" />
        </Anchor>
      </section>
    </div>
  </div>
</template>
<script setup lang="ts" name="AnchorDemo">
import { Anchor, AnchorItem } from 'tdesign-vue-next';

const handleChange = (href: string) => {
  console.log('锚点切换到:', href);
};
</script>
<style scoped>
.anchor-demo {
  display: flex;
  gap: 16px;
}
.anchor-nav {
  width: 200px;
  flex-shrink: 0;
}
.anchor-content {
  flex: 1;
}
.section {
  min-height: 400px;
  padding: 16px;
  margin-bottom: 16px;
  border: 1px solid #dcdcdc;
}
</style>
```
