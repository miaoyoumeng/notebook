---
description: 顺序执行下一个 prompt 文件生成 PRD，支持重复执行。
allowed-tools: ["Bash", "Read", "Glob", "Write", "AskUserQuestion", "Skill"]
argument-hint: <subcommand> 
---

### 命令权限限制说明

- 写文件：只能写文件 `logs/prompts-progress.txt`，禁止写其他文件。
- 读文件：只能读目录 `<当前工作目录>/references/user-story`、 `<当前工作目录>/prompts/`、`<当前工作目录>/prds/` 、`<当前工作目录>/todos/` 和 `logs`， 禁止读其他目录。

### 命令支持的参数

1. `init`: 初始化

- 检查 `logs/prompts-progress.txt` 是否存在，如果不存在则创建（空文件即可）。
- 按字母顺序列出 `<当前工作目录>/prompts/*.prompt.md`，与`<当前工作目录>/logs/prompts-progress.txt`内容对比缺失文档。
- 将缺失的文档，按照文档名称字典序插入对应的位置，并将状态设置为`[文件名] 🟡 待处理` 。
- 并按照如下格式统计。
```
📩 新添加 <数量>
🟢 处理完成 <数量>
🟡 待处理 <数量>
🔴 处理失败 <数量>
```

**`📩 新添加` 本次执行命令新添加的文档**
**`🟡 待处理` 添加完成后，未执行的 prompt 文档**
**`🟢 处理完成` 添加完成后，已执行的 prompt，且成功执行完成的文档**
**`🔴 处理失败` 添加完成后，已执行的 prompt，且执行失败的文档**

- 然后停止

2. `status`：查询当前状态

- 先执行命令 `/solo:commander-prompt-runner init`, 将缺失的文档添加到`logs/prompts-progress.txt`中。
- 再按字母顺序读取 `<当前工作目录>/prompts/*.prompt.md` 内容。
- 分组依次显示`🟢 处理完成`/`🟡 待处理`/`🔴 处理失败`统计数量。
- 然后停止

3. `todo`：查询`未处理完成`的文档。

- 先执行命令 `/solo:commander-prompt-runner init`, 将缺失的文档添加到`logs/prompts-progress.txt`中。
- 再按字母顺序列出 `<当前工作目录>/prompts/*.prompt.md`，分组依次显示`🟡 待处理`/`🔴 处理失败`列表。
- 然后停止

4. `run`：依次执行未完成的 prompt 文档。

- 找出第一个 🟡 或 🔴 状态的文档
- 执行 prompt 文档中的内容。
- 成功后更新状态为 🟢，失败则更新状态为 🔴
- 重复以上步骤，直到全部 🟢 或手动停止

**重复执行时如果某个 prompt 已经生成了输出文件，则直接覆盖。**

5. `clean`：清除`🟢 处理完成`的 prompt 文档。

- 读取文档`logs/prompts-progress.txt`中`🟢 处理完成`的 `*.prompt.md` 文件列表
- 依次备份`<当前工作目录>/prompts/*.prompt.md`中对应名称的文件，备份目录为 `backup/prompts`。
- 确认备份完毕，没有遗漏。
- 删除文档`logs/prompts-progress.txt`中`🟢 处理完成`的对应行。

### 命令效果说明

1. `/solo:commander-prompt-runner init` 

命令执行后

- `logs/prompts-progress.txt` 内容最终格式如下：

```
[文件名] 🟢 处理完成
……
[文件名] 🟡 待处理
……
[文件名] 🔴 处理失败
……
```

- 命令行结果输出显示

```
📩 新添加 <数量>
🟢 处理完成 <数量>
🟡 待处理 <数量>
🔴 处理失败 <数量>
```

2. `/solo:commander-prompt-runner status` 

命令执行后。

- 命令行结果输出显示

```
🟢 处理完成 <数量>
🟡 待处理 <数量>
🔴 处理失败 <数量>
```

3. `/solo:commander-prompt-runner todo` 

命令执行后。

- 命令行结果输出显示

```
[文件名] 🟡 待处理
……
[文件名] 🔴 处理失败
……
```

4. `/solo:commander-prompt-runner run` 

命令执行后。

- 命令行结果输出显示，按照 prompt 规定的内容进行交互。

