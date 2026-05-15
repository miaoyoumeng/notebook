## 内存屏障

内存屏障（Memory barrier）是一组处理器指令，使CPU或编译器对屏障指令前后发出的内存操作强制实施排序约束，通常意味着在屏障之前发出的操作保证在屏障之后发出的操作之前执行。本文将深入探讨Java中内存屏障的概念、应用以及在JVM中的具体实现，从理论到实现阐述这一主题。

##### 基本概念

想象一下，计算机的主内存就像一个巨大的图书馆，而处理器就是图书馆的管理员。在这个图书馆中，读取和存放书籍（数据）需要很长时间。为了提高效率，管理员们各自配备了一个小推车（缓存），可以暂时存放一些常用的书籍。

但是，为了更快地完成工作，这些管理员有时会打乱存取书籍的顺序。比如，他们可能会先取近处的书，再取远处的书，而不是按照原本的清单顺序操作。当只有一个管理员工作时，或者大家只负责各自的区域时，这种做法并不会造成问题。

然而，当多个管理员共同管理整个图书馆，并且需要频繁更新书籍信息时，问题就出现了。一个管理员可能刚刚更新了一本书的信息，但另一个管理员因为按照自己的顺序工作，可能还在使用旧的信息。这就会导致图书馆的信息混乱，无法保证准确性。

这时候，我们就需要引入“同步点”的概念，这就是内存屏障的作用。在关键的地方设置同步点，要求管理员们在通过同步点时，必须先把手头所有的工作完成，确保推车里的信息与图书馆主系统中的信息完全一致，然后才能继续工作。

这样，虽然管理员们的工作效率可能会稍有降低，但是可以保证图书馆信息的一致性和准确性。在计算机世界中，这种"同步点"就是内存屏障，它确保了在多核处理器和共享内存的环境下，程序能够按照预期的方式正确运行。

内存屏障主要解决以下三个问题：

* 处理器重排序：现代处理器为了提高性能，会对指令进行重排序，虽然这种重排序在单线程环境下是透明的，但在多线程环境中可能导致意外的行为；

* 编译器优化：编译器为了提高程序性能也会对代码进行重排序，这种优化在多线程环境下可能破坏程序的预期行为；

* 缓存一致性：在多核系统中，每个核心都有自己的缓存，缓存和内存中的数据不一致可能会导致功能性问题。

#### 内存屏障的应用


在JVM的实现中，内存屏障并非直接暴露给开发者的API，而是作为JVM内部机制，被策略性地插入到指令序列中，这种插入旨在维护Java语言级并发原语的语义完整性。为了深入理解这一机制，我们可以通过分析简单Java程序的源代码及其对应的汇编指令来观察内存屏障的具体应用，所有的汇编指令都是基于鲲鹏Arm处理器捕获的。


###### 显式内存屏障


下面将聚焦于Dekker算法，Dekker算法是第一个已知的正确解决并发编程中互斥问题的方法，用于解决两个线程（或进程）的互斥问题。该算法的基本流程如下：

* 线程设置自己的标志为true，表示想要进入临界区；
* 检查对方的标志：如果对方也想进入临界区，则进入下一步；否则直接进入临界区；
* 检查轮转变量：如果轮转变量指向对方，则将自己的标志设为false，等待轮转变量改变后再重新尝试；如果指向自己，则进入临界区；
* 进入临界区后执行需要的操作；
* 退出时，将自己的标志设为false，并将轮转变量设置为对方的值。


> 临界区（Critical Section）是指在多线程环境下，一段访问共享资源的程序代码。这些共享资源可能是共享内存、共享文件、共享设备等。临界区的特点是：在同一时刻，只能有一个线程执行这段代码。临界区保证了共享资源的互斥访问，防止数据竞争和不一致性问题。


