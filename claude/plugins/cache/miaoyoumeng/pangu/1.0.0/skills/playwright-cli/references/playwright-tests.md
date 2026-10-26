# 运行 Playwright 测试

运行 Playwright 测试使用 `npx playwright test` 或包管理脚本。设置环境变量 `PLAYWRIGHT_HTML_OPEN=never` 可禁止自动打开 HTML 报告。

```bash
# 运行全部测试
PLAYWRIGHT_HTML_OPEN=never npx playwright test

# 通过自定义 npm 脚本运行全部测试
PLAYWRIGHT_HTML_OPEN=never npm run special-test-command
```

# 调试 Playwright 测试

调试失败的测试时加 `--debug=cli`，命令会在测试开始时暂停并打印调试说明。

**重要**：在后台运行该命令，持续检查输出直到出现 `Debugging Instructions`。调试结束后停止该命令。

输出中出现会话名后，用 `playwright-cli` 连接该会话并检查页面。

```bash
# 运行测试
PLAYWRIGHT_HTML_OPEN=never npx playwright test --debug=cli
# ...
# ... "tw-abcdef" 会话的调试说明 ...
# ...

# 连接测试会话
playwright-cli attach tw-abcdef
```

保持测试在后台运行，同时检查页面并定位修复点。测试在开始时暂停，应在问题最可能出现的位置单步执行或暂停。

`playwright-cli` 的每个操作都会生成对应的 Playwright TypeScript 代码。代码出现在输出中，可直接复制进测试。多数情况需要更新定位器或断言，也可能是应用缺陷，按实际情况判断。

修复后停止后台测试进程，重新运行确认测试通过。
