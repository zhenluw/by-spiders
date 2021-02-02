"""
 * @Project_Name: by-spiders
 * @DESCRIPTION:
 * @Author: wzl
 * @Date: 2021/1/30 23:09
 
"""
import datetime
import json
import os
import sys
import threading
import time
import traceback


curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
rootPath = os.path.split(rootPath)[0]
rootPath = os.path.split(rootPath)[0]
sys.path.append(rootPath)
from by.pipline.redisqueue import RedisQueue
from by.pipline import dbpool
from by.utils.tools import DateEnconding
from by.pipline.template import trans_product_entity

cache_shop_insert = RedisQueue('cache_shop_insert', 'mz')
cache_shop_change_insert = RedisQueue('cache_shop_change_insert', 'mz')
cache_shop_update = RedisQueue('cache_shop_update', 'mz')
cache_shop_update_time = RedisQueue('cache_shop_update_time', 'mz')

cache_product_insert = RedisQueue('cache_product_insert', 'mz')
cache_product_change_insert = RedisQueue('cache_product_change_insert', 'mz')
cache_product_update = RedisQueue('cache_product_update', 'mz')
cache_product_update_time = RedisQueue('cache_product_update_time', 'mz')

cache_sub_product_insert = RedisQueue('cache_sub_product_insert', 'mz')
cache_sub_product_change_insert = RedisQueue('cache_sub_product_change_insert', 'mz')
cache_sub_product_update = RedisQueue('cache_sub_product_update', 'mz')


def get_time():
    return int(time.time())


# 店铺插入
def shop_insert():
    # 比较少，不做批量处理，有就直接存储
    while True:
        shop = cache_shop_insert.get_nowait()
        if shop is not None:
            shop = json.loads(shop.decode())
            try:
                dbpool.Pool().insert_temp('shopee_shope', shop,'shopee_shope')
            except Exception:
                traceback.print_exc()
                cache_shop_insert.put(json.dumps(dict(shop),cls = DateEnconding))
        else:
            time.sleep(10)


# 店铺变更插入
def shop_change_insert():
    # 比较少，不做批量处理，有就直接存储
    while True:
        shop = cache_shop_change_insert.get_nowait()
        if shop is not None:
            shop = json.loads(shop.decode())
            try:
                dbpool.Pool().insert_temp('shopee_shope_change', shop,'shopee_shope_change')
            except Exception:
                traceback.print_exc()
                cache_shop_change_insert.put(json.dumps(dict(shop),cls = DateEnconding))
        else:
            time.sleep(10)


# 店铺变更更新
def shop_update():
    # 比较少，不做批量处理，有就直接存储
    while True:
        shop = cache_shop_update.get_nowait()
        if shop is not None:
            shop = json.loads(shop.decode())
            try:
                sql = "update shopee_shope set " \
                      "shopname=%s ," \
                      "icon=%s ," \
                      "products=%s ," \
                      "followers=%s ," \
                      "following=%s ," \
                      "rating_num=%s ," \
                      "rating=%s ," \
                      "chatperformance=%s ," \
                      " abstract=%s ," \
                      " update_time=%s ," \
                      " update_by= %s" \
                      " where shopid= %s"

                abstract = None
                try:
                    abstract = shop['abstract']
                except Exception:
                    pass

                params = (shop['shopname'],
                          shop['icon'],
                          shop['products'],
                          shop['followers'],
                          shop['following'],
                          shop['rating_num'],
                          shop['rating'],
                          shop['chatperformance'],
                          abstract,
                          datetime.datetime.now(),
                          '007',
                          shop['shopid'])
                dbpool.Pool().update(sql,params)
            except Exception:
                traceback.print_exc()
                cache_shop_update.put(json.dumps(dict(shop),cls = DateEnconding))
        else:
            time.sleep(10)


#  店铺时间更新
def shop_update_time():
    # 比较少，不做批量处理，有就直接存储
    while True:
        shopid = cache_shop_update_time.get_nowait()
        if shopid is not None:
            shopid = shopid.decode()
            try:
                sql = "update shopee_shope set update_time=%s , update_by= %s where shopid= %s"
                now_time = datetime.datetime.now()
                dbpool.Pool().update(sql,(now_time,'007',shopid))
            except Exception:
                traceback.print_exc()
                cache_shop_update_time.put(shopid)
        else:
            time.sleep(10)