```java
    private static volatile boolean intentFirst = false;
    private static volatile boolean intentSecond = false;
    private static volatile int turn = 1;

   public static void process1() {
        intentFirst = true;
        while (intentSecond) {
            if (turn == 2) {
                intentFirst = false;
                while (turn == 2) {}
               intentFirst = true;
            }
        }
        turn = 2;
        intentFirst = false;
    }

    public static void process2() {
        intentSecond = true;
        while (intentFirst) {
            if (turn == 1) {
                intentSecond = false;
                while (turn == 1) {}
                intentSecond = true;
            }
        }
        turn = 1;
        intentSecond = false;
    }
```

在现代处理器架构中，即便编译器严格遵循程序员预期的指令顺序，硬件级的优化机制仍可能在不引入显式内存屏障的情况下重排内存操作，这种重排可能导致程序行为偏离预期。我们可以通过分析上述算法中的关键操作来理解这一问题：

volatile 读操作的顺序敏感性：在第7行和第8行，有两个连续的 volatile 读操作，分别用于检测对方线程的进入意图和确定进入临界区的优先权。
volatile 写操作的顺序依赖：第14行和第15行展示了两个连续的 volatile 写操作，这些操作的语义是先让步给对方线程，然后撤销自身的进入意图。
理论上，一个线程撤销进入意图后，另一个线程不应观察到对 turn 变量的写操作先于 intent 变量的写操作。然而，在缺少适当的内存屏障的情况下，处理器的乱序执行可能导致这种非预期的行为。

volatile 关键字通过建立 happens-before 关系来防止上述问题。具体而言：它在 turn 变量的写入和 intent 变量的写入之间建立了严格的 happens-before 关系，强制编译器保持这些内存操作的程序顺序；在必要时插入内存屏障，以阻止处理器级别的重排序。

这种机制确保了 volatile 变量的写操作对其他线程的可见性和有序性，是 Java 内存模型实现线程间通信的关键机制之一。

PrintAssembly 选项是 JVM 的一个诊断标志，允许我们捕获 JIT 编译器生成的汇编指令，还需要一个反汇编程序插件。hsdis 是比较常用的反汇编插件，需要单独下载，下载地址：https://chriswhocodes.com/hsdis/ 。根据系统架构下载对应的文件后，放在 jre 的 lib 目录下或者设置 LD_LIBRARY_PATH 变量路径即可使用。

下面的汇编代码展示了 process1 中第7行的 intentSecond 的读操作。这段代码是在鲲鹏920机器上运行 jdk1.8 捕获的。本文中所有的指令序列都在左侧标有行号。读者不要过分纠结于每条指令的具体语义，而是关注整体结构。


```
01  0x0000ffff794530a4: mov		x0, #0x5008                	// #20488
02  0x0000ffff794530a8: movk	x0, #0x80b6, lsl #16
03  0x0000ffff794530ac: movk	x0, #0x5, lsl #32
04  0x0000ffff794530b0: dmb		ish
05  0x0000ffff794530b4: ldrb	w0, [x0, #125]
06  0x0000ffff794530b8: dmb		ishld           ;*getstatic intentSecond
07  0x0000ffff794530bc: cmp		w0, #0x0
08  0x0000ffff794530c0: mov		x0, #0x1040                	// #4160
09  0x0000ffff794530c4: movk	x0, #0x3040, lsl #16
10  0x0000ffff794530c8: movk	x0, #0xfffd, lsl #32
11  0x0000ffff794530cc: mov		x8, #0x108                 	// #264
12  0x0000ffff794530d0: mov		x9, #0x118                 	// #280
13  0x0000ffff794530d4: csel	x1, x8, x9, eq  // eq = none
14  0x0000ffff794530d8: ldr		x2, [x0, x1]
15  0x0000ffff794530dc: add		x2, x2, #0x1
16  0x0000ffff794530e0: str		x2, [x0, x1]
17  0x0000ffff794530e4: b.eq	0x0000ffff79453288  // b.none
```

