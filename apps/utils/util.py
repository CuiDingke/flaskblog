# 像网易云信发送请求，帮助后台发送短信息
import hashlib
import json

import random
from time import time
import requests
import os

from flask import session
from qiniu import Auth, put_file, etag, put_data, BucketManager
import qiniu.config
# 需要填写你的 Access Key 和 Secret Key
from apps.article.models import Article_category
from apps.user.models import User
from settings import Config


def util_sendmsg(mobile):
    url = 'https://api.netease.im/sms/sendcode.action'
    data = {
        'mobile': mobile,  # 你的手机号码
    }
    AppSecret = '86b36e58e25e'
    AppKey = '07f216ca802c41457e1b229ab89b0678'
    # json类型
    Nonce = 'qweqdqwd12e01029i0dw0qwd'  # 这个字符串时随机的长度不大于128，随便设
    CurTime = str(int((time() * 1000)))  # 采用时间戳
    content = AppSecret + Nonce + CurTime
    CheckSum = hashlib.sha1(content.encode()).hexdigest()  # 对上述进行按要求哈希
    headers = {  # 设置请求头
        'AppKey': AppKey,
        'Nonce': Nonce,
        'CurTime': CurTime,
        'CheckSum': CheckSum
    }

    response = requests.post(url, data=data, headers=headers)  # 发送post请求
    str_result = response.text
    json_result = json.loads(str_result)

    return json_result


def upload_qiniu(filestorage):
    access_key = 'dj_L1cKqSBBKftMLyVUuXnlDwnkeZmZFtfVwIBKm'
    secret_key = 'rRdqBiMmyXMu-MTUBnavP385NX5nu5NOpc1wAAmr'

    # 构建鉴权对象
    q = Auth(access_key, secret_key)

    # 要上传的空间
    bucket_name = 'chuanblog01'

    # 上传后保存的文件名  这个是个变量
    # 获取照片的 名.扩展名
    filename = filestorage.filename
    # 产生随机值
    rran = random.randint(1, 1000)
    # 扩展名
    suffix = filename.rsplit('.')[-1]
    # 名====》filename.rsplit('.')[0]  扩展名=====》filename.rsplit('.')[-1]
    key = filename.rsplit('.')[0] + '_' + str(rran) + '.' + suffix
    # key = 'my-python-logo.png'

    # 生成上传 Token，可以指定过期时间等
    token = q.upload_token(bucket_name, key, 3600)

    # 要上传文件的本地路径
    # localfile = os.path.join(Config.UPLOAD_ICON_DIR, '646173.jpg')
    # ret, info = put_file(token, key, localfile, version='v2')

    # filestorage.read()获取二进制流
    ret, info = put_data(token, key, filestorage.read())
    # print(info)
    # print(ret)
    # 返回值  不要返回错误  在后端用的时候也不要搞错了  懂吗
    return ret, info


def del_qiniu(PhotoFile):
    access_key = 'dj_L1cKqSBBKftMLyVUuXnlDwnkeZmZFtfVwIBKm'
    secret_key = 'rRdqBiMmyXMu-MTUBnavP385NX5nu5NOpc1wAAmr'

    # 构建鉴权对象
    q = Auth(access_key, secret_key)

    # 初始化BucketManager
    bucket = BucketManager(q)

    # 要上传的空间
    bucket_name = 'chuanblog01'
    key = PhotoFile

    ret, info = bucket.delete(bucket_name, key)
    return info


def user_type():
    types = Article_category.query.all()
    user = None
    user_id = session.get('uid', None)
    if user_id:
        user = User.query.get(user_id)
    return user, types
