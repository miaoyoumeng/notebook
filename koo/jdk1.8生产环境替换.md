
# 一、替换策略
## 内网三套环境
1、由缪友猛通过jenkins统一将原来的运行jdk有1.7统一替换为1.8

2、开发人员暂时不得修改任何pom.xml，确定生产环境在jdk1.8情况下
没有问题后再使用jdk1.8的语法

3、内网环境出现任何问题，请各位开发负责人协调修改。

## jdk上线策略

### dubbo
1、修改dubbo.properties,增加一行dubbo.jdk=1.8，目的是开发人员确定这个项目可以用jdk1.8
```
dubbo.jdk=1.8
```

2、jenkins构建的时候选择构建参数，系统选择jdk=1.8。如图

![示图](http://images.koolearn.com/fe_upload/2018/12/2018-12-24-1545624664860.png)

3、回滚时，可以在jenkins构建选择jdk=1.7，代码无需回滚
4、jdk升级1.8是必需完成的事情，遇到任何问题，请各位及时修改。否则项目中依赖的组件无法升级（现在开源的jar包，不少要求最低jdk已经是1.8）


### worker

主要是鲨鱼项目，其他组的worker项目和dubbo完全一样

修改woker.properties,增加一行woker.jdk=1.8


### chronos

主要是鲨鱼项目，其他组的chronos项目和dubbo完全一样

只能改自己的定时任务的启动脚本。