这段简短的指令序列蕴含了丰富的信息。intentSecond 的读取操作位于第5行。Java 内存模型（JMM）要求 JVM 按照程序顺序执行 volatile 读取操作。然而，仅依赖 JVM 层面的顺序保证是不充分的，因为底层处理器仍可能对这些操作进行重排序。为了维护 JMM 的一致性保证，JVM 利用特定的硬件指令，如 dmb 指令来标注第一次读操作，dmb ish 和 dmb ishld 指令的组合使用，确保了该读操作在后续读操作之前完成，从而在硬件层面上防止了潜在的重排序问题。

DMB 是一种内存序列化指令，用于强制执行特定的内存访问顺序，有以下三点特征：

* 序列化保证：确保 DMB 指令之前的所有内存访问操作在 DMB 指令之后的任何内存访问操作开始执行之前完成；
* 防止指令重排：处理器不能将 DMB 指令后的内存访问指令重新排序到 DMB 指令之前；
* 执行顺序控制：DMB 不保证内存访问操作在 DMB 指令执行前完成，而是确保 DMB 前后内存访问操作的相对执行顺序。

内存一致性的维护需要读写双方的协同。如果只有读操作线程在连续读之间插入内存屏障，而写操作线程未在连续写之间做相应处理，则无法保证一致性。有效的线程间通信要求所有参与线程遵守相同的同步协议。在 Dekker 算法的实现中，预期在两个连续的volatile写操作之间存在一个内存屏障，这个屏障的存在确保了写操作的可见性和有序性，是实现线程间正确通信关键。

```java
$ java -XX:+UnlockDiagnosticVMOptions -XX:+PrintAssembly -XX:CompileCommand=compileonly,DekkerAlgorithm.process1  DekkerAlgorithm
```

```
01  0x0000ffff7945329c: str       w1, [x0, #120]
02  0x0000ffff794532a0: dmb       ish             ;*putstatic turn
03  0x0000ffff794532a4: movz      w1, #0x0, lsl #16
04  0x0000ffff794532a8: dmb       ish
05  0x0000ffff794532ac: strb      w1, [x0, #124]
06  0x0000ffff794532b0: dmb       ish             ;*putstatic intentFirst
07  0x0000ffff794532b4: ldp       x29, x30, [sp, #48]
08  0x0000ffff794532b8: add       sp, sp, #0x40
09  0x0000ffff794532bc: adrp      x8, 0x0000ffff90ef0000
```

这段汇编指令对应代码的14、15行。关注一下上面汇编段第4行的 dmb ish 指令，这个指令的作用是确保 turn = 2  和  intentFirst = false 两个操作按照正确的顺序执行，并且对其他线程可见，这对于 Dekker 算法的正确性至关重要，因为它防止了潜在的指令重排序，确保  turn = 2  在 intentFirst = false  之前完成，它保证了当其他核心观察到 intentFirst = false 时，一定能看到更新后的 turn 值。

这里要注意，我们是在鲲鹏AArch64 架构上捕获的指令，AArch64架构是一种弱内存模型。弱内存模型对硬件的约束很少，对微架构的优化提供了很大空间。弱内存模型允许软件/硬件进行指令重排，更容易获得更好的性能，但是软件的编程模型变得非常复杂，需要一些额外的内存屏障指令来保证执行顺序与正确性。在两个连续的写操作之间，弱内存模型可能发生重排序问题。而在强内存模型中，硬件会保证一些操作（如：store-store/load-load/load-store）的顺序执行，不需要额外的内存屏障。JVM 使用内存屏障来弥合 Java 内存模型和运行它的硬件内存模型之间的差异。使用 litmus 工具可以验证内存序相关问题，感兴趣的同学可以阅读文章：使用herd7做ARM内存模型验证（https://wangzhou.github.io/使用herd7做ARM内存模型验证/） 。


###### 隐式内存屏障

**synchronized 关键字**


显式设置内存屏障并不是序列化内存操作的唯一方法，下面使用 Counter 类继续观察内存屏障。

```
public class Counter {
    static int counter = 0;

    public static void main(String[] args) {
        for (int i = 0; i < 100000; i++)
            inc();
    }
    static synchronized void inc() {
        counter += 1;
    }
}
```

