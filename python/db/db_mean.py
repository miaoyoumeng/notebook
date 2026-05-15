# encoding: utf-8
import os
import time
import pymysql
import json
import pandas as pd
import datetime
from decimal import Decimal

class MySQLEncoder(json.JSONEncoder):
    def default(self, obj):
        # 👇️ if passed in object is instance of Decimal
        # convert it to a string
        if isinstance(obj, Decimal):
            return str(obj)
        if isinstance(obj, datetime.datetime):  
            return obj.strftime('%Y-%m-%d %H:%M:%S')  
        # 👇️ otherwise use the default behavior
        return json.JSONEncoder.default(self, obj)


class DataDict(object):
    def __init__(self, host, port, user_name, password, db_name, table):
        # 数据库连接配置
        self.host_name = host
        self.port = port
        self.user_name = user_name
        self.password = password
        self.db_name = db_name
        self.table = table
        

    def read_data(self):

        """脚本执行入口"""
        try:
            # 创建一个连接
            conn = pymysql.connect(host=self.host_name, port=self.port, user=self.user_name, 
            	password=self.password, database=self.db_name)
            # 用cursor()创建一个游标对象
            cursor = conn.cursor()
        except Exception:
            print('数据库连接失败，请检查连接信息！')
            exit(1)
        
        query_sql = 'select * from ' + self.table

        cursor.execute(query_sql)
        col = cursor.description
        result = cursor.fetchall()
        df = pd.DataFrame(list(result))
        list_items = []
        for r in result:

            item = {}
            for i in range(len(col)):
                item[col[i][0]] = r[i]
            # result = json.dumps(r, cls = MySQLEncoder, ensure_ascii = False)

            print(json.dumps(item, cls = MySQLEncoder, ensure_ascii = False))
            print("\n")
        
        cursor.close()
        conn.close()
        # all_json = json.dumps(list_items, cls = MySQLEncoder, ensure_ascii = False)
        # print(all_json)
        return list_items;

     
    

    def test_conn(self):
        """测试数据库连接"""
        try:
            # 创建一个连接
            pymysql.connect(host=self.host_name, port=self.port, user=self.user_name, 
            	password=self.password,database=self.db_name)
            return True
        except Exception:
            print("====db false=====")
            return False

if __name__ == '__main__':
    
    from_host='192.168.202.218'
    from_port=32601
    from_user='root'
    from_password='BvFH0O3XrH59DAny'
    from_database='data_element_gov'
    from_table='login_directory'

    db_reader = DataDict(from_host, from_port, from_user, from_password, from_database, from_table)
    
    if db_reader.test_conn():
        list_items = db_reader.read_data()
        

        # all_json = json.dumps(list_items, cls = MySQLEncoder, ensure_ascii = False)
        # print(all_json)


