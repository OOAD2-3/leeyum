import oss2
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest
from leeyum.domain.utils import validate_phone_number, to_sha1_string
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

    sign_name = '流云校园'
    template_code = 'SMS_183791052'

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
        self.request.add_query_param('TemplateParam', {"code": code})
        response = self.client.do_action_with_exception(self.request)
        return response


class AliStorage(object):
    """
    阿里仓储服务
    """
    def __init__(self):
        self.bucket_name = 'leeyum-bucket'
        self.endpoint = 'oss-cn-hangzhou.aliyuncs.com'
        self.bucket = oss2.Bucket(oss2.Auth(access_key_id, access_secret), self.endpoint, self.bucket_name)

    def upload(self, file_name, file, prefix=''):
        def get_file_name():
            pic_name_format = '{}.{}'
            name = ''
            try:
                suffix = file_name.split('.')[-1]
                name = pic_name_format.format(to_sha1_string(file_name), suffix)
            except:
                name = to_sha1_string(file_name)

            return name if not prefix else '{}.{}'.format(prefix, name)

        result = self.bucket.put_object(get_file_name(), file)
        return result


ALI_SMS = AliSMS()
ALI_STORAGE = AliStorage()
