"""
 * @Project_Name: lav-spiders
 * @DESCRIPTION:
 * @Author: wzl
 * @Date: 2020/9/22 14:12
"""
import threading
import os
import sys
curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
rootPath = os.path.split(rootPath)[0]
sys.path.append(rootPath)
from lavector.spiders.jd.app_jd import jd, online_jd
from lavector.spiders.redbook.app_redbook import  rb_info, search_list
from lavector.spiders.tmall.app_tmall import tmall, online_tmall
from lavector.spiders.weibo.app_weibo import weibo_user, weibo, online_weibo, official_weibo
from lavector.spiders.tiktok.app_tiktok import tiktok, online_tiktok, cookie_pool


def spider_jd():
    for i in range(10):
        jd_threading = threading.Thread(target = jd)
        jd_threading.start()
    for i in range(5):
        online_jd_threading = threading.Thread(target = online_jd)
        online_jd_threading.start()


def spider_tmall():
    for i in range(10):
        tmall_threading = threading.Thread(target = tmall)     # target是要执行的函数名（不是函数），args是函数对应的参数，以元组的形式存在
        tmall_threading.start()
    for i in range(5):
        online_tmall_threading = threading.Thread(target = online_tmall)     # target是要执行的函数名（不是函数），args是函数对应的参数，以元组的形式存在
        online_tmall_threading.start()


def spider_redbook():
    search_list_threading = threading.Thread(target = search_list)
    search_list_threading.start()
    for i in range(15):
        rb_info_threading = threading.Thread(target = rb_info)
        rb_info_threading.start()


def spider_weibo():
    for i in range(5):
        official_weibo_threading = threading.Thread(target = official_weibo)
        official_weibo_threading.start()
    for i in range(10):
        weibo_threading = threading.Thread(target = weibo)
        weibo_threading.start()
    for i in range(15):
        weibo_user_threading = threading.Thread(target = weibo_user)
        weibo_user_threading.start()
    for i in range(10):
        online_weibo_threading = threading.Thread(target = online_weibo)
        online_weibo_threading.start()


def spider_tiktok():
    for i in range(10):
        tiktok_threading = threading.Thread(target = tiktok)
        tiktok_threading.start()
    for i in range(10):
        online_tiktok_threading = threading.Thread(target = online_tiktok)
        online_tiktok_threading.start()
    for _ in range(20):
        t = threading.Thread(target=cookie_pool)
        t.start()


if __name__ == '__main__':
    # 京东
    spider_jd()
    # # 天猫
    spider_tmall()
    # # 小红书
    spider_redbook()
    # 微博
    spider_weibo()
    # 抖音
    # spider_tiktok()