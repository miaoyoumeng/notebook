#!/usr/bin/env python3
#-*- coding:utf-8 -*-
__author__ = 'miaoyoumeng'


import os
import PIL.Image as PImage
import sys
from PIL import Image, ImageDraw, ImageFont
import cv2
import numpy as np
import pandas as pd

def fontSize(font_size = 5):
    if getattr(sys, 'frozen', None):
        base_dir = os.path.join(sys._MEIPASS, 'fonts')
    else:
        base_dir = os.path.join(os.path.dirname(__file__), 'fonts')
    try:
        font = ImageFont.truetype(os.path.join(base_dir, "hei.ttf"), size=mm_2_pixel(font_size)) 
    except IOError:
        print("字体文件加载失败，请检查字体文件路径")
        font = ImageFont.load_default()
    return font   

# 将mm转换为像素
def mm_2_pixel(mm):
    return int(mm * 11.811 * 3) # 300 DPI

# 填充表格记录
def fillTableRecord(draw = None, text = "", top_margin = 0,  left_margin = 0, font = None):
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    position_y = top_margin + text_height / 2
    position_x = left_margin - text_width / 2
    position = (position_x, position_y)
    draw.text(position, text, fill="black", font=font)

# 图片背景
def drawTable(draw = None, width = 0, table_width = 180, 
        truck_no = "", weight_no = "0",
        gross_weight = 0, empty_weight = 0, real_weight = 0,
        gross_date_time = "", empty_date_time = "",
        table_height = 56, top_margin = 25):

    left_margin_px = (width - table_width) / 2 # 居中显示

    # 计算每行和每列的大小
    num_rows = 7
    num_cols = 4
    row_height_px = table_height / num_rows
    col_width_px = table_width / num_cols

    table_line_width = 8
    # 绘制表格
    for i in range(num_rows + 1):
        y = top_margin + i * row_height_px
        draw.line([(left_margin_px, y), (left_margin_px + table_width, y)], fill="black", width=table_line_width)

    # 第一根竖线
    x = left_margin_px
    draw.line([(x, top_margin), (x, top_margin + table_height)], fill="black", width=table_line_width)

    # 第二根竖线
    col_1_width = mm_2_pixel(30)
    x = x  + col_1_width
    draw.line([(x, top_margin), (x, top_margin + table_height)], fill="black", width=table_line_width)
    
    # 第三根竖线
    col_2_width = mm_2_pixel(80)
    x = x  + col_2_width
    draw.line([(x, top_margin), (x, top_margin + table_height)], fill="black", width=table_line_width)
    
    # 第四根竖线
    col_3_width = mm_2_pixel(25)
    x = x  + col_3_width
    draw.line([(x, top_margin), (x, top_margin + table_height)], fill="black", width=table_line_width)
    
    # 第五根竖线
    col_4_width = mm_2_pixel(45)
    x = x  + col_4_width
    draw.line([(x, top_margin), (x, top_margin + table_height)], fill="black", width=table_line_width)

    # 添加表格内容
    table_record_font = fontSize(4)
    
    # 添加表格第一列文案
    x = left_margin_px
    left_margin = x + col_1_width / 2

    fillTableRecord(draw = draw, text = "车       号", top_margin = top_margin + 0 * row_height_px, left_margin = left_margin, font = table_record_font)
    fillTableRecord(draw = draw, text =  "项 目 名 称", top_margin = top_margin + 1 * row_height_px, left_margin = left_margin, font = table_record_font)
    fillTableRecord(draw = draw, text = "货       名", top_margin = top_margin + 2 * row_height_px, left_margin = left_margin, font = table_record_font)
    fillTableRecord(draw = draw, text = "收 货 单 位", top_margin = top_margin + 3 * row_height_px, left_margin = left_margin, font = table_record_font)
    fillTableRecord(draw = draw, text = "收 货 位 置", top_margin = top_margin + 4 * row_height_px, left_margin = left_margin, font = table_record_font)
    fillTableRecord(draw = draw, text = "施 工 部 位", top_margin = top_margin + 5 * row_height_px, left_margin = left_margin, font = table_record_font)
    fillTableRecord(draw = draw, text =  "备       注", top_margin = top_margin + 6 * row_height_px, left_margin = left_margin, font = table_record_font)
   
    # 添加表格第二列文案
    x = x + col_1_width
    left_margin = x + col_2_width / 2

    fillTableRecord(draw = draw, text = truck_no, top_margin = top_margin + 0 * row_height_px, left_margin = left_margin, font = table_record_font)
    fillTableRecord(draw = draw, text = "石铁院新校区二区三标", top_margin = top_margin + 1 * row_height_px, left_margin = left_margin, font = table_record_font)
    fillTableRecord(draw = draw, text = "级配碎石", top_margin = top_margin + 2 * row_height_px, left_margin = left_margin, font = table_record_font)
    fillTableRecord(draw = draw, text = "中铁十六局集团有限公司", top_margin = top_margin + 3 * row_height_px, left_margin = left_margin, font = table_record_font)
    fillTableRecord(draw = draw, text = "铁路职业技术学院（灵寿校区）", top_margin = top_margin + 4 * row_height_px, left_margin = left_margin, font = table_record_font)
    fillTableRecord(draw = draw, text = "地基回填", top_margin = top_margin + 5 * row_height_px, left_margin = left_margin, font = table_record_font)
    fillTableRecord(draw = draw, text = "", top_margin = top_margin + 6 * row_height_px, left_margin = left_margin, font = table_record_font)

    # 添加表格第三列文案
    x = x + col_2_width
    left_margin = x + col_3_width / 2

    fillTableRecord(draw = draw, text = "毛    重", top_margin = top_margin + 0 * row_height_px, left_margin = left_margin, font = table_record_font)
    fillTableRecord(draw = draw, text = "空    重", top_margin = top_margin + 1 * row_height_px, left_margin = left_margin, font = table_record_font)
    fillTableRecord(draw = draw, text = "净    重", top_margin = top_margin + 2 * row_height_px, left_margin = left_margin, font = table_record_font)
    fillTableRecord(draw = draw, text = "毛重时间", top_margin = top_margin + 3 * row_height_px, left_margin = left_margin, font = table_record_font)
    fillTableRecord(draw = draw, text = "空重时间", top_margin = top_margin + 4 * row_height_px, left_margin = left_margin, font = table_record_font)
    fillTableRecord(draw = draw, text = "累计次数", top_margin = top_margin + 5 * row_height_px, left_margin = left_margin, font = table_record_font)
    fillTableRecord(draw = draw, text = "收 货 人", top_margin = top_margin + 6 * row_height_px, left_margin = left_margin, font = table_record_font)

    # 添加表格第四列文案
    x = x + col_3_width
    left_margin = x + col_4_width / 2
    
    fillTableRecord(draw = draw, text = gross_weight, top_margin = top_margin + 0 * row_height_px, left_margin = left_margin, font = table_record_font)
    fillTableRecord(draw = draw, text = empty_weight, top_margin = top_margin + 1 * row_height_px, left_margin = left_margin, font = table_record_font)
    fillTableRecord(draw = draw, text = real_weight, top_margin = top_margin + 2 * row_height_px, left_margin = left_margin, font = table_record_font)
    fillTableRecord(draw = draw, text = gross_date_time, top_margin = top_margin + 3 * row_height_px, left_margin = left_margin, font = table_record_font)
    fillTableRecord(draw = draw, text = empty_date_time, top_margin = top_margin + 4 * row_height_px, left_margin = left_margin, font = table_record_font)
    fillTableRecord(draw = draw, text = weight_no, top_margin = top_margin + 5 * row_height_px, left_margin = left_margin, font = table_record_font)
    fillTableRecord(draw = draw, text = "", top_margin = top_margin + 6 * row_height_px, left_margin = left_margin, font = table_record_font)

