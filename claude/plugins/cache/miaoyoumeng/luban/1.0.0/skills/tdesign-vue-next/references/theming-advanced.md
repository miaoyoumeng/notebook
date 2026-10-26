# 主题定制（Theming）复杂场景

## 适用场景

- 修改品牌色与功能色。
- 运行时切换主题。
- 多品牌或多租户主题。
- 组件级样式覆盖。
- 按屏幕尺寸调整组件尺寸。
- 持久化用户主题配置。

只改一个品牌色时，覆盖 `--td-brand-color` 即可；本文档用于多 token 与动态主题。

## CSS 变量体系

TDesign 的主题由 CSS 变量驱动。常用变量：

```css
:root {
  /* 品牌色 */
  --td-brand-color: #0052d9;
  --td-brand-color-hover: #0034b5;
  --td-brand-color-active: #002a9c;
  --td-brand-color-light: #f2f3ff;

  /* 功能色 */
  --td-error-color: #e34d59;
  --td-warning-color: #ed7b2f;
  --td-success-color: #00a870;

  /* 文字色 */
  --td-text-color-primary: rgba(0, 0, 0, 0.9);
  --td-text-color-secondary: rgba(0, 0, 0, 0.6);
  --td-text-color-placeholder: rgba(0, 0, 0, 0.4);
  --td-text-color-disabled: rgba(0, 0, 0, 0.26);

  /* 背景色 */
  --td-bg-color-page: #f3f3f3;
  --td-bg-color-container: #ffffff;

  /* 边框 */
  --td-border-level-1-color: #e7e7e7;
  --td-border-level-2-color: #dcdcdc;

  /* 圆角 */
  --td-radius-small: 3px;
  --td-radius-default: 6px;
  --td-radius-medium: 9px;
  --td-radius-large: 12px;

  /* 阴影 */
  --td-shadow-1: 0 1px 10px rgba(0, 0, 0, 0.05);
  --td-shadow-2: 0 3px 14px 2px rgba(0, 0, 0, 0.03);
  --td-shadow-3: 0 6px 30px 5px rgba(0, 0, 0, 0.05);
}
```

自定义样式必须在组件库样式之后引入：

```ts
// main.ts
import "tdesign-vue-next/es/style/index.css";
import "./styles/theme.css";
```

## 修改品牌色

```css
/* styles/theme.css */
:root {
  --td-brand-color: #722ed1;
  --td-brand-color-hover: #531dab;
  --td-brand-color-active: #391085;
  --td-brand-color-light: #f9f0ff;
}
```

品牌色通常需要同时提供 hover、active、light 三档，否则交互态会回落到默认蓝色。

## 运行时切换主题

```vue
<template>
  <ConfigProvider>
    <Space>
      <span>主题：</span>
      <RadioGroup v-model="currentTheme" @change="onThemeChange">
        <Radio value="default">默认</Radio>
        <Radio value="blue">蓝色</Radio>
        <Radio value="green">绿色</Radio>
        <Radio value="purple">紫色</Radio>
      </RadioGroup>
    </Space>
    <Divider />
    <Button theme="primary">主题按钮</Button>
  </ConfigProvider>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import {
  Button,
  ConfigProvider,
  Divider,
  Radio,
  RadioGroup,
  Space,
} from "tdesign-vue-next";

type ThemeName = "default" | "blue" | "green" | "purple";

const currentTheme = ref<ThemeName>("default");

const themes: Record<ThemeName, Record<string, string>> = {
  default: {
    "--td-brand-color": "#0052d9",
    "--td-brand-color-hover": "#0034b5",
    "--td-brand-color-active": "#002a9c",
  },
  blue: {
    "--td-brand-color": "#1890ff",
    "--td-brand-color-hover": "#40a9ff",
    "--td-brand-color-active": "#096dd9",
  },
  green: {
    "--td-brand-color": "#52c41a",
    "--td-brand-color-hover": "#73d13d",
    "--td-brand-color-active": "#389e0d",
  },
  purple: {
    "--td-brand-color": "#722ed1",
    "--td-brand-color-hover": "#9254de",
    "--td-brand-color-active": "#531dab",
  },
};

const applyTheme = (name: ThemeName) => {
  const root = document.documentElement;
  Object.entries(themes[name]).forEach(([key, value]) => {
    root.style.setProperty(key, value);
  });
};

const onThemeChange = (name: ThemeName) => {
  applyTheme(name);
  localStorage.setItem("theme", name);
};

onMounted(() => {
  const saved = localStorage.getItem("theme") as ThemeName | null;
  if (saved && themes[saved]) {
    currentTheme.value = saved;
    applyTheme(saved);
  }
});
</script>
```

CSS 变量在运行时生效，组件不需要重新挂载。

## 多品牌主题

