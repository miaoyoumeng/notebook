# vue-validator

Vue 需求开发完成后的验证 skill。

## 用途

当 Vue 功能开发完毕后，使用此 skill 来：
1. 解析开发 task issue，获取 PRD 和 UI 设计稿路径
2. 读取 PRD 文档和 UI HTML 设计稿
3. 启动开发服务器（`pnpm run serve`）
4. 调用 playwright-cli 显示打开浏览器，逐页截图
5. 根据需求文档评估完成度
6. 发现 bug 时截图并调用 issue-writer 创建 bug issue 文档
7. 生成验证报告（含完成度评分、截图、bug 列表）

## 工作流程

```
1. 解析开发 task issue → 提取 PRD 路径、UI 路径、验收标准
2. 读取 PRD 文档 → 明确页面、功能点、交互预期
3. 读取 UI HTML 设计稿 → 明确布局、视觉风格
4. 启动开发服务器 → 检查 8000 端口，未启动则 pnpm run serve
5. Playwright CLI 截图验证 → 显示打开浏览器，逐页截图
6. 评估需求完成度 → 页面完整性、功能覆盖、UI 一致性、数据展示、交互验证
7. Bug 处理 → 截图保存到 /tmp/logs/bugs/，调用 issue-writer
8. 输出验证报告 → 对照表、截图、评分、bug 列表
```

## 目录结构

```
vue-validator/
├── SKILL.md              # 核心工作流程说明（8 步）
├── README.md             # 本文件
├── references/           # 参考文档（可按需添加）
└── evals/
    └── evals.json        # 12 个测试用例，覆盖常见 Vue 功能验证场景
```

## 使用方式

在 Vue 需求开发完成后，提供开发 task issue 内容，调用此 skill 即可开始验证流程。

## 依赖

- Vue 项目（已开发完毕）
- `/solo:playwright-cli` skill（用于浏览器操作）
- `/solo:issue-writer` skill（用于 bug issue 文档生成）

## 截图存放路径

| 类型 | 路径 |
|------|------|
| 验证截图 | `/tmp/logs/screenshots/<feature-name>/` |
| Bug 截图 | `/tmp/logs/bugs/<feature-name>/` |

## 服务启动

- 启动命令：`pnpm run serve`
- 启动前检查：先通过 `lsof -i :8000` 检查端口是否已有进程监听
- 服务地址：`http://localhost:8000/`
- 登录方式：任意输入账号和密码，点击登录即可