# 商品插入
def product_insert():
    start_time0 = get_time()
    count0 = 0
    data_list0 = []
    while True:
        product = cache_product_insert.get_nowait()
        if product is not None:
            product = json.loads(product.decode())
            product = trans_product_entity(product)
            data_list0.append(product)
            count0 += 1
        else:
            time.sleep(10)

        # 首先判断数组内数据个数是否达到100，达到，就批量存入msyql
        if count0 > 100:
            try:
                dbpool.Pool().insert_many_temp('shopee_product', data_list0,'shopee_product')
            except Exception:
                traceback.print_exc()
                for product in data_list0:
                    cache_product_insert.put(json.dumps(dict(product),cls = DateEnconding))

            # 重置 count start_time
            count0 = 0
            start_time0 = get_time()
            data_list0 = []
        else:
            # 虽然数组个数没有100，但接受数据时间超过了10分钟，就批量存入msyql
            time_c = get_time() - start_time0
            if time_c > 300:
                if len(data_list0) > 0:
                    try:
                        dbpool.Pool().insert_many_temp('shopee_product', data_list0,'shopee_product')
                    except Exception:
                        traceback.print_exc()
                        for product in data_list0:
                            cache_product_insert.put(json.dumps(dict(product),cls = DateEnconding))

                # 重置 count = 0 start_time
                count0 = 0
                start_time0 = get_time()
                data_list0 = []


# 商品变更插入
def product_change_insert():
    start_time1 = get_time()
    count1 = 0
    data_list1 = []
    while True:
        product = cache_product_change_insert.get_nowait()
        if product is not None:
            product = json.loads(product.decode())
            product = trans_product_entity(product)
            data_list1.append(product)
            count1 += 1
        else:
            time.sleep(5)

        # 首先判断数组内数据个数是否达到100，达到，就批量存入msyql
        if count1 > 100:
            try:
                dbpool.Pool().insert_many_temp('shopee_product_change', data_list1,'shopee_product_change')
            except Exception:
                traceback.print_exc()
                for product in data_list1:
                    cache_product_change_insert.put(json.dumps(dict(product),cls = DateEnconding))

            # 重置 count start_time
            count1 = 0
            start_time1 = get_time()
            data_list1 = []
        else:
            # 虽然数组个数没有100，但接受数据时间超过了10分钟，就批量存入msyql
            time_c = get_time() - start_time1
            if time_c > 300:
                if len(data_list1) > 0:
                    try:
                        dbpool.Pool().insert_many_temp('shopee_product_change', data_list1,'shopee_product_change')
                    except Exception:
                        traceback.print_exc()
                        for product in data_list1:
                            cache_product_change_insert.put(json.dumps(dict(product),cls = DateEnconding))

                # 重置 count = 0 start_time
                count1 = 0
                start_time1 = get_time()
                data_list1 = []


#  商品时间update
def product_update_time():
    sql = "update shopee_product set update_time=%s ,status = 1 , update_by= %s where spu= %s"
    start_time2 = get_time()
    count2 = 0
    data_list2 = []
    while True:
        spu = cache_product_update_time.get_nowait()
        if spu is not None:
            spu = spu.decode()
            now_time = datetime.datetime.now()
            data_list2.append((now_time,'007',spu))
            count2 += 1
        else:
            time.sleep(5)

        # 首先判断数组内数据个数是否达到100，达到，就批量存入msyql
        if count2 > 200:
            try:
                dbpool.Pool().update_many(sql,'shopee_product update time',data_list2)
            except Exception:
                traceback.print_exc()
                for product in data_list2:
                    cache_product_update_time.put(json.dumps(dict(product),cls = DateEnconding))

            # 重置 count start_time
            count2 = 0
            start_time2 = get_time()
            data_list2 = []

        else:
            # 虽然数组个数没有100，但接受数据时间超过了10分钟，就批量存入msyql
            time_c = get_time() - start_time2
            if time_c > 100:
                if len(data_list2) > 0:
                    try:
                        dbpool.Pool().update_many(sql,'shopee_product update time',data_list2)
                    except Exception:
                        traceback.print_exc()
                        for product in data_list2:
                            cache_product_update_time.put(json.dumps(dict(product),cls = DateEnconding))

                # 重置 count = 0 start_time
                count2 = 0
                start_time2 = get_time()
                data_list2 = []


