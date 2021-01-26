import hashlib
import random
import string
import time
import requests
import urllib3
# import urllib3.contrib.pyopenssl
# requests.packages.urllib3.disable_warnings()
# requests.adapters.DEFAULT_RETRIES = 5   #增加重连次数
proxy = urllib3.ProxyManager('http://s2.proxy.mayidaili.com:8123', cert_reqs='CERT_NONE')

def response():
    appkey = "175626467"
    secret = "c45206bf2209902ec1415b8bd12cbfa0"
    mayi_proxy ={
        'http':'http://s2.proxy.mayidaili.com:8123'
        ,'https':'http://s2.proxy.mayidaili.com:8123'
    }
    paramMap = {
        "app_key": appkey,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    keys = sorted(paramMap)
    codes = "%s%s%s" % (secret, str().join('%s%s' % (key, paramMap[key]) for key in keys), secret)
    sign = hashlib.md5(codes.encode('utf-8')).hexdigest().upper()
    paramMap["sign"] = sign
    keys = paramMap.keys()
    authHeader = "MYH-AUTH-MD5 " + str('&').join('%s=%s' % (key, paramMap[key]) for key in keys)
    s = requests.session()
    s.headers.update({'Mayi-Authorization': authHeader})
    s.proxies.update(mayi_proxy)
    s.keep_alive = False
    return s


def response2():
    appkey = "175626467"
    secret = "c45206bf2209902ec1415b8bd12cbfa0"

    paramMap = {
        "app_key": appkey,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    keys = sorted(paramMap)
    codes = "%s%s%s" % (secret, str().join('%s%s' % (key, paramMap[key]) for key in keys), secret)
    sign = hashlib.md5(codes.encode('utf-8')).hexdigest().upper()
    paramMap["sign"] = sign
    keys = paramMap.keys()
    authHeader = "MYH-AUTH-MD5 " + str('&').join('%s=%s' % (key, paramMap[key]) for key in keys)
    return {'Mayi-Authorization': authHeader}


def requests_get(url,header):
    mayi_proxy ={
        'http':'http://s2.proxy.mayidaili.com:8123'
        ,'https':'http://s2.proxy.mayidaili.com:8123'
    }
    header.update(response2())
    requests.packages.urllib3.disable_warnings()
    response = requests.get(url, proxies=mayi_proxy, headers=header,  allow_redirects=False,  verify=False,timeout=20)
    response.encoding = 'gbk'
    return response.text,response.status_code



def html_get(url,header):
    s = response()
    pg = s.get(url, timeout=(300, 270), headers=header,verify=False)  # tuple: 300 代表 connect timeout, 270 代表 read timeout
    pg.encoding = 'utf-8'
    return pg.text


def html_get_gbk(url,header):
    pg = response().get(url, timeout=(300, 270), headers=header,verify=False)  # tuple: 300 代表 connect timeout, 270 代表 read timeout
    pg.encoding = 'gbk'
    return pg.text,pg.status_code


def html_get_code(url,header):
    pg = response().get(url, timeout=(300, 270), headers=header,verify=False)  # tuple: 300 代表 connect timeout, 270 代表 read timeout
    pg.encoding = 'utf-8'
    return pg.text,pg.status_code


def html_get_cookie(url,header,cookie):
    s = response()
    s.cookies=cookie
    pg = s.get(url, timeout=(300, 270), headers=header,verify=False)  # tuple: 300 代表 connect timeout, 270 代表 read timeout
    pg.encoding = 'utf-8'
    return pg.text



def html_post(url,header,datas):
    # pg = response().post(url, timeout=(300, 270), headers=header,data=datas,verify=False)  # tuple: 300 代表 connect timeout, 270 代表 read timeout
    pg = response().post(url,  headers=header,data=datas,verify=False)  # tuple: 300 代表 connect timeout, 270 代表 read timeout
    pg.encoding = 'utf-8'
    return pg.text

def html_post_code(url,header,datas):
    # pg = response().post(url, timeout=(300, 270), headers=header,data=datas,verify=False)  # tuple: 300 代表 connect timeout, 270 代表 read timeout
    pg = response().post(url,  headers=header,data=datas,verify=False)  # tuple: 300 代表 connect timeout, 270 代表 read timeout
    pg.encoding = 'utf-8'
    return pg.text,pg.status_code


def html_location(url,headers):
    # headers={"Content-Type":"application/json"}
    pg = response().get(url, timeout=(300, 270), headers=headers,verify=False)  # tuple: 300 代表 connect timeout, 270 代表 read timeout
    # reditList = pg.history#可以看出获取的是一个地址序列
    # print(f'获取重定向的历史记录：{reditList}')
    # print(f'获取第一次重定向的headers头部信息：{reditList[0].headers}')
    # print(f'获取重定向最终的url：{reditList[len(reditList)-1].headers["location"]}')
    # return reditList[len(reditList)-1].headers["location"]
    return pg


def html_location2(url,headers,datas):
    pg = response().post(url, timeout=(300, 270), headers=headers,data=datas,verify=False)  # tuple: 300 代表 connect timeout, 270 代表 read timeout
    reditList = pg.history#可以看出获取的是一个地址序列
    print(f'获取重定向的历史记录：{reditList}')
    print(f'获取第一次重定向的headers头部信息：{reditList[0].headers}')
    print(f'获取重定向最终的url：{reditList[len(reditList)-1].headers["location"]}')
    return reditList[len(reditList)-1].headers["location"]


def urllib3_get(url,header):
    appkey = "175626467"
    secret = "c45206bf2209902ec1415b8bd12cbfa0"
    paramMap = {
        "app_key": appkey,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    keys = sorted(paramMap)
    codes = "%s%s%s" % (secret, str().join('%s%s' % (key, paramMap[key]) for key in keys), secret)
    sign = hashlib.md5(codes.encode('utf-8')).hexdigest().upper()
    paramMap["sign"] = sign
    keys = paramMap.keys()
    authHeader = "MYH-AUTH-MD5 " + str('&').join('%s=%s' % (key, paramMap[key]) for key in keys)

    header.update({'Mayi-Authorization': authHeader})
    response = proxy.request('GET',url,headers=header)
    html = response.data.decode()
    response.release_conn()
    # proxy.clear()
    return html,response.status



if __name__ == '__main__':
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.79 Safari/537.36'
    }
    html = requests_get('http://httpbin.org/ip',header)
    # html = urllib3_get('https://www.cnblogs.com/leooys/p/7096552.html',header)
    # html = get_requests('http://httpbin.org/ip',header)
    print(html)

    # url ='https://www.xiaohongshu.com/discovery/item/5fcf5d02000000000100103f'
    # date = time.strftime("%Y%m%d", time.localtime())
    # words = string.ascii_lowercase + string.digits
    # ran = ''.join([random.choice(words).lower() for _ in range(8)])
    # timestamp2 = date + 'e0da970f5deca9dd' + ran
    #
    # header = {
    #     "referer": f'https://www.xiaohongshu.com/web-login/canvas?redirectPath={url}',
    #      'cookie': 'timestamp2={}; '.format(timestamp2),
    #     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.79 Safari/537.36',
    # }
    #
    # header = {
    #     "Host": 'www.xiaohongshu.com',
    #     # 'cookie': 'xhsTrackerId=e96c6c31-aa92-4cd5-ccbc-d446ea7e46d9; extra_exp_ids=gif_exp1,ques_exp1; xhs_spses.5dde=*; xhs_spid.5dde=598ff11fb8ac3cc1.1608184977.1.1608184980.1608184977.ff7d0502-6e3f-4061-a3e6-bd37685d480d',
    #     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:82.0) Gecko/20100101 Firefox/82.0',
    # }
    #
    # print(html_get(url,header))
    # html = urllib3_get(url,header)
    # print(html)
