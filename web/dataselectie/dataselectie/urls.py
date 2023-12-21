# Packages
import re
from django.conf.urls import include, url
from django.urls import path
from django.http import HttpResponse
from django.template import loader
from dataselectie import settings

def openapi(request):
    """
    This will serve a template for the openapi.yml with settings
    for production and acceptation filled in
    TODO : If we now how to do local OAuth authorization we can adapt this also
    for local openapi.yml testing
    """
    template = loader.get_template('openapi.yml')
    match = re.search(r'acc.', settings.DATAPUNT_API_URL)
    prefix = 'acc.' if match else ''
    context = {
        'acc_prod_prefix': prefix
    }
    return HttpResponse(template.render(context, request))


urlpatterns = [
    # url(r'^admin/', admin.site.urls),
    url(r'^dataselectie/bag/', include('datasets.bag.urls')),
    url(r'^dataselectie/brk/', include('datasets.brk.urls')),
    url(r'^dataselectie/hr/', include('datasets.hr.urls')),
    url(r'^status/', include('health.urls')),
    url(r'^dataselectie/api-docs/openapi.yml', openapi)
]
