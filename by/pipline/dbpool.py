import threading
import traceback
import pymysql
import sys
import os
curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
rootPath = os.path.split(rootPath)[0]
sys.path.append(rootPath)
from by.utils import config
from pymysql.cursors import DictCursor
from DBUtils.PooledDB import PooledDB
lock = threading.Lock()

class Pool():
    """
    MYSQL数据库对象，负责产生数据库连接 , 此类中的连接采用连接池实现获取连接对象：conn = Mysql.getConn()
            释放连接对象;conn.close()或del conn
    """
    # 连接池对象
    __pool = None

    def __init__(self):
        # 数据库构造函数，从连接池中取出连接，并生成操作游标
        self._conn = self.__getConn()
        self._cursor = self._conn.cursor()

    def __getConn(self):
        """
        @summary: 静态方法，从连接池中取出连接
        @return MySQLdb.connection
        """
        if Pool.__pool is None:
            __pool = PooledDB(creator=pymysql,
                              mincached=1,
                              maxcached=50,
                              host=config.mysql_host,
                              port=config.mysql_port,
                              user=config.mysql_user,
                              passwd=config.mysql_password,
                              db=config.mysql_db,
                              use_unicode=True,
                              charset="utf8mb4",
                              cursorclass=DictCursor)
        return __pool.connection()

    def __query(self, sql, param=None):
        if param is None:
            count = self._cursor.execute(sql)
        else:
            count = self._cursor.execute(sql, param)
        self._conn.commit()
        return count

    def query0(self, sql, param=None):
        if param is None:
            count = self._cursor.executemany(sql)
        else:
            count = self._cursor.executemany(sql, param)
        self._conn.commit()
        return count

    def begin(self):
        """
        @summary: 开启事务
        """
        self._conn.autocommit(0)

    def end(self, option='commit'):
        """
        @summary: 结束事务
        """
        if option == 'commit':
            self._conn.commit()
        else:
            self._conn.rollback()

    def dispose(self, isEnd=1):
        """
        @summary: 释放连接池资源
        """
        if isEnd == 1:
            self.end('commit')
        else:
            self.end('rollback')
        self._cursor.close()
        self._conn.close()

    def insert_many_temp(self,table_name,commit_id_list,project_name):
        lock.acquire()
        try:
            col = ''  #列的字段
            row_str = '' #行字段
            for key in commit_id_list[0].keys():
                col = col+key+','
                row_str=row_str+'%s'+','
            sql = "INSERT INTO %s (%s) VALUES (%s)"%(table_name,col[:-1],row_str[:-1])
            values = []
            for item in commit_id_list:
                params = ()
                params_list = list(params)
                for key in item.keys():
                    params_list.append(item[key])
                params = tuple(params_list)
                values.append(params)
            self._cursor.executemany(sql, values)
            self.dispose()
            print('{}--批量插入数据'.format(project_name))
        except Exception as e:
            print('{}--存储异常：'.format(project_name),e)
            traceback.print_exc()
        finally:
            # 改完了一定要释放锁:
            lock.release()

    def insert_temp(self,table_name,dic,project_name):
        lock.acquire()
        sql=''
        try:
            col = ''  #列的字段
            row_str = '' #行字段
            for key in dic.keys():
                col = col+key+','
                row_str=row_str+'"%s"'%(dic[key]) +','
                #判断表是否存在，存在执行try，不存在执行except新建表，再insert
            sql = "INSERT INTO %s (%s) VALUES (%s)"%(table_name,col[:-1],row_str[:-1])
            self._cursor.execute(sql)
            self.dispose()
            print('{}--插入数据'.format(project_name))
        except Exception as e:
            print('{}存储异常：{}'.format(project_name,sql),e)
            traceback.print_exc()
        finally:
            # 改完了一定要释放锁:
            lock.release()

    def replace_insert_temp(self,table_name,dic,project_name):
        lock.acquire()
        sql=''
        try:
            col = ''  #列的字段
            row_str = '' #行字段
            for key in dic.keys():
                col = col+key+','
                row_str=row_str+'"%s"'%(dic[key]) +','
                #判断表是否存在，存在执行try，不存在执行except新建表，再insert
            sql = "replace into %s (%s) VALUES (%s)"%(table_name,col[:-1],row_str[:-1])
            self._cursor.execute(sql)
            self.dispose()
            print('{}--插入数据'.format(project_name))
        except Exception as e:
            print('{}存储异常：{}'.format(project_name,sql),e)
            traceback.print_exc()
        finally:
            # 改完了一定要释放锁:
            lock.release()

    def replace_temp(self,table_name,dic,project_name):
        lock.acquire()
        sql=''
        try:
            col = ''  #列的字段
            row_str = '' #行字段
            for key in dic.keys():
                col = col+key+','
                row_str=row_str+'"%s"'%(dic[key]) +','
                #判断表是否存在，存在执行try，不存在执行except新建表，再insert
            sql = "replace  %s (%s) VALUES (%s)"%(table_name,col[:-1],row_str[:-1])
            self._cursor.execute(sql)
            self.dispose()
            print('{}--插入数据'.format(project_name))
        except Exception as e:
            print('{}存储异常：{}'.format(project_name,sql),e)
            traceback.print_exc()
        finally:
            # 改完了一定要释放锁:
            lock.release()

    def get_one(self, sql, param=None):
        """
        @summary: 执行查询，并取出第一条
        @param sql:查询ＳＱＬ，如果有查询条件，请只指定条件列表，并将条件值使用参数[param]传递进来
        @param param: 可选参数，条件列表值（元组/列表）
        @return: result list/boolean 查询到的结果集
        """
        if param is None:
            count = self._cursor.execute(sql)
        else:
            count = self._cursor.execute(sql, param)
        if count > 0:
            result = self._cursor.fetchone()
        else:
            result = False
        self.dispose()
        return result

    def get_all(self, sql, param=None):
        """
        @summary: 执行查询，并取出所有结果集
        @param sql:查询ＳＱＬ，如果有查询条件，请只指定条件列表，并将条件值使用参数[param]传递进来
        @param param: 可选参数，条件列表值（元组/列表）
        @return: result list(字典对象)/boolean 查询到的结果集
        """
        if param is None:
            count = self._cursor.execute(sql)
        else:
            count = self._cursor.execute(sql, param)
        print(count)
        if count > 0:
            print('*****')
            result = self._cursor.fetchall()
        else:
            result = False
        self.dispose()
        return result

    def get_all2(self, sql, param=None):
        """
        @summary: 执行查询，并取出所有结果集
        @param sql:查询ＳＱＬ，如果有查询条件，请只指定条件列表，并将条件值使用参数[param]传递进来
        @param param: 可选参数，条件列表值（元组/列表）
        @return: result list(字典对象)/boolean 查询到的结果集
        """
        if param is None:
            count = self._cursor.execute(sql)
        else:
            count = self._cursor.execute(sql, param)
        print(count)
        if count > 0:
            print('*****')
            result = self._cursor.fetchall()
        else:
            result = False
        # self.dispose()
        return result

    def insert_many(self, sql, values):
        """
        @summary: 向数据表插入多条记录
        @param sql:要插入的ＳＱＬ格式
        @param values:要插入的记录数据tuple(tuple)/list[list]
        @return: count 受影响的行数
        """
        count = self._cursor.executemany(sql, values)
        self.dispose()
        return count

    def update(self, sql, param=None):
        """
        @summary: 更新数据表记录
        @param sql: ＳＱＬ格式及条件，使用(%s,%s)
        @param param: 要更新的  值 tuple/list
        @return: count 受影响的行数
        """
        return self.__query(sql, param)

    def update_many(self, sql,project_name, param=None):
        """
        @summary: 更新数据表记录
        @param sql: ＳＱＬ格式及条件，使用(%s,%s)
        @param param: 要更新的  值 tuple/list
        @return: count 受影响的行数
        """
        count = self.query0(sql, param)
        print('{}--批量update'.format(project_name))
        return count

    def insert(self, sql, param=None):
        """
        @summary: 更新数据表记录
        @param sql: ＳＱＬ格式及条件，使用(%s,%s)
        @param param: 要更新的  值 tuple/list
        @return: count 受影响的行数
        """
        self.__query(sql, param)
        self.dispose()
        return 0

    def delete(self, sql, param=None):
        """
        @summary: 删除数据表记录
        @param sql: ＳＱＬ格式及条件，使用(%s,%s)
        @param param: 要删除的条件 值 tuple/list
        @return: count 受影响的行数
        """
        return self.__query(sql, param)


def update(sql, params):
    """
        @summary: 更新数据表记录
        @param sql: ＳＱＬ格式及条件，使用(%s,%s)
        @param param: 要更新的  值 tuple/list
        @return: count 受影响的行数
    """
    mysql = Pool("notdbMysql")
    mysql.update(sql, params)
    # 释放资源
    mysql.dispose()


def save(sql, params):
    mysql =Pool()
    mysql.insert(sql, params)
    # 释放资源
    # mysql.dispose()


if __name__ == '__main__':
    #查询一条数据的示例代码
    # mysql = Pool()
    # sql_one = "select * from template"
    # result = mysql.get_one_note(sql_one)
    # print(result)
    # 释放资源
    # mysql.dispose()

    #存储数据
    try:
        save("replace into shopee_shope (shopid, shopname)VALUES( %s, %s)"
             ,('2836698382','苍叶鬼屋'))
    except Exception as e:
        print(str(e))

    # #更新数据
    # try:
    #     update("UPDATE book SET page=%s , bname= %s where read_type= %s",('100','战争论','未读'))
    # except Exception as e:
    #     print(str(e))