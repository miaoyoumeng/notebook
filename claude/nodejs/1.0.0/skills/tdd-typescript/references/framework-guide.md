# Vue 3 + TDesign + Vitest 测试指南

---

## 项目搭建

### 安装依赖

```bash
pnpm add -D vitest @vue/test-utils @vitejs/plugin-vue jsdom
```

### vite.config.ts

```typescript
/// <reference types="vitest" />
import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';

export default defineConfig({
  plugins: [vue()],
  test: {
    globals: true,
    environment: 'jsdom',
    include: ['src/**/*.test.ts'],
    coverage: {
      provider: 'v8',
      include: ['src/**/*.ts', 'src/**/*.vue'],
      exclude: ['src/**/*.d.ts', 'src/**/index.ts'],
      thresholds: {
        lines: 80,
        branches: 75,
        functions: 90,
      },
    },
  },
});
```

### package.json scripts

```json
{
  "scripts": {
    "test": "vitest run",
    "test:watch": "vitest",
    "test:coverage": "vitest run --coverage",
    "test:ui": "vitest --ui"
  }
}
```

---

## 常用 Vitest 匹配器

```typescript
// 值匹配
expect(value).toBe(expected);           // ===
expect(value).toEqual(expected);        // 深度相等
expect(value).not.toBe(expected);       // 否定

// 真值
expect(value).toBeNull();
expect(value).toBeDefined();
expect(value).toBeTruthy();
expect(value).toBeFalsy();

// 异常
expect(() => fn()).toThrow(Error);
expect(() => fn()).toThrow('message');

// 异步
await expect(promise).resolves.toBe(value);
await expect(promise).rejects.toThrow();

// Mock
expect(mockFn).toHaveBeenCalled();
expect(mockFn).toHaveBeenCalledTimes(2);
expect(mockFn).toHaveBeenCalledWith(arg);

// 快照
expect(value).toMatchSnapshot();
expect(value).toMatchInlineSnapshot();

// 并发测试
it.concurrent('test', async () => { ... });
describe.concurrent('suite', () => { ... });
```

---

## 纯函数 / 工具函数测试

```typescript
// formatDate.ts
export function formatDate(date: Date, format: string): string {
  const map: Record<string, string> = {
    YYYY: String(date.getFullYear()),
    MM: String(date.getMonth() + 1).padStart(2, '0'),
    DD: String(date.getDate()).padStart(2, '0'),
  };
  return format.replace(/YYYY|MM|DD/g, (k) => map[k]);
}

// formatDate.test.ts
import { describe, it, expect } from 'vitest';
import { formatDate } from './formatDate';

describe('formatDate', () => {
  it('should format date with YYYY-MM-DD', () => {
    const date = new Date('2026-01-15');
    expect(formatDate(date, 'YYYY-MM-DD')).toBe('2026-01-15');
  });

  it('should handle single digit month and day', () => {
    const date = new Date('2026-03-05');
    expect(formatDate(date, 'YYYY-MM-DD')).toBe('2026-03-05');
  });
});
```

---

## Composable 测试

```typescript
// useDebounce.ts
import { ref, watch } from 'vue';

export function useDebounce<T>(source: Ref<T>, delay = 300) {
  const debounced = ref(source.value) as Ref<T>;

  let timer: ReturnType<typeof setTimeout>;
  watch(source, (val) => {
    clearTimeout(timer);
    timer = setTimeout(() => {
      debounced.value = val;
    }, delay);
  });

  return { debounced };
}

// useDebounce.test.ts
import { describe, it, expect, vi } from 'vitest';
import { ref, nextTick } from 'vue';
import { useDebounce } from './useDebounce';

describe('useDebounce', () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('should return initial value immediately', () => {
    const source = ref('hello');
    const { debounced } = useDebounce(source, 300);
    expect(debounced.value).toBe('hello');
  });

  it('should debounce value changes', async () => {
    const source = ref('hello');
    const { debounced } = useDebounce(source, 300);

    source.value = 'world';
    await nextTick();
    expect(debounced.value).toBe('hello'); // 尚未更新

    vi.advanceTimersByTime(300);
    expect(debounced.value).toBe('world'); // 延迟后更新
  });
});
```

---

## TDesign 组件测试

### Table 组件测试

