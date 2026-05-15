# encoding: utf-8
import os
import time
import pymysql
import yaml
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
    def __init__(self, host, port, user, password, database):
        # 数据库连接配置
        self.address = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        
    def read_data(self, sql):

        """脚本执行入口"""
        try:
            # 创建一个连接
            conn = pymysql.connect(host=self.address, port=self.port, user=self.user, 
            	password=self.password, database=self.database)
            # 用cursor()创建一个游标对象
            cursor = conn.cursor()
        except Exception:
            print('数据库连接失败，请检查连接信息！')
            exit(1)
        
        query_sql = sql
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

            list_items.append(item)
            # print("\n")
        
        cursor.close()
        conn.close()
        # all_json = json.dumps(list_items, cls = MySQLEncoder, ensure_ascii = False)
        # print(all_json)
        return list_items;

        

    def write_data(self, item, table):

        """脚本执行入口"""
        try:
            # 创建一个连接
            conn = pymysql.connect(host=self.address, port=self.port, user=self.user, 
                password=self.password, database=self.database)
            # 用cursor()创建一个游标对象
            cursor = conn.cursor()
        except Exception:
            print('数据库连接失败，请检查连接信息！')
            exit(1)
        try:
            table_name = table.get('name')
            primary = table.get('primary')

            for key in item.keys():
                if (key == primary):
                    query_sql = "select " + primary + " from " + table_name + " where " + primary + " = " + str(item["id"])
                    cursor.execute(query_sql)
                    result = cursor.fetchall()

                    if(len(result) == 0):
                        insert_sql = "INSERT INTO `" + table_name + "` (`" + primary + "`) VALUES (%s)"
                        cursor.execute(insert_sql, (str(item[primary])))
                    continue
                if (item[key] == None):
                    continue
                update_sql = "update " + table_name + " set " + key + "= %s where " + primary + " = %s" 
                cursor.execute(update_sql, (str(item[key]), str(item[primary])))
                conn.commit()
            
                #print("更新成功")
        except Exception as e:
            print(e)
            conn.rollback()
            print("sql执行失败")

        finally:
            cursor.close()
            conn.close()
        # print(json.dumps(item, cls = MySQLEncoder, ensure_ascii = False))
        # cursor.execute(query_sql)
        
        return list_items;
    

    def test_conn(self):
        """测试数据库连接"""
        try:
            # 创建一个连接
            pymysql.connect(host=self.address, port=self.port, user=self.user, 
            	password=self.password,database=self.database)
            return True
        except Exception:
            print("====db false=====")
            return False

if __name__ == '__main__':

    with open('policy.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    if (config.__contains__('strategies') == False):
        print("配置文件格式不正确")
        exit(1)
    strategies = config.get('strategies')
    for strategy in strategies:
        source = strategy.get('source')
        from_host = source.get('host')
        from_port = source.get('port')
        from_user = source.get('user')
        from_password = source.get('password')
        from_database = source.get('database')
        from_data = source.get('data')
        from_sql = from_data.get("sql")

        db_reader = DataDict(from_host, from_port, from_user, from_password, from_database)
        if (db_reader.test_conn() == False):
            print("同步原始库联通失败...")
            exit(1)

        target = strategy.get('target')
        to_host = target.get('host')
        to_port = target.get('port')
        to_user = target.get('user')
        to_password = target.get('password')
        to_database = target.get('database')
        to_table = target.get('table')
        table_name = to_table.get('name')

   
        db_writer = DataDict(to_host, to_port, to_user, to_password, to_database)
        if db_writer.test_conn() == False:
            print("同步目标库联通失败...")
            exit(1)
        list_items = db_reader.read_data(from_sql)
        for item in list_items:
            db_writer.write_data(item, to_table)

        # all_json = json.dumps(list_items, cls = MySQLEncoder, ensure_ascii = False)
        # print(all_json)


