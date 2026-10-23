# browser-chat

把问题交给 AI 平台的网页版，等它回答完，把结果写进文件。

## 用途

- **平台**：豆包、DeepSeek、智谱、Kimi、千问、讯飞星火、腾讯元宝、文心一言（共 8 个）
- **走网页版而不是 API**——用你自己的账号和登录态
- **可批量**：一次提交多个 prompt，按顺序逐个等回答
- **落盘**：写进指定文件，或按序号写进指定目录
- **收尾干净**：跑完删掉左侧本次会话记录，不在账号里留痕

## 怎么用

直接说人话即可，Claude 会自己挑平台、拼参数、调脚本：

```text
帮我去 DeepSeek 问一下什么是量子纠缠，结果存到 out/答案.md
用千问和 Kimi 各问一遍「Python 的 GIL 是什么」，分两个文件存
```

也能在斜杠命令后面直接写脚本参数，这些参数原样传给 `console.py`：

```text
/sunny:browser-chat --model=kimi --prompt="Python 的 GIL 是什么" --dir=out --json
```

也可以手工调脚本：

```bash
uv run --project ${CLAUDE_PLUGIN_ROOT} python ${CLAUDE_PLUGIN_ROOT}/skills/browser-chat/scripts/console.py \
    --model=kimi --prompt="问题一" --prompt="问题二" --dir=out
```

完整参数见 `SKILL.md` 的「参数速查」，或 `--model=<平台> --help`。

## 目录结构

```text
browser-chat/
├── SKILL.md          # 技能定义：流程、参数、注意事项
├── README.md         # 本文件
├── scripts/          # 13 个脚本，分工见 SKILL.md「上下文层级」
├── references/       # 按需加载的参考文档（当前为空）
├── assets/           # 模板与资源（当前为空）
└── evals/
     └── evals.json   # 测试用例（当前为空）
```

## 前置条件

- `playwright-cli` 可用
- 首次使用某个平台时，要在弹出的浏览器窗口里**手动登录**一次；登录态随后持久化，下次不用重登
- 依赖（BeautifulSoup、playwright 等）声明在插件根目录的 `pyproject.toml`，所以调用一律走 `uv run --project <插件根目录>`

## 边界

- **只走网页版**，不调 API
- **不代用户登录**——登录、验证码都由用户本人完成
- **不触碰凭证**——不读取、不转存 cookie 与 token
