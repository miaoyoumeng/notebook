

```yaml
server:
  port: 10000
  tomcat:
    max-threads: 1000
  shutdown: graceful
spring:
  application:
    name: ${自定义:zuul-gateway}
  servlet:
    multipart:
      enabled: true
      max-file-size: 100MB
      max-request-size: 100MB
eureka:
  client:
    service-url:
      defaultZone: ${自定义:eureka.cluster.url}
    registry-fetch-interval-seconds: 5
  instance:
    prefer-ip-address: true
    instance-id: ${spring.application.name}:${spring.cloud.client.ip-address}:${server.port}
zuul:
  host:
    max-per-route-connections: 1000
    max-total-connections: 1000
  prefix: /api
  routes:
    ${biz.application.name}: /${自定义:biz-url}
  retryable: true
  add-host-header: true
  sensitive-headers: 
  ignored-headers: ${自定义:Access-Control-Allow-Origin,Token}
ribbon:
  ConnetTimeout: 360000
  ReadTimeout: 360000
  OkToRetryOnAllOperations: true # 是否对所有操作都进行重试
  MaxAutoRetries: 0
  MaxAutoRetriesNextServer: 1
hystrix:
  command:
    default:
      execution:
        isolation:
          thread:
            timeoutInMilliseconds: 750000
          strategy: SEMAPHORE
          semaphore:
            maxConcurrentRequests: 1000
      fallback:
        isolation:
          semaphore:
            maxConcurrentRequests: 200
      circuitBreaker:
        sleepWindowInMilliseconds:  5000
management:
  endpoints:
    web:
      exposure:
        include: '*'
  endpoint:
    health:
      show-details: ALWAYS
feign:
  client:
    config:
      default:
        connectTimeout: 360000
        readTimeout: 360000
```