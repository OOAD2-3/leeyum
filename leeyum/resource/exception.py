class BusinessException(Exception):
    business_code = 400
    business_message = 'Error occur'

    def __init__(self, message=None):
        if message:
            self.business_message = self.business_message + ': ' + message

        super(BusinessException).__init__(self.business_message)


class PhoneNumberWrongException(BusinessException):
    business_code = 400
    business_message = 'Phone number wrong'
