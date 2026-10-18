from djangorestframework_camel_case.util import underscoreize
from django.http import QueryDict

class CamelCaseQueryParamMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.GET:
            data = underscoreize(request.GET.dict())
            new_get = QueryDict(mutable=True)
            new_get.update(data)
            request.GET = new_get
        
        response = self.get_response(request)
        return response