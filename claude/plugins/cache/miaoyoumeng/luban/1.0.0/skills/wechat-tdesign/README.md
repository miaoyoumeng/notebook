# wechat-tdesign

为微信小程序构建基于 TDesign 组件库（`tdesign-miniprogram`）的界面。

## 何时使用

用户需要在微信小程序或 Taro 项目中使用 TDesign 搭建页面、选用组件、定制主题或排查组件问题时使用，例如：

- `用 TDesign 写一个带搜索的商品列表页`
- `tdesign-miniprogram 的表单组件怎么接入`
- `把项目主题色改成品牌绿，并支持暗黑模式`

不要用于网页端的 `tdesign-react`、`tdesign-vue`，也不要用于非 TDesign 的 UI 需求。

## 目录结构

```text
wechat-tdesign/
├── SKILL.md          # frontmatter + 指令正文
├── README.md         # 本文件
├── scripts/          # 确定性可执行脚本
├── references/       # 组件 API 与主题文档
├── assets/           # 模板与资源文件
└── evals/
    └── evals.json    # 测试用例
```

## 使用方式

技能由 Claude 根据用户请求自动触发，无需手动调用。正文见 [SKILL.md](SKILL.md)。

`references/` 包含三类文档，共 75 个文件：

- `miniprogram/`：安装、组件总览、样式、主题、暗黑模式。
- `miniprogram/components/`：59 个组件的 API 与示例。
- `miniprogram-chat/`：AI 聊天组件与 SSE 流式输出。

组件属性与事件以对应参考文档为准。
