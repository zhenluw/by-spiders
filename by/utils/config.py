import socket
ip = socket.gethostbyname(socket.gethostname())

# # Redis数据库地址
redis_host = 'localhost'
# Redis端口
redis_port = 6379
# Redis密码，如无填None
redis_password = ''

# mysql账号
mysql_host='rm-wz951334kg63k127t9o.mysql.rds.aliyuncs.com'
mysql_port=3306
mysql_user='bin_li'
mysql_password='1qaz2wsx'
mysql_db='shopee'

# rabbitmq配置
mq_user = 'lavector'
mq_pass = 'lavector'
mq_queue = 'redbook'
mq_host = '52.82.47.124'
mq_port = 5877


# if ip.startswith("192.168"):
#     redis_host = 'localhost'
#
#     mysql_host='localhost'
#     mysql_port=3306
#     mysql_user='root'
#     mysql_password='123456'
#     mysql_db='zhonghai'




