# 测试策略与示例

## 测试层级

```
┌─────────────────┐
│   E2E (10%)     │  Playwright - 关键用户流程
├─────────────────┤
│  Component(70%) │  Vue Test Utils - 组件渲染和交互
├─────────────────┤
│  Unit (20%)     │  Vitest - 工具函数、composables
└─────────────────┘
```

## 单元测试（Vitest）

```ts
// utils/formatDate.test.ts
import { describe, it, expect } from 'vitest'
import { formatDate } from './formatDate'

describe('formatDate', () => {
  it('formats ISO date to locale string', () => {
    expect(formatDate('2024-01-15T10:30:00Z')).toBe('2024年1月15日')
  })

  it('returns empty string for invalid date', () => {
    expect(formatDate('not-a-date')).toBe('')
  })
})
```

## Composable 测试

```ts
// utils/useCounter.test.ts
import { describe, it, expect } from 'vitest'
import { useCounter } from './useCounter'
import { useSetup } from '@vue/test-utils'

describe('useCounter', () => {
  it('increments correctly', () => {
    const wrapper = useSetup(() => {
      const { count, increment } = useCounter()
      return { count, increment }
    })

    expect(wrapper.count).toBe(0)
    wrapper.increment()
    expect(wrapper.count).toBe(1)
  })
})
```

## 组件测试（Vue Test Utils）

```ts
// components/UserCard.test.ts
import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import UserCard from './UserCard.vue'

describe('UserCard', () => {
  const defaultProps = {
    user: { id: '1', name: '张三', email: 'test@example.com' }
  }

  it('renders user name', () => {
    const wrapper = mount(UserCard, { props: defaultProps })
    expect(wrapper.text()).toContain('张三')
  })

  it('emits delete event on button click', async () => {
    const wrapper = mount(UserCard, { props: defaultProps })
    await wrapper.find('[data-testid="delete-btn"]').trigger('click')
    expect(wrapper.emitted('delete')).toHaveLength(1)
  })

  it('shows loading state', () => {
    const wrapper = mount(UserCard, {
      props: { ...defaultProps, loading: true }
    })
    expect(wrapper.find('.loading-spinner').exists()).toBe(true)
  })
})
```

## E2E 测试（Playwright）

```ts
// e2e/login.spec.ts
import { test, expect } from '@playwright/test'

test('user can login successfully', async ({ page }) => {
  await page.goto('/login')
  await page.fill('[name="email"]', 'test@example.com')
  await page.fill('[name="password"]', 'password123')
  await page.click('button[type="submit"]')

  await expect(page).toHaveURL('/dashboard')
  await expect(page.locator('text=Welcome')).toBeVisible()
})

test('shows error on invalid credentials', async ({ page }) => {
  await page.goto('/login')
  await page.fill('[name="email"]', 'wrong@example.com')
  await page.fill('[name="password"]', 'wrong')
  await page.click('button[type="submit"]')

  await expect(page.locator('.error-message')).toBeVisible()
})
```

## Mock API 请求

```ts
// 使用 vitest 模拟 API
import { vi } from 'vitest'
import { userApi } from '@/api/user'  // API 接口定义在 src/api/ 下

vi.mock('@/api/user', () => ({
  userApi: {
    getAll: vi.fn().mockResolvedValue({
      data: [{ id: '1', name: '张三' }]
    })
  }
}))
```

## 测试配置

```ts
// vitest.config.ts
import { defineConfig } from 'vitest/config'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/test/setup.ts'
  }
})
```
