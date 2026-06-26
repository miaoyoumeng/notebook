# issues-writer

把计划、Spec 或 PRD 拆分为可独立领取的 issue tracker tickets。

## 何时使用

- 你有一份 PRD / 产品文档 / 功能计划，需要落地为开发任务
- 想把一个大功能拆成多人可并行领取的小 issue
- 准备开启一个 sprint，需要把目标拆成可验收的 tickets

## 何时不用

- 需要**从头写**一份 PRD → 使用 `prd-writer`
- 需要修复已有 bug → 直接定位和修改代码
- 需要给已有 issue 排优先级 → issue 管理操作，非拆分创建

## 使用方式

### 基本用法

```
帮我把 /path/to/prd.md 拆成可独立领取的 issues
```

```
/issues-writer 员工可提交请假申请，数据持久化到数据库，主管审批后通知员工
```

### 交互流程

1. **读取源材料** — 从文件或对话内容中提取计划
2. **垂直切片拆分** — 按 tracer bullet 原则拆成 end-to-end 的窄路径
3. **展示并确认** — 列出所有 slices（含 Type/依赖/覆盖场景），等待用户确认
4. **创建 issues** — 按依赖顺序发布到 issue tracker

### 拆分原则

- **垂直切片（Vertical Slice）**：每个 issue 都是一条完整的功能路径，穿过所有技术层
- **可独立验证**：每个 issue 完成后都能 demo 或验收
- **偏多而薄**：8 个 2 小时的 issue 优于 2 个 8 小时的 issue

详见 [SKILL.md](SKILL.md) 中的对比表格和完整示例。

## 输出格式

每个 issue 包含：

| 字段 | 说明 |
|------|------|
| issue 名称 | 短描述，不超过 15 个汉字 |
| issue code | 唯一编码（拼音+随机数） |
| 上级依赖 | 对父 issue 的引用（如有） |
| 任务描述 | end-to-end 行为描述，非 layer-by-layer |
| 产出内容 | 可观测的产出物列表 |
| 验收标准 | 至少 3 条可验证的 checklist |
| Blocked by | 前置依赖或 "None" |
