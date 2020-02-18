import json

from django.utils.deprecation import MiddlewareMixin


class CtxMiddleware(MiddlewareMixin):

    def process_request(self, request):
        if request.META.get('CONTENT_TYPE') == 'application/json' and request.method == 'POST':
            request.json_data = json.loads(request.body)
