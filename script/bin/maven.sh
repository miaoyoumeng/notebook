#!/bin/sh
source /etc/profile

cd `dirname $0`
BIN_DIR=`pwd`
cd ..
PROJECT_DIR=`pwd`

for pom in `find ${PROJECT_DIR}/maven/poms  -name "*\.xml"`;
do
  echo ${pom} ;
  mvn install  -f ${pom}
done

