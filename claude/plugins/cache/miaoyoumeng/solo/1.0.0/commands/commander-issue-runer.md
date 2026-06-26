---
description: 根据已有平台的产品 prd 文档进行评估，修改修改。
allowed-tools: ["Bash", "Read", "Glob", "Write", "AskUserQuestion", "Skill"]
argument-hint: <subcommand> 
---
### 命令权限限制说明

- 写文件：只能写文件 `logs/todo-progress.txt`，禁止写其他文件。
- 读文件：只能读目录 `outputs/prds/` 、`outputs/todos/` 和 `logs`， 禁止读其他目录。

### 命令支持的参数

1. `init`: 初始化

- 检查 `logs/todo-progress.txt` 是否存在，如果不存在则创建（空文件即可）。
- 按字母顺序列出 `outputs/todos/**/*.todo.md`，与`logs/todo-progress.txt`内容对比缺失文档。
- 将缺失的文档，按照文档名称字典序插入对应的位置，并将状态设置为`[文件名] 🟡 待处理` 。
- 并按照如下格式统计。
```
📩 新添加 <数量>
🟢 处理完成 <数量>
🟡 待处理 <数量>
🔴 处理失败 <数量>
```

**`📩 新添加` 本次执行命令新添加的文档**
**`🟡 待处理` 添加完成后，未执行的 todo 文档**
**`🟢 处理完成` 添加完成后，已执行的 todo，且成功执行完成的文档**
**`🔴 处理失败` 添加完成后，已执行的 todo，且执行失败的文档**

- 然后停止

2. `status`：查询当前状态

- 先执行命令 `/solo:commander-todo-runner init`, 将缺失的文档添加到`logs/todo-progress.txt`中。
- 再按字母顺序读取 `outputs/todos/**/*.todo.md` 内容。
- 分组依次显示`🟢 处理完成`/`🟡 待处理`/`🔴 处理失败`统计数量。
- 然后停止

3. `todo`：查询`未处理完成`的文档。

- 先执行命令 `/solo:commander-todo-runner init`, 将缺失的文档添加到`logs/todo-progress.txt`中。
- 再按字母顺序列出 `outputs/todos/**/*.todo.md`，分组依次显示`🟡 待处理`/`🔴 处理失败`列表。
- 然后停止

4. `run`：依次执行未完成的 todo 文档。

- 调用 `/clear` 命令，清空当前对话框的context。
- 找出第一个 🟡 或 🔴 状态的文档
- 读取执行 todo 文档中的全部问题和方案，让我选择确认。
- 全部问题和方案确认完毕后，更新文档中约定的文档路径中，禁止直接更新`outputs/prds`下的 prd 文档。
- 确认是否所有问题都已回答，如果没有则继续提问未回答问题，让我确认。如果全部已回答，则进入下一步骤。
- 成功后更新状态为 🟢，失败则更新状态为 🔴
- 重复以上步骤，直到全部 🟢 或手动停止

**重复执行时如果某个 todo 已经生成了输出文件，则直接覆盖。**

5. `clean`：清除`🟢 处理完成`的 todo 文档。

- 读取文档`logs/todo-progress.txt`中`🟢 处理完成`的 `*.todo.md` 文件列表
- 依次备份`outputs/todos/**/*.todo.md`中对应名称的文件，备份目录为 `backup/todos`。
- 确认备份完毕，没有遗漏。
- 删除文档`logs/todo-progress.txt`中`🟢 处理完成`的对应行。

### 命令效果说明

1. `/solo:commander-todo-runner init` 

命令执行后

- `logs/todo-progress.txt` 内容最终格式如下：

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

2. `/solo:commander-todo-runner status` 

命令执行后。

- 命令行结果输出显示

```
🟢 处理完成 <数量>
🟡 待处理 <数量>
🔴 处理失败 <数量>
```

3. `/solo:commander-todo-runner todo` 

命令执行后。

- 命令行结果输出显示

```
[文件名] 🟡 待处理
……
[文件名] 🔴 处理失败
……
```



4. `/solo:commander-todu-runner run` 

命令执行后。

- 命令行结果输出显示，按照 todo 规定的内容进行交互。
