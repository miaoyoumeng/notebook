### LVS安装


**系统环境**

角色       | IP               |  主机名     | 系统版本
---|---|---|---
DR1（主）  | 192.168.100.213  |  Test3     |   RHEL5.4_X64
DR2（备）  | 192.168.100.214  |  Test4     |   RHEL5.4_X64
RS1       | 192.168.100.211  |  Test1      |  RHEL6.0_X64
RS2       | 192.168.100.212  |  Test2      |  RHEL6.0_X64

IP环境：
两台DR使用各自eth1网卡进行心跳检测（192.168.99.1-2）
VIP为192.168.100.210/24

准备工作：
配置YUM
配置hostname
配置/etc/hosts
配置IP地址

主DR
**1、安装ipvsadm**
ln -s /usr/src/kernels/`uname -r` /usr/src/linux
cd /tol/soft
tar zxvf ipvsadm-1.24.tar.gz
cd ipvsadm-1.24
make  && make install

**2、安装libnet（heartbeat的依赖库）**
cd /tol/soft
tar -xf  libnet-1.1.6.tar.gz
cd libnet-1.1.6
 ./configure
make && make install

**3、安装heartbeat依赖包（perl-MailTools，5.4需要下载，6.0及以上系统自带）**
    perl-MailTools依赖以下的包，版本可能会有所区别（下载地址为：http://rpm.pbone.net/）
    #cd /tol/soft/
    # rpm -ivh perl-Pod-Escapes-1.04-1.2.el5.rf.noarch.rpm
    # rpm -ivh perl-Pod-Simple-3.14-1.el5.rf.noarch.rpm
    # rpm -ivh perl-Test-Pod-1.44-1.el5.rf.noarch.rpm
    # rpm -ivh perl-TimeDate-1.16-5.el5.noarch.rpm
    # rpm -ivh perl-MailTools-2.07-1.el5.rf.noarch.rpm

**4、安装heartbeat**
groupadd haclient
useradd -M -g haclient -s /sbin/nologin  hacluster

cd /tol/soft
tar zxvf heartbeat-2.1.3.tar.gz
cd heartbeat-2.1.3
#以下编译参数出自书《高性能Linux服务器构建实战》,本次实验使用的是这种编译参数
./ConfigureMe configure --disable-swig --disable-snmp-subagent
make && make install

以下编译安装参数出处不详
#./ConfigureMe make --enable-fatal-warnings=no   
#make install

如果编译时出现以下的错：
client_lib.c:1881: error: 'display_orderQ' defined but not used
则编辑源码包目录中的lib/hbclient/Makefile文件 删除里面所有的-Weeror字符，重新编译即可。

**5、从模版中拷贝配置文件到/etc/ha.d/目录下**
    # cd /tol/soft/heartbeat-2.1.3/
    # cp doc/ha.cf /etc/ha.d/            #主配置文件，心跳检测
    # cp doc/haresources /etc/ha.d/            #要管理的资源，（控制服务）
    # cp doc/authkeys /etc/ha.d/            #选择一个算法，主节点和从节点间数据校验用的，（成员管理）
    # cp ldirectord/ldirectord.cf  /etc/ha.d/    #ldirectord的控制脚本，用于realserver的健康检测，（ldirectord插件在安装heartbeat时默认会安装）
                            #

    将ipvsadm的控制脚本复制到heartbeat资源管理目录，为了使heartbeat能对ipvsadm进行控制
    # cp -a /etc/init.d/ipvsadm /etc/ha.d/resource.d/

**6、编辑ha.cf**
这个配置文件比较复杂。只配了关键的几项：
#debugfile /var/log/ha-debug    说明：调试日志文件文件，取默认值
logfile /var/log/ha-log        说明：系统运行日志文件，取默认值
#logfacility local0        说明：日志等级，取默认值，这个表示使用syslog服务记录日志，和logfile不能共存。
keepalive 1            说明：心跳频率，自己设定。1:表示1秒；200ms：表示200毫秒
deadtime 10            说明：节点死亡时间阀值，就是从节点在过了10后秒还没有收到心跳就认为主节点死亡，自己设定
warntime 5            说明：发出警告时间（单位秒），此时间内联系不上主DR，就会写入一个警告日志，不切换服务。
initdead 60            说明：heartbeat首次启动时deadtime应该为多久，因为Heartbear引导启动时，需要给系统网络启动留出时间。
udpport 694            说明：心跳信息传递的udp端口，自己设定
bcast   eth1            说明：采用udp广播播来通知心跳，建议在副节点不只一台时使用，不推荐这种方式，会在局域网产生大量广播数据包。
#ucast eth1 192.168.99.2    说明：采用网卡eth0的udp单播来通知心跳，eth0的后面为对方的IP
#mcast eth0 225.0.0.1 694 1 0    说明：采用udp多播播来通知心跳，生产环境中推荐这种方式。
auto_failback on        说明：主节点重启成功后，资源是自动拿回到主节点还是等到副节点down调后拿回资源
node Test3            说明：主节点名称，与uname –n保持一致。排在第一的默认为主节点，所以不要搞措顺序
node Test4            说明：副节点名称，与uname –n保持一致
#watchdog /dev/watchdog        说明：看门狗。如果本节点在超过一分钟后还没有发出心跳，那么本节点自动重启