```ts
// themes/brand-a.ts
export const brandATheme = {
  "--td-brand-color": "#ff6b00",
  "--td-brand-color-hover": "#ff8533",
  "--td-brand-color-active": "#cc5500",
  "--td-brand-color-light": "#fff2e8",
};

// themes/brand-b.ts
export const brandBTheme = {
  "--td-brand-color": "#00b96b",
  "--td-brand-color-hover": "#20c77c",
  "--td-brand-color-active": "#009456",
  "--td-brand-color-light": "#e8fff5",
};
```

```ts
import { brandATheme } from "@/themes/brand-a";
import { brandBTheme } from "@/themes/brand-b";

const loadBrandTheme = (brand: "brand-a" | "brand-b") => {
  const theme = brand === "brand-a" ? brandATheme : brandBTheme;
  const root = document.documentElement;

  Object.entries(theme).forEach(([key, value]) => {
    root.style.setProperty(key, value);
  });
};

const detectBrand = (): "brand-a" | "brand-b" => {
  return window.location.hostname.includes("brand-a") ? "brand-a" : "brand-b";
};

loadBrandTheme(detectBrand());
```

品牌变量集中定义，业务组件只使用 `var(--td-brand-color)`。

## 组件级样式覆盖

```vue
<template>
  <Button class="custom-button" theme="primary">自定义按钮</Button>
</template>

<style scoped>
.custom-button {
  --td-button-primary-bg-color: var(--custom-primary-color, #0052d9);
  --td-button-primary-border-color: var(--custom-primary-color, #0052d9);

  border-radius: 20px;
  font-weight: 600;
}
</style>
```

优先覆盖 CSS 变量；必须改样式时限定在自定义类名下，不直接选择组件内部类名。

## 响应式尺寸

```css
:root {
  --td-comp-size-xs: 24px;
  --td-comp-size-s: 32px;
  --td-comp-size-m: 40px;
  --td-comp-size-l: 48px;
  --td-font-size-base: 14px;
}

@media (max-width: 768px) {
  :root {
    --td-comp-size-xs: 28px;
    --td-comp-size-s: 36px;
    --td-comp-size-m: 44px;
    --td-comp-size-l: 52px;
    --td-font-size-base: 16px;
  }
}
```

移动端只调整尺寸 token，不复制一套组件样式。

## 主题配置持久化

```ts
// composables/useTheme.ts
import { ref } from "vue";

export interface ThemeConfig {
  mode: "light" | "dark";
  primaryColor: string;
  borderRadius: "small" | "default" | "large";
}

const STORAGE_KEY = "tdesign-theme-config";

const defaultConfig: ThemeConfig = {
  mode: "light",
  primaryColor: "#0052d9",
  borderRadius: "default",
};

export const useTheme = () => {
  const config = ref<ThemeConfig>({ ...defaultConfig });

  const loadConfig = () => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved) {
        config.value = { ...defaultConfig, ...JSON.parse(saved) };
      }
    } catch {
      config.value = { ...defaultConfig };
    }
  };

  const applyConfig = (next: Partial<ThemeConfig>) => {
    config.value = { ...config.value, ...next };

    const root = document.documentElement;
    root.setAttribute("theme-mode", config.value.mode);
    root.style.setProperty("--td-brand-color", config.value.primaryColor);

    const radiusMap = {
      small: "3px",
      default: "6px",
      large: "12px",
    };
    root.style.setProperty("--td-radius-default", radiusMap[config.value.borderRadius]);

    localStorage.setItem(STORAGE_KEY, JSON.stringify(config.value));
  };

  const resetConfig = () => {
    applyConfig(defaultConfig);
  };

  return { config, loadConfig, applyConfig, resetConfig };
};
```

```vue
<script setup lang="ts">
import { onMounted } from "vue";
import { useTheme } from "@/composables/useTheme";

const { config, loadConfig, applyConfig } = useTheme();

onMounted(() => {
  loadConfig();
  applyConfig(config.value);
});
</script>
```

## 常见问题

### 主题变量没有生效

1. 确认自定义样式在 `tdesign-vue-next/es/style/index.css` 之后引入。
2. 确认变量名拼写正确。
3. 在浏览器开发者工具中检查变量是否被更高优先级的选择器覆盖。

### 如何查看全部 CSS 变量

查看 `node_modules/tdesign-vue-next/es/style/` 下的样式文件，或参考 TDesign 设计规范。

### 动态切换后部分组件未更新

组件样式如果硬编码了颜色，不会随 CSS 变量变化。检查业务代码和第三方组件中的硬编码色值。

### SSR 下主题值不一致

在服务端渲染的 HTML 根元素上写入 `theme-mode` 与品牌变量，避免首屏使用默认值。

## 必须避免

- 直接覆盖组件内部类名。
- 用 `!important` 强制覆盖主题样式。
- 在每个组件上单独设置主题。
- 修改 `node_modules` 中的样式文件。
- 业务代码散落硬编码色值。
