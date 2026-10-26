# 视频录制

把浏览器自动化过程录制为视频，用于调试、文档或验证。输出 WebM（VP8/VP9 编码）。

## 基本录制

```bash
# 先打开浏览器
playwright-cli open

# 开始录制
playwright-cli video-start demo.webm

# 添加章节标记，用于段落切换
playwright-cli video-chapter "Getting Started" --description="Opening the homepage" --duration=2000

# 导航并执行操作
playwright-cli goto https://example.com
playwright-cli snapshot
playwright-cli click e1

# 添加下一章节
playwright-cli video-chapter "Filling Form" --description="Entering test data" --duration=2000
playwright-cli fill e2 "test input"

# 停止并保存
playwright-cli video-stop
```

## 实践规则

### 1. 使用描述性文件名

```bash
# 文件名包含上下文
playwright-cli video-start recordings/login-flow-2024-01-15.webm
playwright-cli video-start recordings/checkout-test-run-42.webm
```

### 2. 录制完整演示脚本

为用户录制视频或作为工作证据时，先编写代码片段，再用 `run-code` 执行。这样可以插入适当停顿并为视频添加标注。

1. 用 CLI 走查场景，记录全部定位器与操作。后续需要用这些定位器获取包围盒，以便高亮。
2. 编写视频脚本文件（见下例）。用 `pressSequentially` 配合延迟实现自然输入，插入合理停顿。
3. 执行 `playwright-cli run-code --filename your-script.js`。

**注意**：浮层为 `pointer-events: none`，不干扰页面交互。点击、填写或执行其他操作时，可以保持常驻浮层可见。

```js
async page => {
  await page.screencast.start({ path: 'video.webm', size: { width: 1280, height: 800 } });
  await page.goto('https://demo.playwright.dev/todomvc');

  // 显示章节卡片：模糊页面并弹出对话框，按 duration 自动移除。
  // 自行制作浮层时可使用 page.screencast.showOverlay()。
  await page.screencast.showChapter('Adding Todo Items', {
    description: 'We will add several items to the todo list.',
    duration: 2000,
  });

  // 执行操作
  await page.getByRole('textbox', { name: 'What needs to be done?' }).pressSequentially('Walk the dog', { delay: 60 });
  await page.getByRole('textbox', { name: 'What needs to be done?' }).press('Enter');
  await page.waitForTimeout(1000);

  // 显示下一章节
  await page.screencast.showChapter('Verifying Results', {
    description: 'Checking the item appeared in the list.',
    duration: 2000,
  });

  // 添加常驻标注，操作期间保持可见。
  // 浮层为 pointer-events: none，不阻挡点击。
  const annotation = await page.screencast.showOverlay(`
    <div style="position: absolute; top: 8px; right: 8px;
      padding: 6px 12px; background: rgba(0,0,0,0.7);
      border-radius: 8px; font-size: 13px; color: white;">
      ✓ Item added successfully
    </div>
  `);

  // 标注可见时继续操作
  await page.getByRole('textbox', { name: 'What needs to be done?' }).pressSequentially('Buy groceries', { delay: 60 });
  await page.getByRole('textbox', { name: 'What needs to be done?' }).press('Enter');
  await page.waitForTimeout(1500);

  // 完成后移除标注
  await annotation.dispose();

  // 也可高亮相关定位器并添加上下文标注。
  const bounds = await page.getByText('Walk the dog').boundingBox();
  await page.screencast.showOverlay(`
    <div style="position: absolute;
      top: ${bounds.y}px;
      left: ${bounds.x}px;
      width: ${bounds.width}px;
      height: ${bounds.height}px;
      border: 1px solid red;">
    </div>
    <div style="position: absolute;
      top: ${bounds.y + bounds.height + 5}px;
      left: ${bounds.x + bounds.width / 2}px;
      transform: translateX(-50%);
      padding: 6px;
      background: #808080;
      border-radius: 10px;
      font-size: 14px;
      color: white;">Check it out, it is right above this text
    </div>
  `, { duration: 2000 });

  await page.screencast.stop();
}
```

### 浮层 API

| 方法 | 用途 |
|------|------|
| `page.screencast.showChapter(title, { description?, duration?, styleSheet? })` | 全屏章节卡片，背景模糊，适合段落切换 |
| `page.screencast.showOverlay(html, { duration? })` | 自定义 HTML 浮层，用于标注、标签、高亮 |
| `disposable.dispose()` | 移除未设置时长的常驻浮层 |
| `page.screencast.hideOverlays()` / `page.screencast.showOverlays()` | 临时隐藏或显示全部浮层 |

## 视频与追踪的区别

| 特性 | 视频 | 追踪 |
|------|------|------|
| 输出 | WebM 文件 | 轨迹文件（可在 Trace Viewer 中查看） |
| 内容 | 视觉录制 | DOM 快照、网络、控制台、操作 |
| 用途 | 演示、文档 | 调试、分析 |
| 大小 | 较大 | 较小 |

## 限制

- 录制会略微增加自动化开销
- 大型录像可能占用大量磁盘空间