# 商品变更update
def product_update():
    sql = "update shopee_product set " \
          "historical_sold=%s ," \
          "price=%s ," \
          "height_price=%s ," \
          "product_title=%s ," \
          " quantity=%s ," \
          " status = 1 ," \
          " update_time=%s ," \
          " update_by= %s" \
          " where spu= %s"

    start_time3 = get_time()
    count3 = 0
    data_list3 = []
    while True:
        product = cache_product_update.get_nowait()
        if product is not None:
            product = json.loads(product.decode())
            params = (product['historical_sold'],
                      product['price'],
                      product['height_price'],
                      product['product_title'],
                      product['quantity'],
                      datetime.datetime.now(),
                      '007',
                      str(product['spu']))
            data_list3.append(params)
            count3 += 1
        else:
            time.sleep(5)

        # 首先判断数组内数据个数是否达到100，达到，就批量存入msyql
        if count3 > 100:
            try:
                dbpool.Pool().update_many(sql,'shopee_product update ',data_list3)
            except Exception:
                traceback.print_exc()
                for product in data_list3:
                    cache_product_update.put(json.dumps(dict(product),cls = DateEnconding))

            # 重置 count start_time
            count3 = 0
            start_time3 = get_time()
            data_list3 = []

        else:
            # 虽然数组个数没有100，但接受数据时间超过了10分钟，就批量存入msyql
            time_c = get_time() - start_time3
            if time_c > 300:
                if len(data_list3) > 0:
                    try:
                        dbpool.Pool().update_many(sql,'shopee_product update time',data_list3)
                    except Exception:
                        traceback.print_exc()
                        for product in data_list3:
                            cache_product_update.put(json.dumps(dict(product),cls = DateEnconding))

                # 重置 count = 0 start_time
                count3 = 0
                start_time3 = get_time()
                data_list3 = []


# 子产品插入
def sub_product_insert():
    start_time4 = get_time()
    count4 = 0
    data_list4 = []
    while True:
        sub_product = cache_sub_product_insert.get_nowait()
        if sub_product is not None:
            sub_product = json.loads(sub_product.decode())
            data_list4.append(sub_product)
            count4 += 1
        else:
            time.sleep(5)

        # 首先判断数组内数据个数是否达到100，达到，就批量存入msyql
        if count4 > 200:
            try:
                dbpool.Pool().insert_many_temp('shopee_sub_product', data_list4,'shopee_sub_product')
            except Exception:
                traceback.print_exc()
                for product in data_list4:
                    cache_sub_product_insert.put(json.dumps(dict(product),cls = DateEnconding))

            # 重置 count start_time
            count4 = 0
            start_time4 = get_time()
            data_list4 = []

        else:
            # 虽然数组个数没有100，但接受数据时间超过了10分钟，就批量存入msyql
            time_c = get_time() - start_time4
            if time_c > 300:
                if len(data_list4) > 0:
                    try:
                        dbpool.Pool().insert_many_temp('shopee_sub_product', data_list4,'shopee_sub_product')
                    except Exception:
                        traceback.print_exc()
                        for product in data_list4:
                            cache_sub_product_insert.put(json.dumps(dict(product),cls = DateEnconding))

                # 重置 count = 0 start_time
                count4 = 0
                start_time4 = get_time()
                data_list4 = []


