## 内网域名管理

受集团规范限制，我们域名申请规则如下：

### 一、域名格式
##### 1、内网环境业务项目格式
```
${环境}-dfub-${业务}.test.xdf.cn
```
##### 2、内网工具域名格式
```
dfub-${工具}.test.xdf.cn
```
##### 3、生产环境格式
```
dfub-${业务}.xdf.cn
```
### 二、nginx服务器

内网服务器ip:10.15.5.77


### 三、nginx日志

```
/neworiental/app/nginx/logs/${domain}.log
```

### 四、nginx配置

* 域名 *.test.xdf.cn

```
配置文件目录：/neworiental/app/nginx/conf/vhost/test/
```
* 域名 *.staff.xdf.cn

```
配置文件目录：/neworiental/app/nginx/conf/vhost/staff/
```