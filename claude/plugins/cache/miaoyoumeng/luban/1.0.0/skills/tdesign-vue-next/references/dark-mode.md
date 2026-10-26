# 暗黑模式（Dark Mode）

## 适用场景

- 切换浅色与深色主题。
- 跟随系统偏好。
- 局部区域使用暗黑模式。
- 暗黑模式下的品牌色与自定义变量。
- 防止首屏闪烁。
- 图片与媒体适配。

## 切换方式

TDesign 通过根元素的 `theme-mode` 属性控制暗黑模式：

```html
<html theme-mode="dark"></html>
```

不要使用 class 名切换，例如 `class="dark"`，组件样式不识别。

```ts
const setThemeMode = (mode: "light" | "dark") => {
  document.documentElement.setAttribute("theme-mode", mode);
};
```

## 暗黑模式变量

```css
[theme-mode="dark"] {
  --td-brand-color: #4080ff;
  --td-brand-color-hover: #5c9bff;
  --td-brand-color-active: #2e6fe7;

  --td-text-color-primary: rgba(255, 255, 255, 0.9);
  --td-text-color-secondary: rgba(255, 255, 255, 0.55);
  --td-text-color-placeholder: rgba(255, 255, 255, 0.35);
  --td-text-color-disabled: rgba(255, 255, 255, 0.22);

  --td-bg-color-page: #0f0f0f;
  --td-bg-color-container: #1a1a1a;
  --td-bg-color-container-hover: #262626;
  --td-bg-color-container-active: #333333;
  --td-bg-color-secondarycontainer: #262626;
  --td-bg-color-component: #333333;

  --td-border-level-1-color: #383838;
  --td-border-level-2-color: #464646;

  --td-error-color: #e65050;
  --td-warning-color: #ee9c00;
  --td-success-color: #00b374;

  --td-shadow-1: 0 1px 10px rgba(0, 0, 0, 0.3);
  --td-shadow-2: 0 3px 14px 2px rgba(0, 0, 0, 0.28);
  --td-shadow-3: 0 6px 30px 5px rgba(0, 0, 0, 0.32);
}
```

业务自定义变量也要提供暗黑色值：

```css
:root {
  --custom-panel-bg: #ffffff;
  --custom-panel-text: #333333;
}

[theme-mode="dark"] {
  --custom-panel-bg: #1a1a1a;
  --custom-panel-text: #e5e5e5;
}
```

## 切换组件

```vue
<template>
  <ConfigProvider>
    <Space>
      <span>主题模式：</span>
      <RadioGroup v-model="themeMode" @change="onThemeChange">
        <RadioButton value="light">浅色</RadioButton>
        <RadioButton value="dark">深色</RadioButton>
        <RadioButton value="auto">跟随系统</RadioButton>
      </RadioGroup>
    </Space>

    <Divider />

    <Card title="示例卡片">
      <p>这是一段文字内容</p>
      <template #actions>
        <Button theme="primary">主要按钮</Button>
        <Button>次要按钮</Button>
      </template>
    </Card>
  </ConfigProvider>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref } from "vue";
import {
  Button,
  Card,
  ConfigProvider,
  Divider,
  RadioButton,
  RadioGroup,
  Space,
} from "tdesign-vue-next";

type ThemeMode = "light" | "dark" | "auto";

const themeMode = ref<ThemeMode>("light");
let mediaQuery: MediaQueryList | null = null;

const getSystemTheme = (): "light" | "dark" => {
  return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
};

const applyTheme = (mode: "light" | "dark") => {
  document.documentElement.setAttribute("theme-mode", mode);
};

const handleSystemChange = (event: MediaQueryListEvent) => {
  if (themeMode.value === "auto") {
    applyTheme(event.matches ? "dark" : "light");
  }
};

const onThemeChange = (mode: ThemeMode) => {
  localStorage.setItem("theme-mode", mode);
  applyTheme(mode === "auto" ? getSystemTheme() : mode);
};

onMounted(() => {
  const saved = localStorage.getItem("theme-mode") as ThemeMode | null;
  if (saved) {
    themeMode.value = saved;
  }
  onThemeChange(themeMode.value);

  mediaQuery = window.matchMedia("(prefers-color-scheme: dark)");
  mediaQuery.addEventListener("change", handleSystemChange);
});

onUnmounted(() => {
  mediaQuery?.removeEventListener("change", handleSystemChange);
});
</script>
```

## 可复用 Composable

