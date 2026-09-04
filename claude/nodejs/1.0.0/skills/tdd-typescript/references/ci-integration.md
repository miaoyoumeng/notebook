# CI 集成指南

---

## GitHub Actions — Vite + Vitest + pnpm

```yaml
name: Test & Coverage

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: pnpm/action-setup@v4
        with:
          version: 9

      - uses: actions/setup-node@v4
        with:
          node-version: 22
          cache: 'pnpm'

      - run: pnpm install
      - run: pnpm vitest run --coverage

      - name: Check coverage thresholds
        run: |
          COV=$(cat coverage/coverage-summary.json | jq '.total.lines.pct')
          UNDER=$(echo "$COV < 80" | bc -l)
          if [ "$UNDER" -eq 1 ]; then
            echo "Coverage $COV% is below 80%"
            exit 1
          fi

      - name: Upload coverage
        uses: actions/upload-artifact@v4
        with:
          name: coverage-report
          path: coverage/
```

---

## 覆盖率门禁

在 `vite.config.ts` 中设置阈值：

```typescript
export default defineConfig({
  test: {
    coverage: {
      thresholds: {
        lines: 80,
        branches: 75,
        functions: 90,
        statements: 80,
      },
    },
  },
});
```

当覆盖率低于阈值时，Vitest 会自动返回非零退出码，使 CI 构建失败。

---

## 并行化

```bash
# 默认使用线程池并行
pnpm vitest run

# 限制线程数
pnpm vitest run --poolOptions.threads.maxThreads=4
```

---

## 缓存加速

```yaml
- uses: actions/cache@v4
  with:
    path: node_modules/.vite
    key: vitest-${{ runner.os }}-${{ hashFiles('pnpm-lock.yaml') }}
```
