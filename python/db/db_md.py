# encoding: utf-8
import os
import time
import pymysql



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
        file_path = self.folder_name + os.sep + self.db_name + '.md'
        dict_file = open(file_path, 'a', encoding='UTF-8')
        print(file_path)
        show_tables = 'show tables'
        cursor.execute(show_tables)
        rs = cursor.fetchall()
        for i in range(len(rs)):
            table_name = rs[i][0]
            print('\n 开始生成表%s的数据字典' % (table_name,))
            table_sql = "show full columns from %s" % (table_name,)
            cursor.execute(table_sql)
            desc_rs = cursor.fetchall()
            # dict_file.write('\n \n ### %s' % (table_name,))
            # dict_file.write('\n | 字段名称 | 字段类型 | 默认值 | 字段注释 |是否为空')
            # dict_file.write('\n | --- | --- | --- | --- | --- |')
            for j in range(len(desc_rs)):
                column_name = desc_rs[j][0]
                column_type = desc_rs[j][1]
                column_null = desc_rs[j][3]
                column_defalut = desc_rs[j][5]
                if (column_defalut == None):
                	column_defalut = ''
                column_comments = desc_rs[j][8]
                print(column_type )
                # dict_file.write('\n| ' + column_name + ' | ' + column_type + ' | ' + column_defalut + ' | ' + column_comments + ' | ' + column_null + ' |')

        dict_file.close()
        cursor.close()
        conn.close()

    # def deal_file(self, file_name):
    #     """处理存储文件夹和文件"""
    #     # 不存在则创建文件夹
    #     if not os.path.exists(self.folder_name):
    #         os.mkdir(self.folder_name)
    #     # 删除已存在的文件
    #     if os.path.isfile(file_name):
    #         os.unlink(file_name)

    def test_conn(self):
        """测试数据库连接"""
        try:
            # 创建一个连接
            pymysql.connect(host=self.host_name, port=self.port, user=self.user_name, 
            	password=self.password,database=self.db_name)
            return True
        except Exception:
            return False

if __name__ == '__main__':
    
    host='10.150.20.205'
    port=3306
    user='pv-bd'
    password='oC7WIPHhywRWeHTwmWsj'
    database='bigdata_microservice_alarm'
   
    dataDict = DataDict(host, port, user, password, database)
    if dataDict.test_conn():
    	dataDict.run()