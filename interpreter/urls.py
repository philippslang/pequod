from django.conf.urls import url

from . import views


from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    #url(r'^request/$', altviews.request, name='request'),
    url(r'^request/$', views.request, name='request'),
    url(r'^results/$', views.results_list, name='results_list'),
    url(r'^requests/$', views.request_list, name='request_list'),
    url(r'^requestsfly/$', views.requestfly_list, name='request_list'),
    url(r'^responses/$', views.response_list, name='request_list'),
]


urlpatterns = format_suffix_patterns(urlpatterns)