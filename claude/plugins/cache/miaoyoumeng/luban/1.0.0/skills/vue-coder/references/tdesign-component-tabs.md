# TDesign Tabs 选项卡

选项卡组件用于在同一区域内切换展示不同面板内容，支持水平/垂直布局、多种风格和禁用状态。

## Props

### Tabs Props

| 属性名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| add-button | object / RenderFunction | - | 自定义添加按钮 |
| disabled | boolean | false | 是否禁用整个选项卡 |
| drag-sort | boolean | false | 是否开启拖拽排序 |
| list | TabPanel[] | [] | 选项卡面板列表 |
| placement | string | top | 标签位置：`top` / `bottom` / `left` / `right` |
| show-add-button | boolean | false | 是否显示添加按钮 |
| size | string | medium | 尺寸：`small` / `medium` / `large` |
| theme | string | normal | 主题：`normal` / `card` / `simple` / `text` / `rounded` |
| value | string/number | - | 选中标签的值（v-model） |

### TabPanel Props

| 属性名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| content | string / RenderFunction | - | 面板内容 |
| destroy-on-hide | boolean | true | 隐藏时是否销毁 |
| disabled | boolean | false | 是否禁用 |
| icon | RenderFunction | - | 自定义图标 |
| label | string / RenderFunction | - | 标签标题 |
| panel | string / RenderFunction | - | 面板内容（同 content） |
| value | string/number | - | 面板唯一标识 |
| removable | boolean | false | 是否可删除 |

## Events

| 事件名 | 参数 | 说明 |
|--------|------|------|
| add | `(context: { e: MouseEvent }) => void` | 点击添加按钮时触发 |
| change | `(value: string | number) => void` | 切换面板时触发 |
| remove | `(options: { value: string | number, e: MouseEvent }) => void` | 点击删除按钮时触发 |

## Slots

| 插槽名 | 说明 |
|--------|------|
| default | TabPanel 列表 |
| add-button | 自定义添加按钮 |

## 示例

```vue
<template>
  <Space direction="vertical" :size="24">
    <!-- 基础用法 -->
    <Tabs v-model="activeTab1" @change="handleChange">
      <TabPanel :value="1" label="标签一">
        <p>内容面板一</p>
      </TabPanel>
      <TabPanel :value="2" label="标签二">
        <p>内容面板二</p>
      </TabPanel>
      <TabPanel :value="3" label="标签三">
        <p>内容面板三</p>
      </TabPanel>
    </Tabs>

    <!-- 卡片风格 -->
    <Tabs v-model="activeTab2" theme="card">
      <TabPanel :value="1" label="概览" />
      <TabPanel :value="2" label="详情" />
      <TabPanel :value="3" label="设置" />
    </Tabs>

    <!-- 垂直布局 -->
    <Tabs v-model="activeTab3" placement="left">
      <TabPanel :value="basic" label="基础设置">
        <p>基础配置项</p>
      </TabPanel>
      <TabPanel :value="advanced" label="高级设置">
        <p>高级配置项</p>
      </TabPanel>
      <TabPanel :value="security" label="安全设置">
        <p>安全配置项</p>
      </TabPanel>
    </Tabs>

    <!-- 含禁用和图标 -->
    <Tabs v-model="activeTab4">
      <TabPanel :value="1" label="首页" :icon="() => '🏠'" />
      <TabPanel :value="2" label="文档" :icon="() => '📄'" />
      <TabPanel :value="3" label="禁用项" :disabled="true" />
      <TabPanel :value="4" label="设置" :icon="() => '⚙️'" />
    </Tabs>

    <!-- 可删除 -->
    <Tabs v-model="activeTab5" @remove="handleRemove">
      <TabPanel
        v-for="tab in removableTabs"
        :key="tab.value"
        :value="tab.value"
        :label="tab.label"
        :removable="tab.removable"
      >
        <p>{{ tab.content }}</p>
      </TabPanel>
    </Tabs>

    <!-- 简洁主题 -->
    <Tabs v-model="activeTab6" theme="simple">
      <TabPanel :value="1" label="简单" />
      <TabPanel :value="2" label="简洁" />
    </Tabs>

    <!-- 圆角主题 -->
    <Tabs v-model="activeTab7" theme="rounded">
      <TabPanel :value="1" label="圆角 1" />
      <TabPanel :value="2" label="圆角 2" />
    </Tabs>
  </Space>
</template>
<script setup lang="ts" name="TabsDemo">
import { ref } from 'vue';
import { Space, TabPanel, Tabs } from 'tdesign-vue-next';

const activeTab1 = ref(1);
const activeTab2 = ref(1);
const activeTab3 = ref('basic');
const activeTab4 = ref(1);
const activeTab5 = ref(1);
const activeTab6 = ref(1);
const activeTab7 = ref(1);

const removableTabs = ref([
  { value: 1, label: '标签一', content: '内容一', removable: true },
  { value: 2, label: '标签二', content: '内容二', removable: true },
  { value: 3, label: '标签三', content: '内容三', removable: false },
]);

const handleChange = (value: string | number) => {
  console.log('切换到:', value);
};

const handleRemove = (options: { value: string | number; e: MouseEvent }) => {
  removableTabs.value = removableTabs.value.filter(
    (tab) => tab.value !== options.value
  );
  console.log('删除:', options.value);
};
</script>
<style scoped>
</style>
```
