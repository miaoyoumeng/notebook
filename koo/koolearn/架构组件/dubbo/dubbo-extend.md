
# maven 坐标
```xml
<dependency>
    <groupId>com.koolearn</groupId>
    <artifactId>koo-dubbo-extend</artifactId>
    <version>${最新版本}</version>
</dependency>
 
<dependency>
    <groupId>com.alibaba</groupId>
    <artifactId>dubbo</artifactId>
    <version>2.5.7</version>
</dependency>
```
# 功能点配置


### dubbo路由功能，支持 dubbo 调用优先同机房调用。

   1）Provider端（Service）和 Consumer（如：Web）端，启动参数都新增：-Didc=机房名称。

   2）同时 Consumer 端需要在 dubbo.registry.address 配置项上新增 router=koo 参数。
        如：dubbo.registry.address=zookeeper://xx.xx.xx.xx:2181?router=koo

应用场景：

   1）生产环境多机房下，保证dubbo接口优先调用同机房的服务，在没有同机房dubbo 接口情况下，采用轮询机制调用其他机房服务，保证高可用

   2）开发人员，开发环境场景下，通过上述启动参数，保证在debug调试过程中，调用自己本机的服务，防止调用其他开发人员的接口，进而影响代码效果

### telnet 命令扩展：

新增loglevel命令，支持单独对某个 logger 调整日志级别。命令格式：loglevel loggerName ${日志级别}

应用场景：通过telnet 命令动态调试日志级别

### .dubbo 缓存文件冲突问题。

解决一台机器上部署多个dubbo进程，其中/home/${user}/.dubbo下文件读写锁冲突问题

### 启动参数 -Ddubbo.consumer.check=false 

启动时，支持放弃依赖检查，防止循环依赖，导致不修改配置无法启动。（特殊场景下使用）
此功能一般适用于管理员，开发或者应用不建议单独使用。



### IP 排除

provider 和 consumer端向外暴露时，排除一些不合法的 IP。不合法 IP 的情况包括但不限于虚拟 IP（192.168.1.1） 等。


### 启动过程的日志级别控制

应用场景：在启动过程中，以com.koolearn开头的日志级别调整为debug，启动完成后，日志级别恢复为原来的日志级别。

修改 dubbo.properties 的配置项：dubbo.container，在 spring 两边分别插入：koo_before_spring 和 koo_after_spring。

 如：原配置信息是：
```
   dubbo.container=log4j,spring,xx,yy....
```

修改后的配置信息变为：

```
   dubbo.container=log4j,koo_before_spring,spring,koo_after_spring,xx,yy....
```


### dubbo 超时对接公司报警。


   默认启用，无需配置。


### dubbo monitor 新增 IDC （机房）信息输出。


   默认启用，无需配置。


 

### Dubbo 调用参数和返回结果日志输出

  只输出 package 以 com.koolearn. 开头的调用参数和返回值，使用方法如下：

  通过调整 logger name 为 dubboArgsLog 的日志级别，打印调用 dubbo 接口的输入参数和返回值。

    1）打印接口的输入参数：将此 logger 的日志级别调到能够达到  info 的级别。

    2）打印接口的返回值：将此 logger 的日志级别调到能够达到  debug 的级别。

  日志输出举例：
 

### telnet 命令扩展：新增 gitversion 命令，支持查看当前 dubbo 应用的版本号。

   该功能从 1.0.5 版本正式开始提供。

### 新增环境变量 tomcatno 用于表示机器的标示信息（注意，不是指 hostname）。

   该功能从 1.0.5 版本正式开始提供。

### Dubbo Provider URL 中的 timestamp 引入可视化的时间参数 timestampFormat。

   timestampFormat 的生成规则是：

   当 timestamp 不为空时，直接使用 timestamp 转换。如果 timestamp 为空，那么以当前注册到注册中心的时间为转换时间。

   timestampFormat 的格式为：年-月-日_时-分-秒.毫秒

   举例：

   dubbo://1.1.1.1:20008/com.koolearn.sso.service.IOpenService...&threads=100&timestamp=1547088423042&timestampFormat=2019-01-10_10-47-03.042

  该功能目前正在测试中。


### Dubbo application name 获取方式变更



     如果 META-INF/app.properties 中的 app.name 配置项不为空，那么使用该值作为 application 参数的值，否则，使用 dubbo.properties 的默认配置项：dubbo.application.name。
     注入「应用名称」到 system property 中

   该功能目前正在测试中。