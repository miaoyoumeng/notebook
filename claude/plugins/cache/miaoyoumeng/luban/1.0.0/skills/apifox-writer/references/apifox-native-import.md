# Apifox 原生格式导入策略

适用于项目迁移、备份、跨项目复制和局部资源搬迁。

## 基本导入

```bash
apifox import --project <projectId> --format apifox --file ./project.apifox.yaml
```

## 模块导入模式

| 模式 | 命令 | 用途 |
|------|------|------|
| match-name（默认） | `--module-import-mode match-name` | 匹配已有模块名导入，未匹配则新建 |
| new | `--module-import-mode new` | 每次复制全新模块 |

## 精确模块映射

`--module-map` 优先级高于 `--module-import-mode`，可重复传：

```bash
apifox import --project <projectId> --format apifox --file ./project.apifox.yaml \
  --module-map "商店 API=8049476" \
  --module-map "管理 API=8049482"
```

| 写法 | 用途 |
|------|------|
| `源模块名=目标模块ID` | 导入到指定已有模块 |
| `source:源模块ID=目标模块ID` | 源模块重名时精确指定 |
| `源模块名=default` | 导入到目标项目默认模块 |
| `源模块名=new` | 只让该源模块新建 |

## 导入后验证

- 模块数量是否符合预期，二次导入不应无意新增同名模块
- API、Schema、测试用例、测试场景、WebSocket、Socket.IO 等资源数量
- 单接口测试用例分类可见性
- 如导入测试套件，抽查场景和用例引用是否指向新项目资源
