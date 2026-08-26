#!/bin/bash

## 🟠  🟣  🟡  🟢  🟤  🔴  🔵  ⚪  ⚫

SOURCE_CODE_DIR=$(cd "$(dirname "$0")" && pwd)
delimiter=" -> "

claude_workspace() {
    local workspace=""
    # 解析参数：支持 --prd=xxx 和直接路径两种格式
    for arg in "$@"; do
        case "$arg" in
            --workspace=*)
                workspace="${arg#--workspace=}"
                ;;
            --commander=*)
                commander="${arg#--commander=}"
                ;;
        esac
    done
    if [ ! -d "${workspace}" ]; then
        echo "Error: workspace path is required, please provide the correct full path."
        echo "Usage: console.sh ${commander:-\`Unknown\`} --workspace=/path/to/workspace"
        exit 0
    fi
    echo "${workspace}"
}

claude_setting_dir() {
    local workspace=$(claude_workspace "$@")
    claude_setting_dir=${workspace}/.claude
    if [ ! -d "${claude_setting_dir}" ]; then
        echo "Error: claude  dir \`${workspace}/.claude\` is required, please provide the correct claude workspace."
        exit 0
    fi
    # echo "${claude_setting_dir}"
}

prd_work_dashborad() {
    local workspace=$(claude_workspace "$@")
    prd_work_dashborad=${workspace}/.claude/prd-route-mapping.log
    
    echo ${prd_work_dashborad}
}

claude_starter() {
    local prompt=""
    # 解析参数：支持 --prd=xxx 和直接路径两种格式
    for arg in "$@"; do
        case "$arg" in
            --prompt=*)
                prompt="${arg#--prompt=}"
                ;;
        esac
    done

    if [ -n "${prompt}" ]; then
        local workspace=$(claude_workspace "$@")
        cd ${workspace} &&  claude -p "\"${prompt}\"" \
            --max-turns 100 \
            --dangerously-skip-permissions \
            --verbose \
            --debug-file /tmp/claude-debug.log
    fi
}
###############################################
################     分割线     ################
###############################################
develop_vue() {
    claude_setting_dir "$@"

    local workspace=$(claude_workspace "$@")
    local prd_file=""

    # 解析参数：支持 --prd=xxx 和直接路径两种格式
    for arg in "$@"; do
        case "$arg" in
            --prd=*)
                prd_file="${arg#--prd=}"
                ;;
        esac
    done

    if [ -z "${prd_file}" ]; then
        echo "Error: PRD file path is required, please provide the full path."
        echo "Usage: console.sh develop_vue --prd=/path/to/prd.md [--route=xxx]"
        exit 0
    fi
    if [ ! -f "${prd_file}" ]; then
        echo "PRD file not found: ${prd_file}"
        exit 0
    fi

    prd_work_dashborad=$(prd_work_dashborad "$@")
    if [ ! -f "${prd_work_dashborad}" ]; then
        touch "${prd_work_dashborad}"
    fi

    # 如果 prd_work_dashborad 中已有该 prd 的记录，使用已记录的 route，忽略脚本传入的值
    prd_status=$(grep "^${prd_file}" "${prd_work_dashborad}" | head -1 | awk -F " -> " '{print $3}')

    if [ "X 🟡 待开发 X" != "X ${prd_status} X" ]; then
        echo "prd 文档：${prd_file}，状态不支持开发，请修复为：\`🟡 待开发\`"
        exit 0
    fi

    vue_route=$(grep "^${prd_file}" "${prd_work_dashborad}" | head -1 | awk -F " -> " '{print $2}')
    if [ -z "${vue_route}" ]; then
        echo "rout not find, please provide the prd vue route."
        exit 0
    fi

    local ui_file="${prd_file//\/prds\///ui/}"
    ui_file="${ui_file/.prd.md/-ui.html}"

    if [ ! -f "${ui_file}" ]; then
        echo "UI html file not found: ${ui_file}"
        exit 0
    fi

    claude_prompt="/solo:commander-admin-dev develop  开发步骤如下：
