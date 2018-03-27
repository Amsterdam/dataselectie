# Package
from django.conf.urls import url
# Project
from datasets.brk import views


urlpatterns = (
    url(r'^$', views.BrkSearch.as_view()),
    url(r'^export/$', views.BrkCSV.as_view()),
    url(r'^geolocation/$', views.BrkGeoLocationSearch.as_view()),
)