Counter 类实现了一个典型的读-修改-写操作序列。这种操作模式在并发编程中常见，尤其是在实现原子计数器时。计数器字段被声明为静态非 volatile 变量。为确保操作的原子性，inc 方法被声明为 synchronized 方法。这种同步机制利用了 Java 内置的监视器锁（monitor lock）来保证方法级别的互斥访问。Java 内存模型规定，退出同步块时的内存可见性语义等同于 volatile 内存操作的可见性语义。这意味着在同步块退出时，也能观察到内存屏障指令。

```shell
$ java -XX:+UnlockDiagnosticVMOptions -XX:+PrintAssembly -XX:-UseBiasedLocking -XX:CompileCommand=compileonly,Counter.inc Counter
```

```
01  0x0000ffffa55083fc:   casal   x0, x2, [x9]
02  0x0000ffffa5508400:   cmp     x8, x0
03  0x0000ffffa5508404:   b.eq    0x0000ffffa5508420  // b.none
04  0x0000ffffa5508408:   dmb     ish
05  0x0000ffffa550840c:   mov     x8, sp
06  0x0000ffffa5508410:   sub     x0, x0, x8
07  0x0000ffffa5508414:   ands    x0, x0, #0xffffffffffff0007
08  0x0000ffffa5508418:   str     x0, [x2]
09  0x0000ffffa550841c:   cbnz    x0, 0x0000ffffa5508478
10  0x0000ffffa5508420:   mov     x0, #0x30c0                     // #12480
11  0x0000ffffa5508424:   movk    x0, #0x108, lsl #16
12  0x0000ffffa5508428:   movk    x0, #0x1, lsl #32
13  0x0000ffffa550842c:   ldr     w1, [x0, #112]              ;*getstatic counter
14  0x0000ffffa5508430:   add     w1, w1, #0x1
15  0x0000ffffa5508434:   str     w1, [x0, #112]              ;*putstatic counter
16  0x0000ffffa5508438:   add     x0, sp, #0x20
17  0x0000ffffa550843c:   ldr     x1, [x0]
18  0x0000ffffa5508440:   cbz     x1, 0x0000ffffa5508460
19  0x0000ffffa5508444:   ldr     x2, [x0, #8]
20  0x0000ffffa5508448:   mov     x9, x0
21  0x0000ffffa550844c:   casal   x0, x1, [x2]
```

synchronized 修饰符生成的机器指令序列在数量上显著多于 volatile 修饰符，这反映了两者在实现内存同步和互斥访问方面的复杂度差异。计数器的增量操作被定位于指令序列的第14行，前后能明显观察到 get 和 put 操作。然而，JVM 并未在此处插入显式的内存屏障指令，而是在前后采用了 casal 指令实现原子操作和内存同步。

casal 指令执行比较和交换操作，这个过程是原子的，意味着在执行过程中不会被其他线程中断。casal 保证在这条指令之后的读操作不会被重排到这条指令之前，以及在这条指令之前的写操作不会被重排到这条指令之后。在这段代码中，casal 被用来实现自旋锁。如果获取锁失败，代码会继续尝试，直到成功为止。使用 casal 这样的原子指令可以在某些情况下提供更好的性能，特别是在锁竞争不激烈的场景。


**Atomic 原子类**

下面使用 java.util.concurrent.atomic.AtomicInteger 实现类 Counter2，再次进行观察：

```java
import java.util.concurrent.atomic.AtomicInteger;
public class Counter2 {
    private static final AtomicInteger counter = new AtomicInteger(0);
    public static void main(String[] args) {
        for (int i = 0; i < 1000000; i++) {
            inc();
        }
    }
    public static void inc() {
        counter.incrementAndGet();
    }
}
```

```shell
$ java -XX:+UnlockDiagnosticVMOptions -XX:+PrintAssembly -XX:-UseBiasedLocking Counter2
```

