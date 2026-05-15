
### 协议支持的参数

在使用 jdbc:mysql 协议连接 MySQL 数据库时，可以在 JDBC URL 中添加一些参数来配置连接和数据库的行为。以下是一些常见的 jdbc:mysql 协议后支持的参数：

名称|描述
---|---
user| 数据库的用户名。
password| 数据库的密码。
serverTimezone| 服务器时区，用于解析日期和时间。例如，serverTimezone=UTC。
useSSL| 是否使用 SSL 加密连接。可以设置为 true 或 false。默认为 false。
requireSSL| 是否要求使用 SSL 加密连接。可以设置为 true 或 false。默认为 false。
verifyServerCertificate| 是否验证服务器的证书。可以设置为 true 或 false。默认为 true。
useUnicode| 是否使用 Unicode 字符集。可以设置为 true 或 false。默认为 true。
characterEncoding| 字符编码。例如，characterEncoding=UTF-8。
autoReconnect| 是否在断开连接后自动重新连接。可以设置为 true 或 false。默认为 false。
failOverReadOnly| 是否将只读连接用于故障转移。可以设置为 true 或 false。默认为 true。
maxReconnects| 在自动重新连接期间尝试的最大重连次数。例如，maxReconnects=3。
connectTimeout| 连接超时时间，单位为毫秒。例如，connectTimeout=5000。
socketTimeout| 套接字超时时间，单位为毫秒。例如，socketTimeout=10000。
useLegacyDatetimeCode| 是否使用传统的日期时间编码。可以设置为 true 或 false。默认为 true。
zeroDateTimeBehavior| 当日期时间为零值时的行为。例如，zeroDateTimeBehavior=convertToNull。
rewriteBatchedStatements| 是否启用批量语句重写优化。可以设置为 true 或 false。默认为 false。
useServerPrepStmts| 是否使用服务器端预处理语句。可以设置为 true 或 false。默认为 false。