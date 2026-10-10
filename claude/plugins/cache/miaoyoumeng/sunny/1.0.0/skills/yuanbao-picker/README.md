# yuanbao-picker

把问题提交给腾讯元宝网页版（https://yuanbao.tencent.com/chat），以**深度思考**模式取得回答，并在控制台以 Markdown 展示。

## 怎么用

不需要手动调用。在 Claude Code 里直接描述需求即可触发，例如：

> 问一下元宝：Rust 的借用检查器是怎么工作的

浏览器会自动打开。首次使用需要你在窗口里登录一次（微信扫码、QQ 或手机号均可），之后登录态会保留，不用重复登录。

提交前技能会确认「深度思考」开关已打开——没开就自己点上，确保拿到的是深度思考的回答。

## 什么时候会触发

- 要求向元宝提问、让元宝回答某个问题
- 要求抓取 yuanbao.tencent.com 上的对话内容
- 要求让元宝用深度思考模式回答
- 要求连续追问元宝（多轮问答）

## 目录说明

- `SKILL.md` —— 触发条件与执行步骤
- `scripts/` —— 确定性可执行脚本
- `references/` —— 按需加载的参考文档
- `assets/` —— 模板与资源文件
- `evals/evals.json` —— 测试用例

## 依赖

浏览器自动化由 `playwright-cli` 技能提供（`/wubu:playwright-cli`）。

HTML → Markdown 还原的参考实现见 `skills/deepseek-picker/scripts/extract_markdown.py`。
