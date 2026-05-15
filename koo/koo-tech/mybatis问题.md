# mybatis问题定位及解决方案

# 问题
在旧项目中新增了多个mybatis 的mapper代码，开发、测试都没有问题，但是预发、生产环境报“代码段一”的异常错误

## 原因描述
### spring xml配置（有问题的配置）
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