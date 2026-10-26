# 级联选择（Cascader）补充场景

## 适用场景

- 自定义触发器。
- 读取完整选中路径。
- 省市区三级联动。

本文只覆盖自定义触发器、路径读取与联动实现。

## 自定义触发器

```vue
<template>
  <Cascader v-model="selectedValue" :options="options">
    <template #trigger="{ selectedOptions, visible }">
      <div :class="['custom-trigger', { active: visible }]">
        <span v-if="selectedOptions.length">
          {{ selectedOptions.map((option) => option.label).join(" / ") }}
        </span>
        <span v-else class="placeholder">请选择</span>
        <ChevronDownIcon :class="['icon', { rotate: visible }]" />
      </div>
    </template>
  </Cascader>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { Cascader } from "tdesign-vue-next";
import { ChevronDownIcon } from "tdesign-icons-vue-next";

const selectedValue = ref<string[]>([]);

const options = ref([
  {
    value: "1",
    label: "选项 1",
    children: [{ value: "1-1", label: "选项 1-1" }],
  },
]);
</script>

<style scoped>
.custom-trigger {
  display: flex;
  align-items: center;
  justify-content: space-between;
  min-width: 200px;
  padding: 8px 12px;
  border: 1px solid var(--td-border-level-2-color);
  border-radius: var(--td-radius-default);
  cursor: pointer;
}

.custom-trigger.active {
  border-color: var(--td-brand-color);
}

.placeholder {
  color: var(--td-text-color-placeholder);
}

.icon {
  transition: transform 0.2s;
}

.icon.rotate {
  transform: rotate(180deg);
}
</style>
```

触发器插槽提供 `selectedOptions` 与 `visible`，用于展示完整路径与展开状态。

## 读取完整选中路径

```ts
const onChange = (
  value: unknown,
  context: { selectedOptions: Array<{ label: string }> },
) => {
  const path = context.selectedOptions.map((option) => option.label).join("/");
  console.log("路径", path, value);
};
```

`value` 是选中值，`context.selectedOptions` 是从根到叶的节点数组。

## 省市区三级联动

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

const selectedValue = ref<string[]>([]);

const options = ref([
  { code: "330000", name: "浙江省", children: true },
  { code: "320000", name: "江苏省", children: true },
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

省市区数据按层级请求，避免一次性加载全部地区。叶子节点不要设置 `children: true`。

## 常见问题

### 异步加载后选项不显示

检查返回字段与 `keys` 是否一致；检查 `load` 是否返回 Promise。

### 联动切换后旧值残留

上级选项变化时清空下级 `v-model` 值，避免提交不匹配的组合。

## 必须避免

- `load` 返回非 Promise。
- 直接修改原 `options` 数组而不替换引用。
- 多级选项 `value` 重复。
- 需要选择任意级别却未设置 `check-strictly`。
- 上级切换后不清空下级值。
