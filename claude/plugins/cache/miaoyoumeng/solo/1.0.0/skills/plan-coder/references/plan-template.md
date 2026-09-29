# 方案模板

## 模板结构

```markdown
# 实施方案：[功能名称]

[1-2 句话描述目标]

质量门禁：类型检查（0 错误）、Lint（干净）

---

## 需求覆盖
- [需求点] → Chunk N
- [需求点] → Chunk M, Chunk N

---

## 1. [Chunk 名称]

依赖：- | 可并行：-

[本 chunk 交付什么]

需修改的文件：
- src/xxx.ts - [具体修改]

需创建的文件：
- src/xxx.ts - [用途]

参考文件：
- src/xxx.ts - [为何参考]

备注：[假设、已考虑的替代方案]

风险：
- [具体风险] → [缓解措施]

任务：
- 实现 fn() - [用途]
- 执行质量门禁

验收标准：
- 质量门禁通过
- [具体可验证的标准]

关键函数：fn(), helper()
类型：TypeName
```

## 好的示例

```markdown
## 2. 添加用户验证服务

依赖：1（User 类型）| 可并行：3

实现邮箱/密码验证，含速率限制。

需修改的文件：
- src/services/user.ts - 添加 validateUserInput()

需创建的文件：
- src/services/validation.ts - 验证逻辑 + 速率限制器

参考文件：
- src/services/auth.ts:45-80 - 现有验证模式
- src/types/user.ts - Chunk 1 的 User 类型

任务：
- validateEmail() - RFC 5322
- validatePassword() - 最少 8 位，1 数字，1 特殊字符
- rateLimit() - 5 次/分钟/IP
- 执行质量门禁

验收标准：
- 质量门禁通过
- validateEmail() 拒绝非法格式，接受合法 RFC 5322 邮箱
- validatePassword() 强制执行最少 8 位、1 数字、1 特殊字符
- 速率限制器在 5 次/分钟/IP 后阻止

函数：validateUserInput(), validateEmail(), rateLimit()
类型：ValidationResult, RateLimitConfig
```

## 差的示例

```markdown
## 2. 用户相关
给用户加验证。
文件：user.ts
任务：加验证
```

**差的原因**：无依赖关系、描述模糊、缺少完整路径、无参考文件、任务笼统、未列出函数、无验收标准。

## Chunk 规模指引

| 复杂度 | Chunk 数 | 指引 |
|--------|----------|------|
| 简单 | 1-2 | 每个 1-3 个函数 |
| 中等 | 3-5 | 每个 <200 行代码 |
| 复杂 | 5-8 | 每个可独立演示 |
| 集成 | +1 | 连接前面的工作 |

## 常见模式

| 模式 | 流程 |
|------|------|
| 顺序 | Model → Logic → API → Error handling |
| 基础后并行 | Model → CRUD ops（并行）→ Integration |
| 管道 | Types → Parse/Transform（并行）→ Format → Errors |
