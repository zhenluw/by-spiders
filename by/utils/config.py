import socket
ip = socket.gethostbyname(socket.gethostname())

# # Redis数据库地址
redis_host = 'r-m5efmwd86jari4xiq4pd.redis.rds.aliyuncs.com'
# Redis端口
redis_port = 6379
# Redis密码，如无填None
redis_password = '1qaz@WSX'
# 库
redis_db = 11
# redis_db = 12

# mysql账号
mysql_host = 'rm-wz951334kg63k127t9o.mysql.rds.aliyuncs.com'
mysql_port = 3306
mysql_user = 'bin_li'
mysql_password = '1qaz2wsx'
mysql_db = 'shopee'
# mysql_db = 'shopee_test'


# if ip.startswith("192.168"):
#     redis_host = 'localhost'
#     redis_password = ''

    # mysql_host='localhost'
    # mysql_port=3306
    # mysql_user='root'
    # mysql_password='123456'
    # mysql_db='test'




