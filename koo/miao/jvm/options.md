
 
```shell
-server -Xmx1g -Xms1g -Xmn128m -Xss256k -XX:+UseConcMarkSweepGC -XX:+CMSParallelRemarkEnabled -XX:+UseCMSCompactAtFullCollection -XX:LargePageSizeInBytes=128m -XX:+UseFastAccessorMethods -XX:+UseCMSInitiatingOccupancyOnly -XX:CMSInitiatingOccupancyFraction=70
```
 
#### 一、java参数

名字|描述
---|---
-server|服务端模型，服务部署在服务器类计算机上
-cp| <目录和 zip/jar 文件的类搜索路径>
-classpath|<目录和 zip/jar 文件的类搜索路径><br> 用 : 分隔的目录, JAR 档案<br> 和 ZIP 档案列表, 用于搜索类文件。
-D<名称>=<值>| 设置系统属性
-X |输出非标准选项的帮助
…|……

#### 二、非标准参数

执行命令查看所有参数：
```shell
java -X
```

名字|描述
---|---
-Xms<size>        |设置初始 Java 堆大小
-Xmx<size>        |设置最大 Java 堆大小
-Xmn<size>        |设置 java 年轻代内存大小 
-Xss<size>        |设置 Java 线程堆栈大小
-Xmixed           |混合模式执行 (默认)
-Xint             |仅解释模式执行
-Xbootclasspath:  |<用 : 分隔的目录和 zip/jar 文件><br> 设置搜索路径以引导类和资源
-Xbootclasspath/a:|<用 : 分隔的目录和 zip/jar 文件><br> 附加在引导类路径末尾
-Xbootclasspath/p:|<用 : 分隔的目录和 zip/jar 文件><br> 置于引导类路径之前
-Xdiag            |显示附加诊断消息
-Xnoclassgc       |禁用类垃圾收集
-Xincgc           |启用增量垃圾收集
-Xloggc:<file>    |将 GC 状态记录在文件中 (带时间戳)
-Xbatch           |禁用后台编译
-Xprof            |输出 cpu 配置文件数据
-Xfuture          |启用最严格的检查, 预期将来的默认值
-Xrs              |减少 Java/VM 对操作系统信号的使用(请参阅文档)
-Xcheck:jni       |对 JNI 函数执行其他检查
-Xshare:off       |不尝试使用共享类数据
-Xshare:auto      |在可能的情况下使用共享类数据 (默认)
-Xshare:on        |要求使用共享类数据, 否则将失败。
-XshowSettings    |显示所有设置并继续
-XshowSettings:all|显示所有设置并继续
-XshowSettings:vm |显示所有与vm相关的设置并继续
-XshowSettings:properties|显示所有属性设置并继续
-XshowSettings:locale|显示所有与区域设置相关的设置并继续


#### 三、JVM非Stable参数（-XX）
执行命令查看所有参数：
```shell
java -XX:+PrintFlagsInitial 
```
###### 3.1、功能开关  

参数|默认值|功能
---|---|---
-XX:+DisableExplicitGC	|默认启用	|禁止在运行期显式地调用System.gc()
-XX:+HandlePromotionFailure	|默认启用	|关闭新生代收集担保
-XX:PreBlockSpin=10	|-XX:+UseSpinning 必须先启用，对于java6来说已经默认启用了，这里默认自旋10次	|控制多线程自旋锁优化的自旋次数
-XX:-RelaxAccessControlCheck	|默认不启用	|在Class校验器中，放松对访问控制的检查,作用与reflection里的setAccessible类似
-XX:+UseGCOverheadLimit	|默认启用	|限制GC的运行时间。如果GC耗时过长，就抛OOM
-XX:+ScavengeBeforeFullGC	|默认启用	|在Full GC前触发一次Minor GC
-XX:+CMSParallelRemarkEnabled|默认启用|启用CMS可以开启该阶段的并行标记，使用多个线程进行标记，减少暂停时间。
-XX:-UseConcMarkSweepGC	|默认不启用	|启用CMS低停顿垃圾收集器,减少FGC的暂停时间
-XX:-UseParallelGC	|-server时启用,其他情况下，默认不启用	|策略为新生代使用并行清除，年老代使用单线程Mark-Sweep-Compact的垃圾收集器
-XX:-UseParallelOldGC	|默认不启用	|策略为老年代和新生代都使用并行清除的垃圾收集器
-XX:-UseSerialGC	|-client时启用,其他情况下，默认不启用	|使用串行垃圾收集器
-XX:+UseThreadPriorities	|默认启用	|使用本地线程的优先级
-XX:+UseLWPSynchronization	|限于solaris，默认启用	|使用轻量级进程（内核线程）替换线程同步
-XX:+UseVMInterruptibleIO	|限于solaris，默认启用	|在solaris中，允许运行时中断线程
-XX:+FailOverToOldVerifier	|默认启用	|如果新的Class校验器检查失败，则使用老的校验器<br>(失败原因:因为JDK6最高向下兼容到JDK1.2，而JDK1.2的class info 与JDK6的info存在较大的差异，所以新校验器可能会出现校验失败的情况)
-XX:-UseSpinning	|已启用	|启用多线程自旋锁优化
-XX:+UseTLAB	|默认启用	|启用线程本地缓存区
-XX:+UseSplitVerifier	|默认启用	|使用新的Class类型校验器
-XX:+UseAltSigs	|限于Solaris，默认启用	|为了防止与其他发送信号的应用程序冲突，允许使用候补信号替代 SIGUSR1和SIGUSR2
-XX:+UseBoundThreads|限于Solaris, 默认启用	|绑定所有的用户线程到内核线程, 减少线程进入饥饿状态（得不到任何cpu time）的次数
-XX:-AllowUserSignalHandlers|限于Linux和Solaris，默认不启用	|允许为java进程安装信号处理器,信号处理参见类:sun.misc.Signal, sun.misc.SignalHandler
-XX:+MaxFDLimit	|限于Solaris，默认启用	|设置java进程可用文件描述符为操作系统允许的最大值。

