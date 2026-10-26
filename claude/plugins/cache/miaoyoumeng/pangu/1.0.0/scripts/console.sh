#!/bin/bash

## ⚫ 🟠  🟣  🟡  🟢  🟤  🔴  🔵  ⚪  

# "⚫ inited"
# "🟠 validated"
# "🟣 drawed"

SOURCE_CODE_DIR=$(cd "$(dirname "$0")" && pwd)
delimiter=" -> "

status_init="⚫ inited"
status_validated="🟠 validated"
status_drawed="🟣 drawed"

claude_workspace() {
    local workspace=""
    local commander=""
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
    local claude_setting_dir=${workspace}/.claude
    if [ ! -d "${claude_setting_dir}" ]; then
        echo "Error: claude  dir \`${workspace}/.claude\` is required, please provide the correct claude workspace."
        exit 0
    fi
    echo "${claude_setting_dir}"
}

prd_work_dashborad() {
    local workspace=$(claude_workspace "$@")
    local prd_work_dashborad=${workspace}/.claude/prd-route-mapping.log
    
    echo ${prd_work_dashborad}
}

prd_index_args() {
    local prd_index=""

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
        echo "Usage: console.sh ${commander} --prd-index=/path/to/prd.md"
        exit 0
    fi
    if [ ! -f "${prd_index}" ]; then
        echo "PRD INDEX not found: ${prd_index}"
        exit 0
    fi
    echo "${prd_index}"

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
init_prds() {
    claude_setting_dir "$@"

    local prd_index=$(prd_index_args "$@")
    local prd_work_dashborad=$(prd_work_dashborad "$@")

    local prd_dir=$(dirname ${prd_index})
    for prd_file in $(ls ${prd_dir}/*.md | grep -v ${prd_index});do
        prd_existing=$(grep "^${prd_file}" "${prd_index}" | wc -l)
        if [ ${prd_existing} -eq 0 ]; then
            [ -s "${prd_index}" ] && [ -n "$(tail -c1 ${prd_index})" ] && echo >> "${prd_index}"
            echo "${prd_file}" >> "${prd_index}"
        fi
    done
    while IFS= read -r line; do
        if [  -z "${line}" ]; then
            continue
        fi

        local prd_file=$(echo "$line" | awk -F "${delimiter}" '{print $1}')
        local vue_route=$(echo "$line" | awk -F "${delimiter}" '{print $2}')
        
        if [  -n "${prd_file}" ] && [ ! -f "${prd_file}" ]; then
            echo "PRD file not found: ${prd_file}"
            echo "please correct config ${prd_index} file content. the error prd file is \`${prd_file}\` "
            exit 0
        fi
        
        if [  -z "${vue_route}" ]; then
            continue
        fi
        
        local exits_prd=$(grep "^${prd_file}${delimiter}" "${prd_work_dashborad}")
        local prd_status=$(echo "$exits_prd" | awk -F "${delimiter}" '{print $3}')
        if [ -n "${exits_prd}" ] && [ -z "${prd_status}" ]; then
            [ -s "${prd_work_dashborad}" ] && [ -n "$(tail -c1 ${prd_work_dashborad})" ] && echo >> "${prd_work_dashborad}"
            sed -i '' "s#.*${prd_file}${delimiter}.*#${prd_file}${delimiter}${vue_route}${delimiter}${status_init}#" "${prd_work_dashborad}"
        fi
    done < "${prd_index}"

}
prd_validator(){
    claude_setting_dir "$@"

    local prd_index=$(prd_index_args "$@")

    local prd_work_dashborad=$(prd_work_dashborad "$@")

    local prd_dir=$(dirname ${prd_index})

    local claude_prompt="/solo:commander-admin-prd validator 
# 角色设定

你是一位严苛的 B 端后台产品专家，擅长微服务/电商后台架构。请对指定的 PRD 文档进行深度质量审计。

# 审计范围（严格执行）

- 目标目录：\`${prd_dir}\`
- 排除项：\`index.md\`
- 必审清单（仅审计以下内容，其他文件跳过）："
    local prd_paths=""
    while IFS= read -r line; do
        local prd_file=$(echo "${line}" | awk  -F "${delimiter}" '{print $1}')
        if [ -n "${prd_file}" -a ! -f "${prd_file}" ]; then
            echo "PRD file not found: ${prd_file}"
            exit 0
        fi
        
        local vue_route=$(echo "${line}" | awk -F "${delimiter}" '{print $2}')
        prd_validate_status=$(echo "${line}" | awk -F "${delimiter}" '{print $3}')

        if [ -n "${vue_route}" -a "${status_init}" = "${prd_validate_status}" ]; then
            prd_paths=$(echo "${prd_paths}
${prd_file}")
        fi
    done < "${prd_work_dashborad}"

    while IFS= read -r line; do
        if [ -n "${line}" ];then
            claude_prompt=$(echo "${claude_prompt}
  - ${line}")
        fi
    done <<< "$prd_paths" 

    claude_starter --prompt="${claude_prompt}" "$@"

    while IFS= read -r prd_file; do
        if [ -n "${prd_file}" ];then
            sed -i '' "s#.*${prd_file}.*#${prd_file}${delimiter}${vue_route}${delimiter}${status_validated}#" "${prd_work_dashborad}"
        fi
    done <<< "$prd_paths" 
}

prd_definition(){
    claude_setting_dir "$@"

    local prd_index=$(prd_index_args "$@")

    local prd_work_dashborad=$(prd_work_dashborad "$@")

    local prd_dir=$(dirname ${prd_index})

    local claude_prompt="调用 Skill \`/solo:prd-concept\`
# 角色设定

你是一位严谨的 B 端后台产品架构师，擅长领域建模与数据字典管理。请对指定的 PRD 文档集合进行深度知识抽取，构建结构化、无冗余的业务知识库。
整理出\`字典库\`，\`概念库\`，\`指标库\`。

# 分析范围（严格执行）

- 目标目录：\`${prd_dir}\`
- 排除项：\`index.md\`
- 分析清单（仅分析以下内容，其他文件跳过）："
    local prd_paths=""
    while IFS= read -r line; do
        local prd_file=$(echo "${line}" | awk  -F "${delimiter}" '{print $1}')
        if [ -n "${prd_file}" -a ! -f "${prd_file}" ]; then
            echo "PRD file not found: ${prd_file}"
            exit 0
        fi
        
        local vue_route=$(echo "${line}" | awk -F "${delimiter}" '{print $2}')
        prd_validate_status=$(echo "${line}" | awk -F "${delimiter}" '{print $3}')

        if [ -n "${vue_route}" -a "${status_validated}" = "${prd_validate_status}" ]; then
            prd_paths=$(echo "${prd_paths}
${prd_file}")
        fi
    done < "${prd_work_dashborad}"

    while IFS= read -r line; do
        if [ -n "${line}" ];then
            claude_prompt=$(echo "${claude_prompt}
  - ${line}")
        fi
    done <<< "$prd_paths" 
    claude_prompt=$(echo "${claude_prompt}

# 三大知识库定义（明确抽取边界）

## 1. 字典库
> 定义：所有**枚举值、状态码、类型标签**及其业务含义的映射关系。
- **抽取对象**：字段的可选值集合，如会员等级（普通/银卡/金卡/钻石）、支付渠道（微信/支付宝/银行卡）等。
- 调用 Skill \`/solo:prd-concept\` 解析出\`字典\`，去重保存在\`[当前工作目录]/prds/dicts.md\`。

## 2. 概念库
> 定义：业务实体的**核心定义、属性构成、关联关系**。
- **抽取对象**：名词性业务概念及其关键属性，如\"会员\"（包含等级、积分、注册时间、绑定手机）、\"订单\"（包含订单号、金额、状态、支付时间）。
- 调用 Skill \`/solo:prd-concept\` 解析出\`概念\`，去重保存在\`[当前工作目录]/prds/concepts.md\`

## 3. 指标库
> 定义：所有**统计指标的计算口径、统计维度、数据来源**。
- **抽取对象**：数值型业务指标，如\"今日用户数\"（统计口径：当日注册/当日活跃？去重规则？）、\"对账差异率\"（计算公式）、"确收金额"（确认收入的会计口径）。
- 调用 Skill \`/solo:prd-concept\` 解析出\`指标\`，去重保存在\`[当前工作目录]/prds/metrics.md\`

# 执行约束
- **去重合并**：同一字典/概念/指标若在多个 PRD 中出现，以**定义最完整**的版本为准，并在\"来源文档\"中列出所有引用文件。
- **冲突检测**：若发现同一概念在不同 PRD 中定义矛盾（如"会员等级"在 A 文档为 3 级，在 B 文档为 5 级），必须在报告中以 **⚠️ 冲突警告** 单独列出。
- **严谨兜底**：若某文件读取失败或内容为空，标记为"读取异常"，禁止脑补内容。

---
# 质量红线

- ❌ 禁止将流程描述（如\"点击按钮跳转\"）混入概念库。
- ❌ 禁止将 UI 文案（如\"确认删除弹窗\"）作为字典值。
- ✅ 指标库必须包含**明确的计算公式或统计口径**，禁止仅写\"统计订单数据\"等模糊描述。
- ✅ 若某 PRD 中无任何可抽取内容，须如实记录"无可抽取内容"，而非留空。

# 自修复

- 如果发现概念冲突，则调用 Skill \`/solo:prd-writer\`  按照推荐方案直接修复对应的 prd 文档。
- 修复后重新执行当前命令，最多循环2次。
")

    # echo "${claude_prompt}"
    claude_starter --prompt="${claude_prompt}" "$@"

    # while IFS= read -r prd_file; do
    #     if [ -n "${prd_file}" ];then
    #         sed -i '' "s#.*${prd_file}.*#${prd_file}${delimiter}${vue_route}${delimiter}${status_validated}#" "${prd_work_dashborad}"
    #     fi
    # done <<< "$prd_paths" 
}

prd_draw_ui(){
    claude_setting_dir "$@"

    local prd_index=$(prd_index_args "$@")

    local prd_work_dashborad=$(prd_work_dashborad "$@")

    while IFS= read -r line; do
        if [  -z "${line}" ]; then
            continue
        fi

        local prd_file=$(echo "$line" | awk -F "${delimiter}" '{print $1}')
        local vue_route=$(echo "$line" | awk -F "${delimiter}" '{print $2}')

        # 如果 prd_work_dashborad 中已有该 prd 的记录，使用已记录的 route，忽略脚本传入的值
        local prd_status=$(grep "^${prd_file}" "${prd_work_dashborad}" | head -1 | awk -F "${delimiter}" '{print $3}')
        echo "X ${prd_status} X, X ${status_validated} X"

        if [ "X ${status_validated} X" != "X ${prd_status} X" ]; then
            continue
        fi

        vue_route=$(grep "^${prd_file}" "${prd_work_dashborad}" | head -1 | awk -F "${delimiter}" '{print $2}')
        if [ -z "${vue_route}" ]; then
            echo "rout not find, please provide the prd vue route."
            exit 0
        fi

        local ui_file_tmp="${prd_file//\/prds\///ui/}"
        local ui_file="${ui_file_tmp/.prd.md/-ui.html}"

        local claude_prompt="/solo:commander-admin-dev prd-ui
# 核心任务

你是一位精通 B 端后台管理系统的 UI 开发专家。请依据指定 PRD 文档，生成一个**高保真、可交互**的静态管理后台页面
# 强制执行流程（严格按序，不可跳过）
请将 \`/solo:ui-ux-writer\` 隐含的完整工作流显式执行如下：

1. **语义解析**：深度阅读 PRD，提取页面核心实体（如：会员）、关键字段（昵称、手机号、等级、状态等）、必填/可选约束、以及所有操作按钮（增删改查、导出、批量操作）。
2. **布局推演**：采用标准的后台管理布局（顶部搜索筛选区 + 左侧功能操作栏 + 中间数据表格 + 底部分页器），确保信息层级清晰。
3. **组件化编码**：使用纯 HTML5 + CSS3 + 原生 JavaScript（ES6）编码，模拟 tdesign UI 的视觉风格（圆角按钮、多色标签、清爽间距）。
4. **交互逻辑实现**：必须包含以下 JS 功能：
   - 搜索/重置（前端过滤模拟）；
   - 表格全选/取消全选；
   - 状态切换（如启用/禁用）的弹窗确认模拟；
   - 分页点击切换（展示当前页数据）。
5. **保存输出**：将最终完整代码写入指定的 \`.html\` 文件路径。

# 输入与输出路径

- **输入 PRD**：\`${prd_file}\`
- **输出文件**：\`${ui_file}\`

# 视觉与质量红线（必须达标）

- **字段映射**：表格每一列的字段名、顺序必须与 PRD 中的列表字段描述严格一致。
- **状态可视化**：所有状态字段（如等级、审核状态）必须使用不同颜色的 \`Tag\` 标签展示，禁止仅用文字。
- **响应式交互**：按钮需有 \`hover\`/\`active\` 状态；表单输入框需有 \`focus\` 高亮。
- **代码洁癖**：HTML、CSS、JS 必须分离书写（或清晰分段），并添加必要的注释说明。
- **兜底状态**：若 PRD 中描述的操作按钮（如“导出”、“详情”）无具体逻辑，必须在按钮上绑定 \`alert\` 占位提示，不得点击无效。
"

        claude_starter --prompt="${claude_prompt}" "$@"
        # echo "==${prd_file}${delimiter}${vue_route}${delimiter}${status_drawed}===="
        sed -i '' "s#.*${prd_file}.*#${prd_file}${delimiter}${vue_route}${delimiter}${status_drawed}#" "${prd_work_dashborad}"
    done < "${prd_work_dashborad}"

    
}

develop_vue() {
    claude_setting_dir "$@"

    local prd_index=$(prd_index_args "$@")

    local prd_work_dashborad=$(prd_work_dashborad "$@")

    while IFS= read -r line; do
        if [  -z "${line}" ]; then
            continue
        fi
        local prd_file=$(echo "$line" | awk -F "${delimiter}" '{print $1}')
        

        # 如果 prd_work_dashborad 中已有该 prd 的记录，使用已记录的 route，忽略脚本传入的值
        local prd_status=$(grep "^${prd_file}" "${prd_work_dashborad}" | head -1 | awk -F "${delimiter}" '{print $3}')

        if [ "X ${status_drawed} X" != "X ${prd_status} X" ]; then
            continue
        fi

        local vue_route=$(echo "$line" | awk -F "${delimiter}" '{print $2}')
        if [ -z "${vue_route}" ]; then
            echo "rout not find, please provide the prd vue route."
            exit 0
        fi
        # local ui_filexxx="${${prd_file//\/prds\///ui/}}"
        # echo "========${ui_filexxx}"
        local ui_file_tmp="${prd_file//\/prds\///ui/}"
        local ui_file="${ui_file_tmp/.prd.md/-ui.html}"

        if [ ! -f "${ui_file}" ]; then
            echo "UI html file not found: ${ui_file}"
            exit 0
        fi

        claude_prompt="/solo:commander-admin-dev develop  
# 核心任务

你是一位精通 Vue 3 后台开发的高级前端工程师。请依据 PRD 业务逻辑，将静态 UI 设计稿 **“原样还原”** 为动态 Vue 页面，并确保交互功能完整无遗漏。

# 技术栈与编码规范（强制执行）

- **框架版本**：Vue 3 (Composition API，使用 \`<script setup>\` 语法糖)。
- **UI 组件库**：TDesign Vue Next（\`tdesign-vue-next\`）。若设计稿中存在自定义样式，需通过 \`:deep()\` 或组件内置属性（如 \`style\` / \`class\`）覆盖默认样式以 1:1 匹配设计稿。
- **全局组件引入**：默认已全局注册 TDesign 组件。
- **网络请求**：接口数据需定义清晰的 \`reactive\` 或 \`ref\` 数据模型。
- **代码风格**：\`<template>\`、\`<script setup>\`、\`<style scoped>\` 三部分严格分离，样式必须添加 \`scoped\` 防止污染

# 输入文件（硬性约束）
- **PRD 业务文档**：\`${prd_file}\`
  - *用途*：提取字段校验规则（必填/格式）、状态流转逻辑（如审核通过/驳回）、操作权限点、以及页面各模块的业务说明。
- **静态 UI 设计稿**：\`${ui_file}\`
  - *用途*：作为页面布局、视觉样式（间距、颜色、圆角）、元素层级（表格列、表单分组、弹窗结构）的唯一视觉标准。
- **vue 页面开发路径入口**：\`src/views${vue_route}.vue\`。
"

        claude_starter --prompt="${claude_prompt}" "$@"
    done < "${prd_index}"
}

###########     main     ###########
case "$1" in
    "init")
        shift  # 将第一个参数移除，以便将剩余的参数传递给函数
        init_prds "$@" --commander=init
        ;;
    "prd-validator")
        shift  # 将第一个参数移除，以便将剩余的参数传递给函数
        prd_validator "$@" --commander=prd-validator
        ;;
    "prd-def")
        shift  # 将第一个参数移除，以便将剩余的参数传递给函数
        prd_definition "$@" --commander=prd-def
        ;;
    "prd-ui")
        shift  # 将第一个参数移除，以便将剩余的参数传递给函数
        prd_draw_ui "$@" --commander=prd-ui
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

