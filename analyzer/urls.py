from django.conf.urls import url

from . import views


from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    url(r'^queries/$', views.supported_queries, name='supported_queries'),
    url(r'^query/$', views.query, name='query'),
]


urlpatterns = format_suffix_patterns(urlpatterns)