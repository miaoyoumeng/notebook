---
name: wechat-tdesign
description: "为微信小程序构建基于 TDesign 组件库（tdesign-miniprogram）的界面：完成 pnpm 安装与 npm 构建、组件注册、页面编写、主题与样式定制、暗黑模式适配，并给出 69 个组件的引入路径与 AI 聊天组件用法。当用户在微信小程序或 Taro 项目中使用或引入 TDesign、需要搭建页面/表单/列表/弹窗等 UI、调整主题色与暗黑模式、排查 tdesign-miniprogram 构建失败或样式不生效问题时使用，包括「用 TDesign 写个页面」「tdesign-miniprogram 怎么用」「小程序表单组件」等说法；不要用于网页端的 tdesign-react 或 tdesign-vue，也不要用于非 TDesign 的 UI 需求。"
---

# wechat-tdesign

## 概述

TDesign 小程序组件库（包名 `tdesign-miniprogram`）是腾讯开源的企业级设计体系，提供 69 个组件，覆盖基础、导航、输入、数据展示、反馈与 AI 聊天六类，支持主题定制与暗黑模式。本技能给出接入微信小程序的最小流程、组件索引、常用写法与样式定制方法。

## 上下文层级

1. 常驻上下文：frontmatter 中的 `name` 与 `description`。
2. 技能触发时加载：本文件，含安装流程、组件表、常用模式与验证清单。
3. 按需读取：`references/` 下的组件文档，提供完整属性、事件、插槽与样式类。

组件 API 以 `references/` 文档为准。网页端 TDesign 的属性不能直接套用到小程序组件上，写代码前先读对应文档。

## 使用时机

以下场景使用本技能：

- 在微信小程序中安装、配置并使用 TDesign 组件库。
- 选定组件后需要确认属性、事件与引入路径。
- 按 TDesign 设计规范实现页面，或定制主题色、样式与暗黑模式。
- 构建 AI 聊天界面，使用 Chat 系列组件。
- 排查 npm 构建失败、组件未注册、样式不生效、暗黑模式异常。

不适用于网页端的 `tdesign-react`、`tdesign-vue`，也不适用于非 TDesign 的 UI 需求。

## 编码四原则

- 组件优先：TDesign 已覆盖的结构直接使用组件，不手写等价实现。
- 文档优先：属性与事件查 `references/`，不凭记忆或网页端文档臆测。
- 变量优先：颜色、圆角、间距通过 CSS 变量或 `t-class` 定制，不覆盖组件内部选择器。
- Token 优先：暗黑模式基于设计 token 实现，不在业务代码中散落硬编码色值。

## 流程

### 1. 安装依赖

```bash
pnpm add tdesign-miniprogram
```

pnpm 使用软链接布局，若开发者工具构建 npm 时找不到依赖，在项目根目录 `.npmrc` 中加入 `node-linker=hoisted` 后重新安装。

### 2. 移除 app.json 的新版样式

删除 `app.json` 中的 `"style": "v2"`。该配置启用新版组件样式，会导致 TDesign 组件样式错乱。

### 3. 配置 project.config.json

在 `setting` 中加入：

```json
{
  "setting": {
    "packNpmManually": true,
    "packNpmRelationList": [
      {
        "packageJsonPath": "./package.json",
        "miniprogramNpmDistDir": "./"
      }
    ]
  }
}
```

构建时若出现 `NPM packages not found`，先补该项配置再重新构建。

### 4. TypeScript 项目配置路径

修改 `tsconfig.json`：

```json
{
  "paths": {
    "tdesign-miniprogram/*": [
      "./miniprogram/miniprogram_npm/tdesign-miniprogram/*"
    ]
  }
}
```

### 5. 构建 npm

在微信开发者工具中执行 `工具 - 构建 npm`。构建成功后勾选 `将 JS 编译成 ES5`。

### 6. 注册组件

在页面或组件的 JSON 文件中引入：

```json
{
  "usingComponents": {
    "t-button": "tdesign-miniprogram/button/button"
  }
}
```

### 7. 编写页面

```html
<t-button theme="primary">按钮</t-button>
```

### 8. 按需查阅文档

根据组件名读取 `references/miniprogram/components/<组件名>.md`，获取完整属性、事件与示例。

## 组件清单

### 基础组件（6）

| 组件 | 说明 | 引入路径 |
| --- | --- | --- |
| Button | 按钮 | `tdesign-miniprogram/button/button` |
| Divider | 分割线 | `tdesign-miniprogram/divider/divider` |
| Fab | 悬浮按钮 | `tdesign-miniprogram/fab/fab` |
| Icon | 图标 | `tdesign-miniprogram/icon/icon` |
| Layout | 布局 | `tdesign-miniprogram/row/row` |
| Link | 链接 | `tdesign-miniprogram/link/link` |

