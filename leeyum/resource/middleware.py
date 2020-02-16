from django.utils.deprecation import MiddlewareMixin


class CtxMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # TODO 判断登录态 非登录用户（无session信息，即request.user为AnonymousUser）
        return