```typescript
// UserTable.test.ts
import { describe, it, expect, vi } from 'vitest';
import { mount } from '@vue/test-utils';
import TDesign from 'tdesign-vue-next';
import UserTable from './UserTable.vue';

const mockUsers = [
  { id: '1', name: 'Alice', email: 'alice@example.com', role: 'admin' },
  { id: '2', name: 'Bob', email: 'bob@example.com', role: 'user' },
];

function createWrapper(props = {}) {
  return mount(UserTable, {
    props: { users: mockUsers, ...props },
    global: { plugins: [TDesign] },
  });
}

describe('UserTable', () => {
  it('should render correct number of rows', () => {
    const wrapper = createWrapper();
    expect(wrapper.findAll('tbody tr')).toHaveLength(2);
  });

  it('should display user data correctly', () => {
    const wrapper = createWrapper();
    const firstRow = wrapper.findAll('tbody tr')[0];
    expect(firstRow.text()).toContain('Alice');
    expect(firstRow.text()).toContain('alice@example.com');
  });

  it('should emit row-click event', async () => {
    const wrapper = createWrapper();
    await wrapper.find('tbody tr:first-child').trigger('click');
    expect(wrapper.emitted('row-click')).toBeTruthy();
  });

  it('should show empty state when no data', () => {
    const wrapper = mount(UserTable, {
      props: { users: [] },
      global: { plugins: [TDesign] },
    });
    expect(wrapper.text()).toContain('暂无数据');
  });

  it('should render pagination when total exceeds page size', () => {
    const manyUsers = Array.from({ length: 25 }, (_, i) => ({
      id: String(i), name: `User${i}`, email: `user${i}@example.com`,
    }));
    const wrapper = createWrapper({ users: manyUsers });
    expect(wrapper.find('.t-pagination').exists()).toBe(true);
  });
});
```

### Dialog / Form 组件测试

```typescript
// CreateUserDialog.test.ts
import { describe, it, expect } from 'vitest';
import { mount } from '@vue/test-utils';
import TDesign from 'tdesign-vue-next';
import CreateUserDialog from './CreateUserDialog.vue';

describe('CreateUserDialog', () => {
  const createWrapper = () => mount(CreateUserDialog, {
    props: { visible: true },
    global: { plugins: [TDesign] },
  });

  it('should validate required name field', async () => {
    const wrapper = createWrapper();
    const nameInput = wrapper.find('[data-test="name-input"]');

    await nameInput.setValue('');
    await nameInput.trigger('blur');

    expect(wrapper.text()).toContain('请输入用户名');
  });

  it('should emit confirm with form data when valid', async () => {
    const wrapper = createWrapper();

    await wrapper.find('[data-test="name-input"]').setValue('Alice');
    await wrapper.find('[data-test="email-input"]').setValue('alice@example.com');
    await wrapper.find('[data-test="confirm-btn"]').trigger('click');

    expect(wrapper.emitted('confirm')).toBeTruthy();
    expect(wrapper.emitted('confirm')![0][0]).toMatchObject({
      name: 'Alice',
      email: 'alice@example.com',
    });
  });

  it('should emit cancel on close', async () => {
    const wrapper = createWrapper();
    await wrapper.find('[data-test="cancel-btn"]').trigger('click');
    expect(wrapper.emitted('cancel')).toBeTruthy();
  });
});
```

---

## Mock 策略

### 模块 Mock

```typescript
vi.mock('./api', () => ({
  fetchUsers: vi.fn().mockResolvedValue([{ id: '1', name: 'Alice' }]),
  deleteUser: vi.fn().mockResolvedValue({ success: true }),
}));
```

### 定时器 Mock

```typescript
beforeEach(() => {
  vi.useFakeTimers();
});

afterEach(() => {
  vi.useRealTimers();
});
```

### Mock 函数

```typescript
const onClick = vi.fn();
const wrapper = mount(MyButton, {
  props: { onClick },
});
await wrapper.trigger('click');
expect(onClick).toHaveBeenCalledTimes(1);
```

### Pinia Store Mock

```typescript
import { setActivePinia, createPinia } from 'pinia';

beforeEach(() => {
  setActivePinia(createPinia());
});

// 或 mock 一个 store
vi.mock('@/stores/user', () => ({
  useUserStore: () => ({
    currentUser: ref({ id: '1', name: 'Test' }),
    login: vi.fn(),
    logout: vi.fn(),
  }),
}));
```

---

## 覆盖率输出

### Vitest (v8)

```bash
pnpm vitest run --coverage --coverage.reporter=json --coverage.reporter=lcov
```

生成文件：
- `coverage/lcov.info` — LCOV 格式
- `coverage/coverage-final.json` — JSON 格式
