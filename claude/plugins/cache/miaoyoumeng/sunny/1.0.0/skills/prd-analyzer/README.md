# prd-analyzer

读取产品需求文档（PRD）及关联的 user story，产出领域事件时间线和 DDD 领域模型两份结构化文档。

## 功能

- 产品愿景提炼（FOR/WHO/PRODUCT 模板）
- 用户操作旅程与领域事件提取（含异常路径）
- DDD 领域建模（领域对象 → 聚合 → 限界上下文 → 状态机）
- PRD 审查（需求缺口、设计问题、优化建议）

## 使用方式

```
/prd-analyzer
```

或在对话中提供 PRD 文件路径，skill 会自动触发。

## 输入

- Markdown 格式的 PRD 文档（.md 文件路径）
- PRD 中关联的 user story 文件
- 或用户口头描述的需求（skill 会标注"基于描述构建"）

## 输出

按 `references/` 下的模板产出两份文档：
- **领域事件时间线**（`template-event.md`）：用户旅程、领域事件清单、聚合清单、限界上下文
- **领域模型文档**（`template-domain.md`）：领域对象表、上下文边界、映射关系、状态机

## 目录结构

```
prd-analyzer/
├── SKILL.md                 # Skill 核心说明
├── README.md                # 本文件
├── evals/
│   └── evals.json           # 测试用例
└── references/
    ├── template-event.md    # 领域事件时间线输出模板
    └── template-domain.md   # 领域模型输出模板（领域对象/上下文边界/状态机）
```
