from django.conf.urls import url

from . import views

# careful here, since this is just the base forwarded
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^upload/$', views.rpt_upload_plain, name='rpt_upload'),
]