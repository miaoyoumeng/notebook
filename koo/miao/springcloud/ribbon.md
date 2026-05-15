## Ribbon组件

#### 一、常用参数

参数|默认值|描述
---|---|---
ServerListRefreshInterval|30|默认30秒，单位ms
ConnectTimeout|1000|请求连接的超时时间 ，单位ms
ReadTimeout|1000|请求处理的超时时间 单位ms
OkToRetryOnAllOperations|false|对所有操作请求都进行重试,不配置这个MaxAutoRetries不起作用
MaxAutoRetries|0|对当前实例的重试次数
MaxAutoRetriesNextServer|1|切换实例的重试次数
PoolMaxThreads|200|最大线程数
PoolMinThreads|1|最小线程数
retryableStatusCodes||对Http响应码进行重试，比如：502、504


* 如果MaxAutoRetries=1和MaxAutoRetriesNextServer=1请求在1s内响应，超过1秒先同一个服务器上重试1次，如果还是超时或失败，向其他服务上请求重试1次。那么整个ribbon请求过程的超时时间为：ribbonTimeout = (ribbonReadTimeout + ribbonConnectTimeout) * (maxAutoRetries + 1) * (maxAutoRetriesNextServer + 1)


#### 二、所有参数

参数|默认值|描述
---|---|---
AppName||
BackoffTimeout||
ClientClassName||
ConnIdleEvictTimeMilliSeconds||
ConnectTimeout||
ConnectionCleanerRepeatInterval||
ConnectionManagerTimeout||
ConnectionPoolCleanerTaskEnabled||
CustomSSLSocketFactoryClassName||
DeploymentContextBasedVipAddresses||
EnableConnectionPool||
EnableGZIPContentEncodingFilter||
EnableMarkingServerDownOn\<br>ReachingFailureLimit||
EnablePrimeConnections||
EnableZoneAffinity||
EnableZoneExclusivity||
FollowRedirects||
ForceClientPortConfiguration||
GZipPayload||
IgnoreUserTokenInConnection\<br>PoolForSecureClient||
InitializeNFLoadBalancer||
IsClientAuthRequired||
IsHostnameValidationRequired||
IsSecure||
KeyStore||
KeyStorePassword||
Linger||
MaxAutoRetries||
MaxAutoRetriesNextServer||
MaxConnectionsPerHost||
MaxHttpConnectionsPerHost||@Deprecated，用MaxConnectionsPerHost
MaxRetriesPerServerPrimeConnection||
MaxTotalConnections||
MaxTotalHttpConnections||@Deprecated，用MaxTotalConnections
MaxTotalTimeToPrimeConnections||
MinPrimeConnectionsRatio||
NFLoadBalancerClassName||
NFLoadBalancerMaxTotalPingTime||
NFLoadBalancerPingClassName||
NFLoadBalancerPingInterval||
NFLoadBalancerRuleClassName||
NFLoadBalancerStatsClassName||
NIWSServerListClassName||
NIWSServerListFilterClassName||
OkToRetryOnAllOperations||
PoolKeepAliveTime||
PoolKeepAliveTimeUnits||
PoolMaxThreads|200|最大线程数
PoolMinThreads|1|最小线程数
Port||
PrimeConnectionsClassName||
PrimeConnectionsURI||
PrioritizeVipAddressBasedServers||
ProxyHost||
ProxyPort||
ReadTimeout||
ReceiveBufferSize||
RequestIdHeaderName||
RequestSpecificRetryOn||
RulePredicateClasses||
SecurePort||
SendBufferSize||
ServerDownFailureLimit||
ServerDownStatWindowInMillis||
ServerListRefreshInterval||
ServerListUpdaterClassName||
StaleCheckingEnabled||
TargetRegion||
TrustStore||
TrustStorePassword||
UseIPAddrForServer||
Version||
VipAddress||
listOfServers||动配置调用的服务地址<br>当禁用eureka后需要手动配置
VipAddressResolverClassName|com.netflix.client<br>.SimpleVipAddressResolver|解析器的key使用的是

