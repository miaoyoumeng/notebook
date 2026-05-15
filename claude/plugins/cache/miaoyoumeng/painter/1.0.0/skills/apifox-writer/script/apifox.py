#!/usr/bin/env python3
#-*- coding:utf-8 -*-

__author__ = 'miaoyoumeng'

import http.client
import json
import argparse
import os

from pathlib import Path

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

def main():
    parser = argparse.ArgumentParser(description="处理指定目录下的文件")
    parser.add_argument('--dir', type=str, help="指定需要处理的目录路径")
    args = parser.parse_args()

    if not args.dir:
        print("未提供 --dir 参数。 示例：python script/apifox.py  --dir=a/b")
        exit(0)
    json_list = read_json(args.dir)
    for jsonText in json_list:
        apifox(jsonText)
def remove_tags_recursive(obj):
    """递归删除所有字典中的 'tags' 键"""
    if isinstance(obj, dict):
        obj.pop('tags', None)          # 删除当前层级的 tags
        for v in obj.values():
            remove_tags_recursive(v)   # 递归处理值
    elif isinstance(obj, list):
        for item in obj:
            remove_tags_recursive(item)

def read_json(json_dir: str):
    data_list = []
    # 检查目录是否存在

    if not os.path.exists(json_dir):
        print(f"目录 '{json_dir}' 不存在")
        return data_list
    path = Path(json_dir)
    for filename in path.glob('**/*.swagger.json'):
        # 筛选以 .json 结尾的文件
        file_path = os.path.join(json_dir, filename)
        try:
            # 使用 utf-8 编码打开并读取 JSON 文件
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                remove_tags_recursive(data)
                data_list.append(data)
                print(f"✅ 成功读取: {filename}")
        except json.JSONDecodeError as e:
            print(f"❌ JSON 格式错误 '{filename}': {e}")
        except Exception as e:
            print(f"❌ 读取文件出错 '{filename}': {e}")
    return data_list

def apifox(jsonText: str):
    access_token, project_id = get_apifox_config()
    conn = http.client.HTTPSConnection("api.apifox.com")
    payload = json.dumps({
            "input": str(jsonText),
            "options": {
                "targetEndpointFolderId": 0,
                "targetSchemaFolderId": 0,
                "endpointOverwriteBehavior": "OVERWRITE_EXISTING",
                "schemaOverwriteBehavior": "OVERWRITE_EXISTING",
                "updateFolderOfChangedEndpoint": False,
                "prependBasePath": False
            }
        }, indent=4, ensure_ascii=False).encode("utf-8")

    headers = {
       'X-Apifox-Api-Version': '2024-03-28',
       'Authorization': f"Bearer {access_token}",
       'Content-Type': 'application/json; charset=utf-8'
    }
    apifox_url = f"/v1/projects/{project_id}/import-openapi?locale=zh-CN"
        
    conn.request("POST", apifox_url, payload, headers)
    res = conn.getresponse()
    data = res.read()
    print(data.decode('utf-8'))

if __name__ == '__main__':
    main()