```
01  0x0000ffff95458880: nop
02  0x0000ffff95458884: mov       x9, #0xffffffffffff0000         // #-65536
03  0x0000ffff95458888: movk      x9, #0xfffd, lsl #16
04  0x0000ffff9545888c: str       xzr, [sp, x9]
05  0x0000ffff95458890: sub       sp, sp, #0x50
06  0x0000ffff95458894: stp       x29, x30, [sp, #64]  ;*getstatic unsafe
07  0x0000ffff95458898: add       x2, x1, #0xc
08  0x0000ffff9545889c: ldaxr     w0, [x2]
09  0x0000ffff954588a0: add       w8, w0, #0x1
10  0x0000ffff954588a4: stlxr     w9, w8, [x2]
11  0x0000ffff954588a8: cbnz      w9, 0x0000ffff9545889c
12  0x0000ffff954588ac: dmb       ish
13  0x0000ffff954588b0: add       w0, w0, #0x1
14  0x0000ffff954588b4: ldp       x29, x30, [sp, #64]
15  0x0000ffff954588b8: add       sp, sp, #0x50
16  0x0000ffff954588bc: adrp      x8, 0x0000ffffac670000
17  0x0000ffff954588c0: ldr       wzr, [x8]       ;   {poll_return}
```

我们可以看到第8行和第10行所包裹的加操作，ldaxr 指令从地址 [x2] 加载值到 w0，并确保读取是原子的（带有 Acquire 语义），stlxr 指令将 w8 的值存储到地址 [x2]，并确保写入是原子的（带有 Release 语义），结果存入 w9；11行的 cbnz 指令判断如果 w9 不为零，则跳转到第8行，形成了一个自旋锁循环。12行的 dmb ish 指令确保在这个循环之后的内存操作不会被重排序到循环之前。这种组合确保了变量的新值在所有后续内存操作执行之前，对其他线程可见。

>Acquire语义：通常与读操作相关联，该屏障原语之后的读写操作不能重排到该屏障原语前面。

>Release语义：通常与写操作相关联，该屏障原语之前的读写操作不能重排到该屏障原语后面。

Counter 类和 Counter2 类在同步机制实现上存在显著差异，Counter 类的 synchronized 方法使用了基于监视器（monitor）的锁机制，casal 指令用于实现监视器的进入和退出操作，同步范围覆盖整个方法，提供了方法级的原子性和可见性保证，实现了"全屏障"语义，确保方法执行前后的内存一致性。而 Counter2 类使用 AtomicInteger.incrementAndGet 方法，采用了无锁的原子操作，基于原子指令（如：ldaxr 和 stlxr）来实现细粒度的同步，只对特定的内存位置（计数器变量）进行同步，而非整个方法，通过 Acquire-Release 语义（ldaxr 的 Acquire 屏障和 stlxr 的 Release 屏障）实现了必要的内存排序，保证了操作的原子性和可见性。

这两种方法在同步粒度和性能特性上有所不同：synchronized 提供了更强的隔离性但可能引入更多开销，而 AtomicInteger 通过更精细的同步机制在大多数情况下可以提供更好的性能，特别是在高竞争环境下，选择哪种方法取决于具体的应用场景和性能需求。


#### 底层实现与优化

###### DMB 指令

Data Memory Barrier (DMB) 指令是 Arm 架构中用于实现内存屏障的关键指令。DMB 指令可以通过参数来精确控制其作用范围和访问类型。

**共享属性域**

Arm 架构定义了四种共享属性域，用于指定内存屏障的作用范围：

全系统共享（full system sharable）域，包括所有处理器和外部设备，该选项确保系统中的所有组件都能看到一致的内存视图；
外部共享（outer sharable）域，在整个外部共享内存系统中有效；
内部共享（inner sharable）域，在一个共享集群内的所有处理器之间有效，通常用于多核处理器的L1缓存，这些处理器共享某些内存区域；
不指定共享（non-sharable）域，仅在单个处理器内有效，即内存屏障操作只影响发出指令的处理器，其他处理器和设备不受影响。
这些域的定义允许开发者在优化性能的同时，精确控制内存屏障的影响范围。

