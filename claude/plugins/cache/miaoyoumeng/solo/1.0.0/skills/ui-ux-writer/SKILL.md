---
name: ui-ux-writer
description: "Web 和移动端的 UI/UX 设计智能系统。包含 50+ 种风格、161 套配色方案、57 组字体搭配、161 种产品类型、99 条 UX 指南和 25 种图表类型，覆盖 10 个技术栈（React、Next.js、Vue、Svelte、SwiftUI、React Native、Flutter、Tailwind、shadcn/ui 和 HTML/CSS）。支持的操作：规划、构建、创建、设计、实现、审查、修复、优化、增强、重构和检查 UI/UX 代码。项目类型：网站、落地页、仪表盘、管理后台、电子商务、SaaS、作品集、博客和移动应用。元素类型：按钮、模态框、导航栏、侧边栏、卡片、表格、表单和图表。风格：玻璃态、粘土态、极简主义、粗野主义、新拟态、Bento 网格、暗色模式、响应式、拟物化和扁平化设计。主题：色彩系统、无障碍设计、动画、布局、排版、字体搭配、间距、交互状态、阴影和渐变。集成：shadcn/ui MCP 用于组件搜索和示例。"
tools: ["Read", "Grep", "Glob", "Bash", "Writer"]
model: opus
max_turns: 3
---

# UI/UX - 设计智能系统

适用于 Web 和移动应用的综合设计指南。包含 50+ 种风格、161 套配色方案、57 组字体搭配、161 种产品类型及推理规则、99 条 UX 指南和 25 种图表类型，覆盖 10 个技术栈。提供可检索数据库和基于优先级的推荐。

## 适用时机

当任务涉及 **UI 结构、视觉设计决策、交互模式或用户体验质量控制** 时，应使用此 Skill。

### 必须使用

在以下情况下必须调用此 Skill：

- 设计新页面（落地页、仪表盘、管理后台、SaaS、移动应用）
- 创建或重构 UI 组件（按钮、模态框、表单、表格、图表等）
- 选择配色方案、字体系统、间距标准或布局系统
- 审查 UI 代码的无障碍性、用户体验或视觉一致性
- 实现导航结构、动画或响应式行为
- 做出产品级别的设计决策（风格、信息层级、品牌表达）
- 提升界面的感知质量、清晰度或可用性

### 推荐使用

在以下情况下推荐使用此 Skill：

- UI 看起来"不够专业"但原因不明确
- 收到关于可用性或使用体验的反馈
- 发布前的 UI 质量优化
- 跨平台设计对齐（Web / iOS / Android）
- 构建设计系统或可复用组件库

### 跳过不用

在以下情况下不需要此 Skill：

- 纯后端逻辑开发
- 仅涉及 API 或数据库设计
- 与界面无关的性能优化
- 基础设施或 DevOps 工作
- 非可视化脚本或自动化任务

**判断标准**：如果任务会改变功能的 **外观、感受、动态效果或交互方式**，则应使用此 Skill。

## 按优先级排列的规则分类

*供人工/AI 参考：按优先级 1→10 决定首先关注哪个规则类别；需要时可用 `--domain <Domain>` 查询详情。脚本不读取此表。*

| 优先级 | 类别 | 影响级别 | 领域 | 关键检查项（必须） | 反模式（避免） |
|--------|------|----------|------|---------------------|----------------|
| 1 | 无障碍设计 | 关键 | `ux` | 对比度 4.5:1、替代文本、键盘导航、Aria 标签 | 移除聚焦环、无标签的纯图标按钮 |
| 2 | 触摸与交互 | 关键 | `ux` | 最小尺寸 44×44px、8px+ 间距、加载反馈 | 仅依赖悬停、瞬间状态变化（0ms） |
| 3 | 性能 | 高 | `ux` | WebP/AVIF、懒加载、预留空间（CLS < 0.1） | 布局抖动、累积布局偏移 |
| 4 | 风格选择 | 高 | `style`, `product` | 匹配产品类型、一致性、SVG 图标（不用 emoji） | 随机混合扁平与拟物化、用 emoji 做图标 |
| 5 | 布局与响应式 | 高 | `ux` | 移动优先断点、Viewport meta、无横向滚动 | 横向滚动、固定 px 容器宽度、禁止缩放 |
| 6 | 字体与颜色 | 中 | `typography`, `color` | 基准 16px、行高 1.5、语义化颜色令牌 | 正文 < 12px、灰底灰字、组件中使用原始色值 |
| 7 | 动画 | 中 | `ux` | 持续时间 150–300ms、动画传达含义、空间连贯性 | 纯装饰性动画、对 width/height 做动画、不尊重减少动画设置 |
| 8 | 表单与反馈 | 中 | `ux` | 可见标签、字段旁错误提示、辅助文本、渐进式披露 | 仅用 placeholder 做标签、错误仅显示在顶部、一次性 overwhelming |
| 9 | 导航模式 | 高 | `ux` | 可预期的返回、底部导航 ≤5 项、深度链接 | 导航过载、返回行为异常、无深度链接 |
| 10 | 图表与数据 | 低 | `chart` | 图例、工具提示、无障碍配色 | 仅依赖颜色传达含义 |

## 快速参考

### 1. 无障碍设计（关键）

