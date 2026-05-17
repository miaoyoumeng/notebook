#!/usr/bin/env python3

"""
各种工具函数
"""

import cpca

## 提取最具体的区域
def extract_most_specific_region(location_str):
    # cpca.transform 接收一个列表，返回一个 pandas DataFrame
    df = cpca.transform([location_str], pos_sensitive=True)
    
    # 获取解析结果的第一行
    row = df.iloc[0]
    # print(row)
    # 提取省、市、区三级标准名称
    province = row['省']
    city = row['市']
    district = row['区']
    
    # 根据输入情况，提取最精准的那一级标准名称
    # 如果有区，优先返回区；如果没有区但有市，返回市；以此类推
    if district and district != '':
        return district
    elif city and city != '':
        return city
    elif province and province != '':
        return province
    else:
        return "未知地区"