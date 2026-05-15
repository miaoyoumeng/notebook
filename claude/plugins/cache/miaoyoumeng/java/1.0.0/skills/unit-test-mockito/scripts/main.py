#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Java 单元测试生成脚本 (JUnit 4 + Mockito)
使用 claude-agent-sdk 调用 Claude 生成单元测试

操作步骤:
1. 扫描 Maven 项目下的各个模块
2. 逐个模块扫描 Java 文件
3. 为每个 Java 类生成对应的单元测试（枚举类和常量类除外）
"""

import argparse
import asyncio
from config import PROJECT_ROOT_DIR
from testing import java_unit_test
from java import find_java_files, find_maven_modules

# 单个文件单元测试
async def unit_test_file(java_path: str):
    
    await java_unit_test(java_file = java_path)
# 单个 mavan 模块
async def unit_test_module(maven_name: str):

    # 查找 Java 文件
    java_files = find_java_files(maven_name)

    # 逐个生成测试
    for java_path in java_files:
        await java_unit_test(java_file = java_path)

async def unit_test_project():

    # 查找所有模块
    modules = find_maven_modules(PROJECT_ROOT_DIR)

    # 逐个模块处理
    for module in modules:
        java_files = find_java_files(module)
        # print(f"找到 {len(java_files)} 个 Java 源文件")

        # 逐个生成测试
        for java_file in java_files:
            await java_unit_test(java_file = java_file)

async def main():
    parser = argparse.ArgumentParser(description="根据 --scope 决定其他参数")
    parser.add_argument("--scope", required=True, choices=["file", "dir"],
                        help="执行范围: file, module, project")

    # 定义可能的附加参数
    parser.add_argument("--path", type=str, help="当 --scope file 时，需指定该文件路径path")

    args = parser.parse_args()

    # 后置校验逻辑
    if args.scope == "file":
        if not args.path:
            parser.error("--scope file 需要提供 --path 参数")
        await unit_test_file(java_path = args.path)

    elif args.scope == "dir":
        if not args.path:
            parser.error("--scope dir 需要提供 --path 参数")
        # print(f"处理模块: {args.name}")
        await unit_test_module(maven_name = args.path)

if __name__ == '__main__':
    asyncio.run(main())