- 读取 prd 文档：${prd_file}。
- 读取 prd 对应 ui html 设计稿: ${ui_file}。
- vue 页面开发路径入口：\`src/views${vue_route}.vue\`。
- 功能严格按照设计搞开发页面，不要遗漏功能。
- 开发流程流程严格按照 \`/solo:coder-for-vue\` skill 实现，不要跳过必需的步骤。"

    claude_starter --prompt="${claude_prompt}" "$@"

}

init_prds() {
    claude_setting_dir "$@"

    local workspace=$(claude_workspace "$@")
    local prd_index=""

    # 解析参数：支持 --prd=xxx 和直接路径两种格式

    for arg in "$@"; do
        case "$arg" in
            --prd-index=*)
                prd_index="${arg#--prd-index=}"
                ;;
        esac
    done

    if [ -z "${prd_index}" ]; then
        echo "Error: PRD INDEX path is required, please provide the full path."
        echo "Usage: console.sh init --prd-index=/path/to/prd.md"
        exit 0
    fi
    if [ ! -f "${prd_index}" ]; then
        echo "PRD INDEX not found: ${prd_index}"
        exit 0
    fi

    prd_work_dashborad=$(prd_work_dashborad "$@")

    prd_dir=$(dirname ${prd_index})
    for prd_file in $(ls ${prd_dir}/*.md | grep -v ${prd_index});do
        prd_existing=$(grep "^${prd_file}" "${prd_index}" | wc -l)
        if [ ${prd_existing} -eq 0 ]; then
            [ -s "${prd_index}" ] && [ -n "$(tail -c1 ${prd_index})" ] && echo >> "${prd_index}"
            echo "${prd_file}" >> "${prd_index}"
        fi
    done
    while IFS= read -r line; do
        local prd_file
        local vue_route

        prd_file=$(echo "$line" | awk '{print $1}')
        delimiter=$(echo "$line" | awk '{print $2}')
        vue_route=$(echo "$line" | awk '{print $3}')
        
        if [ ! -f "${prd_file}" ]; then
            echo "PRD file not found: ${prd_file}"
            echo "please correct config ${prd_index} file content. the error prd file is \`${prd_file}\` "
            exit 0
        fi
       
        vue_route=$(grep "^${prd_file}" "${prd_index}" | head -1 | awk -F " -> " '{print $2}')
        prd_existing=$(grep "^${prd_file}" "${prd_work_dashborad}" | wc -l)
        if [ -n "${vue_route}" -a ${prd_existing} -eq 0 ]; then
            [ -s "${prd_work_dashborad}" ] && [ -n "$(tail -c1 ${prd_work_dashborad})" ] && echo >> "${prd_work_dashborad}"
            echo "${prd_file} -> ${vue_route} -> ⚫ 初始化" >> "${prd_work_dashborad}"
        fi
    done < "${prd_index}"

}

prd_draw_ui(){
    claude_setting_dir "$@"
    prd_work_dashborad=$(prd_work_dashborad "$@")

    local prd_file=""
    local commander=""

    # 解析参数：支持 --prd=xxx 和直接路径两种格式
    for arg in "$@"; do
        case "$arg" in
            --prd=*)
                prd_file="${arg#--prd=}"
                ;;
            --commander=*)
                commander="${arg#--commander=}"
                ;;
        esac
    done

    if [ -z "${prd_file}" ]; then
        echo "Error: PRD file path is required, please provide the full path."
        echo "Usage: console.sh ${commander:-\`Unknown\`} --prd=/path/to/prd.md"
        exit 0
    fi
    if [ ! -f "${prd_file}" ]; then
        echo "PRD file not found: ${prd_file}"
        exit 0
    fi

    if [ ! -f "${prd_work_dashborad}" ]; then
        touch "${prd_work_dashborad}"
    fi

    # 如果 prd_work_dashborad 中已有该 prd 的记录，使用已记录的 route，忽略脚本传入的值
    prd_status=$(grep "^${prd_file}" "${prd_work_dashborad}" | head -1 | awk -F " -> " '{print $3}')

    if [ "X ⚫ 初始化 X" != "X ${prd_status} X" ]; then
        echo "prd 文档：${prd_file}，状态不支持开发，当前状态：${prd_status}，请修复为：\`⚫ 初始化\`"
        exit 0
    fi

    vue_route=$(grep "^${prd_file}" "${prd_work_dashborad}" | head -1 | awk -F " -> " '{print $2}')
    if [ -z "${vue_route}" ]; then
        echo "rout not find, please provide the prd vue route."
        exit 0
    fi

    local ui_file="${prd_file//\/prds\///ui/}"
    ui_file="${ui_file/.prd.md/-ui.html}"


    claude_prompt="/solo:commander-admin-dev prd-ui @${prd_file}
开发步骤如下：
- 读取 prd 文档：${prd_file}。
- 开发流程流程严格按照 \`/solo:ui-ux-writer\` skill 实现，不要跳过必需的步骤。
- 生成的静态页路径:${ui_file}"

    claude_starter --prompt="${claude_prompt}" "$@"
}

prd_validator(){
    claude_setting_dir "$@"
    prd_work_dashborad=$(prd_work_dashborad "$@")

    local prd_index=""
    local commander=""

    # 解析参数：支持 --prd=xxx 和直接路径两种格式

    for arg in "$@"; do
        case "$arg" in
            --prd-index=*)
                prd_index="${arg#--prd-index=}"
                ;;
            --commander=*)
                commander="${arg#--commander=}"
                ;;
        esac
    done

    if [ -z "${prd_index}" ]; then
        echo "Error: PRD INDEX path is required, please provide the full path."
        echo "Usage: console.sh init --prd-index=/path/to/prd.md"
        exit 0
    fi
    if [ ! -f "${prd_index}" ]; then
        echo "PRD INDEX not found: ${prd_index}"
        exit 0
    fi

    while IFS= read -r line; do
        local prd_file
        local vue_route

        prd_file=$(echo "${line}" | awk  -F "${delimiter}" '{print $1}')

        if [ ! -f "${prd_file}" ]; then
            echo "PRD file not found: ${prd_file}"
            echo "please correct config ${prd_index} file content. the error prd file is \`${prd_file}\` "
            exit 0
        fi
        
        vue_route=$(echo "${line}" | awk -F "${delimiter}" '{print $2}')
        prd_validate_status=$(echo "${line}" | awk -F "${delimiter}" '{print $3}')

        if [ -n "${vue_route}" -a "🟢 validated" != "${prd_validate_status}" ]; then
            echo "prd: ${prd_file}"
            claude_prompt="/solo:commander-admin-prd validator @${prd_file}"
            claude_starter --prompt="${claude_prompt}" "$@"
            sed -i '' "s#.*${prd_file}.*#${prd_file}${delimiter}${vue_route}${delimiter}🟢 validated#" "${prd_index}"

        fi
    done < "${prd_index}"
}

###########     main     ###########
case "$1" in
    "init")
        shift  # 将第一个参数移除，以便将剩余的参数传递给函数
        init_prds "$@" --commander=init
        ;;
    "prd-ui")
        shift  # 将第一个参数移除，以便将剩余的参数传递给函数
        prd_draw_ui "$@" --commander=prd-ui  
        ;;
    "prd-validator")
        shift  # 将第一个参数移除，以便将剩余的参数传递给函数
        prd_validator "$@" --commander=prd-validator  
        ;;
    "develop-vue") # 开发 vue 页面
        shift  # 将第一个参数移除，以便将剩余的参数传递给函数
        develop_vue "$@" --commander=develop-vue  
        ;;

    *)
        echo "Unknown command: $1"
        exit 1
        ;;
esac

