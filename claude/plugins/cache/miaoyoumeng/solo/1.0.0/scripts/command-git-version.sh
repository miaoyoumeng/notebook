#!/bin/bash

echo "+++++command-git-version.sh execute.+++++"

for arg in "$@"; do
    case $arg in
        --dir=*)
            PROJECT_DEST_DIR="${arg#*=}"
            shift
            ;;
        *)
            echo "未知参数: $arg"
            exit 1
            ;;
    esac
done
if [ "X" == "${PROJECT_DEST_DIR}X" ]; then
    echo " --dir params has not valid value..."
    exit
fi
if [ ! -d "${PROJECT_DEST_DIR}" ]; then
    echo "dir ${PROJECT_DEST_DIR} not exist..."
    exit
fi

if [ -d ${PROJECT_DEST_DIR}/.git ]; then 
	echo "git commit task..."
	cd ${PROJECT_DEST_DIR} 
    GIT_STATUS=`git status -s`
	if [ "X${GIT_STATUS}" != "X" ]; then 
		git add -A  
		git commit -m "auto: snapshot outputs after command task excuted `date "+%Y-%m-%d %H:%M:%S"`" 2>/dev/null 
	else
		echo "git nothing to commit ...."
	fi; 
fi