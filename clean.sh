#!/bin/bash

root_dir=$(cd "$(dirname "$0")" && pwd)

# for dir in $(find ${root_dir} -type d -name ".venv"); do
#    echo "删除 ${dir}"
#    ls  -ld   ${dir} &&rm -rf ${dir}
# done 

# for file in $(find ${root_dir} -type f -name "uv.lock"); do
#    echo "删除 $file"
#    ls  -ld   ${file} &&rm -rf ${file}
# done

for file in $(find ${root_dir} -type f -name ".DS_Store"); do
   echo "删除 $file"
   ls  -ld   ${file} &&rm -rf ${file}
done
