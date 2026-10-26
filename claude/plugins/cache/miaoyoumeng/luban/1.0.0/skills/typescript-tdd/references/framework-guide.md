# TypeScript + Vitest 测试指南

## 安装依赖

```bash
pnpm add -D vitest @vitest/coverage-v8
```

## 测试配置

`vite.config.ts` 或 `vitest.config.ts`：

```typescript
/// <reference types="vitest" />
import { defineConfig } from 'vite';

export default defineConfig({
  test: {
    globals: true,
    environment: 'node',
    include: ['test/**/*.test.ts'],
    coverage: {
      provider: 'v8',
      include: ['src/**/*.ts'],
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

`package.json` 脚本：

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

## 测试文件组织

测试文件放在与 `src` 同级的 `test` 目录，目录结构镜像 `src`：

```text
src/
├── utils/formatPrice.ts
├── services/payment.ts
└── types/user.ts
test/
├── utils/formatPrice.mock.test.ts
├── utils/formatPrice.real.test.ts
├── services/payment.mock.test.ts
└── services/payment.real.test.ts
```

- mock 测试：隔离外部依赖，文件后缀 `*.mock.test.ts`。
- 真实测试：使用真实依赖，文件后缀 `*.real.test.ts`。

## 常用匹配器

```typescript
expect(value).toBe(expected);            // 严格相等
expect(value).toEqual(expected);         // 深度相等
expect(value).not.toBe(expected);        // 否定
expect(value).toBeNull();
expect(value).toBeDefined();
expect(value).toBeTruthy();
expect(value).toBeFalsy();
expect(() => fn()).toThrow(Error);
expect(() => fn()).toThrow('message');
await expect(promise).resolves.toBe(value);
await expect(promise).rejects.toThrow();
expect(mockFn).toHaveBeenCalled();
expect(mockFn).toHaveBeenCalledTimes(2);
expect(mockFn).toHaveBeenCalledWith(arg);
expect(value).toMatchSnapshot();
expect(value).toMatchInlineSnapshot();
```

## 纯函数测试

```typescript
// src/utils/formatDate.ts
export const formatDate = (date: Date, format: string): string => {
  const map: Record<string, string> = {
    YYYY: String(date.getFullYear()),
    MM: String(date.getMonth() + 1).padStart(2, '0'),
    DD: String(date.getDate()).padStart(2, '0'),
  };
  return format.replace(/YYYY|MM|DD/g, (key) => map[key]);
};

// test/utils/formatDate.real.test.ts
import { describe, expect, it } from 'vitest';
import { formatDate } from '../../src/utils/formatDate';

describe('formatDate', () => {
  it('shouldFormatDate_whenUsingYearMonthDay', () => {
    expect(formatDate(new Date('2026-01-15'), 'YYYY-MM-DD')).toBe('2026-01-15');
  });

  it('shouldPadSingleDigitMonthAndDay', () => {
    expect(formatDate(new Date('2026-03-05'), 'YYYY-MM-DD')).toBe('2026-03-05');
  });
});
```

## 异步函数测试

```typescript
// src/services/user.ts
export const fetchUser = async (id: string): Promise<{ id: string; name: string }> => {
  const response = await fetch(`/api/users/${id}`);
  if (!response.ok) throw new Error(`Failed to fetch user: ${id}`);
  return response.json();
};

// test/services/user.mock.test.ts
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { fetchUser } from '../../src/services/user';

describe('fetchUser', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('shouldReturnUser_whenRequestSucceeds', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue({
      ok: true,
      json: async () => ({ id: '1', name: 'Alice' }),
    } as Response);

    const user = await fetchUser('1');
    expect(user).toEqual({ id: '1', name: 'Alice' });
  });

  it('shouldThrow_whenRequestFails', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue({ ok: false } as Response);

    await expect(fetchUser('1')).rejects.toThrow('Failed to fetch user: 1');
  });
});
```

## Mock 策略

模块 mock：

```typescript
vi.mock('../../src/api/user', () => ({
  fetchUsers: vi.fn().mockResolvedValue([{ id: '1', name: 'Alice' }]),
  deleteUser: vi.fn().mockResolvedValue({ success: true }),
}));
```

定时器 mock：

```typescript
beforeEach(() => {
  vi.useFakeTimers();
});

afterEach(() => {
  vi.useRealTimers();
});
```

Mock 函数：

```typescript
const onClick = vi.fn();
onClick('confirm');
expect(onClick).toHaveBeenCalledTimes(1);
expect(onClick).toHaveBeenCalledWith('confirm');
```

## 覆盖率输出

```bash
pnpm vitest run --coverage --coverage.reporter=json-summary --coverage.reporter=lcov
```

生成文件：

- `coverage/lcov.info`：LCOV 格式。
- `coverage/coverage-summary.json`：JSON 摘要。
- `coverage/coverage-final.json`：详细 JSON。
