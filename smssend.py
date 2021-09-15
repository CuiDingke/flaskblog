import sys
from typing import List
from alibabacloud_dysmsapi20170525.client import Client as Dysmsapi20170525Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_dysmsapi20170525 import models as dysmsapi_20170525_models


class Sample:
    def __init__(self):
        pass

    @staticmethod
    def create_client(
            access_key_id: 'LTAI5tRy1fzCr6t6AMc7z3bw',
            access_key_secret: 'JmnzKXdQ81qoAYui9w8DksJ1wm7Hog',
    ) -> Dysmsapi20170525Client:
        config = open_api_models.Config(
            # 您的AccessKey ID,
            access_key_id=access_key_id,
            # 您的AccessKey Secret,
            access_key_secret=access_key_secret
        )
        # 访问的域名
        config.endpoint = 'dysmsapi.aliyuncs.com'
        return Dysmsapi20170525Client(config)

    @staticmethod
    def main(
            args: List[str],
    ) -> None:
        client = Sample.create_client('accessKeyId', 'accessKeySecret')
        add_sms_sign_request = dysmsapi_20170525_models.AddSmsSignRequest(
            phone_numbers='test',
            sign_name='1',
            template_code='test'
        )
        # 复制代码运行请自行打印 API 的返回值
        client.add_sms_sign(add_sms_sign_request)

    @staticmethod
    async def main_async(
            args: List[str],
    ) -> None:
        client = Sample.create_client('accessKeyId', 'accessKeySecret')
        add_sms_sign_request = dysmsapi_20170525_models.AddSmsSignRequest(
            phone_numbers='15736980819',
            sign_name='1',
            template_code='SMS_223584739'
        )
        # 复制代码运行请自行打印 API 的返回值
        await client.add_sms_sign_async(add_sms_sign_request)


if __name__ == '__main__':
    Sample.main(sys.argv[1:])
