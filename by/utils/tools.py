"""
 * @Project_Name: by-spiders
 * @DESCRIPTION:
 * @Author: wzl
 * @Date: 2021/1/27 16:43
"""

import datetime
import json
import random
import time
import re
import traceback

# from fake_useragent import UserAgent


def str_to_timsStamp(timeStr):
    int(time.mktime(time.strptime(timeStr, "%Y-%m-%d")))


def str_to_time(timeStr):
    try:
        return datetime.datetime.strptime(timeStr, '%Y-%m-%d')
    except Exception:
        try:
            return datetime.datetime.strptime(timeStr, '%Y-%m-%d %H')
        except Exception:
            try:
                return datetime.datetime.strptime(timeStr, '%Y-%m-%d %H:%M')
            except Exception:
                try:
                    return datetime.datetime.strptime(timeStr, '%Y-%m-%d %H:%M:%S')
                except Exception as e:
                    traceback.print_exc()


def timsStamp_to_str(timeStamp):
    return time.strftime("%Y-%m-%d", time.localtime(timeStamp))


def timsStamp_to_str2(timeStamp):
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timeStamp))


#获取给定时间段内的每一天
def getBetweenDay(begin_date,end_date):
    date_list = []
    begin_date = datetime.datetime.strptime(begin_date, "%Y-%m-%d")
    end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d")
    while begin_date <= end_date:
        date_str = begin_date.strftime("%Y-%m-%d")
        date_list.append(date_str)
        begin_date += datetime.timedelta(days=1)# days=可以填写任意值，表示切分的间隔天数
    return date_list



class DateEnconding(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, bytes):
            return str(obj, encoding='utf-8')
        if isinstance(obj, datetime.date):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        return json.JSONEncoder.default(self, obj)


def sleep_random_time7():
    sleep_t = random.uniform(7, 10)
    # print('休眠' + str(sleep_t) + '秒')
    time.sleep(sleep_t)


def sleep_random_time5():
    sleep_t = random.uniform(5, 7)
    # print('休眠' + str(sleep_t) + '秒')
    time.sleep(sleep_t)

def sleep_random_time3():
    sleep_t = random.uniform(3, 5)
    # print('休眠' + str(sleep_t) + '秒')
    time.sleep(sleep_t)


def sleep_random_time2():
    sleep_t = random.uniform(2, 4)
    # print('休眠' + str(sleep_t) + '秒')
    time.sleep(sleep_t)



def sleep_random_time1():
    sleep_t = random.uniform(1, 3)
    # print('休眠' + str(sleep_t) + '秒')
    time.sleep(sleep_t)


def parse_time(date):
    if '转赞人数' in date:
        date = date.split('转赞人数')[0].strip()
    if re.match('今天', date):
        date = datetime.datetime.now().strftime('%Y-%m-%d')+' '+date.replace('今天', '').strip()+ ':00'
        return date
    if re.match('刚刚', date):
        date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        return date
    if re.match('\d+秒前', date):
        seconds = re.match('(\d+)', date).group(1)
        date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time() - float(seconds) ))
        return date
    if re.match('\d+分钟前', date):
        minute = re.match('(\d+)', date).group(1)
        date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time() - float(minute) * 60))
        return date
    if re.match('\d+小时前', date):
        hour = re.match('(\d+)', date).group(1)
        date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time() - float(hour) * 60 * 60))
        return date
    if re.match('昨天.*', date):
        date = re.match('昨天(.*)', date).group(1).strip()
        date = time.strftime('%Y-%m-%d', time.localtime(time.time() - 24 * 60 * 60)) + ' ' + date
        date = str_to_time(date)
        return str(date)
    if re.match('\d{1,2}-\d{1,2}', date):
        date = time.strftime('%Y-', time.localtime()) + date
        date = str_to_time(date)
        return str(date)
    if re.match('\d{1,2}月\d{1,2}日', date):
        date = date.replace('月','-')
        date = date.replace('日','')
        date = time.strftime('%Y-', time.localtime()) + date
        date = str_to_time(date)
        return str(date)
    if re.match('\d{4}年\d{1,2}月\d{1,2}日', date):
        date = date.replace('年','-')
        date = date.replace('月','-')
        date = date.replace('日','')
        # if ':' in date:
        #     date = date + ':00'
        date = str_to_time(date)
        return str(date)
    if re.match('\d{4}年\d{1,2}月', date):
        date = date.replace('年','-')
        date = date.replace('月','-')
        date = date + '01'
        return date

    date = str_to_time(date)
    return str(date)