- `color-contrast` - 普通文本最小对比度 4.5:1（大文本 3:1）；Material Design
- `focus-states` - 可交互元素有可见的聚焦环（2–4px；Apple HIG、MD）
- `alt-text` - 有意义的图片提供描述性替代文本
- `aria-labels` - 纯图标按钮使用 aria-label；原生中使用 accessibilityLabel（Apple HIG）
- `keyboard-nav` - Tab 顺序与视觉顺序一致；完整键盘支持（Apple HIG）
- `form-labels` - 使用带 for 属性的 label
- `skip-links` - 为键盘用户提供跳至主内容的链接
- `heading-hierarchy` - 顺序 h1→h6，不跳级
- `color-not-only` - 不只用颜色传达信息（加图标/文字）
- `dynamic-type` - 支持系统文字缩放；文字增长时避免截断（Apple Dynamic Type、MD）
- `reduced-motion` - 尊重 prefers-reduced-motion；按请求减少/禁用动画（Apple Reduced Motion API、MD）
- `voiceover-sr` - 有意义的 accessibilityLabel/accessibilityHint；VoiceOver/读屏器的逻辑阅读顺序（Apple HIG、MD）
- `escape-routes` - 模态框和多步流程提供取消/返回（Apple HIG）
- `keyboard-shortcuts` - 保留系统和无障碍快捷键；拖放操作提供键盘替代方案（Apple HIG）

### 2. 触摸与交互（关键）

- `touch-target-size` - 最小 44×44pt（Apple）/ 48×48dp（Material）；必要时扩展点击区域超过视觉边界
- `touch-spacing` - 触摸目标之间最小 8px/8dp 间距（Apple HIG、MD）
- `hover-vs-tap` - 使用点击/轻触进行主要交互；不只依赖悬停
- `loading-buttons` - 异步操作期间禁用按钮；显示旋转器或进度
- `error-feedback` - 在问题附近显示清晰的错误信息
- `cursor-pointer` - 可点击元素添加 cursor-pointer（Web）
- `gesture-conflicts` - 主内容区避免横向滑动；优先使用纵向滚动
- `tap-delay` - 使用 touch-action: manipulation 减少 300ms 延迟（Web）
- `standard-gestures` - 一致使用平台标准手势；不重新定义（如返回滑动、捏合缩放）（Apple HIG）
- `system-gestures` - 不阻塞系统手势（控制中心、返回滑动等）（Apple HIG）
- `press-feedback` - 按下时视觉反馈（涟漪/高亮；MD 状态层）
- `haptic-feedback` - 确认和重要操作使用触觉反馈；避免过度使用（Apple HIG）
- `gesture-alternative` - 不只依赖纯手势交互；关键操作始终提供可见控件
- `safe-area-awareness` - 主要触摸目标远离刘海、灵动岛、手势条和屏幕边缘
- `no-precision-required` - 避免要求在小图标或细边缘进行像素级精准点击
- `swipe-clarity` - 滑动操作必须显示清晰的提示或暗示（箭头、标签、教程）
- `drag-threshold` - 拖动前使用移动阈值，避免意外拖动

### 3. 性能（高）

- `image-optimization` - 使用 WebP/AVIF，响应式图片（srcset/sizes），懒加载非关键资源
- `image-dimension` - 声明 width/height 或使用 aspect-ratio 防止布局偏移（Core Web Vitals: CLS）
- `font-loading` - 使用 font-display: swap/optional 避免文字不可见（FOIT）；预留空间减少布局偏移（MD）
- `font-preload` - 仅预加载关键字体；避免对每个变体都使用 preload
- `critical-css` - 优先首屏 CSS（内联关键 CSS 或早期加载样式表）
- `lazy-loading` - 通过动态导入/路由级分割懒加载非核心组件
- `bundle-splitting` - 按路由/功能拆分代码（React Suspense / Next.js dynamic）减少初始加载和 TTI
- `third-party-scripts` - 第三方脚本使用 async/defer 加载；审计并移除不需要的（MD）
- `reduce-reflows` - 避免频繁的布局读取/写入；批量 DOM 读取然后写入
- `content-jumping` - 为异步内容预留空间避免布局跳动（Core Web Vitals: CLS）
- `lazy-load-below-fold` - 首屏以下图片和重媒体使用 loading="lazy"
- `virtualize-lists` - 50+ 项的列表使用虚拟化提升内存效率和滚动性能
- `main-thread-budget` - 每帧工作保持在 ~16ms 以内以维持 60fps；将重任务移出主线程（HIG、MD）
- `progressive-loading` - 超过 1s 的操作使用骨架屏/微光效果代替长时间阻塞式加载旋转
- `input-latency` - 点击/滚动的输入延迟保持在 ~100ms 以内（Material 响应标准）
- `tap-feedback-speed` - 点击后 100ms 内提供视觉反馈（Apple HIG）
- `debounce-throttle` - 高频事件（滚动、缩放、输入）使用防抖/节流
- `offline-support` - 提供离线状态消息和基本降级方案（PWA / 移动端）
- `network-fallback` - 为慢速网络提供降级模式（低分辨率图片、更少动画）

### 4. 风格选择（高）

- `style-match` - 风格匹配产品类型（使用 `--design-system` 获取推荐）
- `consistency` - 所有页面使用统一风格
- `no-emoji-icons` - 使用 SVG 图标（Heroicons、Lucide），不用 emoji
- `color-palette-from-product` - 从产品/行业选择调色板（搜索 `--domain color`）
- `effects-match-style` - 阴影、模糊、圆角与所选风格对齐（玻璃态/扁平/粘土等）
- `platform-adaptive` - 尊重平台习惯（iOS HIG vs Material）：导航、控件、排版、动效
- `state-clarity` - 悬停/按下/禁用状态在保持风格的同时视觉可区分（Material 状态层）
- `elevation-consistent` - 卡片、面板、模态框使用一致的高程/阴影层级，避免随机阴影值
- `dark-mode-pairing` - 同时设计亮/暗模式变体以保持品牌、对比度和风格一致
- `icon-style-consistent` - 产品中统一使用一套图标集/视觉语言（描边宽度、圆角半径）
- `system-controls` - 优先使用原生/系统控件而非完全自定义；仅在品牌需要时自定义（Apple HIG）
- `blur-purpose` - 模糊用于指示背景被遮挡（模态框、面板），而非装饰（Apple HIG）
- `primary-action` - 每个屏幕应只有一个主 CTA；次要操作用于视觉上从属（Apple HIG）

