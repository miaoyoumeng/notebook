#!/usr/bin/env python3
#-*- coding:utf-8 -*-

__author__ = 'miaoyoumeng'

import http.client
import json
import argparse

from typing import List, Dict, Optional, Union, Any
from pathlib import Path
from config import get_apifox_token, get_apifox_project_id

def create_http_api(name: str, method: str, path: str, folderId: str, status: str = "developing",
                      responsibleId: str = "0", serverId: str = "", description: str = "",
                      commonParameters: Dict = None, responses: List[Dict] = None, 
                      responseExamples: List[Dict] = None, parameters: Dict = None,
                      requestBody: Dict = None, commonResponseStatus: Dict = None,
                      auth: Dict = None, advancedSettings: Dict = None, 
                      codeSamples: List[Dict] = None, tags: List[str] = None,
                      responseChildren: List[str] = None, customApiFields: Dict = None):
    url = f'/api/v1/api-details'

    access_token = get_apifox_token()
    project_id = get_apifox_project_id()

    authorization = f'Bearer {access_token}'
    project_id = f'{project_id}'

    headers = {
        'Authorization': authorization,
        'X-Apifox-Version': '2023-11-14',
        'X-Apifox-Api-Version': '2024-03-28',
        'X-Project-Id': project_id,
       'Content-Type': 'application/json; charset=utf-8'
    }
    
    payload = {
        'name': name,
        'method': method,
        'path': path,
        'folderId': folderId,
        'status': status,
        'responsibleId': responsibleId,
        'serverId': serverId,
        'description': description,
        'commonParameters': json.dumps(commonParameters or {"query":[],"body":[],"cookie":[],"header":[]}),
        'responses': json.dumps(responses or []),
        'responseExamples': json.dumps(responseExamples or []),
        'type': 'http',
        'parameters': json.dumps(parameters or {}),
        'requestBody': json.dumps(requestBody or {"type":"none","parameters":[]}),
        'commonResponseStatus': json.dumps(commonResponseStatus or {}),
        'auth': json.dumps(auth or {}),
        'advancedSettings': json.dumps(advancedSettings or {}),
        'codeSamples': json.dumps(codeSamples or []),
        'tags': ','.join(tags) if tags else '',
        'responseChildren': json.dumps(responseChildren or []),
        'customApiFields': json.dumps(customApiFields or {})
    }
    

    print("Request URL: %s" % url)
    # print("Headers %s" % json.dumps(headers, indent=2, ensure_ascii=False))
    # print("Request data: %s" % json.dumps(payload, indent=2, ensure_ascii=False))

    conn = http.client.HTTPSConnection("api.apifox.com")
    conn.request("POST", url, json.dumps(payload, indent=2, ensure_ascii=False).encode("utf-8"), headers)
    res = conn.getresponse()
    data = res.read()
    # print(data.decode('utf-8'))

def main():
    parser = argparse.ArgumentParser(description="处理指定目录下的文件")
    parser.add_argument('--dir', type=str, help="指定需要处理的目录路径")
    args = parser.parse_args()

    if not args.dir:
        print("未提供 --dir 参数。 示例：python script/client.py  --dir=a/b")
        exit(0)
    create_http_api(name='apiname', method='POST', path='/apifox/test', folderId='0', status='released', tags=[],
                description='test description', commonParameters={'query': [], 'body': [], 'cookie': [], 'header': []},
                responses=[{'status': 200, 'description': '成功', 'schema': {'type': 'object', 'properties': {'code': {'type': 'integer'}, 'message': {'type': 'string'}}}}],
                responseExamples=[{'status': 200, 'example': {'code': 0, 'message': 'success'}}],
                parameters={'query': [], 'body': [], 'cookie': [], 'header': []},
                requestBody={'type': 'none', 'parameters': []},
                commonResponseStatus={},
                auth={},
                advancedSettings={},
                codeSamples=[],
                responseChildren=[],
                customApiFields={})
    # json_list = read_json(args.dir)
    # for jsonText in json_list:
    #     apifox(jsonText)


if __name__ == '__main__':
    main()