# 子产品变更插入
def sub_product_change_insert():
    start_time5 = get_time()
    count5 = 0
    data_list5 = []
    while True:
        sub_product = cache_sub_product_change_insert.get_nowait()
        if sub_product is not None:
            sub_product = json.loads(sub_product.decode())
            data_list5.append(sub_product)
            count5 += 1
        else:
            time.sleep(5)

        # 首先判断数组内数据个数是否达到100，达到，就批量存入msyql
        if count5 > 200:
            try:
                dbpool.Pool().insert_many_temp('shopee_sub_product_change', data_list5,'shopee_sub_product_change')
            except Exception:
                traceback.print_exc()
                for product in data_list5:
                    print(product)
                    cache_sub_product_change_insert.put(json.dumps(dict(product),cls = DateEnconding))

    # 重置 count start_time
            count5 = 0
            start_time5 = get_time()
            data_list5 = []

        else:
            # 虽然数组个数没有100，但接受数据时间超过了10分钟，就批量存入msyql
            time_c = get_time() - start_time5
            if time_c > 300:
                if len(data_list5) > 0:
                    try:
                        dbpool.Pool().insert_many_temp('shopee_sub_product_change', data_list5,'shopee_sub_product_change')
                    except Exception:
                        traceback.print_exc()
                        for product in data_list5:
                            cache_sub_product_change_insert.put(json.dumps(dict(product),cls = DateEnconding))

                # 重置 count = 0 start_time
                count5 = 0
                start_time5 = get_time()
                data_list5 = []


# 子产品变更update
def sub_product_update():
    sql = "update shopee_sub_product set sales_attributes=%s ,price=%s ," \
          "before_price=%s ,sold=%s ,quantity=%s ,status = %s ,update_time=%s ,update_by= %s" \
          " where spu= %s and sku= %s"
    start_time6 = get_time()
    count6 = 0
    data_list6 = []
    while True:
        sub_product = cache_sub_product_update.get_nowait()
        if sub_product is not None:
            sub_product = json.loads(sub_product.decode())
            params = (sub_product['sales_attributes'],
                      sub_product['price'],
                      sub_product['before_price'],
                      sub_product['sold'],
                      sub_product['quantity'],
                    sub_product['status'],
                      datetime.datetime.now(),
                      '007',
                      str(sub_product['spu']),
                      str(sub_product['sku']))
            data_list6.append(params)
            count6 += 1
        else:
            time.sleep(5)

        # 首先判断数组内数据个数是否达到100，达到，就批量存入msyql
        if count6 > 200:
            try:
                dbpool.Pool().update_many(sql,'shopee_sub_product update',data_list6)
            except Exception:
                traceback.print_exc()
                for product in data_list6:
                    cache_sub_product_update.put(json.dumps(dict(product),cls = DateEnconding))

            # 重置 count start_time
            count6 = 0
            start_time6 = get_time()
            data_list6 = []

        else:
            # 虽然数组个数没有100，但接受数据时间超过了10分钟，就批量存入msyql
            time_c = get_time() - start_time6
            if time_c > 300:
                if len(data_list6) > 0:
                    try:
                        dbpool.Pool().update_many(sql,'shopee_sub_product update',data_list6)
                    except Exception:
                        traceback.print_exc()
                        for product in data_list6:
                            cache_sub_product_update.put(json.dumps(dict(product),cls = DateEnconding))

                # 重置 count = 0 start_time
                count6 = 0
                start_time6 = get_time()
                data_list6 = []



if __name__ == '__main__':
    t_shop_insert = threading.Thread(target = shop_insert)
    t_shop_insert.start()
    t_shop_change_insert = threading.Thread(target = shop_change_insert)
    t_shop_change_insert.start()
    t_shop_update = threading.Thread(target = shop_update)
    t_shop_update.start()
    t_shop_update_time = threading.Thread(target = shop_update_time)
    t_shop_update_time.start()

    t_product_insert = threading.Thread(target = product_insert)
    t_product_insert.start()
    t_product_change_insert = threading.Thread(target = product_change_insert)
    t_product_change_insert.start()

    t_product_update = threading.Thread(target = product_update)
    t_product_update.start()
    t_product_update_time = threading.Thread(target = product_update_time)
    t_product_update_time.start()

    t_sub_product_insert = threading.Thread(target = sub_product_insert)
    t_sub_product_insert.start()
    t_sub_product_change_insert = threading.Thread(target = sub_product_change_insert)
    t_sub_product_change_insert.start()
    t_sub_product_update = threading.Thread(target = sub_product_update)
    t_sub_product_update.start()
