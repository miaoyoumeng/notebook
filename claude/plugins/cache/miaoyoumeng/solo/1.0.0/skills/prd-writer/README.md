# prd-writer

按移动互联网行业标准，通过交互式信息收集生成标准化 PRD 文档。

## 触发方式

- 命令行：`/prd-writer <功能描述>`，如 `/prd-writer 用户管理系统单点登录模块`
- 被其他 skill 或 agent 调用

## 工作流

1. **信息收集** — 询问功能、背景、用户、目标、参考资料（每轮 3-5 问，最多 4 轮）
2. **范围梳理** — 确认角色、用户旅程、关键触点、P0/P1/P2 优先级
3. **编写 PRD** — 按 `references/page-template.md` 模板生成，范例参考 `references/prd-example.md`
4. **遗留问题** — 按 `references/todolist-template.md` 记录待确认事项
5. **自查** — 检查覆盖度、完整性、范围控制，禁止 TBD/TODO
6. **保存** — 输出到 `output/prds/<页面名称>.md` 和 `<页面名称>-todolist.md`
7. **迭代修改** — 用户审阅后提出修改意见，定向修改对应章节

## 输出文件

| 文件 | 说明 |
|------|------|
| `output/prds/<页面名称>.md` | PRD 主文档 |
| `output/prds/<页面名称>-todolist.md` | 遗留问题清单（如有） |

## 示例

```
/prd-writer 电商后台用户管理页面，需要支持注册、登录、个人信息编辑
```

Agent 会先询问业务背景、目标用户等，确认范围后生成完整 PRD。

## 不适用场景

- 市场调研、竞品分析
- 纯数据分析
- UI 视觉设计（配色、图标等）
