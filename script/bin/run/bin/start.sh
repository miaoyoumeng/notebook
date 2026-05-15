#!/bin/sh
source /etc/profile

cd `dirname $0`
BIN_DIR=`pwd`
cd ..
DEPLOY_DIR=`pwd`
CONF_DIR=$DEPLOY_DIR/conf

PIDS=`ps -ef | grep java | grep "$CONF_DIR" |awk '{print $2}'`
if [ -n "$PIDS" ]; then
    echo "ERROR: The $SERVER_NAME already started!"
    echo "PID: $PIDS"
    exit 1
fi

if [ -n "$SERVER_PORT" ]; then
    SERVER_PORT_COUNT=`netstat -tln | grep $SERVER_PORT | wc -l`
    if [ $SERVER_PORT_COUNT -gt 0 ]; then
        echo "ERROR: The $SERVER_NAME port $SERVER_PORT already used!"
        exit 1
    fi
fi

LOGS_DIR=""
if [ -n "$LOGS_FILE" ]; then
    LOGS_DIR=`dirname $LOGS_FILE`
else
    LOGS_DIR=$DEPLOY_DIR/logs
fi
if [ ! -d $LOGS_DIR ]; then
    mkdir $LOGS_DIR
fi
STDOUT_FILE=$LOGS_DIR/console.log

LIB_DIR=$DEPLOY_DIR/lib
LIB_JARS=`ls $LIB_DIR|grep .jar|awk '{print "'$LIB_DIR'/"$0}'|tr "\n" " "`

JAVA_OPTS=" -Djava.awt.headless=true -Djava.net.preferIPv4Stack=true -XX:+HeapDumpOnOutOfMemoryError"
hostname=`hostname`
idc=`echo "$hostname" |awk -F - '{print $1}'`
if [ -n "$idc" ]; then
	JAVA_OPTS="$JAVA_OPTS "
fi

echo "JAVA_OPTS: $JAVA_OPTS"

JAVA_DEBUG_OPTS=""
if [ "$1" = "debug" ]; then
    JAVA_DEBUG_OPTS=" -Xdebug -Xnoagent -Djava.compiler=NONE -Xrunjdwp:transport=dt_socket,address=8000,server=y,suspend=n "
fi
JAVA_JMX_OPTS=""
if [ "$1" = "jmx" ]; then
    JAVA_JMX_OPTS=" -Dcom.sun.management.jmxremote.port=1099 -Dcom.sun.management.jmxremote.ssl=false -Dcom.sun.management.jmxremote.authenticate=false "
fi
JAVA_MEM_OPTS=""
jdk=${JAVA_HOME}

echo "use JAVA_HOME: ${jdk}"
JAVA_BIN=${jdk}/bin/java
BITS=`$JAVA_BIN -version 2>&1 | grep -i 64-bit`
if [ -n "$BITS" ]; then
    JAVA_MEM_OPTS=" -server -Xmx2g -Xms2g -Xmn768m -Xss512k -XX:+UseConcMarkSweepGC -XX:+CMSParallelRemarkEnabled -XX:+UseCMSCompactAtFullCollection -XX:LargePageSizeInBytes=128m -XX:+UseFastAccessorMethods -XX:+UseCMSInitiatingOccupancyOnly -XX:CMSInitiatingOccupancyFraction=70 -Drocketmq.client.logUseSlf4j=true "
else
    JAVA_MEM_OPTS=" -server -Xms1g -Xmx1g -XX:SurvivorRatio=2 -XX:+UseParallelGC  -Drocketmq.client.logUseSlf4j=true "
fi

SPRING_CLOUD_OPS=""

echo -e "Starting the $DEPLOY_DIR ...\c"
CONFIG_FILES=" -Dspring.config.location=${CONF_DIR}/application.yml "
if [ -d "$LOGS_DIR" ];then
     CONFIG_FILES="${CONFIG_FILES} -Dlogging.path=$LOGS_DIR "
fi

nohup $JAVA_BIN $JAVA_MEM_OPTS $JAVA_OPTS $JAVA_DEBUG_OPTS $JAVA_JMX_OPTS ${CONFIG_FILES} -jar ${LIB_JARS}  ${SPRING_CLOUD_OPS} > $STDOUT_FILE  2>&1 &

echo "OK!"
PIDS=`ps -ef | grep java | grep "$DEPLOY_DIR" | awk '{print $2}'`
echo "PID: $PIDS"
echo "STDOUT: $STDOUT_FILE"
