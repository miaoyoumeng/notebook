# 浏览器会话管理

并行运行多个隔离的浏览器会话，并持久化状态。

## 命名会话

用 `-s` 参数隔离浏览器上下文：

```bash
# 浏览器 1：认证流程
playwright-cli -s=auth open https://app.example.com/login

# 浏览器 2：公开浏览（独立 cookies 与存储）
playwright-cli -s=public open https://example.com

# 命令按会话隔离
playwright-cli -s=auth fill e1 "user@example.com"
playwright-cli -s=public snapshot
```

## 会话隔离范围

每个会话独立维护：

- Cookies
- LocalStorage / SessionStorage
- IndexedDB
- 缓存
- 浏览历史
- 打开的标签页

## 会话命令

```bash
# 列出全部会话
playwright-cli list

# 停止会话（关闭浏览器）
playwright-cli close                # 停止默认浏览器
playwright-cli -s=mysession close   # 停止命名浏览器

# 停止全部会话
playwright-cli close-all

# 强制终止全部守护进程（处理僵死进程）
playwright-cli kill-all

# 删除会话用户数据（配置目录）
playwright-cli delete-data                # 删除默认浏览器数据
playwright-cli -s=mysession delete-data   # 删除命名浏览器数据
```

## 环境变量

用环境变量设置默认会话名：

```bash
export PLAYWRIGHT_CLI_SESSION="mysession"
playwright-cli open example.com  # 自动使用 "mysession"
```

## 常见模式

### 并发抓取

```bash
#!/bin/bash
# 并发抓取多个站点

# 启动全部浏览器
playwright-cli -s=site1 open https://site1.com &
playwright-cli -s=site2 open https://site2.com &
playwright-cli -s=site3 open https://site3.com &
wait

# 分别快照
playwright-cli -s=site1 snapshot
playwright-cli -s=site2 snapshot
playwright-cli -s=site3 snapshot

# 清理
playwright-cli close-all
```

### A/B 测试

```bash
# 测试不同用户体验
playwright-cli -s=variant-a open "https://app.com?variant=a"
playwright-cli -s=variant-b open "https://app.com?variant=b"

# 对比
playwright-cli -s=variant-a screenshot
playwright-cli -s=variant-b screenshot
```

### 持久化配置

浏览器配置默认只保存在内存中。`open` 时加 `--persistent` 可持久化到磁盘：

```bash
# 持久化配置（自动生成位置）
playwright-cli open https://example.com --persistent

# 持久化配置并指定目录
playwright-cli open https://example.com --profile=/path/to/profile
```

## 连接已运行的浏览器

用 `attach` 连接已运行的浏览器，而非启动新实例。

### 按 channel 名称连接

按 channel 名称连接运行中的 Chrome 或 Edge。目标浏览器须启用远程调试：在地址栏打开 `chrome://inspect/#remote-debugging`，勾选 `Allow remote debugging for this browser instance`。

```bash
# 连接 Chrome
playwright-cli attach --cdp=chrome

# 连接 Chrome Canary
playwright-cli attach --cdp=chrome-canary

# 连接 Microsoft Edge
playwright-cli attach --cdp=msedge

# 连接 Edge Dev
playwright-cli attach --cdp=msedge-dev
```

支持的 channel：`chrome`、`chrome-beta`、`chrome-dev`、`chrome-canary`、`msedge`、`msedge-beta`、`msedge-dev`、`msedge-canary`。

未指定 `--session` 时，会话名取 channel 名（例如 `--cdp=msedge` 创建 `msedge` 会话），避免 Chrome 与 Edge 并行连接时在 `default` 上冲突。可用 `--session=<name>` 覆盖。

### 通过 CDP 端点连接

连接暴露 Chrome DevTools Protocol 端点的浏览器：

```bash
playwright-cli attach --cdp=http://localhost:9222
```

### 通过浏览器扩展连接

连接安装了 Playwright 扩展的浏览器：

```bash
playwright-cli attach --extension
```

### 断开连接

拆除已连接的会话，不影响外部浏览器：

```bash
# 断开默认连接会话
playwright-cli detach

# 断开指定连接会话
playwright-cli -s=msedge detach
```

`detach` 仅适用于 `attach` 创建的会话。`open` 创建的会话用 `close` 关闭。

## 默认会话

省略 `-s` 时，命令作用于默认会话：

```bash
# 以下命令使用同一个默认会话
playwright-cli open https://example.com
playwright-cli snapshot
playwright-cli close  # 停止默认浏览器
```

## 会话配置

打开时指定会话设置：

```bash
# 使用配置文件
playwright-cli open https://example.com --config=.playwright/my-cli.json

# 指定浏览器
playwright-cli open https://example.com --browser=firefox

# 有界面模式
playwright-cli open https://example.com --headed

# 持久化配置
playwright-cli open https://example.com --persistent
```

## 实践规则

### 1. 会话命名体现用途

```bash
# 推荐：用途清晰
playwright-cli -s=github-auth open https://github.com
playwright-cli -s=docs-scrape open https://docs.example.com

# 避免：名称笼统
playwright-cli -s=s1 open https://github.com
```

### 2. 结束时清理

```bash
# 完成后停止浏览器
playwright-cli -s=auth close
playwright-cli -s=scrape close

# 或一次停止全部
playwright-cli close-all

# 浏览器无响应或残留僵死进程时
playwright-cli kill-all
```

### 3. 删除过期数据

```bash
# 删除旧浏览器数据，释放磁盘空间
playwright-cli -s=oldsession delete-data
```
