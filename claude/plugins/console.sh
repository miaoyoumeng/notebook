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

publish_code() {
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

    # cd ${SOURCE_DIR}
    # WORKSPACE_STATUS=$(git status -s)
    # if [ -n "${WORKSPACE_STATUS}" ]; then
    #     echo "git repository has changes. files must \`git commit\`."
    #     echo "please use \`git add [files]...\`"
    #     exit 0
    # fi

    echo "正在将 ${SOURCE_DIR}/marketplaces/miaoyoumeng/ 同步到 ${USER_CLAUDE_PLUGIN_DIR}/marketplaces/miaoyoumeng ..."
    rsync -av --delete \
        "${SOURCE_DIR}/marketplaces/miaoyoumeng/" \
        "${USER_CLAUDE_PLUGIN_DIR}/marketplaces/miaoyoumeng/" \
        --include='.claude-plugin/' \
        --include=".claude-plugin/marketplace.json" \
        --exclude="*"


    echo "正在将 ${SOURCE_DIR}/cache/ 同步到 ${USER_CLAUDE_PLUGIN_DIR}/cache/ ..."
    rsync -av --delete \
        "${SOURCE_DIR}/cache/" \
        "${USER_CLAUDE_PLUGIN_DIR}/cache/"                  \
        --include='miaoyoumeng'  --include='miaoyoumeng/**' \
        --include='__pycache__/' --include='.venv/'         \
        --exclude="*"

}

case "$1" in
    "publish")
        shift  # 将第一个参数移除，以便将剩余的参数传递给函数
        publish_code "$@"
        ;;
    *)
        echo "subcommand: publish "
        exit 1
        ;;
esac

