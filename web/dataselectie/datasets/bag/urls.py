# Package
from django.conf.urls import url
# Project
from . import views


urlpatterns = (
    url(r'^$', views.BagSearch.as_view()),
    url(r'^export/$', views.BagCSV.as_view()),
    url(r'^geolocation/$', views.BagGeoLocationSearch.as_view()),
)