**访问类型**

DMB 指令还可以根据访问类型进行细分：

* 读内存屏障（Load-Load/Load-Store）：参数后缀为 LD，只影响读取操作，所有在 DMB 指令之前的读取操作必须在 DMB 指令执行完成之前完成；
* 写内存屏障（Store-Store）：参数后缀为 ST，只影响写入操作，所有在 DMB 指令之前的写入操作必须在 DMB 指令执行完成之前完成；
* 读写内存屏障：不带特殊后缀，提供全功能内存屏障，影响所有读取和写入操作，所有在 DMB 指令之前的读取和写入操作都必须在 DMB 指令执行完成之前完成。
在 JVM 中，主要使用内部共享域（ISH）进行内存屏障操作。以下是 JVM 中 DMB 指令相关的定义：

```
// assembler_aarch64.hpp
  enum Membar_mask_bits {
    StoreStore = ISHST,
    LoadStore  = ISHLD,
    LoadLoad   = ISHLD,
    StoreLoad  = ISH,
    AnyAny     = ISH
  };

  void membar(Membar_mask_bits order_constraint) {
    dmb(Assembler::barrier(order_constraint));
  }

  void dmb(barrier imm) {
    system(0b00, 0b011, 0b00011, imm, 0b101);
  }
```

**volatile 的优化**

JDK 源码中的 aarch64.ad 文件描述了 AArch64 架构的特性，包括寄存器、指令集、寻址模式等；描述了如何将 Java 字节码转换成 AArch64 机器码，包括选择适当的 AArch64 指令来实现特定的字节码操作；定义了如何在 AArch64 架构上分配和使用寄存器，以确保高效的指令执行；描述了指令的调度策略，以便最大化 CPU 的执行效率，减少指令间的依赖和延迟。

在 aarch64.ad 文件中介绍了有关对 volatile 读写操作的优化。主要优化策略如下：

* volatile读取：使用 ldar 指令直接从内存加载变量值，保证在加载前后的内存操作不能被重排；
* volatile写入：使用 stlr 指令将值存储到内存，确保在存储操作之前的所有内存访问已完成。

观察 DekkerAlgorithm.process1 C2 编译器的汇编指令：

```shell
java -XX:+UnlockDiagnosticVMOptions -XX:+PrintAssembly -XX:-TieredCompilation -XX:CompileCommand=compileonly,DekkerAlgorithm.process1  DekkerAlgorithm
```
```
  0x0000ffff8cef4258: mov       x10, #0x2e20                    // #11808
  0x0000ffff8cef425c: movk      x10, #0x80b6, lsl #16
  0x0000ffff8cef4260: movk      x10, #0x5, lsl #32
  0x0000ffff8cef4264: orr       w12, wzr, #0x1
  0x0000ffff8cef4268: add       x11, x10, #0x7c
  0x0000ffff8cef426c: stlrb     w12, [x11]      ;*putstatic interFirst
  0x0000ffff8cef4270: add       x11, x10, #0x7d
  0x0000ffff8cef4274: ldarb     w11, [x11]      ;*getstatic interSecond
  0x0000ffff8cef4278: cbnz      w11, 0x0000ffff8cef42a8
  0x0000ffff8cef427c: orr       w13, wzr, #0x2
```
我们可以发现这种优化方式相比使用完整的 DMB 指令，提供了更细粒度的控制和更高的性能。
--------

#### CAS 的实现


Compare-And-Swap (CAS) 操作在 JVM 中的实现如下：

```shell
  //   dmb      ish
  // retry:
  //   ldxr<x>   rval raddr
  //   cmp       rval rold
  //   b.ne done
  //   stlxr<x>  rval, rnew, rold
  //   cbnz      rval retry
  // done:
  //   cset      r0, eq
  //   dmb ishld
```

