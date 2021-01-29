"""
 * @Project_Name: by-spiders
 * @DESCRIPTION:
 * @Author: wzl
 * @Date: 2021/1/28 12:53
 
"""
import json_tools

src = {'numbers': [1, 3, 4, 8], 'foo': 'bar'}
dst = {'numbers': [1, 3, 4, 8,8], 'foo': 'bar6'}
patch = json_tools.diff(src, dst)
# print(patch)
# print(len(patch))
print(len('各位关注CYD插画留学的薯宝宝们，马上过年啦，抽个精致小巧的吸尘器，把你的小世界打扫的干干净净哦。奖品:小米米家随手吸尘器活动时间2021年1月26日到2021年2月10日开奖时间:2021年2月18日小米超便携吸尘器，家里，车里，办公室里，犄角旮旯，轻松吸干净。'))
