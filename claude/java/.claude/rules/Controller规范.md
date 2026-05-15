---
paths:
  - "**/*/*Controller.java"
---

## 编写 controller 规范

###  请求参数空值处理 (Null Handling)，示例如下

- 仅在不可避免时接受 `@Nullable`；否则使用 `@NonNull`
- 对Controller输入参数校验使用 `miao.you.meng.web.valid.ParameterValidator`

```java
ParameterValidator.init()
     .notNull(user, "用户不能为空")
     .hasLength(name, "姓名不能为空")
     .maxLength(email, 100, "邮箱长度不能超过 100 个字符")
     .validateAndThrow();
```



