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
print(patch)
print(len(patch))