### 5. 布局与响应式（高）

- `viewport-meta` - width=device-width initial-scale=1（永不禁止缩放）
- `mobile-first` - 移动优先设计，然后扩展到平板和桌面
- `breakpoint-consistency` - 使用系统化的断点（如 375 / 768 / 1024 / 1440）
- `readable-font-size` - 移动端正文最小 16px（避免 iOS 自动缩放）
- `line-length-control` - 移动端每行 35–60 字符；桌面端 60–75 字符
- `horizontal-scroll` - 移动端无横向滚动；确保内容适配视口宽度
- `spacing-scale` - 使用 4pt/8dp 增量间距系统（Material Design）
- `touch-density` - 组件间距适合触摸操作：不过于拥挤，不导致误触
- `container-width` - 桌面端一致的 max-width（max-w-6xl / 7xl）
- `z-index-management` - 定义分层的 z-index 尺度（如 0 / 10 / 20 / 40 / 100 / 1000）
- `fixed-element-offset` - 固定导航栏/底部栏必须为底层内容预留安全间距
- `scroll-behavior` - 避免嵌套滚动区域干扰主滚动体验
- `viewport-units` - 移动端优先使用 min-h-dvh 而非 100vh
- `orientation-support` - 横屏模式下保持布局可读可操作
- `content-priority` - 移动端先展示核心内容；折叠或隐藏次要内容
- `visual-hierarchy` - 通过大小、间距、对比度建立层级——不只依赖颜色

### 6. 字体与颜色（中）

- `line-height` - 正文字行高使用 1.5-1.75
- `line-length` - 每行限制 65-75 字符
- `font-pairing` - 标题/正文字体个性匹配
- `font-scale` - 一致的字体尺度（如 12 14 16 18 24 32）
- `contrast-readability` - 浅色背景使用较深色文字（如 slate-900 配白色）
- `text-styles-system` - 使用平台字体系统：iOS 11 Dynamic Type 样式 / Material 5 类型角色（display, headline, title, body, label）（HIG、MD）
- `weight-hierarchy` - 使用字重强化层级：粗体标题（600–700）、常规正文（400）、中等标签（500）（MD）
- `color-semantic` - 定义语义化颜色令牌（primary, secondary, error, surface, on-surface），组件中不使用原始色值（Material 色彩系统）
- `color-dark-mode` - 暗色模式使用低饱和度/较浅色调变体，非颜色反转；分别测试对比度（HIG、MD）
- `color-accessible-pairs` - 前景/背景对必须满足 4.5:1（AA）或 7:1（AAA）；使用工具验证（WCAG、MD）
- `color-not-decorative-only` - 功能色（错误红、成功绿）必须包含图标/文字；避免仅靠颜色表达含义（HIG、MD）
- `truncation-strategy` - 优先换行而非截断；截断时使用省略号并通过 tooltip/展开提供全文（Apple HIG）
- `letter-spacing` - 尊重平台默认字间距；避免正文字使用紧缩的字间距（HIG、MD）
- `number-tabular` - 数据列、价格、计时器使用等宽数字防止布局偏移
- `whitespace-balance` - 有意使用空白分组相关项和分隔区块；避免视觉杂乱（Apple HIG）

### 7. 动画（中）

- `duration-timing` - 微交互使用 150–300ms；复杂过渡 ≤400ms；避免 >500ms（MD）
- `transform-performance` - 仅使用 transform/opacity；避免对 width/height/top/left 做动画
- `loading-states` - 加载超过 300ms 时显示骨架屏或进度指示器
- `excessive-motion` - 每视图最多动画 1-2 个关键元素
- `easing` - 进入使用 ease-out，退出使用 ease-in；UI 过渡避免线性
- `motion-meaning` - 每个动画必须表达因果关系，不只为了装饰（Apple HIG）
- `state-transition` - 状态变化（悬停/活跃/展开/折叠/模态）应平滑动画，非跳变
- `continuity` - 页面/屏幕过渡应保持空间连贯性（共享元素、方向性滑动）（Apple HIG）
- `parallax-subtle` - 谨慎使用视差；必须尊重减少动画设置且不引起迷失方向（Apple HIG）
- `spring-physics` - 优先使用弹簧/物理曲线而非线性或 cubic-bezier 以获得自然感（Apple HIG 流体动画）
- `exit-faster-than-enter` - 退出动画比进入动画短（约进入的 60–70%）以感觉更灵敏（MD 动效）
- `stagger-sequence` - 列表/网格项逐个错开 30–50ms 进入；避免全部同时或过慢显示（MD）
- `shared-element-transition` - 使用共享元素/主角动画实现屏幕间的视觉连贯性（MD、HIG）
- `interruptible` - 动画必须可中断；用户点击/手势立即取消进行中的动画（Apple HIG）
- `no-blocking-animation` - 动画期间永不阻塞用户输入；UI 必须保持可交互（Apple HIG）
- `fade-crossfade` - 同一容器内内容替换使用淡入淡出/交叉淡入（MD）
- `scale-feedback` - 可点击卡片/按钮按下时轻微缩放（0.95–1.05）；释放时恢复（HIG、MD）
- `gesture-feedback` - 拖拽、滑动和捏合必须提供实时视觉响应追踪手指（MD Motion）
- `hierarchy-motion` - 使用 translate/scale 方向表达层级：从下方进入=更深，向上退出=返回（MD）
- `motion-consistency` - 全局统一持续时长/缓动令牌；所有动画共享相同的节奏感
- `opacity-threshold` - 淡出元素不应在 opacity 0.2 以下徘徊；要么完全淡出要么保持可见
- `modal-motion` - 模态框/面板应从触发源做动画（缩放+淡入或滑入）以提供空间上下文（HIG、MD）
- `navigation-direction` - 前进导航动画向左/上；后退向右/下——保持逻辑方向一致（HIG）
- `layout-shift-avoid` - 动画不得导致布局重排或 CLS；位置变化使用 transform