这个描述正如前文“Atomic 原子类”章节中类 Counter2 中所展示的，AtomicInteger.incrementAndGet 方法的实现逻辑。

#### 编译器层面

在编译器层面，JVM 通过 Atomic 类和 OrderAccess 类来实现调用：

```
// atomic_linux_aarch64.inline.hpp
#define FULL_MEM_BARRIER  __sync_synchronize()
#define READ_MEM_BARRIER  __atomic_thread_fence(__ATOMIC_ACQUIRE);
#define WRITE_MEM_BARRIER __atomic_thread_fence(__ATOMIC_RELEASE);

// orderAccess_linux_aarch64.inline.hpp
inline void OrderAccess::loadload()   { acquire(); }
inline void OrderAccess::storestore() { release(); }
inline void OrderAccess::loadstore()  { acquire(); }
inline void OrderAccess::storeload()  { fence(); }

inline void OrderAccess::acquire() {
  READ_MEM_BARRIER;
}

inline void OrderAccess::release() {
  WRITE_MEM_BARRIER;
}

inline void OrderAccess::fence() {
  FULL_MEM_BARRIER;
}
```

这些实现利用了 GCC 提供的内置函数，如 __ sync_synchronize() 和 __ atomic_thread_fence()，来生成不同类型的内存屏障，实现了从编译器层面对内存操作的精确控制。通过这些底层实现和优化，JVM 能够在保证内存一致性的同时，最大化并发操作的性能。

#### 隐性同步机制
JVM 包含多种隐式同步机制，这些机制主常源于多线程编程中与变量共享相关的特性。

final 字段
Java 为 final 字段制定了特殊的内存模型规则，主要涉及两个方面：

构造函数内的安全发布：确保 final 字段的初始化在对象对其他线程可见之前完成，这防止了半初始化对象的暴露；
读取的一致性保证：当一个线程首次读取包含最终字段的对象时，它保证能看到该字段的正确初始化值。
这些规则旨在不使用 volatile 关键字的情况下，为 final 字段提供一定程度的线程安全性。

```
// parse1.cpp
void Parse::do_exits() {
  set_parse_bci(InvocationEntryBci);

  // Now peephole on the return bits
  Node* region = _exits.control();
  _exits.set_control(gvn().transform(region));

  Node* iophi = _exits.i_o();
  _exits.set_i_o(gvn().transform(iophi));

  if (method()->is_initializer() && (wrote_final() PPC64_ONLY(|| wrote_volatile()))) {
    _exits.insert_mem_bar(Op_MemBarRelease, alloc_with_final());

    if (DoEscapeAnalysis && alloc_with_final()) {
      AllocateNode *alloc = AllocateNode::Ideal_allocation(alloc_with_final(), &_gvn);
      alloc->compute_MemBar_redundancy(method());
    }
  }
  // ......
}
```
do_exits 方法在方法编译的最后阶段被调用，用于生成方法退出相关的代码。为了处理 final 字段的写入，使用 wrote_final() 方法进行判断，如果判断为 TRUE，则插入 Op_MemBarRelease 内存屏障，确保在构造函数返回之前，所有对 final 字段的写入都已经完成并对其他线程可见。这个屏障防止了构造函数中的写入操作与构造函数之后的代码重排序，保证了对象的安全发布。代码合入见于 https://bugs.openjdk.org/browse/JDK-6934604 。

数组创建

```
// c1_Runtime1_aarch64.cpp
OopMapSet* Runtime1::generate_code_for(StubID id, StubAssembler* sasm) {
 // ......
    case new_type_array_id:
    case new_object_array_id:
    // ......
          __ initialize_header(obj, klass, length, t1, t2);
          __ ldrb(t1, Address(klass, in_bytes(Klass::layout_helper_offset()) + (Klass::_lh_header_size_shift / BitsPerByte)));
          assert(Klass::_lh_header_size_shift % BitsPerByte == 0, "bytewise");
          assert(Klass::_lh_header_size_mask <= 0xFF, "bytewise");
          __ andr(t1, t1, Klass::_lh_header_size_mask);
          __ sub(arr_size, arr_size, t1);  // body length
          __ add(t1, t1, obj);       // body start
          __ initialize_body(t1, arr_size, 0, t2);
          __ membar(Assembler::StoreStore);
          __ verify_oop(obj);
    // ......
}
```
在创建新数组时，代码显式插入了 membar(Assembler::StoreStore)。这个内存屏障在初始化数组体后立即使用，目的是：

