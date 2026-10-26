# 追踪

捕获详细执行轨迹，用于调试与分析。轨迹包含 DOM 快照、截图、网络活动和控制台日志。

## 基本用法

```bash
# 开始录制轨迹
playwright-cli tracing-start

# 执行操作
playwright-cli open https://example.com
playwright-cli click e1
playwright-cli fill e2 "test"

# 停止录制
playwright-cli tracing-stop
```

## 轨迹输出文件

开始追踪后，Playwright 创建 `traces/` 目录，包含下列文件：

### `trace-{timestamp}.trace`

**操作日志**，主轨迹文件，包含：

- 每个执行的操作（点击、填写、导航）
- 操作前后的 DOM 快照
- 每一步的截图
- 时间信息
- 控制台消息
- 源码位置

### `trace-{timestamp}.network`

**网络日志**，完整网络活动：

- 全部 HTTP 请求与响应
- 请求头与请求体
- 响应头与响应体
- 时间分布（DNS、连接、TLS、TTFB、下载）
- 资源大小
- 失败请求与错误

### `resources/`

**资源目录**，缓存的资源：

- 图片、字体、样式表、脚本
- 用于回放的响应体
- 重建页面状态所需的资源

## 轨迹捕获内容

| 类别 | 内容 |
|------|------|
| **操作** | 点击、填写、悬停、键盘输入、导航 |
| **DOM** | 每个操作前后的完整 DOM 快照 |
| **截图** | 每一步的视觉状态 |
| **网络** | 全部请求、响应、头、体、时间 |
| **控制台** | 全部 console.log、warn、error 消息 |
| **时间** | 每个操作的精确耗时 |

## 使用场景

### 调试失败操作

```bash
playwright-cli tracing-start
playwright-cli open https://app.example.com

# 这次点击失败，原因是什么？
playwright-cli click e5

playwright-cli tracing-stop
# 打开轨迹，查看点击时的 DOM 状态
```

### 分析性能

```bash
playwright-cli tracing-start
playwright-cli open https://slow-site.com
playwright-cli tracing-stop

# 查看网络瀑布图，定位慢资源
```

### 留存证据

```bash
# 录制完整用户流程，用于文档
playwright-cli tracing-start

playwright-cli open https://app.example.com/checkout
playwright-cli fill e1 "4111111111111111"
playwright-cli fill e2 "12/25"
playwright-cli fill e3 "123"
playwright-cli click e4

playwright-cli tracing-stop
# 轨迹展示事件的精确顺序
```

## 轨迹、视频与截图的区别

| 特性 | 轨迹 | 视频 | 截图 |
|------|------|------|------|
| **格式** | .trace 文件 | .webm 视频 | .png/.jpeg 图片 |
| **DOM 检查** | 支持 | 不支持 | 不支持 |
| **网络细节** | 支持 | 不支持 | 不支持 |
| **逐步回放** | 支持 | 连续画面 | 单帧 |
| **文件大小** | 中等 | 大 | 小 |
| **适用** | 调试 | 演示 | 快速取证 |

## 实践规则

### 1. 在问题发生前开始追踪

```bash
# 追踪完整流程，而非仅失败步骤
playwright-cli tracing-start
playwright-cli open https://example.com
# ... 问题出现前的全部步骤 ...
playwright-cli tracing-stop
```

### 2. 清理旧轨迹

轨迹可能占用大量磁盘空间：

```bash
# 删除 7 天前的轨迹
find .playwright-cli/traces -mtime +7 -delete
```

## 限制

- 追踪会增加自动化开销
- 大型轨迹可能占用大量磁盘空间
- 部分动态内容可能无法完美回放
