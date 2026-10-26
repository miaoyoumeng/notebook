# typescript-tdd

TypeScript + Vitest + Vite 项目的 TDD 单元测试技能。

## 用途

指导 Claude 按测试驱动开发流程完成任务：

1. 写一个失败的测试；
2. 运行并确认失败原因；
3. 写最小实现让测试通过；
4. 重构并保持全部测试通过。

铁律：没有失败的测试之前，禁止写产品代码。已经写了产品代码，删除后从测试重新开始。

## 适用场景

- 编写 TypeScript 单元测试；
- 实践测试驱动开发；
- 为功能或缺陷补测试；
- 提升测试覆盖率；
- 生成 mock、stub、spy；
- 修复 Bug（先写复现测试）。

不适用于端到端测试、性能压测、非 TypeScript 项目。

## 使用方式

在 Claude Code 中安装含本技能的 `luban` 插件后，直接描述任务即可触发。示例：

```text
给 src/utils/formatPrice.ts 写单元测试，先写测试再实现。
```

```text
登录接口在 token 过期时返回 500，帮我修一下，先补个复现测试。
```

```text
这个 Vitest 配置的覆盖率只有 62%，把 src/services 提到 80%。
```

技能会读取 `package.json`、`vite.config.ts`、`vitest.config.ts`，按项目已有命令执行，不覆盖项目配置。

## 目录结构

```text
typescript-tdd/
├── SKILL.md                          # 技能指令：工作流、判定标准、验证命令
├── README.md                         # 本文件
├── references/
│   ├── tdd-best-practices.md         # TDD 纪律、验证清单、借口与危险信号
│   ├── testing-anti-patterns.md      # 五类测试反模式与 mock 门控
│   ├── framework-guide.md            # Vitest 配置、测试组织、纯函数与异步函数
│   └── ci-integration.md             # GitHub Actions、覆盖率门禁、缓存
├── scripts/
│   ├── test_generator.py             # 生成测试桩、分析函数结构
│   ├── coverage_analyzer.py          # 解析 LCOV/JSON 覆盖率
│   ├── tdd_workflow.py               # RED/GREEN/REFACTOR 阶段引导
│   └── fixture_generator.py          # 生成夹具、边界值与 mock
├── assets/
│   └── sample_input.json             # 脚本输入示例
└── evals/
    └── evals.json                    # 测试用例
```

## 测试文件组织

测试文件放在与 `src` 同级的 `test` 目录，结构镜像 `src`：

```text
src/utils/formatPrice.ts
test/utils/formatPrice.real.test.ts   # 使用真实依赖
test/utils/formatPrice.mock.test.ts   # 隔离外部依赖
```

## 验证命令

优先使用项目已有脚本；缺少时直接调用本地二进制：

```bash
pnpm tsc --noEmit
pnpm vitest run
pnpm vitest run --coverage
```

安装 Vitest：

```bash
pnpm add -D vitest @vitest/coverage-v8
```

## 脚本

脚本依赖 `typer` 与 `rich`，使用 `uv` 运行：

```bash
# 生成测试桩
uv run --with typer --with rich python scripts/test_generator.py \
  generate --input src/utils/formatPrice.ts \
  --output test/utils/formatPrice.real.test.ts

# 分析覆盖率
uv run --with typer --with rich python scripts/coverage_analyzer.py \
  analyze --report coverage/lcov.info --threshold 80

# 初始化 TDD 状态
uv run --with typer --with rich python scripts/tdd_workflow.py \
  init --path .tdd-state.json

# 生成夹具
uv run --with typer --with rich python scripts/fixture_generator.py \
  fixture --entity User --count 5 --source src/types.ts
```

`test_generator.py` 按源文件名生成相对 import；输出到 `test/` 镜像目录后，按实际相对路径修正 import。

脚本生成的是测试桩，不等于测试。真正编写测试必须走 TDD 流程。
