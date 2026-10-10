# doubao-picker

把问题提交给豆包网页版（https://www.doubao.com/chat），并把页面返回的回答以 Markdown 输出到控制台。

## 怎么用

不需要手动调用。在 Claude Code 里直接描述需求即可触发，例如：

> 帮我问一下豆包：Transformer 的注意力机制是怎么工作的

回答以 Markdown 直接打印在控制台；需要留档时从控制台复制。本技能不写文件。

## 什么时候会触发

- 要求向豆包提问、让豆包回答某个问题
- 要求抓取 www.doubao.com 上的对话内容
- 要求把豆包的回答取出来（含连续追问的多轮问答）

## 目录说明

- `SKILL.md` —— 技能定义、执行流程与校验规则
- `scripts/` —— 确定性可执行脚本
- `evals/evals.json` —— 测试用例

## 依赖

浏览器自动化由 `playwright-cli` 技能提供。