### 8. 表单与反馈（中）

- `input-labels` - 每个输入框有可见标签（不只用 placeholder）
- `error-placement` - 在相关字段下方显示错误
- `submit-feedback` - 提交时先加载中再显示成功/错误状态
- `required-indicators` - 标记必填字段（如星号）
- `empty-states` - 无内容时提供有用的消息和操作
- `toast-dismiss` - 轻提示自动 3-5 秒后消失
- `confirmation-dialogs` - 破坏性操作前确认
- `input-helper-text` - 复杂输入下方提供持久辅助文本，不只用 placeholder（Material Design）
- `disabled-states` - 禁用元素使用降低透明度（0.38–0.5）+ 光标变化 + 语义属性（MD）
- `progressive-disclosure` - 渐进式揭示复杂选项；不一开始 overwhelming 用户（Apple HIG）
- `inline-validation` - 失焦时验证（非击键时）；用户完成输入后才显示错误（MD）
- `input-type-keyboard` - 使用语义化输入类型（email、tel、number）触发正确的移动端键盘（HIG、MD）
- `password-toggle` - 密码字段提供显示/隐藏切换（MD）
- `autofill-support` - 使用 autocomplete / textContentType 属性使系统能自动填充（HIG、MD）
- `undo-support` - 允许撤销破坏性或批量操作（如"撤销删除"轻提示）（Apple HIG）
- `success-feedback` - 完成操作后以简短视觉反馈确认（勾选、轻提示、颜色闪烁）（MD）
- `error-recovery` - 错误消息必须包含清晰的恢复路径（重试、编辑、帮助链接）（HIG、MD）
- `multi-step-progress` - 多步流程显示步骤指示器或进度条；允许后退导航（MD）
- `form-autosave` - 长表单应自动保存草稿，防止意外关闭时数据丢失（Apple HIG）
- `sheet-dismiss-confirm` - 关闭未保存更改的面板/模态框前确认（Apple HIG）
- `error-clarity` - 错误消息必须说明原因 + 如何解决（不只说"输入无效"）（HIG、MD）
- `field-grouping` - 逻辑上对相关字段分组（fieldset/legend 或视觉分组）（MD）
- `read-only-distinction` - 只读状态应在视觉和语义上与禁用区分（MD）
- `focus-management` - 提交错误后自动聚焦第一个无效字段（WCAG、MD）
- `error-summary` - 多个错误时在顶部显示摘要并锚定到每个字段（WCAG）
- `touch-friendly-input` - 移动端输入高度 ≥44px 以满足触摸目标要求（Apple HIG）
- `destructive-emphasis` - 破坏性操作使用语义化危险色（红色）且与主操作视觉分离（HIG、MD）
- `toast-accessibility` - 轻提示不得抢夺焦点；使用 aria-live="polite" 进行读屏公告（WCAG）
- `aria-live-errors` - 表单错误使用 aria-live 区域或 role="alert" 通知读屏器（WCAG）
- `contrast-feedback` - 错误和成功状态颜色必须满足 4.5:1 对比度（WCAG、MD）
- `timeout-feedback` - 请求超时必须显示清晰的反馈并重试选项（MD）

### 9. 导航模式（高）

- `bottom-nav-limit` - 底部导航最多 5 项；图标配合文字标签（Material Design）
- `drawer-usage` - 抽屉/侧边栏用于二级导航，非主要操作（Material Design）
- `back-behavior` - 返回导航必须可预期且一致；保留滚动/状态（Apple HIG、MD）
- `deep-linking` - 所有关键屏幕必须可通过深度链接 / URL 访问，用于分享和通知（Apple HIG、MD）
- `tab-bar-ios` - iOS：使用底部 Tab Bar 作为顶级导航（Apple HIG）
- `top-app-bar-android` - Android：使用顶部应用栏配合导航图标作为主结构（Material Design）
- `nav-label-icon` - 导航项必须同时有图标和文字标签；纯图标导航损害可发现性（MD）
- `nav-state-active` - 当前位置必须在导航中视觉高亮（颜色、字重、指示器）（HIG、MD）
- `nav-hierarchy` - 主导航（标签/底部栏）vs 次导航（抽屉/设置）必须清晰分离（MD）
- `modal-escape` - 模态框和面板必须提供清晰的关闭/ dismissing 方式；移动端下滑关闭（Apple HIG）
- `search-accessible` - 搜索必须易于触达（顶部栏或标签）；提供近期/建议查询（MD）
- `breadcrumb-web` - Web：3+ 级深度的层级使用面包屑辅助定位（MD）
- `state-preservation` - 返回时恢复之前的滚动位置、筛选状态和输入（HIG、MD）
- `gesture-nav-support` - 支持系统手势导航（iOS 返回滑动、Android 预测性返回）无冲突（HIG、MD）
- `tab-badge` - 谨慎使用导航项上的标记显示未读/待处理；用户访问后清除（HIG、MD）
- `overflow-menu` - 操作超过可用空间时使用溢出/更多菜单而非挤在一起（MD）
- `bottom-nav-top-level` - 底部导航仅用于顶级屏幕；永不嵌套子导航（MD）
- `adaptive-navigation` - 大屏幕（≥1024px）偏好侧边栏；小屏幕使用底部/顶部导航（Material Adaptive）
- `back-stack-integrity` - 永不静默重置导航栈或意外跳回首页（HIG、MD）
- `navigation-consistency` - 导航位置在所有页面必须保持一致；不随页面类型改变
- `avoid-mixed-patterns` - 不在同一层级混用 Tab + 侧边栏 + 底部导航
- `modal-vs-navigation` - 模态框不能用于主导航流程；这会打破用户路径（HIG）
- `focus-on-route-change` - 页面切换后，将焦点移至读屏器的主内容区域（WCAG）
- `persistent-nav` - 核心导航必须从深层页面仍可触达；不在子流程中完全隐藏（HIG、MD）
- `destructive-nav-separation` - 危险操作（删除账户、退出登录）必须与常规导航项视觉和空间分离（HIG、MD）
- `empty-nav-state` - 导航目标不可用时，解释原因而非静默隐藏（MD）