### 导航组件（8）

| 组件 | 说明 | 引入路径 |
| --- | --- | --- |
| BackTop | 返回顶部 | `tdesign-miniprogram/back-top/back-top` |
| Drawer | 抽屉 | `tdesign-miniprogram/drawer/drawer` |
| Indexes | 索引列表 | `tdesign-miniprogram/indexes/indexes` |
| Navbar | 导航条 | `tdesign-miniprogram/navbar/navbar` |
| SideBar | 侧边导航栏 | `tdesign-miniprogram/side-bar/side-bar` |
| Steps | 步骤条 | `tdesign-miniprogram/steps/steps` |
| TabBar | 底部标签栏 | `tdesign-miniprogram/tab-bar/tab-bar` |
| Tabs | 选项卡 | `tdesign-miniprogram/tabs/tabs` |

### 输入组件（16）

| 组件 | 说明 | 引入路径 |
| --- | --- | --- |
| Calendar | 日历 | `tdesign-miniprogram/calendar/calendar` |
| Cascader | 级联选择器 | `tdesign-miniprogram/cascader/cascader` |
| CheckBox | 多选框 | `tdesign-miniprogram/checkbox/checkbox` |
| DateTimePicker | 日期时间选择器 | `tdesign-miniprogram/date-time-picker/date-time-picker` |
| Input | 输入框 | `tdesign-miniprogram/input/input` |
| Picker | 选择器 | `tdesign-miniprogram/picker/picker` |
| Radio | 单选框 | `tdesign-miniprogram/radio/radio` |
| Rate | 评分 | `tdesign-miniprogram/rate/rate` |
| Search | 搜索框 | `tdesign-miniprogram/search/search` |
| Slider | 滑动选择器 | `tdesign-miniprogram/slider/slider` |
| Stepper | 步进器 | `tdesign-miniprogram/stepper/stepper` |
| Switch | 开关 | `tdesign-miniprogram/switch/switch` |
| Textarea | 多行文本框 | `tdesign-miniprogram/textarea/textarea` |
| TreeSelect | 树形选择器 | `tdesign-miniprogram/tree-select/tree-select` |
| Upload | 上传 | `tdesign-miniprogram/upload/upload` |
| Form | 表单 | `tdesign-miniprogram/form/form` |

### 数据展示组件（18）

| 组件 | 说明 | 引入路径 |
| --- | --- | --- |
| Avatar | 头像 | `tdesign-miniprogram/avatar/avatar` |
| Badge | 徽章 | `tdesign-miniprogram/badge/badge` |
| Cell | 单元格 | `tdesign-miniprogram/cell/cell` |
| Collapse | 折叠面板 | `tdesign-miniprogram/collapse/collapse` |
| CountDown | 倒计时 | `tdesign-miniprogram/count-down/count-down` |
| Empty | 空状态 | `tdesign-miniprogram/empty/empty` |
| Footer | 页脚 | `tdesign-miniprogram/footer/footer` |
| Grid | 宫格 | `tdesign-miniprogram/grid/grid` |
| Image | 图片 | `tdesign-miniprogram/image/image` |
| ImageViewer | 图片预览 | `tdesign-miniprogram/image-viewer/image-viewer` |
| Progress | 进度条 | `tdesign-miniprogram/progress/progress` |
| Result | 结果 | `tdesign-miniprogram/result/result` |
| Skeleton | 骨架屏 | `tdesign-miniprogram/skeleton/skeleton` |
| Sticky | 吸顶容器 | `tdesign-miniprogram/sticky/sticky` |
| Swiper | 轮播图 | `tdesign-miniprogram/swiper/swiper` |
| Table | 表格 | `tdesign-miniprogram/table/table` |
| Tag | 标签 | `tdesign-miniprogram/tag/tag` |
| List | 列表 | `tdesign-miniprogram/list/list` |

### 反馈组件（12）

| 组件 | 说明 | 引入路径 |
| --- | --- | --- |
| ActionSheet | 动作面板 | `tdesign-miniprogram/action-sheet/action-sheet` |
| Dialog | 对话框 | `tdesign-miniprogram/dialog/dialog` |
| DropdownMenu | 下拉菜单 | `tdesign-miniprogram/dropdown-menu/dropdown-menu` |
| Guide | 引导 | `tdesign-miniprogram/guide/guide` |
| Loading | 加载 | `tdesign-miniprogram/loading/loading` |
| Message | 全局提示 | `tdesign-miniprogram/message/message` |
| NoticeBar | 消息提醒 | `tdesign-miniprogram/notice-bar/notice-bar` |
| Overlay | 遮罩层 | `tdesign-miniprogram/overlay/overlay` |
| Popup | 弹出层 | `tdesign-miniprogram/popup/popup` |
| PullDownRefresh | 下拉刷新 | `tdesign-miniprogram/pull-down-refresh/pull-down-refresh` |
| SwipeCell | 滑动操作 | `tdesign-miniprogram/swipe-cell/swipe-cell` |
| Toast | 轻提示 | `tdesign-miniprogram/toast/toast` |

