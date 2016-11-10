# Packages
from django.conf.urls import include, url

urlpatterns = [
    # url(r'^admin/', admin.site.urls),
    url(r'^dataselectie/bag/', include('datasets.bag.urls')),
    url(r'^dataselectie/hr/', include('datasets.hr.urls')),
    url(r'^status/', include('health.urls'))
]