#获取给定时间段内的每一天
def getBetweenDay(begin_date,end_date):
    date_list = []
    begin_date = datetime.datetime.strptime(begin_date, "%Y-%m-%d")
    end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d")
    while begin_date <= end_date:
        date_str = begin_date.strftime("%Y-%m-%d")
        date_list.append(date_str)
        begin_date += datetime.timedelta(days=1)# days=可以填写任意值，表示切分的间隔天数
    return date_list


def calculate_age(birth_s):
    birth_d = datetime.datetime.strptime(str(birth_s), "%Y-%m-%d %H:%M:%S")
    today_d = datetime.datetime.now()
    birth_t = birth_d.replace(year=today_d.year)
    if today_d > birth_t:
        age = today_d.year - birth_d.year
    else:
        age = today_d.year - birth_d.year - 1
    # print('出生日期：%s' % birth_d)
    # print('今年生日：%s' % birth_t)
    # print('今天日期：%s' % today_d)
    # print('如果今天日期大于今年生日，今年-出生年=年龄')
    # print('如果今天日期不大于今年生日，今年-出生年-1=年龄')
    # print('年龄：%s' % age)
    return age


def replace_special_string(s):
    return re.sub(u"([^\u4e00-\u9fa5\u0030-\u0039\u0041-\u005a\u0061-\u007a])","",s)
    # return re.sub('[a-zA-Z0-9\'!"#$%&\'()*+,-./:;<=>?@，。?★、…【】《》？“”\‘\'！[\\]^_`{|}~\s]+', "", s)
    # return re.sub('[\'!"#$%&\'()*+,-./:;<=>?@，。?★、…【】《》？“”\‘\'！[\\]^_`{|}~\s]+', "", s)


def replace_special_num(s):
    return re.sub("\D", "", s)


# def ua():
#     return UserAgent().random


def random_ua():
    ua = [
         "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4830.198 Safari/537.36",
         # "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0",
         # "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko",
        # "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
        #  "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36 Edg/87.0.664.66"


         # 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
         # 'Opera/9.80 (Windows NT 6.1; U; zh-cn) Presto/2.9.168 Version/11.50',
         # 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; GTB7.0)',
         # 'Mozilla/5.0 (Windows; U; Windows NT 6.1; ) AppleWebKit/534.12 (KHTML, like Gecko) Maxthon/3.0 Safari/534.12',
         # 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/534.3 (KHTML, like Gecko) Chrome/6.0.472.33 Safari/534.3 SE 2.X MetaSr 1.0',
         # 'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; InfoPath.3; .NET4.0C; .NET4.0E)',
         # 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/13.0.782.41 Safari/535.1 QQBrowser/6.9.11079.201',
         # "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko",
    ]
    num = random.randint(0, len(ua)-1)
    # print(num)
    return ua[num]
    # return ua[0]


def get_date():
    today=datetime.date.today()
    oneday=datetime.timedelta(days=1)
    yesterday=today-oneday
    return today,yesterday


if __name__ == '__main__':

    a='最爱吃的就是安利\\(//∇//)\\11aa'
    # dd = datetime.datetime.strptime(a, '%Y-%m-%d %H')
    # print(dd)
    # print(replace_special_string(a))
    print(random_ua())
