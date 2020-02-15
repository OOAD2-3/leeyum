from django.http import HttpResponse

from leeyum.views import BaseViewSet, BaseSerializer


class ArticleSerializer(BaseSerializer):
    pass


class ArticleViewSet(BaseViewSet):
    pass

from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def test(req):
    name = req.POST.get('name')
    file = req.FILES.get('file')
    return HttpResponse('OK')