###### 3.2、CMS GC参数

参数|说明
---|---
-XX:+UseConcMarkSweepGC |激活CMS收集器
-XX:ConcGCThreads |设置CMS线程的数量
-XX:+UseCMSInitiatingOccupancyOnly |只根据老年代使用比例来决定是否进行CMS
-XX:CMSInitiatingOccupancyFraction |设置触发CMS老年代回收的内存使用率占比
-XX:+CMSParallelRemarkEnabled |并行运行最终标记阶段，加快最终标记的速度
-XX:+UseCMSCompactAtFullCollection |每次触发CMS Full GC的时候都整理一次碎片
-XX:CMSFullGCsBeforeCompaction=* |经过几次CMS Full GC的时候整理一次碎片
-XX:+CMSClassUnloadingEnabled| 让CMS可以收集永久带，默认不会收集
-XX:+CMSScavengeBeforeRemark |最终标记之前强制进行一个Minor GC
-XX:+ExplicitGCInvokesConcurrent |当调用System.gc()的时候，执行并行gc，只有在CMS或者G1下该参数才有效

###### 3.3、G1 GC参数
参数|说明
---|---
-XX:+UseG1GC	|使用 G1 (Garbage First) 垃圾收集器
-XX:MaxGCPauseMillis=n	|设置最大GC停顿时间(GC pause time)指标(target). 这是一个软性指标(soft goal), JVM 会尽量去达成这个目标.
-XX:InitiatingHeapOccupancyPercent=n	|启动并发GC周期时的堆内存占用百分比. G1之类的垃圾收集器用它来触发并发GC周期,基于整个堆的使用率,而不只是某一代内存的使用比. 值为 0 则表示"一直执行GC循环". 默认值为 45.
-XX:ParallelGCThreads=n	|设置垃圾收集器在并行阶段使用的线程数,默认值随JVM运行的平台不同而不同.
-XX:ConcGCThreads=n	|并发垃圾收集器使用的线程数量. 默认值随JVM运行的平台不同而不同.
-XX:G1ReservePercent=n	|设置堆内存保留为假天花板的总量,以降低提升失败的可能性. 默认值是 10.
-XX:G1HeapRegionSize=n	|使用G1时Java堆会被分为大小统一的的区(region)。此参数可以指定每个heap区的大小. 默认值将根据 heap size 算出最优解. 最小值为 1Mb, 最大值为 32Mb.

###### 3.4、性能参数

参数|默认值或限制|说明
---|---|---
-XX:NewSize=2.125m	|默认 2.125m	|新生代预估上限的默认值
-XX:MaxNewSize=size	| 2.5m	|新生代占整个堆内存的最大值
-XX:LargePageSizeInBytes=4m	|默认4m	|设置堆内存的内存页大小
-XX:MaxHeapFreeRatio=70|	70	|GC后，如果发现空闲堆内存占到整个预估上限值的70%，则收缩预估上限值
-XX:MinHeapFreeRatio=40	|40	|GC后，如果发现空闲堆内存占到整个预估上限值的40%，则增大上限值
-XX:NewRatio=2	|默认 2	|新生代和年老代的堆内存占用比例, 例如2表示新生代占年老代的1/2，占整个堆内存的1/3
-XX:SurvivorRatio=8	|默认 8	|Eden与Survivor的占用比例。例如8表示，一个survivor区占用 1/8 的Eden内存，即1/10的新生代内存，为什么不是1/9？因为我们的新生代有2个survivor，即S0和S1。所以survivor总共是占用新生代内存的 2/10，Eden与新生代的占比则为 8/10
-XX:ThreadStackSize=512	|默认 512.	|线程堆栈大小
-XX:+UseBiasedLocking|默认启用	|启用偏向锁
-XX:+AggressiveOpts|默认启用|启用JVM开发团队最新的调优成果。例如编译优化，偏向锁，并行年老代收集等
-XX:CompileThreshold=10000|1000	|通过JIT编译器，将方法编译成机器码的触发阀值，可以理解为调用方法的次数，例如调1000次，将方法编译为机器码
-XX:ReservedCodeCacheSize=32m	|默认 32m	|设置代码缓存的最大值，编译时用
-XX:TargetSurvivorRatio=50	|50	|实际使用的survivor空间大小占比。默认是50%，最高90%
-XX:+UseFastAccessorMethods	|默认启用	|优化原始类型的getter方法性能(get/set:Primitive Type)
-XX:+UseLargePages	|默认启用	|启用大内存分页
-XX:+UseStringCache	|默认启用	|启用缓存常用的字符串。
-XX:AllocatePrefetchLines=1	|1	|Number of cache lines to load after the last object allocation using prefetch instructions generated in JIT compiled code. Default values are 1 if the last allocated object was an instance and 3 if it was an array.
-XX:AllocatePrefetchStyle=1	|1	|Generated code style for prefetch instructions.<br>0 – no prefetch instructions are generate*d*,<br>1 – execute prefetch instructions after each allocation,<br>2 – use TLAB allocation watermark pointer to gate when prefetch instructions are executed.
-XX:+OptimizeStringConcat	|在Java 6更新20中引入	|优化字符串连接操作在可能的情况下
-XX:+UseMPSS	|默认启用	|启用solaris的MPSS，不能与ISM同时使用
-XX:-UseISM	|默认启用	|启用solaris的ISM
-XX:+UseCompressedStrings	|Java 6 update 21有一选项	|其中，对于不需要16位字符的字符串，可以使用byte[] 而非char[]。对于许多应用，这可以节省内存，但速度较慢（5％-10％）

