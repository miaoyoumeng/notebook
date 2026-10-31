# typescript-taster

识别 TypeScript 代码中的 AI 味道，输出按严重程度分级的检测报告。

## 用途

- 扫描 TypeScript 代码库。
- 检测 AI 生成的典型模式：类型冗余、过度注释、防御性检查、模板化模式、命名风格。
- 输出检测报告与修复建议。

## 触发词

- 检查 AI 味道
- 代码味道检测
- AI 代码审查

## 输出

- 检测报告：`[当前工作目录]/.claude/taste-typescript-{YYYYMMDD}.md`
- 只检测不修复，不修改任何代码文件。

## 目录说明

| 路径 | 用途 |
|------|------|
| `SKILL.md` | 触发描述、检测流程与报告格式 |
| `references/detection-rules.md` | P0-P4 检测规则 |
| `references/ts-style-guide.md` | TypeScript 代码风格 |
| `scripts/` | 暂无脚本 |
| `assets/` | 暂无资源文件 |
| `evals/evals.json` | 测试用例 |

## 限制

- 仅支持 TypeScript。
- 不检测测试文件与配置文件。
