# 组件模式与最佳实践

## 组件分类

### 基础组件（Base Components）

通用、无业务逻辑的 UI 元素，放在 `src/components/base/`：

```vue
<!-- BaseButton.vue -->
<script setup lang="ts">
interface Props {
  variant?: 'primary' | 'secondary' | 'danger'
  size?: 'sm' | 'md' | 'lg'
  disabled?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'primary',
  size: 'md',
  disabled: false
})

const emit = defineEmits<{
  click: [event: MouseEvent]
}>()
</script>

<template>
  <button
    :class="['btn', `btn-${variant}`, `btn-${size}`]"
    :disabled="disabled"
    @click="emit('click', $event)"
  >
    <slot />
  </button>
</template>
```

### 业务组件

包含业务逻辑的组件，放在 `src/components/`：

```vue
<!-- UserList.vue -->
<script setup lang="ts">
import { useUserStore } from '@/stores/user'
import { useFetch } from '@/utils/useFetch'

const userStore = useUserStore()
const { data, loading, error } = useFetch<User[]>('/api/users')
</script>
```

### 页面组件

完整的页面视图，放在 `src/views/`，通常由 `src/pages/` 的页面级组件通过懒加载引入：

```vue
<!-- UserProfile.vue -->
<script setup lang="ts">
import { useRoute } from 'vue-router'
import { useRouteMeta } from '@/routers/guards'
import UserDetail from '@/components/UserDetail.vue'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const userStore = useUserStore()

const userId = computed(() => route.params.id as string)

onMounted(async () => {
  await userStore.fetchUser(userId.value)
})
</script>
```

## Props 设计原则

1. **使用接口而非内联类型**：复杂 props 应定义独立的 interface
2. **设置合理的默认值**：使用 `withDefaults` 提供默认值
3. **验证必要字段**：关键 props 应标记为必填

## 事件设计原则

1. **具名元组语法**：`defineEmits<{ update: [value: string] }>()`
2. **事件名使用动词**：`update`、`delete`、`submit`
3. **避免事件嵌套**：不要在事件回调中触发其他事件

## 插槽使用

```vue
<template>
  <div class="card">
    <header><slot name="header" /></header>
    <main><slot /></main>
    <footer><slot name="footer" /></footer>
  </div>
</template>
```

## 性能优化

1. **大列表使用 `vue-virtual-scroller`**
2. **计算属性缓存**：复杂计算用 `computed`
3. **避免不必要的响应**：使用 `shallowRef` 处理深层数据
4. **路由懒加载**：`() => import('@/views/xxx.vue')` 在 `src/routers/` 中按需加载页面
