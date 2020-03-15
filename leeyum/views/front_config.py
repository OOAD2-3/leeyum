from django.core.paginator import Paginator

from leeyum.domain.models import ExpressNewsStore
from leeyum.views import BaseViewSet, JSONResponse


class FrontConfigViewSet(BaseViewSet):
    def express_news(self, request):
        page = request.GET.get('page', 1)
        page_size = request.GET.get('page_size', 10)

        news = [obj.to_dict() for obj in ExpressNewsStore.objects.all().reverse()]
        paginator = Paginator(news, page_size)
        page_info = paginator.page(page)
        return JSONResponse({"article_list": page_info.object_list, "has_next_page": page_info.has_next(),
                             "page": paginator.num_pages, "page_size": paginator.per_page, "total": paginator.count})

    def page_config(self, request):
        config_data = {
            "logo": "",
            "banner_pics": [
                "",
                "",
            ],
            "page_foot": {
                "contact": {
                    "qq": "123456",
                    "tel": "13063031520",
                    "wechat_QR_code": ""
                },
                "address": "福建省厦门市思明区厦门大学学生公寓",
                "copyright": "版权所有 © All Rights Reserved，憨ICP备1234567号-999"
            }
        }
        return JSONResponse(data=config_data)