### AI 聊天组件（9）

| 组件 | 说明 | 引入路径 |
| --- | --- | --- |
| ChatList | 聊天列表 | `tdesign-miniprogram/chat-list/chat-list` |
| ChatMessage | 聊天消息 | `tdesign-miniprogram/chat-message/chat-message` |
| ChatSender | 消息发送器 | `tdesign-miniprogram/chat-sender/chat-sender` |
| ChatContent | 消息内容 | `tdesign-miniprogram/chat-content/chat-content` |
| ChatActionbar | 消息操作栏 | `tdesign-miniprogram/chat-actionbar/chat-actionbar` |
| ChatLoading | 加载状态 | `tdesign-miniprogram/chat-loading/chat-loading` |
| ChatMarkdown | Markdown 内容 | `tdesign-miniprogram/chat-markdown/chat-markdown` |
| ChatThinking | 思考过程 | `tdesign-miniprogram/chat-thinking/chat-thinking` |
| Attachments | 附件列表 | `tdesign-miniprogram/attachments/attachments` |

## 常用模式

### Button

```html
<!-- 基础按钮 -->
<t-button theme="primary" size="large">主要按钮</t-button>
<t-button theme="light" size="large">浅色按钮</t-button>
<t-button size="large">默认按钮</t-button>

<!-- 描边与文本按钮 -->
<t-button theme="primary" size="large" variant="outline">描边按钮</t-button>
<t-button theme="primary" size="large" variant="text">文本按钮</t-button>

<!-- 图标按钮 -->
<t-button
  theme="primary"
  icon="app"
  content="图标按钮"
  size="large"
></t-button>

<!-- 加载、禁用、通栏、幽灵按钮 -->
<t-button theme="primary" size="large" loading>加载中</t-button>
<t-button theme="primary" size="large" disabled>禁用</t-button>
<t-button theme="primary" size="large" block>通栏按钮</t-button>
<t-button theme="primary" ghost size="large">幽灵按钮</t-button>
```

### Input

```json
{
  "usingComponents": {
    "t-input": "tdesign-miniprogram/input/input"
  }
}
```

```html
<t-input
  label="标签"
  placeholder="请输入"
  value="{{value}}"
  bind:change="onChange"
/>
```

### Dialog

```json
{
  "usingComponents": {
    "t-dialog": "tdesign-miniprogram/dialog/dialog"
  }
}
```

```html
<t-dialog
  visible="{{visible}}"
  title="标题"
  content="内容"
  confirm-btn="确认"
  cancel-btn="取消"
  bind:confirm="onConfirm"
  bind:cancel="onCancel"
/>
```

### Toast

```javascript
import Toast from 'tdesign-miniprogram/toast/index';

Toast({
  context: this,
  selector: '#t-toast',
  message: '提示内容',
});
```

### AI 聊天界面

```json
{
  "usingComponents": {
    "t-chat-list": "tdesign-miniprogram/chat-list/chat-list",
    "t-chat-message": "tdesign-miniprogram/chat-message/chat-message",
    "t-chat-sender": "tdesign-miniprogram/chat-sender/chat-sender"
  }
}
```

```html
<t-chat-list layout="single">
  <t-chat-message
    avatar="{{item.avatar}}"
    name="{{item.name}}"
    content="{{item.content}}"
    role="{{item.role}}"
  />
  <view slot="footer">
    <t-chat-sender bind:send="onSend" />
  </view>
</t-chat-list>
```

```javascript
Component({
  data: {
    messages: [
      {
        role: 'user',
        content: [{ type: 'text', data: '你好' }],
      },
      {
        role: 'assistant',
        content: [{ type: 'text', data: '你好，有什么可以帮你？' }],
      },
    ],
  },
  methods: {
    onSend(e) {
      const { value } = e.detail;
      // 处理发送消息
    },
  },
});
```

## 样式定制

### 方式一：style 属性

```html
<t-button style="color: red">自定义样式</t-button>
<t-button custom-style="color: red">自定义样式</t-button>
```

### 方式二：关闭样式隔离

在页面中直接覆盖样式：

```css
.t-button--primary {
  background-color: navy;
}
```

在自定义组件中启用样式共享：

```javascript
Component({
  options: {
    styleIsolation: 'shared',
  },
});
```

### 方式三：外部样式类

```html
<t-button t-class="my-button-class">按钮</t-button>
```

