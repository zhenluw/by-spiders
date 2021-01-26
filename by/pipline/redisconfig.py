import os
import random
import sys
import redis
curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)
from by.utils import config
from by.pipline.redisclient import RedisClient

class RedisConfig(object):
    def __init__(self, website, host=config.redis_host, port=config.redis_port, password=config.redis_password):
        """
        初始化Redis连接
        :param host: 地址
        :param port: 端口
        :param password: 密码
        """
        self.db = redis.StrictRedis(host=host, port=port, password=password, decode_responses=True,db=10)
        self.website = website

    def name(self):
        """
        获取Hash的名称
        :return: Hash名称
        """
        return "{website}".format(website=self.website)

    def set(self, username, value):
        """
        设置键值对
        :param username: 用户名
        :param value: 密码或Cookies
        :return:
        """
        return self.db.hset(self.name(), username, value)

    def get(self, username):
        """
        根据键名获取键值
        :param username: 用户名
        :return:
        """
        return self.db.hget(self.name(), username)

    def delete(self, username):
        """
        根据键名删除键值对
        :param username: 用户名
        :return: 删除结果
        """
        return self.db.hdel(self.name(), username)

    def count(self):
        """
        获取数目
        :return: 数目
        """
        return self.db.hlen(self.name())

    def random(self):
        """
        随机得到键值，用于随机Cookies获取
        :return: 随机Cookies
        """
        return random.choice(self.db.hvals(self.name()))

    def usernames(self):
        """
        获取所有账户信息
        :return: 所有用户名
        """
        return self.db.hkeys(self.name())

    def all(self):
        """
        获取所有键值对
        :return: 用户名和密码或Cookies的映射表
        """
        return self.db.hgetall(self.name())


if __name__ == '__main__':
    conn = RedisClient( 'weibo_cookies')
    # conn.set('a0t4emhq@anjing.cool','{"ALF": "1626341785", "SSOLoginState": "1594805785", "ALC": "ac%3D2%26bt%3D1594805785%26cv%3D5.0%26et%3D1626341785%26ic%3D1928992869%26login_time%3D1594805784%26scf%3D%26uid%3D7323678780%26vf%3D0%26vs%3D0%26vt%3D0%26es%3D34cc1675066ee4e6de4892c58d1ea679", "LT": "1594805785", "tgc": "TGT-NzMyMzY3ODc4MA==-1594805785-tc-2F9342958900A9FDBEA4AEFFD82ABEFE-1", "SCF": "Aisf4l3pEHvwu77qFRFRd2j3KZ-usuJDOFnoSyvDYc-MkO3e7MVh2D3EnfwxLR5qlgRFDX0Ou7ySC6LISZZK0pI.", "SUB": "_2A25yCr5JDeRhGeFN6VEX9ybLwzyIHXVRYaiBrDV_PUNbm9AKLXTQkW9NQEcl8Ssqjt_AZideZBjYJ16UJ6ldSntj", "SUBP": "0033WrSXqPxfM725Ws9jqgMF55529P9D9W5lJws7mR9arLiOXCBkS65r5NHD95QNe0z0SoMRS0n7Ws4Dqc_5i--4iK.4iKnRPEH8SCHFeFHFeCH8SE-4SCHFSbH8SFHFxFHWeFH8SbHFeb-4ebH8SFHFxC-RSbH81C-ReC-RxBtt", "U_TRS1": "00000065.30581780.5f0ece19.9baaaa7d", "U_TRS2": "00000065.30691780.5f0ece19.5ef84efc", "sso_info": "v02m6alo5qztKWRk6SljpOkpY6DoZ-JlJS1iZSIsImUiLGJlJS3iZOktYmUiLaJlJS0iZSJhImUhLCJlJS2iZSIsomTpLKJlJS0iZSJhYmToLaJlJS5iZOgsYmToYWJp5WpmYO0t4yziLONo5y4jbOgsA=="}')
    a='vpjujtcccqdqido-qgh@yahoo.com'
    print(conn.get(a))
    # print(conn.random())
    # print(conn.random())
    # print(conn.all())
    conn.delete(a)
    print(conn.get(a))

