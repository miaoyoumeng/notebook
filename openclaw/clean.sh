#!/bin/bash

root_dir=$(pwd)

for dir in $(find ${root_dir} -type d -name ".venv"); do
   echo "删除 ${dir}"
   ls  -ld   ${dir} &&rm -rf ${dir}
done 

for file in $(find ${root_dir} -type f -name "uv.lock"); do
   echo "删除 $file"
   ls  -ld   ${file} &&rm -rf ${file}
done
