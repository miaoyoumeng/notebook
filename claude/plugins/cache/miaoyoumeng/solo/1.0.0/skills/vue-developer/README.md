# Vue Developer Skill

## 简介

本 Skill 提供基于 Vue3 + TypeScript 构建全栈应用程序的完整工作流规范和开发标准。

## 目录结构

```
vue-developer/
├── SKILL.md                 # Skill 核心内容
├── README.md                # 使用说明
├── references/              # 参考文档
│   ├── component-patterns.md    # 组件模式与最佳实践
│   ├── state-management.md      # Pinia 状态管理详解
│   ├── api-integration.md       # API 请求层设计
│   └── testing-guide.md         # 测试策略与示例
├── evals/
│   └── evals.json           # 评估测试用例
└── script/                  # 辅助脚本（可选）
```

## 使用说明

当需要以下操作时，此 Skill 会被触发：

- 根据 PRD 和 UI 设计稿开发管理后台页面
- 使用 Vue3 + TypeScript 开发新功能页面
- 调用 tdesign-vue-next 完成页面布局
- 调用 rest-api-writer 完成 API 接口定义
- 调用 tdd-typescript 完成交互逻辑开发
- 对 Vue 项目进行编译构建和错误修复

## 核心工作流

1. **读取 PRD** → 阅读 `outputs/prds/admin/` 下的 PRD 文件
2. **读取 UI 设计稿** → 阅读 `outputs/ui/admin/` 下的 HTML 设计稿
3. **开发页面布局** → 调用 `/solo:tdesign-vue-next`，仅使用 TDesign 组件
4. **发现 API 接口** → 调用 `/solo:rest-api-writer` 完成接口定义
5. **开发页面交互** → 调用 `/solo:tdd-typescript` 实现交互逻辑
6. **编译构建** → 执行 `pnpm run build`，修复编译错误直至通过

## 开发规范要点

- 全部使用 `<script setup lang="ts">`
- 禁止 `any` 类型
- API 调用必须通过 `request/` 封装 + `api/` 接口 + stores 调用
- 组件名 PascalCase，文件名 PascalCase
- 每个业务模块独立的 store 和 API 文件
- 布局框架放在 `layouts/`，页面组件放在 `pages/`，业务视图放在 `views/`
- 路由配置放在 `routers/`（复数）
- 类型声明放在 `typings/`，全局样式放在 `styles/`
