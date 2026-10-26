# rest-api-writer

根据 PRD、页面描述、原型截图或文字需求设计 RESTful API，输出 OpenAPI 3.2 YAML 接口文档。

## 适用场景

- 新业务模块需要设计接口。
- 已有 PRD 或页面原型需要落地为接口约定。
- 前后端联调前需要明确请求、响应与错误码。

## 触发方式

在对话中描述业务需求或明确要求设计接口文档，Claude 会自动加载本技能。也可以直接说「帮我设计 XX 模块的接口」或「根据这个页面写 REST API」。

支持的输入：

- PRD 文档内容。
- 文字描述。
- 截图或原型图。

## 输出内容

OpenAPI 3.2 YAML 文档，包含：

- `info`：API 基本信息。
- `servers`：服务器地址列表。
- `paths`：接口路径、HTTP 方法、参数、请求体与响应。
- `components`：可复用的 Schema、响应与安全方案。
- `security`：全局认证要求。

生成的文档可导入 Apifox、Swagger 等工具。

## 目录结构

```text
rest-api-writer/
├── SKILL.md                         # 技能指令与执行流程
├── README.md                        # 本文件
├── scripts/
│   └── validate.py                  # OpenAPI YAML 校验脚本
├── references/
│   ├── rest-api-template-*.md       # 输出模板（5 个）
│   ├── core-*.md                    # OpenAPI 核心对象
│   ├── schema-*.md                  # Schema 相关主题
│   ├── security*.md                 # 安全相关主题
│   └── ...                          # 路径、参数、响应等主题
├── assets/                          # 模板与资源文件
└── evals/
    └── evals.json                   # 测试用例
```

## 校验脚本

生成 YAML 后执行：

```shell
uv run python scripts/validate.py /tmp/api.yaml
```

从标准输入读取：

```shell
cat /tmp/api.yaml | uv run python scripts/validate.py --stdin
```

脚本依赖 `pyyaml` 与 `openapi-spec-validator`，已在 `pyproject.toml` 中声明。

## 设计约定摘要

- 路径使用名词复数，操作用 HTTP 方法表达，不在 URL 中使用动词。
- 仅使用 GET、POST、PUT、PATCH、DELETE。
- 列表接口使用 `page`、`pageSize`、`sortField`、`sortOrder`。
- 成功响应包含 `code`、`displayMsg`、`data`、`uniqCode`、`msg`。
- 分页数据包含 `list`、`pageNo`、`pageSize`、`total`。

完整规则与检查清单见 `SKILL.md`。
