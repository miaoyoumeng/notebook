# TDD TypeScript — TypeScript + Vue 3 + TDesign 严格 TDD Skill

**版本**: 1.0.0
**更新日期**: 2026-05-29

**严格遵循 TDD 铁律的 TypeScript 单元测试 skill。** 针对 Vue 3 + TDesign + Vite 技术栈，基于 Vitest。

> **铁律：** 没有失败的测试之前，禁止写产品代码。
> 已经写了？删掉。从头开始。

## 目录

- [概述](#概述)
- [铁律](#铁律)
- [安装](#安装)
- [快速开始](#快速开始)
- [脚本模块](#脚本模块)
- [配置](#配置)
- [技术栈](#技术栈)
- [测试质量标准](#测试质量标准)
- [故障排除](#故障排除)
- [测试反模式](#测试反模式)

## 概述

TDD TypeScript skill 将**严格的 TDD 纪律**集成到 Vue 3 + TDesign + Vite 项目中：

- **铁律约束**: 没有失败测试之前禁止写产品代码
- **强制验证**: RED 必须亲眼看到失败，GREEN 必须亲眼看到通过
- **反模式门控**: 防止测试 mock 行为、生产类污染等常见错误
- **智能测试桩生成**: 从代码或需求生成测试桩
- **覆盖率分析**: 解析 LCOV/JSON 覆盖率报告，识别缺口

## 铁律

```
没有失败的测试之前，禁止写产品代码
```

**违反铁律的惩罚：**
- 已经写了产品代码？**删掉**。从头开始。
- 不要保留"作为参考"
- 不要在写测试时"适配"它
- **删除就是删除**

**强制验证：**
- RED：必须**亲眼看到测试失败**
- GREEN：必须**亲眼看到测试通过**，且其他测试依然通过，输出干净
- REFACTOR：每次小重构后**必须重新运行测试**

详见 `references/tdd-best-practices.md` 和 `references/testing-anti-patterns.md`。

## 安装

```bash
# 项目级别安装
cp -r tdd-typescript /path/to/your/project/.claude/skills/

# 用户级别安装
cp -r tdd-typescript ~/.claude/skills/
```

## 快速开始

### 1. 从代码生成测试

```
@tdd-typescript

为以下 TypeScript composable 生成测试：
import { ref } from 'vue';

export function useCounter(initial = 0) {
  const count = ref(initial);
  const increment = () => count.value++;
  const decrement = () => count.value--;
  return { count, increment, decrement };
}
```

### 2. 分析覆盖率

```
@tdd-typescript

分析覆盖率报告：coverage/lcov.info
源代码目录：src/
目标：80% 覆盖率
按优先级推荐
```

### 3. TDD 工作流引导

```
@tdd-typescript

引导我完成用户表格组件的 TDD 实现。

需求：
- 展示用户列表（TDesign Table 组件）
- 支持编辑和删除操作
- 空数据时显示空状态
- 支持分页

技术栈：Vue 3 + TDesign + Vitest
```

## 脚本模块

### test_generator.py
从 TypeScript 源码生成测试用例：
- 解析 TypeScript 源码结构
- 生成 describe/it 代码块
- 支持函数、composable 等模式
- 覆盖 happy path、错误、边界场景

### coverage_analyzer.py
解析和分拆覆盖率报告：
- 支持 LCOV 和 JSON 格式
- 按优先级分类缺口（P0/P1/P2）
- 生成可操作的改进建议

### tdd_workflow.py
引导 Red-Green-Refactor 工作流：
- 验证每个阶段的完成条件
- 重构建议
- 工作流状态追踪

### fixture_generator.py
生成测试夹具和 mock 数据：
- 从 TypeScript interface/type 生成 mock 对象
- 边界值生成
- 边缘场景数据

## 配置

### .tdd-typescript.json（可选，项目根目录）

```json
{
  "coverage_threshold": 80,
  "test_directory": "src/__tests__/",
  "quality_rules": {
    "max_assertions_per_test": 3,
    "require_descriptive_names": true,
    "enforce_isolation": true
  }
}
```

## 技术栈

### 测试框架
- **Vitest** 0.34+ — 测试运行器，与 Vite 原生集成

### 测试工具
- **@vue/test-utils** 2+ — Vue 3 组件挂载和交互测试
- **v8** — 覆盖率提供者（Vitest 内置）
- **fast-check** — Property-Based 测试
- **Stryker** — 变异测试

### 项目基础设施
- **Vite** 5+ — 构建工具
- **Vue** 3.3+ — 组件框架（Composition API）
- **TDesign Vue Next** — UI 组件库
- **TypeScript** 4.5+

## 测试质量标准

| 指标 | 目标 |
|------|------|
| 行覆盖率 | 80%+ |
| 分支覆盖率 | 75%+ |
| 函数覆盖率 | 90%+ |
| 单次测试耗时 | < 100ms |
| 每测试断言数 | 1-3 |

## 故障排除

**问题：生成的测试语法不正确**
```
解决：确认使用的是 Vitest，生成器默认使用 Vitest 语法
```

**问题：覆盖率报告无法识别**
```
解决：验证格式（LCOV 或 JSON），尝试粘贴原始覆盖率数据
```

**问题：建议过多，难以处理**
```
解决：要求按优先级输出，如 "只显示 P0 级别的建议"
```

**问题：Vue 组件测试报错 "TDesign component not found"**
```
解决：在 mount 的 global.plugins 中注册 TDesign
```

## 测试反模式

**写 mock 或添加测试工具时，必读 `references/testing-anti-patterns.md`。**

**铁律：**
1. 永不测试 mock 行为
2. 永不在生产类上添加仅测试用方法
3. 永不在未理解依赖的情况下使用 mock

**常见违规：**
- 断言 `*-mock` test ID → 测试的是 mock 而不是组件
- 类的方法只在测试文件中调用 → 移到测试工具
- Mock 设置占测试 >50% → 考虑集成测试
- Mock "保险起见" → 先理解依赖再 mock

---

## 目录结构

```
tdd-typescript/
├── SKILL.md                       # Skill 定义（含铁律）
├── README.md                      # 本文件
├── pyproject.toml                 # Python 依赖
├── references/
│   ├── tdd-best-practices.md      # TDD 纪律（含铁律、红旗）
│   ├── testing-anti-patterns.md   # 测试反模式与门控函数
│   ├── framework-guide.md         # Vue 3 + Vitest 测试指南
│   └── ci-integration.md          # CI 集成指南（GitHub Actions + pnpm）
├── scripts/
│   ├── test_generator.py          # 测试桩生成（桩 ≠ 测试，仍须走 TDD）
│   ├── coverage_analyzer.py       # 覆盖率分析
│   ├── tdd_workflow.py            # TDD 工作流引导
│   └── fixture_generator.py       # 夹具生成
└── assets/
    └── sample_input.json          # 示例输入
```

## 版本历史

### v1.0.0 (2026-05-29)
- 初始版本
- **严格遵循 TDD 铁律**：没有失败测试之前禁止写产品代码
- 专注于 TypeScript + Vue 3 + TDesign + Vite 技术栈
- 基于 Vitest 测试框架
- 强制 RED/GREEN 验证步骤
- 5 大测试反模式门控
- LCOV/JSON 覆盖率分析
- 测试夹具生成
- CI 集成指南（GitHub Actions + pnpm）
