#!/usr/bin/env python3
"""根据路由路径在 src/views/ 下创建 Vue 页面文件及模块 components 目录。

用法:
    uv run python vue-route.py --route=/xxx/yyy/zzz

规则:
    - 路由 /xxx/yyy/zzz → src/views/xxx/yyy/zzz.vue
    - 最后一段作为文件名，前面所有段作为目录
    - 路由以 /index 结尾时例外，使用 index.vue
    - 同时在 src/views/<第一段>/components/ 下创建模块公共组件目录
    - 目录和文件已存在时跳过
"""

import argparse
import os
import sys
from pathlib import Path

VUE_TEMPLATE = """<script setup lang="ts">
import { ref, onMounted } from 'vue'

// TODO: 定义组件 Props
interface Props {
  // title?: string
}

const props = withDefaults(defineProps<Props>(), {
  // count: 0
})

// TODO: 定义组件事件
const emit = defineEmits<{
  // update: [value: string]
}>()

// TODO: 页面状态
const loading = ref(false)

onMounted(() => {
  // TODO: 初始化逻辑
})
</script>

<template>
  <div class="{{ page_name }}-page">
    <!-- TODO: 页面内容 -->
    <h1>{{ page_title }}</h1>
  </div>
</template>

<style scoped lang="scss">
.{{ page_name }}-page {
  // TODO: 页面样式
}
</style>
"""


def parse_route(route: str) -> tuple[list[str], str]:
    """解析路由路径，返回目录部分和文件名。

    Args:
        route: 路由路径，如 /xxx/yyy/zzz 或 /xxx/yyy/index

    Returns:
        (dirs, filename): 目录列表和文件名
    """
    # 去掉前导和末尾的 /
    route = route.strip("/")
    parts = route.split("/")

    if len(parts) < 2:
        raise ValueError(f"路由路径至少需要两级: /{route}，当前只有 {len(parts)} 级")

    # 判断是否以 index 结尾
    if parts[-1] == "index":
        dirs = parts[:-1]
        filename = "index.vue"
    else:
        dirs = parts[:-1]
        filename = f"{parts[-1]}.vue"

    return dirs, filename


def create_vue_page(route: str, base_dir: Path) -> Path:
    """在 base_dir/src/views/ 下根据路由路径创建 Vue 页面。

    Args:
        route: 路由路径
        base_dir: 项目根目录

    Returns:
        创建的 .vue 文件路径
    """
    dirs, filename = parse_route(route)

    views_dir = base_dir / "src" / "views"
    target_dir = views_dir / Path(*dirs) if dirs else views_dir
    target_file = target_dir / filename

    # 创建页面目录
    if target_dir.exists():
        print(f"[跳过] 目录已存在: {target_dir}")
    else:
        target_dir.mkdir(parents=True, exist_ok=True)
        print(f"[创建] 目录: {target_dir}")

    # 创建文件
    if target_file.exists():
        print(f"[跳过] 文件已存在: {target_file}")
    else:
        # 生成模板内容
        page_name = dirs[-1] if dirs else "page"
        page_title = filename.replace(".vue", "")

        template = VUE_TEMPLATE.replace("{{ page_name }}", page_name)
        template = template.replace("{{ page_title }}", page_title)

        target_file.write_text(template, encoding="utf-8")
        print(f"[创建] 文件: {target_file}")

    # 创建模块 components 目录（以路由第一段作为模块名）
    if dirs:
        module_name = dirs[0]
        components_dir = views_dir / module_name / "components"
        if components_dir.exists():
            print(f"[跳过] 组件目录已存在: {components_dir}")
        else:
            components_dir.mkdir(parents=True, exist_ok=True)
            print(f"[创建] 组件目录: {components_dir}")

    return target_file


def main():
    parser = argparse.ArgumentParser(
        description="根据路由路径在 src/views/ 下创建 Vue 页面文件"
    )
    parser.add_argument(
        "--route",
        required=True,
        help="路由路径，例如 /user/today/list",
    )
    parser.add_argument(
        "--base-dir",
        default=".",
        help="项目根目录（默认当前目录）",
    )

    args = parser.parse_args()

    route = args.route
    base_dir = Path(args.base_dir).resolve()

    # 验证路由格式
    if not route.startswith("/"):
        print(f"错误: 路由路径必须以 / 开头: {route}", file=sys.stderr)
        sys.exit(1)

    print(f"项目根目录: {base_dir}")
    print(f"路由路径: {route}")
    print("-" * 40)

    try:
        created_file = create_vue_page(route, base_dir)
        print("-" * 40)
        print(f"完成: {created_file}")
    except ValueError as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
