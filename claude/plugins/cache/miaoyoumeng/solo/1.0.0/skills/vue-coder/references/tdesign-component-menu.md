# TDesign Menu 导航菜单

导航菜单组件用于构建侧边栏或顶部导航，支持水平/垂直布局、多级嵌套、展开/收起等功能。

## Props

### Menu Props

| 属性名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| collapsed | boolean | false | 是否折叠（仅 vertical） |
| expand-mutex | boolean | false | 是否互斥展开（同时只展开一个子菜单） |
| expand-type | string | 'popup' | 展开方式：`popup` / `accordion` |
| height | string/number | - | 菜单高度 |
| logo | object | - |  Logo 配置（icon、title） |
| operations | RenderFunction | - | 菜单顶部操作区 |
| theme | string | light | 主题：`light` / `dark` |
| value | string/number | - | 激活的菜单项（v-model） |
| width | string/number | 232 | 菜单宽度 |

### MenuItem Props

| 属性名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| content | string | - | 菜单项内容 |
| disabled | boolean | false | 是否禁用 |
| icon | RenderFunction | - | 自定义图标 |
| router | boolean | false | 是否使用 vue-router |
| target | string | - | 链接打开方式 |
| to | string/object | - | 路由目标 |
| value | string/number | - | 菜单项唯一标识 |

### SubMenu Props

| 属性名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| content | string | - | 子菜单标题 |
| disabled | boolean | false | 是否禁用 |
| icon | RenderFunction | - | 子菜单图标 |
| value | string/number | - | 子菜单唯一标识 |

## Events

| 事件名 | 参数 | 说明 |
|--------|------|------|
| change | `(value: string | number) => void` | 菜单项选中值变化时触发 |
| collapsed-change | `(collapsed: boolean) => void` | 折叠状态变化时触发 |

## Slots

| 插槽名 | 说明 |
|--------|------|
| default | MenuItem / SubMenu 列表 |

## 示例

```vue
<template>
  <Space>
    <!-- 垂直菜单（侧边栏） -->
    <Menu
      v-model="activeValue"
      :width="200"
      theme="light"
      @change="handleChange"
    >
      <MenuItem value="home" :icon="() => '🏠'">首页</MenuItem>
      <MenuItem value="user" :icon="() => '👤'">用户管理</MenuItem>
      <SubMenu value="system" content="系统设置" :icon="() => '⚙️'">
        <MenuItem value="basic">基础设置</MenuItem>
        <MenuItem value="advanced">高级设置</MenuItem>
        <MenuItem value="security">安全设置</MenuItem>
      </SubMenu>
      <MenuItem value="disabled" disabled>禁用项</MenuItem>
    </Menu>

    <!-- 水平菜单 -->
    <Menu v-model="activeValue" theme="dark" expand-type="popup">
      <MenuItem value="home">首页</MenuItem>
      <MenuItem value="docs">文档</MenuItem>
      <SubMenu value="more" content="更多">
        <MenuItem value="about">关于</MenuItem>
        <MenuItem value="contact">联系</MenuItem>
      </SubMenu>
    </Menu>

    <!-- 折叠菜单 -->
    <Menu
      v-model="activeValue"
      :collapsed="isCollapsed"
      theme="light"
      @collapsed-change="handleCollapsedChange"
    >
      <template #operations>
        <Button size="small" @click="toggleCollapsed">
          {{ isCollapsed ? '展开' : '收起' }}
        </Button>
      </template>
      <MenuItem value="home" :icon="() => '🏠'">首页</MenuItem>
      <SubMenu value="settings" content="设置" :icon="() => '⚙️'">
        <MenuItem value="basic">基础</MenuItem>
        <MenuItem value="theme">主题</MenuItem>
      </SubMenu>
    </Menu>

    <!-- 手风琴模式 -->
    <Menu v-model="activeValue" expand-mutex expand-type="accordion">
      <SubMenu value="module1" content="模块一">
        <MenuItem value="m1-1">子项 1-1</MenuItem>
        <MenuItem value="m1-2">子项 1-2</MenuItem>
      </SubMenu>
      <SubMenu value="module2" content="模块二">
        <MenuItem value="m2-1">子项 2-1</MenuItem>
        <MenuItem value="m2-2">子项 2-2</MenuItem>
      </SubMenu>
    </Menu>
  </Space>
</template>
<script setup lang="ts" name="MenuDemo">
import { ref } from 'vue';
import { Button, Menu, MenuItem, SubMenu, Space } from 'tdesign-vue-next';

const activeValue = ref('home');
const isCollapsed = ref(false);

const handleChange = (value: string | number) => {
  console.log('菜单选中:', value);
};

const handleCollapsedChange = (collapsed: boolean) => {
  isCollapsed.value = collapsed;
};

const toggleCollapsed = () => {
  isCollapsed.value = !isCollapsed.value;
};
</script>
<style scoped>
</style>
```
