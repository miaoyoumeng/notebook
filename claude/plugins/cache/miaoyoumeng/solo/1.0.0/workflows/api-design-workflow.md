# API 设计工作流

这个工作流用于模拟团队讨论，设计出符合 PRD 的 REST API。

## 执行步骤

1.  **读取 PRD**：首先，请阅读项目根目录下的 `prd.md` 文件。
2.  **前端视角**：调用 `vuer` Agent，让它基于 PRD 提出 API 设计建议。
3.  **后端视角**：调用 `javaer` Agent，让它基于 PRD 和前端建议，提出 API 设计建议。
4.  **架构师决策**：调用 `architecter` Agent，让它综合 PRD 和前后端建议，
5.  **输出 api 文档**: 在`<当前工作目录>/api/`输出最终的 `api-<system-name>.yaml` 文件。

其中`<system-name>`参考文档 *${CLAUDE_PLUGIN_ROOT}/knowledges/microservices.md*