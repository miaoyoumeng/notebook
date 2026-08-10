# user-story-writer

产品经理生成标准化 User Story 文档的 Skill。

## 功能说明

通过交互式信息收集确认需求背景、目标、用户角色和需求类型，读取用户提供的上下文材料，生成 User Story 内容，用户批准后保存为标准化文档。

## 使用方式

```
/solo:user-story-writer
```

## 核心能力

| 能力 | 说明 |
|------|------|
| 用户故事格式 | As-a / I-want / So-that 标准模板 |
| 验收标准 | GIVEN-WHEN-THEN、检查表、MoSCoW 三种格式 |
| INVEST 标准 | 六原则质量检查（Independent/Negotiable/Valuable/Estimable/Small/Testable） |
| 故事拆分 | 10 种拆分模式（工作流/CRUD/角色/规则/复杂度等） |
| 反模式防御 | 禁止占位符、模糊描述、技术化描述等 |

## 工作流程

1. **信息收集** — 交互式确认需求背景、目标、用户角色
2. **读取上下文** — 处理用户提供的调研报告、原型图等材料
3. **生成内容** — 生成 User Story，每个场景包含完整的触发条件、用户行为、期望结果、边界条件
4. **用户批准** — 呈现内容且用户批准之后，保存成文档

## 交付物

- **保存路径**：`stories/story-${module-name}-${yyyy-MM-dd}.md`
- **文档格式**：每个功能模块对应一个独立的 User Story 文档
- **内容要求**：用户故事 + 验收标准 + 边界条件，禁止占位符

## 参考文档

| 文档 | 内容 |
|------|------|
| [验收标准编写指南](references/acceptance-criteria-guide.md) | 三种格式详解、最佳实践、常见错误 |
| [INVEST 标准指南](references/invest-criteria-guide.md) | 六原则详解、检查清单、修复策略 |
| [故事拆分指南](references/story-splitting-guide.md) | 10 种拆分模式、反模式、决策树 |

## 禁止事项

永远不要写：
- "TBD"、"TODO"、"稍后实现"、"细节待补充"
- "用户可以进行相关操作"（需明确具体行为）
- "系统会进行适当处理"（需明确具体响应）
- "参考场景 N"（需完整描述）
- 只描述功能不说明用户能得到什么
- 引用未定义的角色、流程或数据模型
