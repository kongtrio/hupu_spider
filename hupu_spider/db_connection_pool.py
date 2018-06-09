# -*- coding: UTF-8 -*-
"""
@描述：数据库连接池管理模块
@作者：CYH
@版本：V1.0
@创建时间：2016-11-24 上午8:43:14
"""

# 下面是更好的封装，有时间改良一下
# http://www.bkjia.com/Pythonjc/1212034.html
import pymysql
from DBUtils.PooledDB import PooledDB
from hupu_spider import db_config as Config

'''
@功能：PT数据库连接池
'''


class DBConnectionPool(object):
    __pool = None

    def __enter__(self):
        self.conn = self.getConn()
        self.cursor = self.conn.cursor()
        return self

    def getConn(self):
        if self.__pool is None:
            self.__pool = PooledDB(creator=pymysql, mincached=Config.DB_MIN_CACHED, maxcached=Config.DB_MAX_CACHED,
                                   maxshared=Config.DB_MAX_SHARED, maxconnections=Config.DB_MAX_CONNECYIONS,
                                   blocking=Config.DB_BLOCKING, maxusage=Config.DB_MAX_USAGE,
                                   setsession=Config.DB_SET_SESSION,
                                   host=Config.DB_TEST_HOST, port=Config.DB_TEST_PORT,
                                   user=Config.DB_TEST_USER, passwd=Config.DB_TEST_PASSWORD,
                                   db=Config.DB_TEST_DBNAME, use_unicode=False, charset=Config.DB_CHARSET)

        return self.__pool.connection()

    """
    @summary: 释放连接池资源
    """

    def __exit__(self, type, value, trace):
        self.cursor.close()
        self.conn.close()


'''
@功能：获取PT数据库连接
'''


def get_db_connect():
    return DBConnectionPool()
