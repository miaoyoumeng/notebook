# 自研功能列表

* 集群地址配置：解决了defaultZone不同节点间由于需要相互注册，造成配置文件不相同问题。保证可以做到集群配置相同对
* 

# 部署方式

* 部署目录结构：标准部署目录结构
* 配置文件
```yml
server:
  port: 10086
spring:
  application:
    name: dfub-registry
eureka:
  client:
    service-url:
      defaultZone: http://${ip1}:{port}/eureka,http://${ip2}:{port}/eureka,http://${ip3}:{port}/eureka
  instance:
    prefer-ip-address: true
    instance-id: ${spring.application.name}:${spring.cloud.client.ip-address}:${server.port}
management:
  endpoints:
    web:
      exposure:
        include: '*'
  endpoint:
    health:
      show-details: ALWAYS
logging:
  level:
    root: info
```