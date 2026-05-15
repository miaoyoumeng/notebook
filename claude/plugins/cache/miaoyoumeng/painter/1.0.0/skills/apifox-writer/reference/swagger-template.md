# swagger 的 api 模板

仅支持REST 规范中的 GET、POST、DELETE、PUT请求，其他类型的请求不予支持。

## 1. GET 请求示例

```text
{
  "swagger": "2.0",
  "info": {
    "title": "api 名称",
    "description": "api 描述",
    "version": "1.0.0"
  },
  "paths": {
    "/get/request/api": {
      "get": {
        "summary": "api 概要信息",
        "description": "api 简单描述内容",
        "parameters": [
        ……  按要求自定义样参数
        ],
        "responses": {
          "200": {
            "description": "",
            "headers": {},
            "examples": {
              "application/json": {
                "code": 200,
                "data": {
                  ……  按要求自定义样例数据
                },
                "msg": "success"
              }
            },
            "schema": {
              "type": "object",
              "properties": {
                "code": {
                  "type": "integer"
                },
                "data": {
                  ……  按实际业务需求自定义样例数据属性
                },
                "msg": {
                  "type": "string"
                }
              },
              "required": [
                "code",
                "data",
                "msg"
              ]
            }
          }
        },
        "consumes": [
          "application/json"
        ],
        "produces": [
          "application/json"
        ]
      }
    }
  }
}

```

## 2. POST 请求示例

```text
{
  "swagger": "2.0",
  "info": {
    "title": "api 名称",
    "description": "api 描述",
    "version": "1.0.0"
  },
  "paths": {
    "/post/request/api": {
      "post": {
        "summary": "api 概要信息",
        "description": "api 简单描述内容",
        "parameters": [
          ……  按要求自定义样参数
        ],
        "responses": {
          "200": {
            "description": "",
            "headers": {},
            "schema": {
              "type": "object",
              "properties": {
                "code": {
                  "type": "integer"
                },
                "msg": {
                  "type": "string"
                },
                "data": {
                  ……  按实际业务需求自定义样例数据属性
                }
              },
              "required": [
                "code",
                "msg",
                "data"
              ]
            }
          }
        },
        "consumes": [
          "application/json"
        ],
        "produces": [
          "application/json"
        ]
      }
    }
  }
}
```

## 3. DELETE 请求示例

```text
{
  "swagger": "2.0",
  "info": {
    "title": "api 名称",
    "description": "api 描述",
    "version": "1.0.0"
  },
  "paths": {
    "/delete/request/api": {
      "delete": {
        "summary": "api 概要信息",
        "description": "api 简单描述内容",
        "parameters": [
        ……  按要求自定义样参数
        ],
        "responses": {
          "200": {
            "description": "",
            "headers": {},
            "examples": {
              "application/json": {
                "code": 200,
                "data": {
                  ……  按要求自定义样例数据
                },
                "msg": "success"
              }
            },
            "schema": {
              "type": "object",
              "properties": {
                "code": {
                  "type": "integer"
                },
                "data": {
                  ……  按实际业务需求自定义样例数据属性
                },
                "msg": {
                  "type": "string"
                }
              },
              "required": [
                "code",
                "data",
                "msg"
              ]
            }
          }
        },
        "consumes": [
          "application/json"
        ],
        "produces": [
          "application/json"
        ]
      }
    }
  }
}
```

## 4. PUT 请求示例

```text
{
  "swagger": "2.0",
  "info": {
    "title": "api 名称",
    "description": "api 描述",
    "version": "1.0.0"
  },
  "paths": {
    "/put/request/api": {
      "put": {
        "summary": "api 概要信息",
        "description": "api 简单描述内容",
        "parameters": [
          ……  按要求自定义样参数
        ],
        "responses": {
          "200": {
            "description": "",
            "headers": {},
            "schema": {
              "type": "object",
              "properties": {
                "code": {
                  "type": "integer"
                },
                "msg": {
                  "type": "string"
                },
                "data": {
                  ……  按实际业务需求自定义样例数据属性
                }
              },
              "required": [
                "code",
                "msg",
                "data"
              ]
            }
          }
        },
        "consumes": [
          "application/json"
        ],
        "produces": [
          "application/json"
        ]
      }
    }
  }
}
```

