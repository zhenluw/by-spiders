import logging
import os
import random
import sys
import redis
curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)
from by.utils import config


class RedisClient(object):
    # 使用多线程的话,保证线程安全就把下面的线程锁打开
    # mutex = threading.Lock()
    config = None
    connection_pool = None
    connection_client = None

    def __init__(self):
        """
        :param config: {"host":"",
                        "port": 0,
                        "db": 0,
                        "password": "",
                        "encoding": "",
                        "decode_responses": False,
                        "max_connections": 1,
                        "target_max_memory": 1024
                        }
        """
        temp_pool = redis.ConnectionPool(host=config.redis_host, port=config.redis_port, db=config.redis_db, password=config.redis_password, decode_responses=True)
        self.connection_pool = temp_pool
        temp_client = redis.Redis(connection_pool=self.connection_pool)
        self.connection_client = temp_client

    def random(self,name):
        """
        随机得到键值，用于随机Cookies获取
        :return: 随机Cookies
        """
        return random.choice(self.connection_client.hvals(name))

    def rpush(self, key, json_text, expired_in_seconds=0):
        r = self.connection_client
        # self.mutex.acquire()
        pipe = r.pipeline()
        pipe.rpush(key, json_text)
        if expired_in_seconds > 0:
            pipe.expire(key, expired_in_seconds)
        pipe.execute()
        # self.mutex.release()

    def lpush(self, key, json_text, expired_in_seconds=0):
        r = self.connection_client
        # self.mutex.acquire()
        pipe = r.pipeline()
        pipe.lpush(key, json_text)
        if expired_in_seconds > 0:
            pipe.expire(key, expired_in_seconds)
        pipe.execute()
        # self.mutex.release()

    def lpop_pipline(self, key, length):
        i = 0
        poped_items = []
        r = self.connection_client
        # self.mutex.acquire()
        curent_len = r.llen(key)
        if curent_len > 0:
            target_len = 0
            if curent_len > length:
                target_len = length
            else:
                target_len = curent_len
            pipe = r.pipeline()
            while i < target_len:
                pipe.lpop(key)
                i += 1
            temp_poped_items = pipe.execute()
            poped_items = temp_poped_items
        # self.mutex.release()
        return poped_items

    def lpop(self, key):
        poped_items = []
        r = self.connection_client
        # self.mutex.acquire()
        data = r.lpop(key)
        if data:
            poped_items.append(data)
        # self.mutex.release()
        return poped_items

    def rpop_pipline(self, key, length):
        i = 0
        poped_items = []
        r = self.connection_client
        # self.mutex.acquire()
        curent_len = r.llen(key)
        if curent_len > 0:
            target_len = 0
            if curent_len > length:
                target_len = length
            else:
                target_len = curent_len
            pipe = r.pipeline()
            while i < target_len:
                pipe.rpop(key)
                i += 1
            temp_poped_items = pipe.execute()
            poped_items = temp_poped_items
        # self.mutex.release()
        return poped_items

    def rpop(self, key):
        poped_items = []
        r = self.connection_client
        # self.mutex.acquire()
        data = r.rpop(key)
        if data:
            poped_items.append(data)
        # self.mutex.release()
        return poped_items

    def hincrby(self, hash_key, field, amount=1):
        r = self.connection_client
        # self.mutex.acquire()
        result = r.hincrby(hash_key, field, amount)
        # self.mutex.release()
        return result

    def hgetall(self, key):
        r = self.connection_client
        # self.mutex.acquire()
        result = r.hgetall(key)
        # self.mutex.release()
        return result

    def hget(self, name, key):
        r = self.connection_client
        # self.mutex.acquire()
        result = r.hget(name, key)
        # self.mutex.release()
        return result

    def flushdb(self):
        r = self.connection_client
        r.flushdb(asynchronous=False)
        return

    def llen(self, key):
        r = self.connection_client
        # self.mutex.acquire()
        result = r.llen(key)
        # self.mutex.release()
        return result

    def hdel(self, key, *field):
        r = self.connection_client
        # self.mutex.acquire()
        result = r.hdel(key, *field)
        # self.mutex.release()
        return result

    def hset(self, key, field, value, expired_in_seconds=0):
        r = self.connection_client
        # self.mutex.acquire()
        pipline = r.pipeline()
        pipline.hset(key, field, value)
        if expired_in_seconds > 0:
            pipline.expire(key, expired_in_seconds)
        pipline.execute()
        # self.mutex.release()

    def info(self, section=None):
        r = self.connection_client
        # self.mutex.acquire()
        result = r.info(section)
        # self.mutex.release()
        return result

    def exceed_memory_limits(self):
        result = False
        if "target_max_memory" in self.config.keys():
            target_max_memory = self.config["target_max_memory"]
            redis_info = self.info("memory")
            distance = self.__max_memory_distance(redis_info, target_max_memory)
            if distance and distance <= 0:
                result = True
        return result

    def __max_memory_distance(self, redis_info_dict, target_max):
        result = None
        if "used_memory" in redis_info_dict.keys():
            temp_used = int(redis_info_dict["used_memory"])
            temp_used = temp_used / (1024 * 1024)
            result = target_max - temp_used
        else:
            logging.warning(u"used_memory is not found!")
        return result

    def sadd(self, key, *value):
        r = self.connection_client
        # self.mutex.acquire()
        result = r.sadd(key, *value)
        # self.mutex.release()
        return result

    def get(self, key):
        r = self.connection_client
        # self.mutex.acquire()
        result = r.get(key)
        # self.mutex.release()
        return result

    def smembers(self, key):
        r = self.connection_client
        # self.mutex.acquire()
        result = r.smembers(key)
        # self.mutex.release()
        return result

    def sismember(self, key, value):
        r = self.connection_client
        # self.mutex.acquire()
        result = r.sismember(key, value)
        # self.mutex.release()
        return result

    def exists(self, key):
        r = self.connection_client
        # self.mutex.acquire()
        result = r.exists(key)
        # self.mutex.release()
        return result

    def keys(self, pattern):
        r = self.connection_client
        # self.mutex.acquire()
        result = r.keys(pattern=pattern)
        # self.mutex.release()
        return result

    def delele(self, key):
        r = self.connection_client
        # self.mutex.acquire()
        r.delete(key)
        # self.mutex.release()

    def srem(self, name, *values):
        r = self.connection_client
        # self.mutex.acquire()
        r.srem(name, *values)
        # self.mutex.release()

    def scan(self, cursor, match=None, count=50):
        """
        :param cursor:
        :param match:
        :param count:
        :return:
         (new_cursor,
            [key1, key2, key3 ...])
        """
        r = self.connection_client
        # self.mutex.acquire()
        result = r.scan(cursor=cursor, match=match, count=count)
        # self.mutex.release()
        return result

    def hmget(self, hash_key, fields_list):
        r = self.connection_client
        # self.mutex.acquire()
        result = r.hmget(hash_key, fields_list)
        # self.mutex.release()
        return result

    def set(self, key, value, ex=None):
        r = self.connection_client
        # self.mutex.acquire()
        result = r.set(key, value, ex)
        # self.mutex.release()
        return result

    def close(self):
        if self.connection_pool:
            self.connection_pool.disconnect()


if __name__ == '__main__':
    redis_db = RedisClient(1)
    redis_db.hincrby('lty', 1, 2)
    re = redis_db.hgetall('lty')
    print(re)