###### 3.5、调试参数

参数	|	说明
---|---
-XX:ErrorFile=./hs_err_pid<pid>.log	|错误文件
-XX:HeapDumpPath=./java_pid<pid>.hprof	|指定HeapDump的文件路径或目录
-XX:-HeapDumpOnOutOfMemoryError|	当抛出OOM时进行HeapDump
-XX:OnOutOfMemoryError=”<cmd args>; |当发生OOM时执行用户指定的命令
-XX:OnError=”<cmd args>;<cmd args>”	|当发生错误时执行用户指定的命令
-XX:-PrintGC	 	|当GC发生时打印信息
-XX:-PrintGCDetails	|1打印GC详细信息
-XX:-PrintGCTimeStamps	|打印GC用时
-XX:ParallelGCThreads=	 	|设置新生代与老年代并行垃圾回收器的线程数
-XX:-CITime	 |打印发费在JIT编译上的时间
-XX:-PrintClassHistogram	|1.4.2	当Ctrl+Break发生时打印Class实例信息,与jmap -histo相同
-XX:-PrintConcurrentLocks	|默认值：6	当Ctrl+Break发生时打印java.util.concurrent的锁信息, 与jstack -l相同
-XX:-PrintCommandLineFlags	|默认值：5	打印命令行上的标记
-XX:-PrintCompilation	 	|当方法被编译时打印信息
-XX:-PrintTenuringDistribution	| 	打印Tenuring年龄信息
-XX:-TraceClassLoading	 	|跟踪类加载
-XX:-TraceClassLoadingPreorder	|1.4.2	跟踪所有加载的引用类
-XX:-TraceClassResolution	|1.4.2	跟踪常量池的变化
-XX:-TraceClassUnloading	| 	跟踪类的卸载
-XX:-TraceLoaderConstraints	|默认值：6	Trace recording of loader constraints
-XX:+PerfSaveDataToFile	 |	退出时保存jvmstat二进制文件
-XX:+UseCompressedOops	 	|Enables the use of compressed pointers (object references represented as 32 bit offsets instead of 64-bit pointers) for optimized 64-bit performance with Java heap sizes less than 32gb.
-XX:+AlwaysPreTouch	 	|Pre-touch the Java heap during JVM initialization. Every page of the heap is thus demand-zeroed during initialization rather than incrementally during application execution.
-XX:AllocatePrefetchDistance=	 |	Sets the prefetch distance for object allocation. Memory about to be written with the value of new objects is prefetched into cache at this distance (in bytes) beyond the address of the last allocated object. Each Java thread has its own allocation point. The default value varies with the platform on which the JVM is running.
-XX:InlineSmallCode=	 	|当编译的代码小于指定的值时,内联编译的代码
-XX:MaxInlineSize=35	 |	内联方法的最大字节数
-XX:FreqInlineSize=	 |	内联频繁执行的方法的最大字节码大小
-XX:LoopUnrollLimit=	 	|Unroll loop bodies with server compiler intermediate representation node count less than this value. The limit used by the server compiler is a function of this value, not the actual value. The default value varies with the platform on which the JVM is running.
-XX:InitialTenuringThreshold=7	 |	设置初始的对象在新生代中最大存活次数
-XX:MaxTenuringThreshold=	 |	设置对象在新生代中最大的存活次数,最大值15,并行回收机制默认为15,CMS默认为4
-XX:-ExtendedDTraceProbes	|JDK6中引入仅在Solaris	启用性能的影响DTrace探测器