确保数组体的初始化操作（store 操作）在后续的任何 store 操作之前完成；

防止初始化操作与后续可能的操作发生重排序；

保证其他线程看到一个完全初始化的对象，避免出现对象的部分可见性问题。

代码合入见于 https://bugs.openjdk.org/browse/JDK-8233839 。

字符串拼接
字符串作为 Java 中最常用的数据结构之一，其底层实现依赖于数组结构。在理解了上述数组创建的机制后，我们将继续探讨字符串拼接时采用的内存屏障。

```
// stringopts.cpp
void PhaseStringOpts::replace_string_concat(StringConcat* sc) {
    // ......
    // Intialize the string
    if (java_lang_String::has_offset_field()) {
      kit.store_String_offset(kit.control(), result, __ intcon(0));
      kit.store_String_length(kit.control(), result, length);
    }
    kit.store_String_value(kit.control(), result, char_array);
    assert(AllocateNode::Ideal_allocation(result, _gvn) != NULL, "should be newly allocated");
    kit.insert_mem_bar(Op_MemBarRelease, result);
  } else {
    result = C->top();
  }
  // hook up the outgoing control and result
  kit.replace_call(sc->end(), result);

  // Unhook any hook nodes
  string_sizes->disconnect_inputs(NULL, C);
  sc->cleanup();
}
```
C2 的字符串连接优化通过创建单个字符缓冲区数组（或具有压缩字符串的字节数组）并直接从该数组加载/存储来替代一系列 StringBuilder.append() 调用。最终的 StringBuilder.toString() 调用被一个新的 String 分配替换，该分配被初始化到缓冲区数组。

根据指令的调度，可能会发生对新分配的 String 对象的引用在 String.value 字段初始化之前转义。在高度并发的情况下，另一个线程可能会尝试从这样一个部分初始化的 String 对象中取消引用 String.value 并导致崩溃。而且，String 的 value 字段在定义中也为 final 字段。

所以代码中插入了 Op_MemBarRelease，主要意图如下：

确保字符串初始化的可见性：代码中刚刚完成了新 String 对象的分配和初始化，确保在任何其他线程可能看到这个新创建的 String 对象引用之前，所有的初始化操作（包括字符数组的赋值、offset 和 length 字段的设置等）都已经完成并对其他线程可见；
处理 final 字段：确保 final 字段的正确设置和可见性；
一致性保证：确保在任何并发场景下，其他线程看到的 String 对象状态都是完整且一致的。
代码合入见于 https://bugs.openjdk.org/browse/JDK-8159244 。

这些隐式同步机制展示了 Java 在内存模型和并发安全性方面的深层考虑，为开发者提供了额外的安全保障，同时也优化了特定场景下的性能。

#### 结语

本文探讨了 Java 内存屏障的概念、应用及其在 JVM 中的实现。从理论出发，解释了内存屏障的基本概念和必要性，然后通过具体的代码示例和汇编指令分析，展示了 Java 如何在不同场景下应用内存屏障。讨论了 volatile 关键字、synchronized 方法和原子操作的底层实现，以及 ARM 架构中 DMB 指令的使用。此外，还探讨了 JVM 中的一些隐式同步机制，如 final 字段、数组创建和字符串优化中的内存屏障应用。

这些分析揭示了 Java 内存模型的复杂性，也展示了 JVM 为了在保证内存一致性的同时优化性能所做的努力。希望通过本文的介绍，能够让读者更好地掌握 Java 内存屏障的概念和应用，为并发编程打下坚实的基础。



