# 检查元素属性

快照未显示元素的 `id`、`class`、`data-*` 属性或其他 DOM 属性时，用 `eval` 读取。

## 示例

```bash
playwright-cli snapshot
# 快照把按钮显示为 e7，但未暴露 id 与 data 属性

# 读取元素 id
playwright-cli eval "el => el.id" e7

# 读取全部 CSS 类名
playwright-cli eval "el => el.className" e7

# 读取指定属性
playwright-cli eval "el => el.getAttribute('data-testid')" e7
playwright-cli eval "el => el.getAttribute('aria-label')" e7

# 读取计算样式
playwright-cli eval "el => getComputedStyle(el).display" e7
```
