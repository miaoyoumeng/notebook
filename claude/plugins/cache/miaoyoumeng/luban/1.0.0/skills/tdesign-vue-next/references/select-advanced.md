# 选择器（Select）复杂场景

## 适用场景

- 远程搜索。
- 大数据量选项与虚拟滚动。
- 分页加载选项。
- 自定义选项渲染。
- 多选上限与标签折叠。
- 创建新选项。
- 分组选项与联动选择。

简单下拉使用 `Select` + `options` + `v-model` 即可。

## 远程搜索

远程搜索必须关闭本地过滤，让服务端决定结果：

```vue
<template>
  <Select
    v-model="selectedValue"
    filterable
    :filter="() => true"
    :options="options"
    :loading="loading"
    placeholder="输入关键字搜索"
    @search="onSearch"
  />
</template>

<script setup lang="ts">
import { ref } from "vue";
import { Select } from "tdesign-vue-next";
import type { SelectOption } from "tdesign-vue-next";

const selectedValue = ref("");
const options = ref<SelectOption[]>([]);
const loading = ref(false);

let timer: ReturnType<typeof setTimeout> | undefined;

const onSearch = (keyword: string) => {
  clearTimeout(timer);

  if (!keyword) {
    options.value = [];
    return;
  }

  timer = setTimeout(async () => {
    loading.value = true;
    try {
      const response = await fetch(`/api/search?keyword=${encodeURIComponent(keyword)}`);
      const data = await response.json();
      options.value = data.map((item: { id: string; name: string }) => ({
        label: item.name,
        value: item.id,
      }));
    } finally {
      loading.value = false;
    }
  }, 300);
};
</script>
```

`filterable` 打开搜索输入，`:filter="() => true"` 阻止组件再次过滤服务端结果。

## 分页加载

通过 `popup-props` 监听下拉滚动，滚动到底部时加载下一页：

```vue
<template>
  <Select
    v-model="selectedValue"
    :options="options"
    :loading="loading"
    :popup-props="{ onScroll: onPopupScroll }"
  />
</template>

<script setup lang="ts">
import { ref } from "vue";
import { Select } from "tdesign-vue-next";
import type { SelectOption } from "tdesign-vue-next";

const selectedValue = ref("");
const options = ref<SelectOption[]>([]);
const loading = ref(false);
const page = ref(1);
const hasMore = ref(true);

const fetchOptions = async (pageNum: number) => {
  if (loading.value || !hasMore.value) return;

  loading.value = true;
  try {
    const response = await fetch(`/api/options?page=${pageNum}&pageSize=20`);
    const { data, total } = await response.json();
    const nextOptions = data.map((item: { id: string; name: string }) => ({
      label: item.name,
      value: item.id,
    }));

    options.value = pageNum === 1 ? nextOptions : [...options.value, ...nextOptions];
    hasMore.value = options.value.length < total;
    page.value = pageNum;
  } finally {
    loading.value = false;
  }
};

const onPopupScroll = (context: { e: Event }) => {
  const target = context.e.target as HTMLElement;
  const { scrollTop, scrollHeight, clientHeight } = target;

  if (scrollTop + clientHeight >= scrollHeight - 20) {
    fetchOptions(page.value + 1);
  }
};

fetchOptions(1);
</script>
```

首次展开前先加载一页，避免下拉为空。

## 虚拟滚动

```vue
<template>
  <Select
    v-model="selectedValue"
    :options="largeOptions"
    :scroll="{ type: 'virtual' }"
    :popup-props="{ overlayInnerStyle: { maxHeight: '300px' } }"
  />
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import type { SelectOption } from "tdesign-vue-next";

const selectedValue = ref("");

const largeOptions = computed<SelectOption[]>(() =>
  Array.from({ length: 10000 }, (_, index) => ({
    label: `选项 ${index + 1}`,
    value: index + 1,
  })),
);
</script>
```