def drawMiddleText(draw = None, text = "", x = 0, y = 0, font = None) :
    # 使用textbbox代替textsize
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    position = ((x - text_width) / 2, (y - text_height) / 2) 
    draw.text(position, text, fill = "black", font = font)

def drawLeftText(draw = None, text = "", x = 0, y = 0, font = None) :
    # 使用textbbox代替textsize
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    position = (x, (y - text_height) / 2)
    draw.text(position, text, fill = "black", font = font)


def drawRightText(draw = None, text = "", x = 0, y = 0, font = None) :
    # 使用textbbox代替textsize
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    position = (x - text_width, (y - text_height) / 2)
    draw.text(position, text, fill = "black", font = font)

def drawTitle(draw = None, text = "", width = 0, margin_top = 0 ):
    # # 加载字体文件，这里假设有一个宋体字体文件simsun.ttc
    font = fontSize(7)
    drawMiddleText(draw = draw, text = text, x = width, y = margin_top, font = font)

def drawSubTitle(draw = None, date_text = "", mark_text = "", width = 0, table_width = 0, margin_top = 0):
    font = fontSize(5)

    left_margin_px = int((width - table_width) / 2)
    drawLeftText(draw = draw, text = "日期: " + date_text, x = left_margin_px, y = margin_top, font = font)
    
    # 添加单号
    mark_text = "单号: " + mark_text
    drawMiddleText(draw = draw, text = mark_text, x = width, y = margin_top, font = font)

    # 添加备注
    mark_text = "计量单位 吨"
    right_margin_px = int(table_width + (width - table_width) / 2)
    drawRightText(draw = draw, text = mark_text, x = right_margin_px, y = margin_top, font = font)

