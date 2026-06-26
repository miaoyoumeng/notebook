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
rsync -av --delete "${SOURCE_DIR}/marketplaces/miaoyoumeng/" "${USER_CLAUDE_PLUGIN_DIR}/marketplaces/miaoyoumeng" --exclude="rsync.sh" --exclude=".DS_Store" --exclude="*__pycache__*"


echo "正在将 ${SOURCE_DIR}/cache/miaoyoumeng/ 同步到 ${USER_CLAUDE_PLUGIN_DIR}/cache/miaoyoumeng ..."
rsync -av --delete "${SOURCE_DIR}/cache/miaoyoumeng/" "${USER_CLAUDE_PLUGIN_DIR}/cache/miaoyoumeng" --exclude="rsync.sh" --exclude=".venv" --exclude=".DS_Store" --exclude="*__pycache__*" --exclude=".in_use" --exclude=".orphaned_at"

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


