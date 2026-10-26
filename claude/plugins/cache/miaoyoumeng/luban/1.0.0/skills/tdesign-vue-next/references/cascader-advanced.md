# 级联选择（Cascader）复杂场景

## 适用场景

- 异步加载子级选项。
- 根据上级选择动态更新选项。
- 选择任意一级。
- 多选级联。
- 搜索过滤。
- 自定义面板与触发器。

简单级联使用 `Cascader` + `options` + `v-model` 即可。

## 字段映射

```vue
<template>
  <Cascader
    v-model="selectedValue"
    :options="options"
    :keys="{ value: 'code', label: 'name', children: 'children' }"
    placeholder="请选择地区"
  />
</template>
```

`keys` 与实际字段一致，否则选中与渲染都会异常。

## 异步加载

初始只加载第一级，子级通过 `load` 按需请求：

```vue
<template>
  <Cascader
    v-model="selectedValue"
    :options="options"
    :load="loadOptions"
    :keys="{ value: 'code', label: 'name', children: 'children' }"
    placeholder="请选择地区"
  />
</template>

<script setup lang="ts">
import { ref } from "vue";
import { Cascader } from "tdesign-vue-next";
import type { CascaderOption, CascaderProps } from "tdesign-vue-next";

interface RegionItem {
  code: string;
  name: string;
  children?: RegionItem[] | boolean;
}

const selectedValue = ref<string[]>([]);

const options = ref<RegionItem[]>([
  { code: "330000", name: "浙江省", children: true },
  { code: "320000", name: "江苏省", children: true },
  { code: "440000", name: "广东省", children: true },
]);

const loadOptions: CascaderProps["load"] = async (node): Promise<CascaderOption[]> => {
  const response = await fetch(`/api/regions?parent=${encodeURIComponent(String(node.value))}`);
  const data = await response.json();

  return data.map((item: { code: string; name: string; hasChildren: boolean }) => ({
    code: item.code,
    name: item.name,
    children: item.hasChildren ? true : undefined,
  }));
};
</script>
```

`load` 返回 Promise；叶子节点不要设置 `children: true`。

## 选择任意一级

```vue
<template>
  <Cascader
    v-model="selectedValue"
    :options="options"
    :check-strictly="true"
    placeholder="可选择任意级别"
    @change="onChange"
  />
</template>

<script setup lang="ts">
import { ref } from "vue";
import { Cascader } from "tdesign-vue-next";
import type { CascaderChangeContext, CascaderValue } from "tdesign-vue-next";

const selectedValue = ref<string[]>([]);

const options = ref([
  {
    value: "fruit",
    label: "水果",
    children: [
      { value: "apple", label: "苹果" },
      { value: "banana", label: "香蕉" },
    ],
  },
  {
    value: "vegetable",
    label: "蔬菜",
    children: [
      { value: "cabbage", label: "白菜" },
      { value: "carrot", label: "胡萝卜" },
    ],
  },
]);

const onChange = (value: CascaderValue, context: CascaderChangeContext) => {
  console.log("选中值", value);
  console.log("选中节点", context.node);
};
</script>
```

不设置 `check-strictly` 时，只有叶子节点可选。

## 多选级联

```vue
<template>
  <Cascader
    v-model="selectedValues"
    :options="options"
    multiple
    :min-collapsed-num="2"
    :max="5"
    placeholder="最多选择 5 项"
  />
</template>

<script setup lang="ts">
import { ref } from "vue";
import type { CascaderValue } from "tdesign-vue-next";

const selectedValues = ref<CascaderValue[]>([]);

const options = ref([
  {
    value: "category-1",
    label: "分类 1",
    children: [
      { value: "item-1-1", label: "项目 1-1" },
      { value: "item-1-2", label: "项目 1-2" },
    ],
  },
  {
    value: "category-2",
    label: "分类 2",
    children: [
      { value: "item-2-1", label: "项目 2-1" },
      { value: "item-2-2", label: "项目 2-2" },
    ],
  },
]);
</script>
```

多选值的层级结构要与 `options` 深度一致。

## 搜索过滤

```vue
<template>
  <Cascader
    v-model="selectedValue"
    :options="options"
    filterable
    :filter="customFilter"
    placeholder="支持搜索"
  />
</template>

<script setup lang="ts">
import { ref } from "vue";
import type { CascaderProps } from "tdesign-vue-next";

const selectedValue = ref<string[]>([]);

const options = ref([
  {
    value: "zhejiang",
    label: "浙江省",
    children: [
      {
        value: "hangzhou",
        label: "杭州市",
        children: [{ value: "xihu", label: "西湖区" }],
      },
    ],
  },
]);

const customFilter: CascaderProps["filter"] = (filterWords, node) => {
  const keyword = filterWords.toLowerCase();
  const label = String(node.label ?? "").toLowerCase();
  const value = String(node.value ?? "").toLowerCase();

  return label.includes(keyword) || value.includes(keyword);
};
</script>
```

搜索只匹配当前层级节点时，父级路径也要一并返回，否则结果不可见。

## 自定义面板

```vue
<template>
  <Cascader v-model="selectedValue" :options="options">
    <template #panel="{ cascader }">
      <div class="custom-panel">
        <div class="panel-header">自定义面板头部</div>
        <component :is="cascader" />
        <div class="panel-footer">
          <Button size="small" @click="clearSelection">清除</Button>
          <Button size="small" theme="primary" @click="confirmSelection">确认</Button>
        </div>
      </div>
    </template>
  </Cascader>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { Button, Cascader } from "tdesign-vue-next";

const selectedValue = ref<string[]>([]);

const options = ref([
  {
    value: "1",
    label: "选项 1",
    children: [
      { value: "1-1", label: "选项 1-1" },
      { value: "1-2", label: "选项 1-2" },
    ],
  },
]);

const clearSelection = () => {
  selectedValue.value = [];
};

const confirmSelection = () => {
  console.log("确认选择", selectedValue.value);
};
</script>

<style scoped>
.custom-panel {
  display: flex;
  flex-direction: column;
}

.panel-header {
  padding: 8px 12px;
  border-bottom: 1px solid var(--td-border-level-1-color);
  font-weight: 500;
}

.panel-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  padding: 8px 12px;
  border-top: 1px solid var(--td-border-level-1-color);
}
</style>
```

## 联动更新选项

```vue
<template>
  <Space>
    <Select v-model="category" :options="categories" @change="onCategoryChange" />
    <Cascader
      v-model="selectedValue"
      :options="cascaderOptions"
      :disabled="!category"
      placeholder="请先选择类别"
    />
  </Space>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import { Cascader, Select, Space } from "tdesign-vue-next";

const category = ref("");
const selectedValue = ref<string[]>([]);

const categories = [
  { label: "电子产品", value: "electronics" },
  { label: "服装", value: "clothing" },
];

const optionsMap: Record<string, Array<Record<string, unknown>>> = {
  electronics: [
    {
      value: "phone",
      label: "手机",
      children: [
        { value: "iphone", label: "iPhone" },
        { value: "android", label: "Android" },
      ],
    },
  ],
  clothing: [
    {
      value: "men",
      label: "男装",
      children: [
        { value: "shirt", label: "衬衫" },
        { value: "pants", label: "裤子" },
      ],
    },
  ],
};

const cascaderOptions = computed(() => optionsMap[category.value] ?? []);

const onCategoryChange = () => {
  selectedValue.value = [];
};
</script>
```

类别切换后清空级联选择，避免提交与类别不匹配的值。