### 10. 图表与数据（低）

- `chart-type` - 图表类型匹配数据类型（趋势→折线图、对比→柱状图、占比→饼图/环形图）
- `color-guidance` - 使用无障碍配色；避免仅红/绿这对色盲不友好的组合（WCAG、MD）
- `data-table` - 提供表格替代方案以保障无障碍性；图表本身对读屏器不友好（WCAG）
- `pattern-texture` - 用图案、纹理或形状补充颜色，使数据不依赖颜色也可区分（WCAG、MD）
- `legend-visible` - 始终显示图例；放置在图表附近，而非滚动折线下方的分离位置（MD）
- `tooltip-on-interact` - 悬停（Web）或点击（移动端）时提供工具提示/数据标签显示精确值（HIG、MD）
- `axis-labels` - 轴标签带单位和可读刻度；移动端避免截断或旋转标签
- `responsive-chart` - 小屏幕上图表必须重排或简化（如水平条形图替代垂直、减少刻度）
- `empty-data-state` - 无数据时显示有意义的空状态（"暂无数据" + 指引），非空白图表（MD）
- `loading-chart` - 图表数据加载时使用骨架屏或微光占位；不显示空的坐标框架
- `animation-optional` - 图表进入动画必须尊重 prefers-reduced-motion；数据应立即可读（HIG）
- `large-dataset` - 1000+ 数据点时聚合或抽样；提供下钻而非全部渲染（MD）
- `number-formatting` - 轴和标签上使用区域感知的数字、日期、货币格式化（HIG、MD）
- `touch-target-chart` - 图表可交互元素（数据点、扇区）必须有 ≥44pt 点击区域或在触摸时放大（Apple HIG）
- `no-pie-overuse` - 饼/环形图不超过 5 个分类；超过时切换为柱状图提高清晰度
- `contrast-data` - 数据线/柱与背景 ≥3:1；数据文字标签 ≥4.5:1（WCAG）
- `legend-interactive` - 图例应可点击以切换系列可见性（MD）
- `direct-labeling` - 小数据集直接在图表上标值以减少视线移动
- `tooltip-keyboard` - 工具提示内容必须可键盘触达，不只依赖悬停（WCAG）
- `sortable-table` - 数据表格必须支持排序并用 aria-sort 指示当前排序状态（WCAG）
- `axis-readability` - 轴刻度不拥挤；保持可读间距，小屏幕自动跳级
- `data-density` - 限制每张图表的信息密度避免认知超载；需要时拆分为多张图表
- `trend-emphasis` - 强调数据趋势而非装饰；避免遮蔽数据的重渐变/阴影
- `gridline-subtle` - 网格线应低对比度（如 gray-200）使其不与数据竞争
- `focusable-elements` - 图表可交互元素（点、条、扇区）必须可键盘导航（WCAG）
- `screen-reader-summary` - 为读屏器提供文本摘要或 aria-label 描述图表关键洞察（WCAG）
- `error-state-chart` - 数据加载失败必须显示错误消息和重试操作，非损坏/空白图表
- `export-option` - 对数据密集型产品，提供 CSV/图片的图表数据导出
- `drill-down-consistency` - 下钻交互必须保持清晰的路径和层级面包屑
- `time-scale-clarity` - 时间序列图表必须清晰标注时间粒度（日/周/月）并允许切换

## 使用方法

使用下方 CLI 工具搜索特定领域。

---

## 前置条件

检查 Python 是否已安装：

```bash
uv run python --version || python --version
```

---

## 如何使用此 Skill

在用户请求以下任何内容时使用此 Skill：

| 场景 | 触发示例 | 从哪开始 |
|------|---------|---------|
| **新项目 / 新页面** | "构建一个落地页"、"构建一个仪表盘" | 步骤 1 → 步骤 2（设计系统） |
| **新组件** | "创建一个价格卡片"、"添加一个模态框" | 步骤 3（领域搜索：style, ux） |
| **选择风格 / 颜色 / 字体** | "什么风格适合金融应用？"、"推荐一个配色方案" | 步骤 2（设计系统） |
| **审查现有 UI** | "审查这个页面的 UX 问题"、"检查无障碍性" | 上方快速参考清单 |
| **修复 UI Bug** | "按钮悬停坏了"、"加载时布局偏移" | 快速参考 → 相关部分 |
| **改进 / 优化** | "让它更快"、"改善移动端体验" | 步骤 3（领域搜索：ux, react） |
| **实现暗色模式** | "添加暗色模式支持" | 步骤 3（领域：style "dark mode"） |
| **添加图表 / 数据可视化** | "添加一个分析仪表盘图表" | 步骤 3（领域：chart） |
| **技术栈最佳实践** | "React 性能技巧"、"SwiftUI 导航" | 步骤 4（技术栈搜索） |

遵循以下工作流程：

### 步骤 1：分析用户需求

