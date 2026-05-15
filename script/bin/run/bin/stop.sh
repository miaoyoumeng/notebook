#!/bin/bash
cd `dirname $0`
BIN_DIR=`pwd`
cd ..
DEPLOY_DIR=`pwd`
CONF_DIR=$DEPLOY_DIR/conf


PIDS=`ps -ef | grep java | grep "$CONF_DIR" |awk '{print $2}'`
if [ -z "$PIDS" ]; then
    echo "ERROR: The $DEPLOY_DIR does not started!"
    exit 0
fi

echo -e "Stopping the $DEPLOY_DIR ...\c"
for PID in $PIDS ; do
    kill $PID > /dev/null 2>&1
done

COUNT=15
while [ ${COUNT} -gt 1 ]; do
    echo -e ".\c"
    sleep 1
    echo "${COUNT}.\c"
    for PID in $PIDS ; do
        PID_EXIST=`ps -f -p $PID | grep java`
        if [  -n "$PID_EXIST" ]; then
            COUNT=$[$COUNT-1]
        else
            COUNT=0
            break
        fi
    done
done
if [ ${COUNT} -eq 1 ];then
    for PID in $PIDS ; do
        kill -9  $PID > /dev/null 2>&1
    done
fi 

echo "OK!"
echo "PID: $PIDS"
