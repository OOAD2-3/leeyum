import oss2
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest
from leeyum.domain.utils import validate_phone_number
from sensitive_settings import access_key_id, access_secret

__all__ = ('ALI_SMS', 'ALI_STORAGE')


class AliSMS(object):
    """
    阿里短信服务
    Short Message Service
    """

    domain = 'dysmsapi.aliyuncs.com'
    version = '2017-05-25'
    action_name = 'SendSms'

    sign_name = ''
    template_code = ''

    def __init__(self):
        self.client = AcsClient(access_key_id, access_secret, 'cn-hangzhou')
        self.request = self.__init_request()

    def __init_request(self):
        """
        初始化短信发送项
        """
        request = CommonRequest()
        request.set_accept_format('json')
        request.set_domain(self.domain)
        request.set_method('POST')
        request.set_protocol_type('https')  # https | http
        request.set_version(self.version)
        request.set_action_name(self.action_name)

        request.add_query_param('RegionId', "cn-hangzhou")
        request.add_query_param('SignName', self.sign_name)
        request.add_query_param('TemplateCode', self.template_code)
        return request

    def send_sms(self, phone_number, code):
        """
        短信发送执行体
        """
        validate_phone_number(phone_number)
        self.request.add_query_param('PhoneNumbers', phone_number)
        self.request.add_query_param('TemplateParam', code)
        response = self.client.do_action_with_exception(self.request)
        return response


class AliStorage(object):
    """
    阿里仓储服务
    """
    def __init__(self):
        return
        self.bucket_name = ''
        self.endpoint = ''
        self.bucket = oss2.Bucket(oss2.Auth(access_key_id, access_secret), self.endpoint, self.bucket_name)

    def upload(self, file):
        file_name = ''
        self.bucket.put_object(file_name, file)


ALI_SMS = AliSMS()
ALI_STORAGE = AliStorage()