从用户请求中提取关键信息：
- **产品类型**：娱乐类（社交、视频、音乐、游戏）、工具类（扫描、编辑、转换）、生产力类（任务管理、笔记、日历）或混合
- **目标受众**：C 端消费者用户；考虑年龄组、使用场景（通勤、休闲、工作）
- **风格关键词**：俏皮、活力、极简、暗色模式、内容优先、沉浸式等
- **技术栈**：React Native（此项目唯一的技术栈）

### 步骤 2：生成设计系统（必须）

**始终从 `--design-system` 开始** 获取全面的推荐及推理：

```bash
uv run python skills/ui-ux-writer/scripts/search.py "<product_type> <industry> <keywords>" --design-system [-p "Project Name"]
```

此命令：
1. 并行搜索多个领域（product、style、color、landing、typography）
2. 从 `ui-reasoning.csv` 应用推理规则选择最佳匹配
3. 返回完整的设计系统：模式、风格、颜色、字体、效果
4. 包含需避免的反模式

**示例：**
```bash
uv run python skills/ui-ux-writer/scripts/search.py "beauty spa wellness service" --design-system -p "Serenity Spa"
```

### 步骤 2b：持久化设计系统（Master + 覆盖模式）

要保存设计系统以实现 **跨会话的分层检索**，添加 `--persist`：

```bash
uv run python skills/ui-ux-writer/scripts/search.py "<query>" --design-system --persist -p "Project Name"
```

这将创建：
- `design-system/MASTER.md` — 全局单一事实源，包含所有设计规则
- `design-system/pages/` — 用于页面级覆盖的文件夹

**带页面级覆盖：**
```bash
uv run python skills/ui-ux-writer/scripts/search.py "<query>" --design-system --persist -p "Project Name" --page "dashboard"
```

这还会创建：
- `design-system/pages/dashboard.md` — 偏离 Master 的页面级规则

**分层检索工作原理：**
1. 构建特定页面（如"结算"）时，先检查 `design-system/pages/checkout.md`
2. 如果页面文件存在，其规则 **覆盖** Master 文件
3. 如果不存在，则仅使用 `design-system/MASTER.md`

**上下文感知检索提示词：**
```
我正在构建 [页面名称] 页面。请阅读 design-system/MASTER.md。
同时检查 design-system/pages/[页面名].md 是否存在。
如果页面文件存在，优先使用其规则。
如果不存在，则仅使用 Master 规则。
现在，生成代码...
```

### 步骤 3：用详细搜索补充（按需）

获取设计系统后，使用领域搜索获取更多细节：

```bash
uv run python skills/ui-ux-writer/scripts/search.py "<keyword>" --domain <domain> [-n <max_results>]
```

**使用详细搜索的场景：**

| 需求 | 领域 | 示例 |
|------|------|------|
| 产品类型模式 | `product` | `--domain product "entertainment social"` |
| 更多风格选项 | `style` | `--domain style "glassmorphism dark"` |
| 配色方案 | `color` | `--domain color "entertainment vibrant"` |
| 字体搭配 | `typography` | `--domain typography "playful modern"` |
| 图表推荐 | `chart` | `--domain chart "real-time dashboard"` |
| UX 最佳实践 | `ux` | `--domain ux "animation accessibility"` |
| 替代字体 | `typography` | `--domain typography "elegant luxury"` |
| 单个 Google 字体 | `google-fonts` | `--domain google-fonts "sans serif popular variable"` |
| 落地页结构 | `landing` | `--domain landing "hero social-proof"` |
| React 性能 | `react` | `--domain react "rerender memo list"` |
| 应用界面无障碍 | `web` | `--domain web "accessibilityLabel touch safe-areas"` |
| AI 提示词 / CSS 关键词 | `prompt` | `--domain prompt "minimalism"` |

### 步骤 4：技术栈指南（React Native）

获取 React Native 实现特定的最佳实践：

```bash
uv run python skills/ui-ux-writer/scripts/search.py "<keyword>" --stack react-native
```

---

## 搜索参考

### 可用领域

| 领域 | 用途 | 示例关键词 |
|------|------|-----------|
| `product` | 产品类型推荐 | SaaS、电子商务、作品集、医疗健康、美妆、服务 |
| `style` | UI 风格、颜色、效果 | 玻璃态、极简主义、暗色模式、粗野主义 |
| `typography` | 字体搭配、Google 字体 | 优雅、俏皮、专业、现代 |
| `color` | 按产品类型配色 | saas、ecommerce、healthcare、beauty、fintech、service |
| `landing` | 页面结构、CTA 策略 | hero、hero-centric、testimonial、pricing、social-proof |
| `chart` | 图表类型、库推荐 | trend、comparison、timeline、funnel、pie |
| `ux` | 最佳实践、反模式 | animation、accessibility、z-index、loading |
| `google-fonts` | Google 字体单独查找 | sans serif、monospace、japanese、variable font、popular |
| `react` | React/Next.js 性能 | waterfall、bundle、suspense、memo、rerender、cache |
| `web` | 应用界面指南（iOS/Android/React Native） | accessibilityLabel、touch targets、safe areas、Dynamic Type |
| `prompt` | AI 提示词、CSS 关键词 | （风格名称） |

### 可用技术栈

| 技术栈 | 关注点 |
|--------|--------|
| `react-native` | 组件、导航、列表 |

---

## 示例工作流

**用户请求：** "做一个 AI 搜索首页。"

### 步骤 1：分析需求
- 产品类型：工具（AI 搜索引擎）
- 目标受众：寻找快速智能搜索的 C 端用户
- 风格关键词：现代、极简、内容优先、暗色模式
- 技术栈：React Native

### 步骤 2：生成设计系统（必须）

```bash
uv run python skills/ui-ux-writer/scripts/search.py "AI search tool modern minimal" --design-system -p "AI Search"
```

