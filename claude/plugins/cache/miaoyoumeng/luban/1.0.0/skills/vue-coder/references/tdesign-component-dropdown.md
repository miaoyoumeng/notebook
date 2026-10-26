# TDesign Dropdown 下拉菜单

下拉菜单组件用于在触发区域弹出选项列表，支持单选/多选、分组、禁用等场景。

## Props

### Dropdown Props

| 属性名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| direction | string | right | 弹出方向：`right` / `bottom` / `left` |
| disabled | boolean | false | 是否禁用 |
| hideAfterSelect | boolean | true | 选中后是否隐藏 |
| max-column-width | number | - | 最大列宽（px） |
| options | DropdownOption[] | [] | 选项列表 |
| placement | string | bottom-left | 弹出位置 |
| popup-props | object | - | Popup 透传属性 |
| size | string | medium | 尺寸：`small` / `medium` / `large` |
| split | boolean | false | 是否显示分割线 |
| trigger | string | hover | 触发方式：`hover` / `click` / `focus` / `context-menu` |

### DropdownItem Props

| 属性名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| content | string | - | 选项内容 |
| disabled | boolean | false | 是否禁用 |
| icon | RenderFunction | - | 自定义图标 |
| prefix-icon | RenderFunction | - | 前缀图标 |
| suffix-icon | RenderFunction | - | 后缀图标 |
| children | DropdownItem[] | - | 子菜单（支持多级） |
| divider | boolean | false | 是否显示分割线 |

## Events

| 事件名 | 参数 | 说明 |
|--------|------|------|
| click | `(option: DropdownOption, context: { e: MouseEvent }) => void` | 选项点击时触发 |

## Slots

| 插槽名 | 说明 |
|--------|------|
| default | 触发区域内容 |
| dropdown | 自定义下拉面板内容 |

## 示例

```vue
<template>
  <Space>
    <!-- 基础用法（hover 触发） -->
    <Dropdown :options="basicOptions" @click="handleClick">
      <Button>下拉菜单</Button>
    </Dropdown>

    <!-- click 触发 -->
    <Dropdown :options="basicOptions" trigger="click">
      <Button variant="outline">点击触发</Button>
    </Dropdown>

    <!-- 禁用选项 -->
    <Dropdown :options="disabledOptions">
      <Button>含禁用项</Button>
    </Dropdown>

    <!-- 多级菜单 -->
    <Dropdown :options="nestedOptions">
      <Button>多级菜单</Button>
    </Dropdown>

    <!-- 自定义内容 -->
    <Dropdown>
      <Button>自定义面板</Button>
      <template #dropdown>
        <div class="custom-dropdown">
          <div class="dropdown-item" @click="handleSelect('custom')">
            自定义内容
          </div>
          <div class="dropdown-item">其他选项</div>
        </div>
      </template>
    </Dropdown>

    <!-- 带图标 -->
    <Dropdown :options="iconOptions" placement="bottom-right">
      <Button><Icon name="setting" /> 设置</Button>
    </Dropdown>
  </Space>
</template>
<script setup lang="ts" name="DropdownDemo">
import { Button, Dropdown, Icon, Space } from 'tdesign-vue-next';
import type { DropdownOption } from 'tdesign-vue-next';

const basicOptions: DropdownOption[] = [
  { content: '选项一', value: '1' },
  { content: '选项二', value: '2' },
  { content: '选项三', value: '3' },
];

const disabledOptions: DropdownOption[] = [
  { content: '选项一', value: '1' },
  { content: '选项二（禁用）', value: '2', disabled: true },
  { content: '选项三', value: '3' },
];

const nestedOptions: DropdownOption[] = [
  {
    content: '一级菜单',
    value: '1',
    children: [
      { content: '二级-1', value: '1-1' },
      { content: '二级-2', value: '1-2' },
    ],
  },
  { content: '独立选项', value: '2' },
];

const iconOptions: DropdownOption[] = [
  { content: '复制', value: 'copy', icon: () => '📋' },
  { content: '删除', value: 'delete', icon: () => '🗑️' },
];

const handleClick = (option: DropdownOption) => {
  console.log('选中:', option.value, option.content);
};

const handleSelect = (value: string) => {
  console.log('自定义选中:', value);
};
</script>
<style scoped>
.custom-dropdown {
  padding: 8px 0;
  min-width: 120px;
}
.dropdown-item {
  padding: 8px 16px;
  cursor: pointer;
}
.dropdown-item:hover {
  background-color: #f0f0f0;
}
</style>
```
