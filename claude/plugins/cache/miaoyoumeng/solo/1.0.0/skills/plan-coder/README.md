# plan-coder

根据用户 prompt 生成 src 目录下的代码修改方案。

## 用途

- 接收用户的功能需求或修改请求
- 迭代研究 `src` 目录代码库
- 输出分步骤的 Mini-PR 修改方案

## 核心定位

spec = 做什么，plan-coder = 怎么做。

## 输出

- 方案文件：`/tmp/plan-coder-{timestamp}-{name}.md`
- 研究日志：`/tmp/plan-coder-research-{timestamp}-{name}.md`

## 触发

修改代码、生成方案、实现方案、代码修改计划