**输出：** 包含模式、风格、颜色、字体、效果和反模式的完整设计系统。

### 步骤 3：用详细搜索补充（按需）

```bash
# 获取现代工具类产品的风格选项
uv run python skills/ui-ux-writer/scripts/search.py "minimalism dark mode" --domain style

# 获取搜索交互和加载的 UX 最佳实践
uv run python skills/ui-ux-writer/scripts/search.py "search loading animation" --domain ux
```

### 步骤 4：技术栈指南

```bash
uv run python skills/ui-ux-writer/scripts/search.py "list performance navigation" --stack react-native
```

**然后：** 综合设计系统 + 详细搜索结果并实现设计。

---

## 输出格式

`--design-system` 标志支持两种输出格式：

```bash
# ASCII 框（默认）- 最适合终端显示
uv run python skills/ui-ux-writer/scripts/search.py "fintech crypto" --design-system

# Markdown - 最适合文档
uv run python skills/ui-ux-writer/scripts/search.py "fintech crypto" --design-system -f markdown
```

---

## 更好效果的技巧

### 查询策略

- 使用 **多维关键词** — 组合产品 + 行业 + 基调 + 密度：`"entertainment social vibrant content-dense"` 而非仅仅 `"app"`
- 对同一需求尝试不同关键词：`"playful neon"` → `"vibrant dark"` → `"content-first minimal"`
- 先用 `--design-system` 获取完整推荐，再用 `--domain` 深入你不确定的任何维度
- 始终添加 `--stack react-native` 获取实现特定的指导

### 常见卡点

| 问题 | 解决方法 |
|------|---------|
| 无法决定风格/颜色 | 用不同关键词重新运行 `--design-system` |
| 暗色模式对比度问题 | 快速参考 §6：`color-dark-mode` + `color-accessible-pairs` |
| 动画感觉不自然 | 快速参考 §7：`spring-physics` + `easing` + `exit-faster-than-enter` |
| 表单 UX 差 | 快速参考 §8：`inline-validation` + `error-clarity` + `focus-management` |
| 导航感觉混乱 | 快速参考 §9：`nav-hierarchy` + `bottom-nav-limit` + `back-behavior` |
| 小屏幕上布局崩溃 | 快速参考 §5：`mobile-first` + `breakpoint-consistency` |
| 性能 / 卡顿 | 快速参考 §3：`virtualize-lists` + `main-thread-budget` + `debounce-throttle` |

### 交付前清单

- 在实现前运行 `--domain ux "animation accessibility z-index loading"` 做 UX 验证
- 运行快速参考 **§1–§3**（关键 + 高）做最终审查
- 在 375px（小屏手机）和横屏方向上测试
- 验证开启 **减少动画** 和 **Dynamic Type** 最大尺寸时的行为
- 独立检查暗色模式对比度（不要假设亮色模式的值可用）
- 确认所有触摸目标 ≥44pt 且无内容隐藏在安全区域后面

---

## 专业 UI 通用规则

这些是经常被忽略、导致 UI 看起来不专业的问题：
范围说明：以下规则适用于 App UI（iOS/Android/React Native/Flutter），非桌面 Web 交互模式。

### 图标与视觉元素

| 规则 | 标准 | 避免 | 重要性 |
|------|------|------|--------|
| **不用 Emoji 作结构图标** | 使用矢量图标（如 Lucide、react-native-vector-icons、@expo/vector-icons） | 在导航、设置或系统控件中使用 emoji（🎨 🚀 ⚙️） | Emoji 依赖字体、跨平台不一致，无法通过设计令牌控制 |
| **仅使用矢量资源** | 使用 SVG 或平台矢量图标，可清晰缩放并支持主题 | 模糊或像素化的栅格 PNG 图标 | 确保可扩展性、清晰渲染和暗/亮模式适配 |
| **稳定的交互状态** | 使用颜色、透明度或高程过渡实现按下状态，不改变布局边界 | 导致周围内容移动或触发视觉抖动的布局变换 | 防止不稳定交互，保持移动端的流畅动感和感知质量 |
| **正确的品牌 Logo** | 使用官方品牌素材并遵循使用指南（间距、颜色、安全空间） | 猜测 Logo 路径、非官方重新着色或修改比例 | 防止品牌误用，确保法律/平台合规 |
| **一致的图标尺寸** | 将图标尺寸定义为设计令牌（如 icon-sm、icon-md = 24pt、icon-lg） | 随机混用 20pt / 24pt / 28pt 等任意值 | 保持界面整体的节奏和视觉层级 |
| **描边一致性** | 同一视觉层使用一致的描边宽度（如 1.5px 或 2px） | 随意混合粗细描边风格 | 不一致的描边降低感知精致度和凝聚力 |
| **填充 vs 描边的规范** | 每个层级使用一种图标风格 | 在同一层级混用填充和描边图标 | 保持语义清晰和风格连贯 |
| **触摸目标最小值** | 最小 44×44pt 交互区域（图标较小时使用 hitSlop） | 小图标无扩展点击区域 | 满足无障碍性和平台可用性标准 |
| **图标对齐** | 图标对齐文字基线并保持一致的内边距 | 图标不对齐或周围间距不一致 | 防止降低感知质量的细微视觉不平衡 |
| **图标对比度** | 遵循 WCAG 对比度标准：小元素 4.5:1，较大 UI 图标最小 3:1 | 与背景融为一体的低对比度图标 | 确保亮色和暗色模式下的无障碍性 |

### 交互（App）