```ts
// composables/useDarkMode.ts
import { ref } from "vue";

export type ThemeMode = "light" | "dark" | "auto";

const STORAGE_KEY = "theme-mode";
const mode = ref<ThemeMode>("light");
const isDark = ref(false);
let mediaQuery: MediaQueryList | null = null;
let initialized = false;

export const useDarkMode = () => {
  const systemIsDark = () => {
    return window.matchMedia("(prefers-color-scheme: dark)").matches;
  };

  const applyTheme = (dark: boolean) => {
    isDark.value = dark;
    document.documentElement.setAttribute("theme-mode", dark ? "dark" : "light");
  };

  const handleSystemChange = (event: MediaQueryListEvent) => {
    if (mode.value === "auto") {
      applyTheme(event.matches);
    }
  };

  const setMode = (nextMode: ThemeMode) => {
    mode.value = nextMode;
    localStorage.setItem(STORAGE_KEY, nextMode);
    applyTheme(nextMode === "auto" ? systemIsDark() : nextMode === "dark");
  };

  const toggle = () => {
    setMode(isDark.value ? "light" : "dark");
  };

  const init = () => {
    if (initialized) return;
    initialized = true;

    const saved = localStorage.getItem(STORAGE_KEY) as ThemeMode | null;
    setMode(saved ?? "auto");

    mediaQuery = window.matchMedia("(prefers-color-scheme: dark)");
    mediaQuery.addEventListener("change", handleSystemChange);
  };

  const cleanup = () => {
    mediaQuery?.removeEventListener("change", handleSystemChange);
    mediaQuery = null;
    initialized = false;
  };

  return { mode, isDark, setMode, toggle, init, cleanup };
};
```

```vue
<!-- App.vue -->
<script setup lang="ts">
import { onMounted, onUnmounted } from "vue";
import { useDarkMode } from "@/composables/useDarkMode";

const { init, cleanup } = useDarkMode();

onMounted(init);
onUnmounted(cleanup);
</script>
```

## 局部暗黑模式

```vue
<template>
  <div class="page">
    <p>浅色区域</p>

    <div class="dark-section" theme-mode="dark">
      <Card title="暗黑区域">
        <p>这个区域使用暗黑模式</p>
        <Button theme="primary">按钮</Button>
      </Card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Button, Card } from "tdesign-vue-next";
</script>

<style scoped>
.dark-section {
  padding: 20px;
  border-radius: var(--td-radius-default);
}

.dark-section[theme-mode="dark"] {
  --td-bg-color-page: #0f0f0f;
  --td-bg-color-container: #1a1a1a;
  --td-text-color-primary: rgba(255, 255, 255, 0.9);
  --td-bg-color-container-hover: #262626;
  --td-border-level-1-color: #383838;
}
</style>
```

局部容器必须定义该区域用到的变量，不能只加 `theme-mode` 属性。

## 防止首屏闪烁

在 `<head>` 中放置同步脚本，先于 CSS 与 Vue 应用执行：

```html
<!-- index.html -->
<script>
  (() => {
    const saved = localStorage.getItem("theme-mode");
    let theme = "light";

    if (saved === "dark") {
      theme = "dark";
    } else if (saved === "auto" || !saved) {
      theme = window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
    }

    document.documentElement.setAttribute("theme-mode", theme);
  })();
</script>
```

同时内联首屏基础变量，避免样式文件加载前的白屏：

```html
<style>
  :root {
    --td-bg-color-page: #f3f3f3;
    --td-text-color-primary: rgba(0, 0, 0, 0.9);
  }

  [theme-mode="dark"] {
    --td-bg-color-page: #0f0f0f;
    --td-text-color-primary: rgba(255, 255, 255, 0.9);
  }

  body {
    background-color: var(--td-bg-color-page);
    color: var(--td-text-color-primary);
  }
</style>
```

## 图片与媒体

```vue
<template>
  <picture>
    <source srcset="/images/logo-dark.svg" media="(prefers-color-scheme: dark)" />
    <img src="/images/logo-light.svg" alt="Logo" />
  </picture>

  <img :src="isDark ? '/images/hero-dark.png' : '/images/hero-light.png'" alt="Hero" />
</template>

<script setup lang="ts">
import { useDarkMode } from "@/composables/useDarkMode";

const { isDark } = useDarkMode();
</script>

<style scoped>
[theme-mode="dark"] .icon-invertible {
  filter: invert(1);
}

[theme-mode="dark"] .photo {
  filter: brightness(0.9);
}
</style>
```

## 常见问题

### 切换时页面闪烁

在 `<head>` 中同步设置 `theme-mode`，不要等 Vue 挂载后再设置。

### 如何判断当前模式

```ts
const isDark = document.documentElement.getAttribute("theme-mode") === "dark";
```
