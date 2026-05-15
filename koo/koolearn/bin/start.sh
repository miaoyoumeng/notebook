#!/bin/bash

source /etc/profile
cd `dirname $0`
BIN_DIR=`pwd`
cd ..
DEPLOY_DIR=`pwd`
LOGS_DIR=$DEPLOY_DIR/logs
if [ ! -d $LOGS_DIR ]; then
	mkdir $LOGS_DIR
fi
nohup gitbook serve >> ${LOGS_DIR}/stdout.log &
