# Package
from django.conf.urls import url
# Project
from . import views


urlpatterns = (
    url(r'^$', views.HrSearch.as_view()),
    url(r'^export/$', views.HrCSV.as_view()),
    url(r'^geolocation/$', views.HrGeoLocationSearch.as_view()),
)
