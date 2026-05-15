#!/usr/bin/env python3
#-*- coding:utf-8 -*-

__author__ = 'miaoyoumeng'

import os
import tomli

def get_apifox_config():
    try:
        import tomllib
    except ImportError:
        try:
            import tomli as tomllib
        except ImportError:
            print("请安装 tomli 库：pip install tomli")
            sys.exit(1)
    # 扩展 ~ 为用户主目录
    config_path = os.path.expanduser("~/.apifox/config.toml")
    try:
        with open(config_path, "rb") as f:
            config = tomllib.load(f)
        # 根据文件结构，access_token 位于 [default] 节下
        access_token = config.get("default", {}).get("access_token")
        project_id = config.get("default", {}).get("project_id")

        return access_token, project_id
    except FileNotFoundError:
        print(f"错误：配置文件不存在 - {config_path}")
        exit(1)
    except tomllib.TOMLDecodeError as e:
        print(f"错误：TOML 解析失败 - {e}")
        exit(1)
    except Exception as e:
        print(f"意外错误：{e}")
        exit(1)
    exit(1)


def get_apifox_token() -> str:
    access_token, _ = get_apifox_config()
    return access_token

def get_apifox_project_id() -> str:
    _, project_id = get_apifox_config()
    return project_id