```css
.my-button-class {
  background-color: navy !important;
}
```

### 方式四：CSS 变量

TDesign 提供丰富的 CSS 变量用于主题定制：

```css
page {
  --td-button-primary-bg-color: #0052d9;
  --td-button-border-radius: 8rpx;
}
```

## 暗黑模式

### 1. 修改 app.json

```json
{
  "darkmode": true
}
```

### 2. 引入设计 token

在 `app.wxss` 中：

```css
@import 'miniprogram_npm/tdesign-miniprogram/common/style/theme/_index.wxss';
```

### 3. 使用 CSS 变量

```css
.text {
  color: var(--td-text-color-secondary);
}
```

### 4. 特殊组件适配

位于 `custom-tab-bar` 或 `root-portal` 中的组件，需要外层包裹 `.page` 类：

```html
<view class="page">
  <t-tab-bar />
</view>
```

## 验证清单

- `node_modules/tdesign-miniprogram` 存在，`miniprogram_npm/tdesign-miniprogram` 已生成。
- `app.json` 中不含 `"style": "v2"`。
- `project.config.json` 已配置 `packNpmManually` 与 `packNpmRelationList`。
- TypeScript 项目的 `tsconfig.json` 中 `paths` 指向构建产物目录。
- 基础库版本不低于 `^2.12.0`。
- 页面或组件 JSON 中 `usingComponents` 的路径与实际组件一致。
- 编译控制台无组件未找到、样式冲突类报错。
- 切换深色模式后，组件与业务区域的配色均正确。

## 危险信号

- 未构建 npm 就引用组件，控制台报 `Component is not found`。
- 保留 `"style": "v2"`，组件样式整体错乱。
- 直接覆盖组件内部类名或滥用 `!important`，升级后失效。
- 自定义组件中样式不生效却未检查 `styleIsolation`。
- 只开启 `darkmode` 而未引入主题 token，暗黑模式无效果。
- `custom-tab-bar`、`root-portal` 内暗黑样式异常却未包裹 `.page`。
- 照搬网页端 TDesign 的属性名或事件名，小程序组件不支持。

## 理由辩解

- 「项目已有其他组件库，混着用即可」：同类组件只保留一套，混用会增加包体并引发样式冲突。
- 「只用一个按钮，手写 view 更省事」：涉及交互态、主题与无障碍时，组件成本更低。
- 「样式改不动就直接加 !important」：先确认样式隔离与外部样式类，覆盖只作最后手段。
- 「暗黑模式以后再适配」：色值分散后改造成本更高，应从 CSS 变量起步。

## 验证

在微信开发者工具中编译并预览：构建 npm 成功并勾选 `将 JS 编译成 ES5`；打开使用组件的页面，控制台无报错；切换深色模式检查组件与自定义区域；在真机或不同机型模拟器中检查 rpx 尺寸表现。

## 实现检查表

- [ ] 依赖安装与 npm 构建完成。
- [ ] `app.json`、`project.config.json`、`tsconfig.json` 按要求修改。
- [ ] 组件已在 `usingComponents` 中注册，路径正确。
- [ ] 交互事件（如 `change`、`confirm`、`cancel`）已绑定并处理。
- [ ] 视觉定制通过 `t-class` 或 CSS 变量完成。
- [ ] 暗黑模式验证通过。

## 参考资料

基础文档位于 `references/miniprogram/`：

- `getting-started.md`：安装、构建与基础库版本要求。
- `overview.md`：组件总览。
- `custom-style.md`：样式定制。
- `custom-theme.md`：主题定制。
- `dark-mode.md`：暗黑模式。

组件 API 文档位于 `references/miniprogram/components/`，按组件名读取：

`action-sheet` `avatar` `back-top` `badge` `button` `calendar` `cascader` `cell` `checkbox` `collapse` `count-down` `date-time-picker` `dialog` `divider` `drawer` `dropdown-menu` `empty` `fab` `footer` `form` `grid` `guide` `icon` `image` `image-viewer` `indexes` `input` `link` `list` `loading` `message` `navbar` `notice-bar` `overlay` `picker` `popup` `progress` `pull-down-refresh` `radio` `rate` `result` `search` `side-bar` `skeleton` `slider` `stepper` `steps` `sticky` `swipe-cell` `swiper` `switch` `tab-bar` `table` `tabs` `tag` `textarea` `toast` `tree-select` `upload`

AI 聊天文档位于 `references/miniprogram-chat/`：

- `getting-started.md`：聊天组件快速开始。
- `sse.md`：SSE 流式输出。
- `components/`：`attachments` `chat-actionbar` `chat-content` `chat-list` `chat-loading` `chat-markdown` `chat-message` `chat-sender` `chat-thinking`。
