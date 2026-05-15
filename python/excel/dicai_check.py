#!/usr/bin/env python3
#-*- coding:utf-8 -*-
__author__ = 'miaoyoumeng'

import os
import random
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


def destExcelWriter(columns, sheetName):
    excelFile = "/Users/miaoyoumeng/值.xlsx"
    if os.path.exists(excelFile):
        with pd.ExcelWriter(excelFile, mode='a', engine='openpyxl', if_sheet_exists='replace') as writer:
        # 将过滤后的数据写入新的Sheet
            columns.to_excel(writer, sheet_name=sheetName)
    else: 
        columns.to_excel(excelFile, sheet_name=sheetName, index=False)

def generatorTimeExcelSheet(lines, start_step, vehicles, split_factor, date_time, end_hour = 15):
    up_lines = int(lines * split_factor)
    down_lines = lines - up_lines

    start_time = date_time + timedelta(hours = 5, minutes=40, seconds=33)

    up_middle_time = date_time +  timedelta(hours = 9, minutes = 5, seconds = 45)
    down_middle_time = date_time +  timedelta(hours = 13, minutes = 15, seconds = 7) 

    end_time = date_time +  timedelta(hours = end_hour, minutes = 25, seconds = 17)


    up_time_delta = (up_middle_time - start_time).total_seconds()
    down_time_delta = (end_time - down_middle_time).total_seconds()

    # 空重时间
    up_empty_times = [start_time + timedelta(seconds=random.uniform(0, up_time_delta)) for _ in range(up_lines)]
    down_empty_times = [down_middle_time + timedelta(seconds=random.uniform(0, down_time_delta)) for _ in range(down_lines)]

    empty_times = [*up_empty_times, *down_empty_times]

    empty_times.sort()
    old = empty_times.copy()
    
    # 生成过磅单号（按空重时间排序）
    empty_sorted_indices = sorted(range(len(empty_times)), key=lambda i: empty_times[i])

    empty_sorted_indices[0] = start_step
    start_step = start_step + 1
    for i in range(1, len(empty_times)):
        #生成过磅单号（按空重时间排序）
        empty_sorted_indices[i] = start_step
        step = 1
        if (random.randint(0, 20) < 4):
            if (random.randint(0, 20) < 4):
                step = random.randint(5, 10)
            else:
                step = random.randint(2, 5)

        start_step = start_step + step
        
        # 生成空重时间，需要根据step联动
        if (empty_times[i] - empty_times[i - 1]).total_seconds() < 2.5 * 60 :
            if (empty_times[i] - empty_times[i - 1]).total_seconds() < 0 :
                empty_times[i] = empty_times[i - 1] 
            empty_times[i] = empty_times[i] + timedelta(seconds= step * random.uniform(2.8, 8) * 60 + random.randint(0, 60))

        

    # for i in range(1, len(empty_times)):
    #     if (empty_times[i] - empty_times[i - 1]).total_seconds() < 5 * 60 :
    #         print(str(empty_times[i]) + '  ' + str((empty_times[i] - empty_times[i - 1]).total_seconds() ))
    
    df = pd.DataFrame({'原始时间':old, '空重时间': empty_times})

    np.random.seed(42)  # 可选：为了结果可复现

    seconds_offset = np.random.randint(6 * 30 + random.randint(0, 60), 11 * 60 + random.randint(0, 60), size=len(df))  # 生成 6~40 的随机整数
    
    df['毛重时间'] = df['空重时间'] + pd.to_timedelta(seconds_offset, unit='s')
    df['等待时间'] = seconds_offset

        
    date_time_format = date_time.strftime("%Y%m%d")
    ticket_numbers = [f"A{str(date_time_format)}{str(i).zfill(4)}" for i in empty_sorted_indices]

    df['过磅单号'] = ticket_numbers

    sorted_values = df.sort_values(by='毛重时间')

    vehicles_result = []
    while len(vehicles_result) < lines:
        # 复制原始数组并打乱
        temp_vehicles = vehicles.copy()
        random.shuffle(temp_vehicles)
        
        # 计算还需要多少元素
        remaining = lines - len(vehicles_result)
    
        # 如果剩余数量小于等于一次打乱的数量，则只取所需数量
        if remaining <= len(temp_vehicles):
            vehicles_result.extend(temp_vehicles[:remaining])
        else:
            # 否则，将整个打乱后的数组加入结果
            vehicles_result.extend(temp_vehicles)

    # print(vehicles_result)
    sorted_values['运输车号'] = vehicles_result

    print(sorted_values)
    new_order = ['原始时间', '毛重时间', '空重时间', '等待时间', '过磅单号', '运输车号']
    sorted_values = sorted_values[new_order]
    # 保存为 Excel 文件
    destExcelWriter(sorted_values, str(date_time_format))

def generatorWeightExcelSheet(lines, target_weight):
    net_weights = []
    while abs(sum(net_weights) - target_weight) > 0.1 or len(net_weights) < lines:
        if len(net_weights) >= lines:
            net_weights = []
        net_weights = [round(random.uniform(45, 58), 2) for _ in range(lines)]
    print(sum(net_weights))

if __name__ == '__main__':

    generatorWeightExcelSheet(114, 5894.92)

    # generatorTimeExcelSheet(lines = 108, start_step = 68, vehicles = [207,210,2306,323,434,585,595,7382,7435,8838,9938], 
    #     split_factor = 0.43, date_time = datetime(2025, 2, 10))

    # generatorTimeExcelSheet(lines = 116, start_step = 2, vehicles = [207,210,2306,323,434,585,595,609,657,7382,7435,814,9938], 
    #     split_factor = 0.47, date_time = datetime(2025, 2, 11))

    # generatorTimeExcelSheet(lines = 116, start_step = 2, vehicles = [210,2306,323,434,585,595,609,657,7382,7435,814,8838,9938], 
    #     split_factor = 0.47, date_time = datetime(2025, 2, 12))

    # generatorTimeExcelSheet(lines = 113, start_step = 4, vehicles = [207,2306,323,434,595,609,7435,814,9938], 
    #     split_factor = 0.63, date_time = datetime(2025, 2, 13))

    
    