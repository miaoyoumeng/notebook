---
description: 根据用户提供的 prd 文档，分析拆解 prd 文档。
allowed-tools: ["Bash(uv run python *)", "Read", "Glob", "Write", "AskUserQuestion", "Skill"]
---
## 上下文

我是“一人公司”负责人，服务器代码拆分如下:

### 服务器后台模块划分

参考文档 *${CLAUDE_PLUGIN_ROOT}/knowledges/microservices.md*

## 目标

仔细阅读 prd 文档，深度思考、理解 prd 文档的需求。调用`/sole:prd-analyzer`和`/sole:prd-checker`两个 skill 分析 prd 文档。
- 产品

## 命令权限限制说明

- 写文件：只能写文件 `logs/prd-analyzer-progress.txt`，禁止写其他文件。
- 读文件：只能读目录 `references/user-story`、`outputs/prds/`和`logs`， 禁止读其他目录。


## 工作步骤


## 清晰的工作界限

- 此技能主要是阅读。
- 它可以运行轻量级静态检查助手。
- 它不会修补存储库代码。
- 它不拥有最终的复制输出。
- 它应该将可疑模式标记为启发式方法，而不是已确认的错误。

## 输出期望

- `analysis_outputs/SUMMARY.md`
- `analysis_outputs/RISKS.md`
- `analysis_outputs/status.json`

## 输出结果校验工作流