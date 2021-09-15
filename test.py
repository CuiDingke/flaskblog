# filename = '1154.jpg'
# result = filename.rsplit('.')
# print(result[-1])
# f = filename.endswith('jpg')
# print(f)

# -*- coding: utf-8 -*-
# flake8: noqa
# import os
#
# from qiniu import Auth, put_file, etag
# import qiniu.config
#
# # 需要填写你的 Access Key 和 Secret Key
# from settings import Config
#
# access_key = 'dj_L1cKqSBBKftMLyVUuXnlDwnkeZmZFtfVwIBKm'
# secret_key = 'rRdqBiMmyXMu-MTUBnavP385NX5nu5NOpc1wAAmr'
#
# # 构建鉴权对象
# q = Auth(access_key, secret_key)
#
# # 要上传的空间
# bucket_name = 'chuanblog'
#
# # 上传后保存的文件名
# key = 'my-python-logo.png'
#
# # 生成上传 Token，可以指定过期时间等
# token = q.upload_token(bucket_name, key, 3600)
#
# # 要上传文件的本地路径
# localfile = os.path.join(Config.UPLOAD_ICON_DIR, '646173.jpg')
#
# ret, info = put_file(token, key, localfile, version='v2')
# print(info.status_code)
# print(info.text_body)
# print(ret['key'])
# # assert ret['key'] == key
# # assert ret['hash'] == etag(localfile)


# -*- coding: utf-8 -*-
# flake8: noqa
from qiniu import Auth
from qiniu import BucketManager

access_key = 'dj_L1cKqSBBKftMLyVUuXnlDwnkeZmZFtfVwIBKm'
secret_key = 'rRdqBiMmyXMu-MTUBnavP385NX5nu5NOpc1wAAmr'

#初始化Auth状态
q = Auth(access_key, secret_key)

#初始化BucketManager
bucket = BucketManager(q)

#你要测试的空间， 并且这个key在你空间中存在
bucket_name = 'chuanblog'
key = '矩形56_930.png'

#获取文件的状态信息
ret, info = bucket.stat(bucket_name, key)
print(info)
assert 'hash' in ret
