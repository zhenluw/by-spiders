import os
import sys
curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
rootPath = os.path.split(rootPath)[0]
sys.path.append(rootPath)
import redis
from by.utils import config


class RedisQueue(object):
    def __init__(self, namespace,name,  **redis_kwargs):
        # redis的默认参数为：host='localhost', port=6379, db=0， 其中db为定义redis database的数量
        self.__db= redis.Redis(host=config.redis_host, port=config.redis_port, password=config.redis_password,db=10)
        self.key = '%s:%s' %(namespace, name)

    def qsize(self):
        return self.__db.llen(self.key)  # 返回队列里面list内元素的数量

    def put(self, item):
        self.__db.rpush(self.key, item)  # 添加新元素到队列最右方

    def get_wait(self, timeout=None):
        # 返回队列第一个元素，如果为空则等待至有元素被加入队列（超时时间阈值为timeout，如果为None则一直等待）
        # blpop，从左边弹出一个元素 brpop，从右边谈，和blpop相同
        item = self.__db.blpop(self.key, timeout=timeout)
        # if item:
        #     item = item[1]  # 返回值为一个tuple
        return item

    def get_nowait(self):
        # 直接返回队列第一个元素，如果队列为空返回的是None
        item = self.__db.lpop(self.key)
        return item

    def get_brpop(self,*args):
        # 直接返回队列第一个元素，如果队列为空返回的是None
        item = self.__db.brpop(args,0)
        return item


# if __name__ == '__main__':
#     while True:
#         result = q_online_weibo.test('redbook:mz','redbook_list:mz')
#         if result is not None:
#             print(result)