以上这些是我个人认为必配项，下面这些是可选项:

stonith baytech /etc/ha.d/conf/stonith.baytech    说明：主/副等所有节点的一种校验。
respawn userid /path/name/to/run        说明：和heartbeat必须一起启动的本地服务
ping 192.168.100.254                说明：伪节点IP，伪节点就是其失效时主/副节点不会正常工作但本身不是主/副节点之一。
#respawn hacluster /usr/lib/heartbeat/ipfail    说明：与ping选项一起使用，取默认值。
baud   19200                    说明：串口波特率，与serial一起使用。
serial /dev/ttyS0  # Linux            说明：采用串口来传递心跳信息。

**7、编辑authkeys并修改文件权限为0600**
auth    3        #采用第三个认证
3 md5 Hello!        #主从DR相互之间验证采用Hello!作为口令，并通过MD5加密。

**8、编辑haresources**
最后一行添加（若有多个VIP则添加多行）
test1  192.168.100.210/24/eth0  ldirectord::ldirectord.cf
#一共三个字段，第一个字段为主节点的主机名，第二个字段为VIP，第三个字段为资源名称::参数，多个资源空格隔开

**9、编辑ldirectord.cf**
# Global Directives

checktimeout=3            #ldirectord等待健康检查执行完毕的等待时间，单位秒
checkinterval=1            #指定ldirectord在两个检查之间的间隔时间
#fallback=127.0.0.1:80        #当IPVS表中没有真实服务器时，客户端计算机应该被重定向的ip地址
autoreload=yes            #自动应用配置文件的改动
logfile="/var/log/ldirectord.log"    #日志文件
#logfile="local0"
#emailalert="admin@x.y.z"
#emailalertfreq=3600
#emailalertstatus=all
quiescent=no            #当设置为no时，节点没有响应后，ldirectord将会从IPVS表中移除真实服务器而不是“停止”它
                    从IPVS表移除节点将中断现有的客户端连接，并使LVS丢掉所有的连接跟踪记录和持续连接模板

                    如果将这个选项设置为yes，当某个节点崩溃时，对某些客户端而言可能会显示为集群关闭了
                    因为在这个节点崩溃前这些客户端被分配给它了，而连接跟踪记录和程序连接模板仍然保留在Director上

virtual=192.168.100.210:80            #VIP：端口号，在这行后面的行必须缩进4个空格或者一个tab字符。
    real=192.168.100.211:80 gate -w 1    #指定realserver，gate表示DR模式，ipip表示TUN模式，masq表示NAT模式，-w 后面接的是权重，值越大分配的请求越多
    real=192.168.100.212:80 gate -w 1
    service=http                #服务类型，
    request="index.html"            #ldirectord将根据realserver的地址去请求这个页面
    receive="ok"                #指定请求页面的返回内容，也就是上面的test.html的内容
    virtualhost=test.com        #虚拟服务器的名称，一般为VIP所对应的域名
    scheduler=wlc            #指定调度算法
    protocol=tcp            #指定协议类型，LVS支持TCP和UDP协议
    #persistent=3            #
      checktype=negotiate        #指定ldirectord的检测类型，有：connect、external、negotiate、off、on、ping、checktimeout
                        默认为negotiate    通过页面交互来判断服务器节点是否正常。
      checkport=80            #指定监控端口号

**10、启动heartbeat**
    #service heartbeat start
    #chkconfig heartbeat on
启动成功后，本机会自动配置上haresources中配置的VIP。并且ipvsadm -l -n能查看到相关信息

**11、系统其他配置**
    DR上每增加一个VIP就需要加一条路由
    route add -host VIP dev eth0:0    （实验中不加也可以，待验证）

    打开内核转发（如果LB和RS不在同一网段的话需要打开）
    echo 1 > /proc/sys/net/ipv4/ip_forward

    关闭防火墙
    service iptables stop &&　chkconfig iptables off

备DR
和主DR的配置一样，ha.d下的所有配置文件可以copy主DR的

测试DR主从切换：
1、模拟主DR宕机    #/usr/lib64/heartbeat/hb_standby    #32位的系统则是/usr/lib/heartbeat/hb_standby
    输出：2014/01/07_15:59:16 Going standby [all].

2、查看主DR上的VIP都已经消失。

3、备份DR自动接管服务

4、模拟主DR恢复服务，然后夺回控制权。    #/usr/lib64/heartbeat/hb_takeover

Realserver

编辑一个启动脚本

```shell
#!/bin/bash

#配置VIP
ifconfig lo:1 192.168.100.210 netmask 255.255.255.255 broadcast 192.168.100.210 up
route add -host 192.168.100.210 dev lo:1

#设置屏蔽arp广播
echo "1" > /proc/sys/net/ipv4/conf/lo/arp_ignore
echo "2" > /proc/sys/net/ipv4/conf/lo/arp_announce
echo "1" > /proc/sys/net/ipv4/conf/all/arp_ignore
echo "2" > /proc/sys/net/ipv4/conf/all/arp_announce
```

