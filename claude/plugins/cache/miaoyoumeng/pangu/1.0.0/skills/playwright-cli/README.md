# playwright-cli

命令行驱动的浏览器自动化技能。支持页面交互、截图、录屏、控制台与网络取证，以及 Playwright 测试的生成与调试。

## 适用场景

- 打开网页并填写表单、点击、上传文件
- 验证页面功能、复现前端缺陷
- 截图、导出 PDF、录制视频与追踪
- 读取控制台日志与网络请求，模拟接口响应
- 生成、运行、调试 Playwright 测试
- 保存并复用登录态

## 快速开始

安装：

```bash
pnpm add -g @playwright/cli@latest
```

基本操作：

```bash
playwright-cli open https://example.com
playwright-cli snapshot
playwright-cli fill e1 "user@example.com"
playwright-cli click e2
playwright-cli screenshot --filename=result.png
playwright-cli close
```

## 文件结构

```text
playwright-cli/
├── SKILL.md                 # 技能入口：命令参考、流程、验证清单
├── README.md                # 本文件
├── references/              # 10 篇专题参考文档，按需加载
└── evals/evals.json         # 测试用例骨架
```

## 使用方式

在 Claude Code 中直接描述浏览器任务即可触发，例如：

- “打开 http://localhost:3000，用测试账号登录，截图首页”
- “检查这个页面控制台有没有报错”
- “把这段操作录成视频”
- “给登录流程生成 Playwright 测试”

执行细节见 `SKILL.md`；测试生成、追踪、请求模拟等专题见 `references/`。

## 维护

- 命令清单与上游 `playwright-cli` 保持一致，升级后核对新增命令。
- 修改 `SKILL.md` 后，用 `/pangu:commander-skill chirping score playwright-cli` 检查质量。
