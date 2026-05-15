# Maven坐标 

1、 具体坐标
```xml
<dependency>
    <groupId>com.koolearn</groupId>
    <artifactId>koo-framework-mybatis</artifactId>
    <version>${最新版本号}</version>
</dependency>
```
2、[内网仓库网址](http://maven.koolearn-inc.com/nexus/index.html#nexus-search;quick~koo-framework-mybatis)

3、连接池：Druid

# 代码集成配置

1、spring 配置

```xml
<bean id="dataSource" class="com.koolearn.framework.mybatis.datasource.KooDataSource">
    <property name="bizName" value="${数据源名称}"/>
</bean>

<bean id="sqlSessionFactory" class="com.koolearn.framework.mybatis.spring.KooSqlSessionFactoryBean">
    <property name="dataSource" ref="dataSource"/>
    <property name="mapperLocations">
        <array>
            <value>${mybatis配置路径}</value>
            <value>${示例：classpath:mapping/*.xml}</value>
        </array>
    </property>
    <property name="configLocation" value="classpath:mybatis-configuration.xml"/>
</bean>

<bean class="org.mybatis.spring.mapper.MapperScannerConfigurer">
    <property name="basePackage" value="${包名，可以多个}"/>
    <property name="sqlSessionFactoryBeanName" value="sqlSessionFactory"/>
    <property name="annotationClass" value="com.koolearn.framework.mybatis.annotation.DAO"/>
</bean>

<tx:annotation-driven />
```

二、与事务管理相关

1）替换你的事务管理类为：KooDataSourceTransactionManager

在开发过程中要检查你的配置文件和代码，确保事务生效。
```xml
<bean id="transactionManager" class="com.koolearn.framework.mybatis.datasource.KooDataSourceTransactionManager">
    <property name="dataSource" ref="${数据源名称}"/>
</bean>
```

com.koolearn.framework.mybatis.datasource.KooDataSource

# 路由规则

1 新增机房属性，机房属性的作用是尽可能的保证应用与slave数据库连接的调用发生在同一个机房内。

Java启动时，加入环境变量：-DappLocation=${机房名称} -Didc=${机房名称}，此处用于表示你的应用所在的机房。

A.机房策略下，应用根据机房名称会优先使用同机房的数据源，同机房的数据源如果有多个，则随机选取。

B.如果同机房数据源没有或变得不可用时，则随机选择任意一个非同机房数据源。

# mybatis 插件配置

```xml
<configuration>
    <plugins>
        <plugin interceptor="com.koolearn.framework.mybatis.datasource.plugin.CatPlugin"/>
        <plugin interceptor="com.koolearn.framework.mybatis.datasource.plugin.SQLThreadLocal"/>
        <plugin interceptor="com.koolearn.framework.mybatis.datasource.plugin.SqlIntercept"/>
    </plugins>
</configuration>
```

#  日志

在测试环境，强烈建议增加如下log4j日志信息，以便于问题排查：

```xml
<logger name="com.koolearn.framework.mybatis" additivity="false">
    <level value="DEBUG" />
    <appender-ref ref="你的日志规则" />
</logger>
```
# 分表

1 分库分表需要在你的 mybatis 项目中加入下列配置：
```xml
<plugins>
    <plugin interceptor="com.koolearn.framework.mybatis.datasource.plugin.SQLThreadLocal" />
</plugins>
```
# mybatis问题定位及解决方案

## 问题
在旧项目中新增了多个mybatis 的mapper代码，开发、测试都没有问题，但是预发、生产环境报“代码段一”的异常错误

### 原因描述
#### spring xml配置（有问题的配置）
```xml
<bean class="org.mybatis.spring.mapper.MapperScannerConfigurer">
		<property name="basePackage" value="${业务系统包名}" />
</bean>

```
### spring xml配置（解决问题的配置）
``` xml
<bean class="org.mybatis.spring.mapper.MapperScannerConfigurer">
	<property name="basePackage" value="${业务系统包名}" />
    <property name="sqlSessionFactoryBeanName" value="sqlSessionFactory" />
</bean>

```
跟踪了两种配置对应的启动过程，发现缺少sqlSessionFactoryBeanName配置，创建Mapper bean的时候，会大量重复的set sqlSessionFactoryBeanName属性，导致线程的堆栈满（对应启动参数-xss, 本地开发环境、docker运行环境没用限制，默认1M，生产dubbo启动脚本，被限制256k），进而初始化数据源失败。而cat在捕获这个Throwable之后，没用继续抛出，所以看到的异常都是cat 初始化失败。


## 需要大家做的
需要大家检查一下配置，并在合适的时候修改一下代码对应的配置。目前这个问题只会在启动过程中出现，如果已经正常启动，则业务不受影响。


## 代码段一
``` java
[main] -[2018-12-18 23:36:38] {ERROR} org.apache.ibatis.executor.BaseExecutor 52 - Could not get a databaseId from dataSource
java.lang.NullPointerException
        at com.dianping.cat.Cat.newTransaction(Cat.java:363)
        at com.koolearn.framework.mybatis.datasource.KooDataSource.getConnection(KooDataSource.java:93)
        at org.apache.ibatis.mapping.VendorDatabaseIdProvider.getDatabaseProductName(VendorDatabaseIdProvider.java:77)
        at org.apache.ibatis.mapping.VendorDatabaseIdProvider.getDatabaseName(VendorDatabaseIdProvider.java:62)
        at org.apache.ibatis.mapping.VendorDatabaseIdProvider.getDatabaseId(VendorDatabaseIdProvider.java:50)
        at org.mybatis.spring.SqlSessionFactoryBean.buildSqlSessionFactory(SqlSessionFactoryBean.java:449)
        at org.mybatis.spring.SqlSessionFactoryBean.afterPropertiesSet(SqlSessionFactoryBean.java:340)
        at org.springframework.beans.factory.support.AbstractAutowireCapableBeanFactory.invokeInitMethods(AbstractAutowireCapableBeanFactory.java:1573)
        at org.springframework.beans.factory.support.AbstractAutowireCapableBeanFactory.initializeBean(AbstractAutowireCapableBeanFactory.java:1511)
        at org.springframework.beans.factory.support.AbstractAutowireCapableBeanFactory.doCreateBean(AbstractAutowireCapableBeanFactory.java:521)
        at org.springframework.beans.factory.support.AbstractAutowireCapableBeanFactory.createBean(AbstractAutowireCapableBeanFactory.java:458)
        at org.springframework.beans.factory.support.AbstractBeanFactory$1.getObject(AbstractBeanFactory.java:293)
        at org.springframework.beans.factory.support.DefaultSingletonBeanRegistry.getSingleton(DefaultSingletonBeanRegistry.java:223)
        at org.springframework.beans.factory.support.AbstractBeanFactory.doGetBean(AbstractBeanFactory.java:290)
        at org.springframework.beans.factory.support.AbstractBeanFactory.getBean(AbstractBeanFactory.java:191)
        at org.springframework.beans.factory.support.DefaultListableBeanFactory.findAutowireCandidates(DefaultListableBeanFactory.java:921)
        at org.springframework.beans.factory.support.DefaultListableBeanFactory.doResolveDependency(DefaultListableBeanFactory.java:864)
        at org.springframework.beans.factory.support.DefaultListableBeanFactory.resolveDependency(DefaultListableBeanFactory.java:779)
        at org.springframework.beans.factory.support.AbstractAutowireCapableBeanFactory.autowireByType(AbstractAutowireCapableBeanFactory.java:1226)
        at org.springframework.beans.factory.support.AbstractAutowireCapableBeanFactory.populateBean(AbstractAutowireCapableBeanFactory.java:1133)
        at org.springframework.beans.factory.support.AbstractAutowireCapableBeanFactory.doCreateBean(AbstractAutowireCapableBeanFactory.java:519)
        at org.springframework.beans.factory.support.AbstractAutowireCapableBeanFactory.createBean(AbstractAutowireCapableBeanFactory.java:458)
        at org.springframework.beans.factory.support.AbstractBeanFactory$1.getObject(AbstractBeanFactory.java:293)
        at org.springframework.beans.factory.support.DefaultSingletonBeanRegistry.getSingleton(DefaultSingletonBeanRegistry.java:223)
        at org.springframework.beans.factory.support.AbstractBeanFactory.doGetBean(AbstractBeanFactory.java:290)
        at org.springframework.beans.factory.support.AbstractBeanFactory.getTypeForFactoryBean(AbstractBeanFactory.java:1371)
```