def generatorGravelOrder(company = "", date_text = "", transport_order_no = "", 
              truck_no = "", gross_weight = "", empty_weight = "", real_weight = "",
              gross_date_time = "", empty_date_time = "", weight_no = ""):

    width = mm_2_pixel(215) # 215mm转换为像素
    height = mm_2_pixel(90) # 90cm转换为像素
    margin_top_title = mm_2_pixel(15)
    
    image = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(image)

    table_width_px = mm_2_pixel(180) 
    table_height_px = mm_2_pixel(56) 
    top_margin_px = mm_2_pixel(25) 


    # 添加公司名称
    drawTitle(draw = draw, text = company, width = width, margin_top = margin_top_title)

    margin_top_sub_title = mm_2_pixel(35)

    drawSubTitle(draw = draw, date_text = date_text, mark_text= transport_order_no, width = width, table_width = table_width_px, margin_top = margin_top_sub_title)

    drawTable(draw = draw, width = width, table_width = table_width_px, 
        truck_no = truck_no, weight_no = weight_no,
        gross_weight = gross_weight, empty_weight = empty_weight, real_weight = real_weight,
        gross_date_time = gross_date_time, empty_date_time = empty_date_time,
        table_height = table_height_px, top_margin = top_margin_px)
    
    image_name = "/Users/miaoyoumeng/公司/合同/级配砂石/台账/pngs/" + date_text + "." + weight_no + '.png'
    image.save(image_name)


if __name__ == '__main__':

    df = pd.read_excel(
        '/Users/miaoyoumeng/公司/合同/级配砂石/级配砂石过磅台账-石铁院.xls',           
        sheet_name='出2025.09.11',        
        usecols='A:O',   
        header=2,
        skiprows=0, 
        nrows=108    
    )
    
    for index, row in df.iterrows():
        company = str(row['供货单位'])
        date_text = str(row['日 期'])
        transport_order_no = str(row['过磅单号'])

        truck_no = str(row['运输车号'])

        gross_weight = str(row['毛重（t）'])
        empty_weight = str(row['皮重（t）'])
        real_weight = str(row['净重（t）'])

        gross_date_time = str(row['毛重时间'].strftime('%Y-%m-%d %H:%M:%S'))
        empty_date_time = str(row['空重时间'].strftime('%Y-%m-%d %H:%M:%S'))

        weight_no = str(index + 1)
        # print(f'毛重时间：{gross_date_time}, 空重时间：{empty_date_time}')
        generatorGravelOrder(company = company, date_text = date_text, transport_order_no = transport_order_no, 
              truck_no = truck_no, gross_weight = gross_weight, empty_weight = empty_weight, real_weight = real_weight,
              gross_date_time = gross_date_time,  empty_date_time = empty_date_time, weight_no = weight_no)
        