选项超过 1000 条时启用虚拟滚动，并限制下拉高度。

## 自定义选项

```vue
<template>
  <Select v-model="selectedValue" :options="options">
    <template #option="{ option }">
      <div class="custom-option">
        <Avatar :image="option.avatar" size="small" />
        <span class="name">{{ option.label }}</span>
        <span class="desc">{{ option.description }}</span>
      </div>
    </template>
  </Select>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { Avatar, Select } from "tdesign-vue-next";

const selectedValue = ref("");
const options = ref([
  { label: "张三", value: 1, avatar: "/avatar-1.png", description: "前端工程师" },
  { label: "李四", value: 2, avatar: "/avatar-2.png", description: "后端工程师" },
]);
</script>

<style scoped>
.custom-option {
  display: flex;
  align-items: center;
  gap: 8px;
}

.name {
  font-weight: 500;
}

.desc {
  color: var(--td-text-color-secondary);
  font-size: 12px;
}
</style>
```

## 多选上限

```vue
<template>
  <Select
    v-model="selectedValues"
    multiple
    :max="3"
    :min-collapsed-num="2"
    :options="options"
    :tag-props="{ closable: true }"
    placeholder="最多选择 3 项"
  />
</template>

<script setup lang="ts">
import { ref } from "vue";

const selectedValues = ref<number[]>([]);
const options = ref([
  { label: "选项 1", value: 1 },
  { label: "选项 2", value: 2 },
  { label: "选项 3", value: 3 },
  { label: "选项 4", value: 4 },
  { label: "选项 5", value: 5 },
]);
</script>
```

`min-collapsed-num` 控制标签折叠数量，超出部分显示为 `+N`。

## 创建新选项

```vue
<template>
  <Select
    v-model="selectedValue"
    filterable
    creatable
    :options="options"
    placeholder="输入或选择"
    @create="onCreate"
  />
</template>

<script setup lang="ts">
import { ref } from "vue";
import type { SelectOption } from "tdesign-vue-next";

const selectedValue = ref("");
const options = ref<SelectOption[]>([
  { label: "选项 1", value: "option-1" },
  { label: "选项 2", value: "option-2" },
]);

const onCreate = (value: string) => {
  options.value.push({ label: value, value });
};
</script>
```

## 联动选择

```vue
<template>
  <Space>
    <Select
      v-model="province"
      :options="provinceOptions"
      placeholder="选择省份"
      @change="onProvinceChange"
    />
    <Select
      v-model="city"
      :options="cityOptions"
      :disabled="!province"
      placeholder="选择城市"
    />
  </Space>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import { Select, Space } from "tdesign-vue-next";

const province = ref("");
const city = ref("");

const provinceOptions = ref([
  { label: "广东省", value: "guangdong" },
  { label: "浙江省", value: "zhejiang" },
]);

const cityData: Record<string, Array<{ label: string; value: string }>> = {
  guangdong: [
    { label: "广州", value: "guangzhou" },
    { label: "深圳", value: "shenzhen" },
  ],
  zhejiang: [
    { label: "杭州", value: "hangzhou" },
    { label: "宁波", value: "ningbo" },
  ],
};

const cityOptions = computed(() => (province.value ? cityData[province.value] ?? [] : []));

const onProvinceChange = () => {
  city.value = "";
};
</script>
```

上级变化时清空下级值，避免提交不匹配的组合。

## 常见问题

### 远程搜索首次展开无数据

初始化时加载一页默认选项，或在首次展开时触发搜索。

### 多选标签换行过多

设置 `min-collapsed-num`，超出部分折叠。

### 选项需要展示更多信息

使用 `#option` 插槽自定义渲染，不要把所有信息拼进 `label`。

### 如何清除选择

设置 `clearable`，用户可点击清除图标。

### 键盘导航

Select 默认支持方向键切换、`Enter` 选中、`Esc` 关闭。

