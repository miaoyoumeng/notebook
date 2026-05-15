#!/bin/sh
source /etc/profile

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
if [ -z "${DEST_DIR}" ]; then
    echo "错误：缺少 --dir 参数。"
    echo "用法: $0 --dir=/目标路径"
    exit 1
fi
# 获取脚本所在目录（例如 /aaa）
SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)

# 源目录：脚本目录下的 hooks 子目录
SOURCE_DIR="${SCRIPT_DIR}/.claude"

# 检查源目录是否存在
if [ ! -d "${SOURCE_DIR}/" ]; then
    echo "错误：源目录不存在: ${SOURCE_DIR}/"
    exit 1
fi
# 检查源目录是否存在
if [ ! -d "${DEST_DIR}/.claude" ]; then
    mkdir ${DEST_DIR}/.claude
fi

# 检查源目录是否存在
if [ ! -d "${DEST_DIR}" ]; then
    echo "错误：目标目录不存在: ${DEST_DIR}"
    exit 1
fi

echo "正在将 ${SOURCE_DIR} 同步到 ${DEST_DIR}/.claude/ ..."
rsync -av "${SOURCE_DIR}/" "${DEST_DIR}/.claude/" --exclude="rsync.sh" --exclude="settings.json"  --exclude=".DS_Store" --exclude="*__pycache__*"

rsync -av --delete "${SCRIPT_DIR}/pyproject.toml" "${DEST_DIR}/" 