| 规则 | 应该 | 不应该 |
|------|------|--------|
| **点击反馈** | 在 80-150ms 内提供清晰的按下反馈（涟漪/透明度/高程） | 点击无视觉响应 |
| **动画时机** | 微交互保持约 150-300ms，带平台原生缓动 | 瞬间切换或慢动画（>500ms） |
| **无障碍聚焦** | 确保读屏器聚焦顺序与视觉顺序一致，标签描述清晰 | 无标签控件或混乱的聚焦遍历 |
| **禁用状态清晰度** | 使用禁用语义（`disabled`/原生 disabled 属性），降低强调，无点击操作 | 看起来可点击但无任何反应的控件 |
| **触摸目标最小值** | 点击区域 >=44x44pt（iOS）或 >=48x48dp（Android），图标较小时扩展点击区域 | 微小点击区域或无内边距的纯图标点击区域 |
| **手势冲突预防** | 每个区域保持一个主手势，避免嵌套的点击/拖拽冲突 | 重叠手势导致意外操作 |
| **语义化原生控件** | 优先使用原生交互原语（`Button`、`Pressable`、平台等价物）配合正确的无障碍角色 | 通用容器作为无语义的主控件 |

### 亮/暗模式对比度

| 规则 | 应该 | 不应该 |
|------|------|--------|
| **表面可读性（亮色）** | 卡片/表面与背景清晰分离，有足够的不透明度/高程 | 过度透明导致层级模糊的表面 |
| **文字对比度（亮色）** | 正文与亮色表面的对比度 >=4.5:1 | 低对比度的灰色正文 |
| **文字对比度（暗色）** | 暗色表面主文字对比度 >=4.5:1，次文字 >=3:1 | 与背景融为一体的暗色模式文字 |
| **边框和分隔线可见性** | 分隔线在两种主题下均可见（不只亮色模式） | 仅特定主题存在的边框在某模式下消失 |
| **状态对比度对等** | 按下/聚焦/禁用状态在亮色和暗色主题中同样可区分 | 只为一种主题定义交互状态 |
| **令牌驱动主题** | 使用语义化颜色令牌，跨应用表面/文字/图标按主题映射 | 每个屏幕硬编码的色值 |
| **遮罩和模态可读性** | 模态遮罩足够强以隔离前景内容（通常 40-60% 黑色） | 弱遮罩使背景视觉上产生竞争 |

### 布局与间距

| 规则 | 应该 | 不应该 |
|------|------|--------|
| **安全区域合规** | 所有固定头部、标签栏和 CTA 栏尊重顶部/底部安全区域 | 将固定 UI 放在刘海、状态栏或手势区域下方 |
| **系统栏清除** | 为状态/导航栏和手势主页指示器添加间距 | 可点击内容与 OS 界面冲突 |
| **一致的内容宽度** | 每个设备类别（手机/平板）保持可预测的内容宽度 | 屏幕之间混用任意宽度 |
| **8dp 间距节奏** | 内边距/间距/区块间距使用一致的 4/8dp 间距系统 | 无节奏的随机间距增量 |
| **可读的文字宽度** | 大设备上保持长文可读（平板上避免边缘到边缘的段落） | 全宽长文降低可读性 |
| **区块间距层级** | 按层级定义清晰的垂直节奏层级（如 16/24/32/48） | 相似 UI 层级有不一致的间距 |
| **按断点自适应边距** | 较大宽度和横屏时增加水平内边距 | 所有设备尺寸/方向使用相同的窄边距 |
| **滚动与固定元素共存** | 添加底部/顶部内容内边距，使列表不被固定栏遮挡 | 滚动内容被粘性头部/底部遮挡 |

---

## 交付前清单

交付 UI 代码前，验证以下项目：
范围说明：此清单适用于 App UI（iOS/Android/React Native/Flutter）。

### 视觉质量
- [ ] 不用 emoji 做图标（使用 SVG 代替）
- [ ] 所有图标来自一致的图标家族和风格
- [ ] 使用官方品牌素材，比例和安全空间正确
- [ ] 按下状态视觉不改变布局边界或导致抖动
- [ ] 一致使用语义化主题令牌（无每个屏幕临时硬编码的颜色）

### 交互
- [ ] 所有可点击元素提供清晰的按下反馈（涟漪/透明度/高程）
- [ ] 触摸目标满足最小尺寸（>=44x44pt iOS，>=48x48dp Android）
- [ ] 微交互时机保持在 150-300ms 范围内，带原生感觉的缓动
- [ ] 禁用状态视觉清晰且非交互
- [ ] 读屏器聚焦顺序与视觉顺序一致，交互标签描述清晰
- [ ] 手势区域避免嵌套/冲突交互（点击/拖拽/返回滑动冲突）

### 亮/暗模式
- [ ] 亮色和暗色模式下主文字对比度 >=4.5:1
- [ ] 亮色和暗色模式下次文字对比度 >=3:1
- [ ] 分隔线/边框和交互状态在两种模式下均可区分
- [ ] 模态框/抽屉遮罩不透明度足够强以保持前景可读性（通常 40-60% 黑色）
- [ ] 两种主题均在交付前经过测试（非从单一主题推断）

### 布局
- [ ] 头部、标签栏和底部 CTA 栏尊重安全区域
- [ ] 滚动内容不在固定/粘性栏后面被遮挡
- [ ] 在小屏手机、大屏手机和平板上验证（竖屏 + 横屏）
- [ ] 水平内边距/gutter 按设备尺寸和方向正确适配
- [ ] 组件、区块和页面层级保持 4/8dp 间距节奏
- [ ] 大设备上长文宽度保持可读（无边缘到边缘的段落）

### 无障碍性
- [ ] 所有有意义的图片/图标有无障碍标签
- [ ] 表单字段有标签、提示和清晰的错误消息
- [ ] 颜色不是唯一的指示器
- [ ] 支持减少动画和动态文字尺寸，不导致布局破坏
- [ ] 无障碍特性/角色/状态（选中、禁用、展开）正确播报



