#!/bin/sh
source /etc/profile

#  installed_plugins.json
#  known_marketplaces.json

USER_CLAUDE_PLUGIN_DIR="${HOME}/.claude/plugins"

# 检查是否提供了 --dir 参数
if [ -z "${USER_CLAUDE_PLUGIN_DIR}" ]; then
    echo "错误：user claude plugin dir。"
    exit 1
fi
# 获取脚本所在目录（例如 /aaa）
SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)

pull_code() {
    # 源目录：脚本目录下的 hooks 子目录
    DEST_DIR="${SCRIPT_DIR}/cache/miaoyoumeng/solo/1.0.0/"

    SOURCE_DIR="/Users/miaoyoumeng/apps/claude/office/solo/"

    if [ ! -d "${DEST_DIR}" ]; then
        echo "错误：目标 cache 目录不存在: ${DEST_DIR}"
        exit 1
    fi

    if [ ! -d "${SOURCE_DIR}" ]; then
        echo "错误：插件源目录不存在: ${SOURCE_DIR}"
        exit 1
    fi
    echo "正在将 ${SOURCE_DIR} 同步 ${DEST_DIR} ..."
    rsync -av --delete "${SOURCE_DIR}" "${DEST_DIR}" \
            --exclude="rsync.sh" \
            --exclude=".DS_Store" \
            --exclude="*__pycache__*" \
            --exclude=".venv" \
            --exclude="uv.lock" \
            --exclude="uv.lock" 

}

push_code() {
    # 源目录：脚本目录下的 hooks 子目录
    SOURCE_DIR="${SCRIPT_DIR}"

    # 检查源目录是否存在
    if [ ! -d "${SOURCE_DIR}/marketplaces/miaoyoumeng" ]; then
        echo "错误：源 marketplaces 目录不存在: ${SOURCE_DIR}/marketplaces/miaoyoumeng"
        exit 1
    fi
    # 检查源目录是否存在
    if [ ! -d "${SOURCE_DIR}/cache/miaoyoumeng" ]; then
        echo "错误：源 cache 目录不存在: ${SOURCE_DIR}/cache/miaoyoumeng"
        exit 1
    fi
    # 检查源目录是否存在

    if [ ! -d "${USER_CLAUDE_PLUGIN_DIR}/marketplaces/miaoyoumeng" ]; then
        echo "错误：marketplaces 目录不存在: ${USER_CLAUDE_PLUGIN_DIR}/marketplaces/miaoyoumeng"
        exit 1
    fi

    if [ ! -d "${USER_CLAUDE_PLUGIN_DIR}/cache/miaoyoumeng" ]; then
        echo "错误：cache 目录不存在: ${USER_CLAUDE_PLUGIN_DIR}/cache/miaoyoumeng"
        exit 1
    fi


    echo "正在将 ${SOURCE_DIR}/marketplaces/miaoyoumeng/ 同步到 ${USER_CLAUDE_PLUGIN_DIR}/marketplaces/miaoyoumeng ..."
    rsync -av --delete \
        "${SOURCE_DIR}/marketplaces/miaoyoumeng/" \
        "${USER_CLAUDE_PLUGIN_DIR}/marketplaces/miaoyoumeng" \
        --exclude="rsync.sh" \
        --exclude=".DS_Store" \
        --exclude="uv.lock" \
        --exclude="*__pycache__*"


    echo "正在将 ${SOURCE_DIR}/cache/miaoyoumeng/ 同步到 ${USER_CLAUDE_PLUGIN_DIR}/cache/miaoyoumeng ..."
    rsync -av --delete \
        "${SOURCE_DIR}/cache/miaoyoumeng/" \
        "${USER_CLAUDE_PLUGIN_DIR}/cache/miaoyoumeng" \
        --exclude="rsync.sh" \
        --exclude=".venv" \
        --exclude="uv.lock" \
        --exclude=".DS_Store" \
        --exclude="*__pycache__*" \
        --exclude=".in_use" \
        --exclude=".orphaned_at"

    for arg in "$@"; do
        case $arg in
            --dir=*)
                DEST_DIR="${arg#*=}"
                shift
                ;;
            *)
                echo "未知参数: $arg"
                exit 1
                ;;
        esac
    done

    # 检查是否提供了 --dir 参数
    if [ "X" != "${DEST_DIR}X" -a  -d "${DEST_DIR}" ]; then
    # if [ -d "${DEST_DIR}" ]; then
        echo "--dir 参数: ${DEST_DIR}"
        echo "用法: $0 --dir=/目标路径"
        rsync -av --delete "${SCRIPT_DIR}/pyproject.toml" "${DEST_DIR}/" 
    #else 
    #    echo "没有有效目录"
    fi
}

case "$1" in
    "pull")
        shift  # 将第一个参数移除，以便将剩余的参数传递给函数
        pull_code "$@"
        ;;
    "push")
        shift  # 将第一个参数移除，以便将剩余的参数传递给函数
        push_code "$@"
        ;;
    "consistency")
        shift  # 将第一个参数移除，以便将剩余的参数传递给函数
        pull_code "$@"
        push_code "$@"
        ;;
    *)
        echo "subcommand: pull or push "
        exit 1
        ;;
esac

