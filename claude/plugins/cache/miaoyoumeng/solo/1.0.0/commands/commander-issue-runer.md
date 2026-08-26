---
description: 根据 issues 内容进行修改。
allowed-tools: ["Bash", "Read", "Glob", "Write", "AskUserQuestion", "Skill"]
argument-hint: <subcommand> 
---
### 命令权限限制说明

- 写文件：只能写文件 `<当前工作目录>/logs/issues-progress.txt`，禁止写其他文件。
- 读文件：只能读目录 `<当前工作目录>/prds/` 、`<当前工作目录>/issues/` 和 `<当前工作目录>/logs`， 禁止读其他目录。

### 命令支持的参数

1. `status`：查询当前状态

- 检查 `<当前工作目录>/logs/issues-progress.txt` 是否存在，如果不存在则创建（空文件即可）。
- 按字母顺序列出 `<当前工作目录>/issues/**/feature-*.md`，与`<当前工作目录>/logs/issues-progress.txt`内容对比缺失文档。
- 将缺失的文档，按照文档名称字典序插入对应的位置，并将状态设置为`[文件名] 🟡 待处理` 。
- 再按字母顺序读取 `<当前工作目录>/issues/**/feature-*.md` 内容。
- 分组依次显示`🟢 处理完成`/`🟡 待处理`/`🔴 处理失败`统计数量。
- 然后停止

2. `run`：依次执行未完成的 issues 文档。

- 找出第一个 🟡 或 🔴 状态的文档
- 读取执行 issues 文档中的全部问题和方案，让我选择确认。
- 全部问题和方案确认完毕后，更新文档中约定的文档路径中，禁止直接更新`<当前工作目录>/prds`下的 prd 文档。
- 确认是否所有问题都已回答，如果没有则继续提问未回答问题，让我确认。如果全部已回答，则进入下一步骤。
- 成功后更新状态为 🟢，失败则更新状态为 🔴
- 重复以上步骤，直到全部 🟢 或手动停止

**重复执行时如果某个 issues 已经生成了输出文件，则直接覆盖。**

3. `clean`：清除`🟢 处理完成`的 issue 文档。

- 读取文档`<当前工作目录>/logs/issues-progress.txt`中`🟢 处理完成`的 `*.md` 文件列表
- 依次备份`<当前工作目录>/issues/**/*.md`中对应名称的文件，备份目录为 `<当前工作目录>/backup/issues`。
- 确认备份完毕，没有遗漏。
- 删除`<当前工作目录>/logs/issues-progress.txt`中`🟢 处理完成`的对应实际路径 markdown 文件。
- 删除文档`<当前工作目录>/logs/issues-progress.txt`中`🟢 处理完成`的对应行。

### 命令效果说明

1. `/solo:commander-issues-runner status` 

命令执行后。

- 命令行结果输出显示

```
🟢 处理完成 <数量>
🟡 待处理 <数量>
🔴 处理失败 <数量>
```

2. `/solo:commander-todu-runner run` 

命令执行后。

- 命令行结果输出显示，按照 issues 规定的内容进行交互。


3. `/solo:commander-todu-runner clean` 

命令行结果输出显示

```
🟢  备份完成 <数量>
```

