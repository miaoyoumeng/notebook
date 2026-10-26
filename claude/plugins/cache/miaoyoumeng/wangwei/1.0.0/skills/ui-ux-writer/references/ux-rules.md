# UI/UX 规则清单

实现与审查时按优先级核对。表中条目为检查项；`--domain ux` 检索的是 `assets/data/ux-guidelines.csv` 中的详细说明，与本表条目各自独立。

## 规则优先级

按优先级 1→10 决定核对顺序。

| 优先级 | 类别 | 影响级别 | 领域 | 关键检查项 | 反模式 |
|--------|------|----------|------|-----------|--------|
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

## 1. 无障碍设计（关键）

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

## 2. 触摸与交互（关键）

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

## 3. 性能（高）

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

## 4. 风格选择（高）

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

## 5. 布局与响应式（高）

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

## 6. 字体与颜色（中）

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

## 7. 动画（中）

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

## 8. 表单与反馈（中）

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

## 9. 导航模式（高）

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

## 10. 图表与数据（低）

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
