# encoding: utf-8
import os
import time
import pymysql
import re


constant_fields = [ "create_time", "update_time", "is_deleted" ]

class DataDict(object):
    def __init__(self, host, port, user_name, password, db_name):
        # 数据库连接配置
        self.host_name = host
        self.port = port
        self.user_name = user_name
        self.password = password
        self.db_name = db_name
        self.folder_name = os.getcwd()

    def run(self):
        """脚本执行入口"""
        try:
            # 创建一个连接
            conn = pymysql.connect(host=self.host_name, port=self.port, user=self.user_name, 
            	password=self.password,database=self.db_name)
            # 用cursor()创建一个游标对象
            cursor = conn.cursor()
        except Exception:
            print('数据库连接失败，请检查连接信息！')
            exit(1)
    
        show_tables = 'show tables'
        cursor.execute(show_tables)
        rs = cursor.fetchall()
        for i in range(len(rs)):
            table_name = rs[i][0]

            #print('开始生成表%s的数据字典' % (table_name,))
            table_sql = "show full columns from %s" % (table_name,)
            cursor.execute(table_sql)
            desc_rs = cursor.fetchall()

            column_set = []
            for j in range(len(desc_rs)):
                column_name = desc_rs[j][0]
                column_set.append(column_name)
                
                column_type = desc_rs[j][1]

                column_null = desc_rs[j][3]
                column_defalut = desc_rs[j][5]
                if (column_defalut == None):
                    column_defalut = ''
                column_comments = desc_rs[j][8]
            for field in constant_fields:
                if (field in column_set):
                    sql = "ALTER TABLE `" + table_name + "` DROP COLUMN  " + field
                    cursor.execute(sql)
                    column_set.remove(field)

            for field in constant_fields:
                if (field not in column_set):
                    sql = None
                    if ("create_time" == field):
                        sql = "ALTER TABLE `" + table_name + "` ADD COLUMN " + field +" datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间' ;"
                    elif ("update_time" == field):
                        sql = "ALTER TABLE `" + table_name + "` ADD COLUMN " + field +" datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间'  ;"
                    elif ("is_deleted" == field):
                        sql = "ALTER TABLE `" + table_name + "` ADD COLUMN " + field +"  tinyint(1) unsigned NOT NULL DEFAULT 0 COMMENT '删除标识';"
                    elif("id" == field):
                        sql = "ALTER TABLE `" + table_name + "` ADD COLUMN " + field +"  bigint unsigned NOT NULL AUTO_INCREMENT;"
                    if (sql != None and sql != ''):
                        cursor.execute(sql)

        cursor.close()
        conn.close()


    def test_conn(self):
        """测试数据库连接"""
        try:
            # 创建一个连接
            pymysql.connect(host=self.host_name, port=self.port, user=self.user_name, 
            	password=self.password,database=self.db_name)
            return True
        except Exception as e:
            print(str(e))
            print("数据库连接失败")
            return False


if __name__ == '__main__':
    
    host='10.90.1.42'
    port=32436
    user='root'
    password='Tsingj_02!@'
    database='db_security'
   
    dataDict = DataDict(host, port, user, password, database)
    if dataDict.test_conn():
    	dataDict.run()
        