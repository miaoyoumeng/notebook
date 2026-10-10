# kimi-picker

把问题提交给 Kimi 网页版（https://www.kimi.com/），并把页面返回的回答以 Markdown 输出到控制台。

## 怎么用

不需要手动调用。在 Claude Code 里直接描述需求即可触发，例如：

> 帮我问一下 Kimi：Transformer 的注意力机制是怎么工作的

回答以 Markdown 直接打印在控制台；需要留档时从控制台复制。本技能不写文件。

## 什么时候会触发

- 要求向 Kimi 提问、让 Kimi 回答某个问题
- 要求抓取 www.kimi.com 上的对话内容
- 要求把 Kimi 的回答取出来（含连续追问的多轮问答）

## 输出说明

只输出**正文**。Kimi 在正文之前会先输出一段思考过程，本技能自动排除，不会混进结果。

含公式的回答会被降级：Kimi 网页只渲染 KaTeX 的 HTML 版，不保留 LaTeX 原文，公式会丢失上标与分式结构（`$E=mc^2$` 变成 `$E=mc2$`）。需要精确公式时请从 Kimi 页面手工复制。

## 目录说明

- `SKILL.md` —— 技能定义、执行流程与校验规则
- `scripts/` —— 确定性可执行脚本
- `evals/evals.json` —— 测试用例

## 依赖

浏览器自动化由 `playwright-cli` 技能提供。
