# 选择器（Select）补充场景

## 适用场景

- 分组选项。
- 前缀图标。
- 分组与搜索同时使用。

本文只覆盖分组与图标两类配置。

## 分组选项

```vue
<template>
  <Select v-model="selectedValue" :options="groupedOptions" />
</template>

<script setup lang="ts">
import { ref } from "vue";

const selectedValue = ref("");
const groupedOptions = ref([
  {
    label: "华东地区",
    group: "east",
    children: [
      { label: "上海", value: "shanghai" },
      { label: "杭州", value: "hangzhou" },
      { label: "南京", value: "nanjing" },
    ],
  },
  {
    label: "华南地区",
    group: "south",
    children: [
      { label: "广州", value: "guangzhou" },
      { label: "深圳", value: "shenzhen" },
    ],
  },
]);
</script>
```

分组项使用 `label`、`group`、`children`。父级只做分组标题，不作为可选项。

## 前缀图标

```vue
<template>
  <Select v-model="selectedValue" :options="options">
    <template #prefixIcon>
      <SearchIcon />
    </template>
  </Select>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { Select } from "tdesign-vue-next";
import { SearchIcon } from "tdesign-icons-vue-next";

const selectedValue = ref("");
const options = ref([
  { label: "选项 1", value: 1 },
  { label: "选项 2", value: 2 },
]);
</script>
```

图标从 `tdesign-icons-vue-next` 引入，不手写 SVG。

## 分组与搜索

开启 `filterable` 时，组件按叶子选项的 `label` 过滤。分组标题不参与匹配；需要按分组名搜索时，在业务层过滤 `options` 后传入新数组。

```vue
<template>
  <Space direction="vertical" style="width: 100%">
    <Input v-model="keyword" placeholder="搜索分组或选项" />
    <Select v-model="selectedValue" filterable :options="filteredOptions" />
  </Space>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import { Input, Select, Space } from "tdesign-vue-next";

const selectedValue = ref("");
const keyword = ref("");
const groupedOptions = ref([
  {
    label: "华东地区",
    group: "east",
    children: [{ label: "上海", value: "shanghai" }],
  },
]);

const filteredOptions = computed(() => {
  if (!keyword.value) return groupedOptions.value;
  return groupedOptions.value
    .map((group) => ({
      ...group,
      children: group.children.filter((item) =>
        item.label.includes(keyword.value),
      ),
    }))
    .filter((group) => group.children.length > 0);
});
</script>
```

## 常见问题

### 分组标题被当作可选项

分组项不要设置 `value`，只保留 `label`、`group`、`children`。

### 前缀图标不显示

确认插槽名是 `prefixIcon`，图标组件已从 `tdesign-icons-vue-next` 导入。

## 必须避免

- 把分组标题写成普通选项。
- 使用未导入的图标组件。
- 在 `options` 上直接原地过滤，导致原始分组数据丢失。
