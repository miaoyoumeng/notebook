#!/bin/bash
cd `dirname $0`
BIN_DIR=`pwd`
${BIN_DIR}/stop.sh
${BIN_DIR}/start.sh $@